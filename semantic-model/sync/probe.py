#!/usr/bin/env python3
"""S2 日探针（脚本化）——W16-D7 §6.2 坑1 的直接修复。

修复目标：探针从未脚本化是人肉流程，cd 顺序 fallback 曾命中 /root/langchat-docs
（含同名 lanlnk/ 目录树）得假值 87（真仓 /root/docs = 24）。本脚本钉死三仓绝对路径，
杜绝错仓；同时把 G-07 的「数表」探针接进日常：behind 计数 + canonical 表集合 diff
（git show origin/main:... 秒级，无 pull 依赖）。

用法：
  python3 sync/probe.py                 # 人读输出
  python3 sync/probe.py --json          # 机读 JSON（S2 日探针标准输出）
  python3 sync/probe.py --baseline governance/canonical-baseline-w40.txt

判定：
  - behind 任一仓 > 300 → BARRIER（S4 挡板口径，沿用）
  - canonical 集合 diff 有增量且 cited=0 → DRIFT（G-07 口径，须 citing change）
  - 其余 → OK
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# 三仓绝对路径——钉死，禁止 cwd fallback（坑1 教训）
REPOS = {
    "lnkcre": "/root/lnkcre",
    "docs": "/root/docs",
    "LnkChatBI": "/root/LnkChatBI",
}
CANONICAL_PATH = "backend/internal/platform/database/testdata/canonical_tables.txt"
BASELINE = Path(__file__).resolve().parent.parent / "governance" / "canonical-baseline-w40.txt"
BARRIER = 300


def run_git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git -C {repo} {' '.join(args)} 失败: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def table_set(lines) -> set:
    return {l.strip() for l in lines if l.strip() and not l.startswith("#")}


def probe() -> dict:
    out = {"ts_repos": {}, "heads_behind": {}, "canonical": {}, "verdict": None, "notes": []}
    # 1) 三仓 fetch（只 fetch 不 pull）+ behind 计数
    for name, path in REPOS.items():
        run_git(path, "fetch", "origin")
        head = run_git(path, "rev-parse", "--short", "HEAD")
        origin = run_git(path, "rev-parse", "--short", "origin/main")
        behind = int(run_git(path, "rev-list", "--count", "HEAD..origin/main"))
        out["ts_repos"][name] = {"path": path, "head": head, "origin_main": origin}
        out["heads_behind"][name] = behind

    # 2) canonical 表集合 diff（origin/main，无 pull 依赖）
    raw = run_git(REPOS["lnkcre"], "show", f"origin/main:{CANONICAL_PATH}")
    origin_tables = table_set(raw.splitlines())
    base_tables = table_set(BASELINE.read_text().splitlines())
    added = sorted(origin_tables - base_tables)
    removed = sorted(base_tables - origin_tables)
    fp = lambda s: hashlib.sha256("\n".join(sorted(s)).encode()).hexdigest()[:16]
    out["canonical"] = {
        "baseline_file": str(BASELINE.name),
        "baseline_count": len(base_tables),
        "origin_main_count": len(origin_tables),
        "set_sha256_16": {"baseline": fp(base_tables), "origin_main": fp(origin_tables)},
        "added": added,
        "removed": removed,
    }

    # 3) 判定
    max_behind = max(out["heads_behind"].values())
    drifted = bool(added or removed)
    if max_behind > BARRIER:
        out["verdict"] = "BARRIER"
        out["notes"].append(f"behind max {max_behind} > {BARRIER}（S4 挡板）")
    elif drifted:
        out["verdict"] = "DRIFT"
        out["notes"].append("canonical 集合漂移：须 citing change（登记 or 显式不入域）后经 digest 裁决重冻结")
    else:
        out["verdict"] = "OK"
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        result = probe()
    except Exception as e:
        print(json.dumps({"verdict": "FATAL", "error": str(e)}, ensure_ascii=False) if a.json
              else f"FATAL: {e}", file=sys.stderr)
        sys.exit(2)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"S2 探针 · 判决 {result['verdict']}")
        for n, b in result["heads_behind"].items():
            print(f"  {n:10s} behind {b:4d}  head {result['ts_repos'][n]['head']}")
        c = result["canonical"]
        print(f"  canonical  baseline {c['baseline_count']} ({c['baseline_file']}) → origin/main {c['origin_main_count']}"
              f"  +{len(c['added'])}/-{len(c['removed'])}")
        for t in c["added"]:
            print(f"    + {t}")
        for t in c["removed"]:
            print(f"    - {t}")
        for note in result["notes"]:
            print(f"  · {note}")
    sys.exit(0 if result["verdict"] == "OK" else 1)

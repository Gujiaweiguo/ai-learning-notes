#!/usr/bin/env python3
"""G-05 frozen-effect CI 门禁（W16-② 交付）。

两个门，对应 W14-D4 对账登记的两个缺口：
  anchors 门 —— 缺口1「registry 无机器可读代码锚点」：逐锚点对账 effect-registry 五类冻结
    effect 与 lnkcre 代码事实（OK / DRIFTED / BROKEN）。
  registry 门 —— 缺口2「frozen 无 CI 强制」：effect-registry.yaml 冻结清单的任何
    增/删/改，必须带 --change <id> 且该 change 已立案（proposal.md 存在），否则红。

v0.2（2026-09-22，W17-D2 定轨第 5 项）：expect 从子串升级为**定界签名**（边缘词界匹配）。
  治 W16-D2 实验证实的「扩名不改名」盲区：StatusDraft → StatusDraftLegacy 对子串匹配
  不可见（0% 检出）；定界后扩名=签名消失→BROKEN（证据被改写）。
  边界仅加在 pattern 两侧为词字符的边缘：`StatusDraft` 右缘是词字符→加界（防后缀扩名）；
  `func Foo(` 右缘是 `(`→不加界（后随实参是合法命中，非扩名）。首版全边界的误伤
  （7 锚点假 BROKEN）即本条款的实跑证据：定界的对象是标识符边缘，不是任意文本边缘。

用法：
  frozen_effect_ci.py anchors --anchors g05-effect-anchors.yaml --repo /root/lnkcre [--change ID] [--strict] [--json]
  frozen_effect_ci.py registry --old a.yaml --new b.yaml [--change ID] [--changes-dir DIR] [--json]

退出码：0 绿 / 1 红。DRIFTED 默认黄（维护信号）；--strict 下升级为红。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

RED, GREEN, YELLOW = "\033[31m", "\033[32m", "\033[33m"
RESET = "\033[0m"


def word_boundary(pat: str) -> re.Pattern:
    """v0.2 定界签名：仅在 pattern 边缘为词字符的一侧加词边界。
    - 边缘是 [A-Za-z0-9_]（如 `StatusDraft` 右缘）→ 加界：`StatusDraftLegacy` 不再命中（防扩名）；
    - 边缘是非词字符（如 `func Foo(` 的 `(` 右缘）→ 不加界：`(` 后随实参是合法命中。
    首版两侧全加界导致 7 锚点假 BROKEN（expect 以 `(` 结尾、实参被误判扩名）——
    定界的对象是标识符边缘，不是任意文本边缘。"""
    left = r"(?<![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", pat) else ""
    right = r"(?![A-Za-z0-9_])" if re.search(r"[A-Za-z0-9_]$", pat) else ""
    return re.compile(left + re.escape(pat) + right)


def _col(v: str) -> str:
    return {"OK": GREEN, "DRIFTED": YELLOW, "BROKEN": RED, "RED": RED, "GREEN": GREEN}.get(v, "") + v + RESET


def check_anchor(repo: Path, a: dict):
    f = repo / a["file"]
    if not f.exists():
        return "BROKEN", "文件不存在"
    try:
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:  # pragma: no cover
        return "BROKEN", f"读取失败: {e}"
    ln, exp = int(a["line"]), a["expect"]
    rx = word_boundary(exp)  # v0.2 定界签名：扩名/改名一律视为签名变化
    if 1 <= ln <= len(lines) and rx.search(lines[ln - 1]):
        return "OK", ""
    for i, l in enumerate(lines, 1):
        if rx.search(l):
            return "DRIFTED", f"内容位移 {ln} → {i}（上游插删行，需 re-anchor）"
    return "BROKEN", "expect 定界签名已不在文件中（实现证据被改写/删除/扩名——v0.2 盲区闭合）"


def cmd_anchors(args) -> int:
    data = yaml.safe_load(Path(args.anchors).read_text(encoding="utf-8"))
    repo = Path(args.repo)
    results = []
    for eff, spec in data["effects"].items():
        for a in spec["anchors"]:
            v, msg = check_anchor(repo, a)
            results.append({"effect": eff, "file": a["file"], "line": a["line"],
                            "role": a.get("role", ""), "verdict": v, "detail": msg})
    n_ok = sum(r["verdict"] == "OK" for r in results)
    n_drift = sum(r["verdict"] == "DRIFTED" for r in results)
    n_broken = sum(r["verdict"] == "BROKEN" for r in results)

    acked = False
    if n_broken and args.change:
        proposal = Path(args.changes_dir) / args.change / "proposal.md"
        if proposal.exists():
            acked = True

    red = (n_broken > 0 and not acked) or (n_drift > 0 and args.strict)
    summary = {"gate": "anchors", "baseline_commit": data.get("baseline_commit"),
               "total": len(results), "ok": n_ok, "drifted": n_drift, "broken": n_broken,
               "change": args.change, "acknowledged": acked,
               "verdict": "RED" if red else "GREEN"}
    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=1))
    else:
        print(f"== G-05 anchors 门 @ {data.get('baseline_commit', '?')[:9]} ==")
        for r in results:
            print(f"[{_col(r['verdict'])}] {r['effect']:24s} {r['file']}:{r['line']}  {r['detail']}")
        if acked:
            print(f"  BROKEN 已由 change {args.change} 立案承认 → 不红")
        print(f"合计 {len(results)} 锚点：OK {n_ok} / DRIFTED {n_drift} / BROKEN {n_broken} → {_col(summary['verdict'])}")
    return 1 if red else 0


def _sig(e: dict) -> str:
    return hashlib.sha256(json.dumps(e, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def cmd_registry(args) -> int:
    old = {e["id"]: _sig(e) for e in yaml.safe_load(Path(args.old).read_text(encoding="utf-8"))["effect_types"]}
    new = {e["id"]: _sig(e) for e in yaml.safe_load(Path(args.new).read_text(encoding="utf-8"))["effect_types"]}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(i for i in set(old) & set(new) if old[i] != new[i])
    diffs = {"added": added, "removed": removed, "modified": modified}

    if not (added or removed or modified):
        out = {"gate": "registry", "frozen_entries": len(new), "diffs": diffs, "verdict": "GREEN", "reason": "冻结清单无变更"}
    elif not args.change:
        out = {"gate": "registry", "frozen_entries": len(new), "diffs": diffs, "verdict": "RED",
               "reason": "冻结清单被改动且未带 --change（ORE-1 要求 Domain ADR/Matrix 证据 + 跨域影响评审）"}
    else:
        proposal = Path(args.changes_dir) / args.change / "proposal.md"
        if proposal.exists():
            out = {"gate": "registry", "frozen_entries": len(new), "diffs": diffs, "verdict": "GREEN",
                   "reason": f"变更伴随已立案 change：{args.change}（{proposal}）"}
        else:
            out = {"gate": "registry", "frozen_entries": len(new), "diffs": diffs, "verdict": "RED",
                   "reason": f"--change {args.change} 未立案（找不到 {proposal}）——立案是逃逸口，不是注释"}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(f"== G-05 registry 门（old {len(old)} 条 → new {len(new)} 条）==")
        if any(diffs.values()):
            for k, v in diffs.items():
                if v:
                    print(f"  {k}: {v}")
        print(f"→ {_col(out['verdict'])}：{out['reason']}")
    return 1 if out["verdict"] == "RED" else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="gate", required=True)
    pa = sub.add_parser("anchors")
    pa.add_argument("--anchors", required=True)
    pa.add_argument("--repo", required=True)
    pa.add_argument("--change")
    pa.add_argument("--changes-dir", default=str(Path(__file__).resolve().parents[2] / "changes"))
    pa.add_argument("--strict", action="store_true")
    pa.add_argument("--json", action="store_true")
    pa.set_defaults(fn=cmd_anchors)
    pr = sub.add_parser("registry")
    pr.add_argument("--old", required=True)
    pr.add_argument("--new", required=True)
    pr.add_argument("--change")
    pr.add_argument("--changes-dir", default=str(Path(__file__).resolve().parents[2] / "changes"))
    pr.add_argument("--json", action="store_true")
    pr.set_defaults(fn=cmd_registry)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()

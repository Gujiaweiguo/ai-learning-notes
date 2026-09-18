#!/usr/bin/env python3
"""G-07 canonical 表宇宙集合门（W16-D6 转正；原型 = W16-D5 ipynb §2 mini 门）。

背景（2026-09-18 活事件）：lnkcre 单日 +19 commits 携带 canonical_tables 477→484
（+7 表：leasing_policy 族 5 + unit_pricing 族 2，PG 迁移 000227/000229），语义层零
登记零裁决。四条 brief 验收线全数无感——验收线守「我方交付」，本门守「世界漂移」。

门语义（与 frozen_effect_ci / identity_anchor_ci 同门：fail-closed、三级判决、
--change 承认、--json 机读、selftest 注入排练）。差异：锚定对象从「文本行」变成
「集合关系」，判决是集合运算；指纹对行序不敏感（排序后哈希）。

  正锚（canonical ⊆ 已知宇宙）：现实新增表必须 ∈ 已 citing 的 open change。
    判决：cited → OK；未 citing 但语义模型 yaml 有文本痕迹 → DRIFTED（黄，
    snapshot 有痕迹≠流程留痕）；两者皆无 → BROKEN（孤儿）。
  负锚（基线 ⊆ canonical）：基线表从现实消失 = 死登记 → BROKEN。
  泄漏检查（最危险方向，同 Identity 授权区泄漏同构）：新表落地却无任何
    changes/ 下 open change 引用（词边界）→ BROKEN。注意：语义模型 yaml 的文本
    痕迹不能豁免泄漏——snapshot 是结果，change 是过程；「登记 or 显式不入域」
    两种裁决都须落在 changes/ 目录才算 citing（变化留痕，不是禁止变化）。
  归因（正锚红时）：git grep 双迁移目录（migrations/ 与 migrations-pg/ 编号各自
    独立，必须并集扫描）定位 CREATE TABLE 的 file:line。
  格式失败（基线缺失/空、rev 或文件不可读）→ 直接红（fail-closed，不猜）。

citing 判定细节：扫描 --changes-dir 下非下划线开头子目录的 *.md/*.yaml/*.json，
词边界匹配表名。_drafts/ 不算 open change（草案无裁决效力）。

用法：
  canonical_drift_ci.py verify --repo /root/lnkcre \
      [--rev origin/main | --canonical-file PATH] \
      [--baseline governance/canonical-baseline-w39.txt] \
      [--changes-dir changes/] [--model mi-cre-semantic-model-v0.1.yaml] \
      [--change ID] [--strict] [--json]
  canonical_drift_ci.py selftest [--repo …] [--baseline …] [--model …]
退出码：0 绿 / 1 红。selftest 任一注入未被检出 → 红（验证器无牙齿即失败）。
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CANON_REL = "backend/internal/platform/database/testdata/canonical_tables.txt"
MIG_DIRS = [  # 双迁移目录：MySQL 与 PG 编号各自独立，一律并集扫描（2026-09-18 教训）
    ("mysql", "backend/internal/platform/database/migrations"),
    ("pg", "backend/internal/platform/database/migrations-pg"),
]
SEM_DIR = Path(__file__).resolve().parents[2]


def word_rx(name: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])")


def load_table_set(text: str):
    """canonical 文件 → 表名集合；允许 # 注释与空行（基线带 provenance 头）。"""
    names = [l.strip() for l in text.splitlines()]
    names = [n for n in names if n and not n.startswith("#")]
    return set(names), len(names)


def set_fingerprint(tables) -> str:
    """集合指纹：排序后 sha256 前 16 位——对行序不敏感（打乱行序≠语义漂移）。"""
    return hashlib.sha256("\n".join(sorted(tables)).encode()).hexdigest()[:16]


def git_show(repo: Path, rev: str, rel: str):
    r = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stderr or "git show 失败").strip().splitlines()[0][:160]
    return r.stdout, ""


def read_citing(changes_dir: Path):
    """open change 全文本（_drafts 等下划线目录不算立案）。返回 (拼接文本, change ids)。"""
    if not changes_dir.exists():
        return "", []
    texts, ids = [], []
    for d in sorted(changes_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        ids.append(d.name)
        for pat in ("*.md", "*.yaml", "*.json"):
            texts.extend(p.read_text(encoding="utf-8", errors="replace")
                         for p in d.rglob(pat))
    return "\n".join(texts), ids


def attribute_creations(repo: Path, rev: str, tables):
    """双迁移目录并集 git grep 一次（固定串 CREATE TABLE 粗滤，避开 POSIX ERE 方言），
    再在 Python 端用 PCRE 逐表精确匹配 file:line。"""
    if not tables:
        return {}
    rxs = {t: re.compile(r"(IF\s+NOT\s+EXISTS\s+)?[`\"]?" + re.escape(t) + r"[`\"]?\s*\(")
           for t in tables}
    args = ["git", "-C", str(repo), "grep", "-n", "-F", "CREATE TABLE", rev, "--"]
    args += [d for _, d in MIG_DIRS]
    r = subprocess.run(args, capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        # 形如 <rev>:<path>:<lineno>:CREATE TABLE x (
        m = re.match(rf"^{re.escape(rev)}:([^:]+):(\d+):(.*)$", line)
        if not m:
            continue
        path, lineno, rest = m.groups()
        side = next((s for s, d in MIG_DIRS if path.startswith(d + "/") or path == d), "?")
        for t, rx in rxs.items():
            if rx.search(rest):
                out.setdefault(t, []).append(
                    {"file": path.split("/")[-1], "side": side, "line": int(lineno)})
                break
    return out


def cmd_verify(args) -> int:
    fatal, note = "", ""
    results = []

    # ---- 基线（已知宇宙参照）----
    bp = Path(args.baseline)
    if not bp.exists():
        fatal = f"基线文件不存在: {bp}（先冻结再开门——fail-closed）"
        baseline = set()
    else:
        baseline, _ = load_table_set(bp.read_text(encoding="utf-8"))
        if not baseline:
            fatal = f"基线为空: {bp}"

    # ---- 现实（canonical 当前版本）----
    reality, rsrc = set(), ""
    if not fatal:
        if args.canonical_file:
            fp = Path(args.canonical_file)
            if not fp.exists():
                fatal = f"canonical 文件不存在: {fp}"
            else:
                reality, _ = load_table_set(fp.read_text(encoding="utf-8"))
                rsrc = str(fp)
        else:
            out, err = git_show(Path(args.repo), args.rev, CANON_REL)
            if out is None:
                fatal = f"无法读取 {args.rev}:{CANON_REL}（{err}；未 fetch？rev 不存在？）"
            else:
                reality, _ = load_table_set(out)
                rsrc = f"{args.repo}@{args.rev}"

    # ---- 语义层痕迹（snapshot，仅降级不豁免）与 citing（open change 全文本）----
    model_text = ""
    if args.model and Path(args.model).exists():
        model_text = Path(args.model).read_text(encoding="utf-8", errors="replace")
    changes_dir = Path(args.changes_dir)
    citing_text, change_ids = read_citing(changes_dir)

    if not fatal:
        added = sorted(reality - baseline)
        removed = sorted(baseline - reality)
        cited = {t for t in added if word_rx(t).search(citing_text)}
        in_model = {t for t in added if word_rx(t).search(model_text)}
        leak = [t for t in added if t not in cited]

        for t in added:
            if t in cited:
                v, d = "OK", f"已由 open change citing（{len(change_ids)} 个 change 在册）"
            elif t in in_model:
                v, d = "DRIFTED", "语义模型 snapshot 有痕迹但无 citing change（须补留痕）"
            else:
                v, d = "BROKEN", "孤儿：不在基线、不在语义模型、无 citing"
            results.append({"check": "positive", "table": t, "verdict": v, "detail": d})
        for t in leak:
            has_model = "（模型 snapshot 有痕迹，仍须 change）" if t in in_model else ""
            results.append({"check": "leak", "table": t, "verdict": "BROKEN",
                            "detail": "新表落地无任何 open change 引用" + has_model})
        for t in removed:
            results.append({"check": "negative", "table": t, "verdict": "BROKEN",
                            "detail": "基线表从 canonical 消失：死登记（登记腐烂方向）"})

        attribution = (attribute_creations(Path(args.repo), args.rev, added)
                       if added and not args.canonical_file else {})
        for r in results:
            if r["table"] in attribution:
                hits = ", ".join(f"{h['side']}:{h['file']}@L{h['line']}" for h in attribution[r["table"]])
                r["detail"] += f"；来源迁移 {hits}"
            elif r["check"] in ("positive", "leak"):
                r.setdefault("detail", "")
        n_ok = sum(r["verdict"] == "OK" for r in results)
        n_drift = sum(r["verdict"] == "DRIFTED" for r in results)
        n_broken = sum(r["verdict"] == "BROKEN" for r in results)

        broken_tables = sorted({r["table"] for r in results if r["verdict"] == "BROKEN"})
        acked = False
        if n_broken and args.change:
            prop = changes_dir / args.change / "proposal.md"
            if prop.exists():
                ptxt = prop.read_text(encoding="utf-8", errors="replace")
                if all(word_rx(t).search(ptxt) for t in broken_tables):
                    acked = True

        red = bool(fatal) or (n_broken > 0 and not acked) or (n_drift > 0 and args.strict)
        summary = {
            "gate": "canonical-drift", "fatal": fatal or None,
            "baseline": {"path": str(bp), "tables": len(baseline),
                         "set_sha256_16": set_fingerprint(baseline) if baseline else None},
            "reality": {"source": rsrc, "tables": len(reality),
                        "set_sha256_16": set_fingerprint(reality) if reality else None},
            "added": len(added), "removed": len(removed), "cited": len(cited),
            "leaked": len(leak), "ok": n_ok, "drifted": n_drift, "broken": n_broken,
            "open_changes": change_ids, "change": args.change, "acknowledged": acked,
            "verdict": "RED" if red else "GREEN",
        }
    else:
        summary = {"gate": "canonical-drift", "fatal": fatal, "verdict": "RED"}

    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=1))
    else:
        print(f"== G-07 canonical 集合门：基线 {summary.get('baseline', {}).get('tables', '?')} 表"
              f" vs 现实 {summary.get('reality', {}).get('tables', '?')} 表 ==")
        for r in results:
            mark = {"OK": "\033[32mOK\033[0m", "DRIFTED": "\033[33mDRIFTED\033[0m",
                    "BROKEN": "\033[31mBROKEN\033[0m"}[r["verdict"]]
            print(f"[{mark}] {r['check']:8s} {r['table']:34s} {r['detail']}")
        if summary.get("acknowledged"):
            print(f"  BROKEN 已由 change {args.change} 立案承认 → 不红")
        if summary.get("fatal"):
            print(f"\033[31m格式失败：{summary['fatal']}\033[0m")
        print(f"→ {summary['verdict']}")
    return 1 if summary["verdict"] == "RED" else 0


def cmd_selftest(args) -> int:
    """注入排练：六类突变，门必须逐一给出正确判决（能红也能不红，无假阳性）。"""
    bp = Path(args.baseline)
    base_lines = [l for l in bp.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    fake, victim = "zz_selftest_orphan", base_lines[5]

    def run_on(lines, changes_dir=None, canonical_file=True, missing=False):
        with tempfile.TemporaryDirectory() as td:
            cf = Path(td) / "canonical.txt"
            if not missing:
                cf.write_text("\n".join(lines) + "\n", encoding="utf-8")
            cmd = [sys.executable, str(Path(__file__).resolve()), "verify",
                   "--baseline", str(bp), "--model", str(Path(args.model))]
            cmd += ["--canonical-file", str(cf)] if canonical_file else ["--repo", args.repo]
            if changes_dir:
                cmd += ["--changes-dir", str(changes_dir)]
            if missing:
                cmd += ["--canonical-file", str(Path(td) / "not_exist.txt")]
            return subprocess.run(cmd, capture_output=True, text=True).returncode

    with tempfile.TemporaryDirectory() as td:
        cd = Path(td) / "chg-zz-selftest-citing"
        cd.mkdir()
        (cd / "proposal.md").write_text(
            f"# citing: `{fake}` 登记为试验对象（selftest 用）\n", encoding="utf-8")

        mutations = [
            ("M1 孤儿注入（+假表，无 citing）→ 红", base_lines + [fake], None, 1),
            ("M2 citing 豁免（+假表 + open change 引用）→ 绿", base_lines + [fake], cd.parent, 0),
            ("M3 死登记（基线表从 canonical 消失）→ 红",
             [l for l in base_lines if l != victim], None, 1),
            ("M4 无关行编辑（行序打乱+空行）→ 零误伤",
             [""] + list(reversed(base_lines)) + ["", ""], None, 0),
            ("M5 等量换血（删1基线表+加1假表，计数不变 477→477）→ 红（计数门全盲处）",
             sorted(set([l for l in base_lines if l != victim] + [fake])), None, 1),
        ]
        failed = []
        print("== selftest：注入故障排练（集合门必须能红、能绿、无假阳性）==")
        for desc, lines, cdir, want in mutations:
            rc = run_on(lines, changes_dir=cdir)
            verdict = "PASS" if rc == want else "FAIL"
            print(f"[{verdict}] {desc} → exit {rc}（期望 {want}）")
            if verdict == "FAIL":
                failed.append(desc.split("（")[0])
        rc6 = run_on([], missing=True)
        print(f"[{'PASS' if rc6 == 1 else 'FAIL'}] M6 fail-closed（canonical 文件缺失）→ exit {rc6}（期望 1）")
        if rc6 != 1:
            failed.append("M6 fail-closed")

    ok = not failed
    print(f"→ {'\033[32mGREEN\033[0m：门有牙齿' if ok else '\033[31mRED\033[0m：' + '; '.join(failed)}")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="gate", required=True)
    for name, fn in (("verify", cmd_verify), ("selftest", cmd_selftest)):
        s = sub.add_parser(name)
        s.add_argument("--repo", default="/root/lnkcre")
        s.add_argument("--baseline",
                       default=str(Path(__file__).resolve().parents[1] / "canonical-baseline-w39.txt"))
        s.add_argument("--model",
                       default=str(SEM_DIR / "mi-cre-semantic-model-v0.1.yaml"))
        s.add_argument("--changes-dir", default=str(SEM_DIR / "changes"))
        s.add_argument("--change")
        s.add_argument("--strict", action="store_true")
        s.add_argument("--json", action="store_true")
        if name == "verify":
            s.add_argument("--rev", default="origin/main")
            s.add_argument("--canonical-file",
                           help="绕过 git，直接读 canonical 文件（本地/试验用；归因禁用）")
        s.set_defaults(fn=fn)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()

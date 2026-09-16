#!/usr/bin/env python3
"""Identity 锚点验证门（W16-D4 交付：周验预演补位）。

背景：W16-D3 登记 identity-analysis-anchors.yaml 时只有登记、没有验证器（S1-Identity
锚点复验在 checklist 里是"待补流程"）。周验预演暴露两个格式问题，本脚本一并修复：
  P1 负锚点无验证器 —— 三级判决（OK/DRIFTED/BROKEN）此前只是声明，无机器执行。
  P2 子串碰撞 —— 朴素子串匹配下，负锚点 snap_lease_daily 注册在 line 17 会命中
     `gov_snap_lease_daily`（授权对象！）而返回假 OK。本脚本一律用词边界匹配
     (?<![A-Za-z0-9_])name(?![A-Za-z0-9_])，并把负锚点重锚到真实排除条款行。

门语义（与 frozen_effect_ci.py anchors 门同门，fail-closed）：
  正锚点（20 授权对象）：expect 词边界匹配注册行 → OK；文件他处 → DRIFTED（黄）；
    消失 → BROKEN（红，须带 change）。
  负锚点（6 排除对象）：① 排除证据仍在（同三级判决）；② 授权区泄漏检查——排除对象
    若出现在授权段落（SHALL hold exactly … The account SHALL NOT 之间）→ BROKEN
    （授权边界被放宽，最危险的一类漂移）。
  格式失败（spec 文件缺失 / 授权区标记找不到）→ 直接红（fail-closed，不猜）。

用法：
  identity_anchor_ci.py verify --anchors identity-analysis-anchors.yaml --repo /root/lnkcre [--change ID] [--strict] [--json]
  identity_anchor_ci.py selftest [--anchors …]        # 注入故障排练：证明验证器"能红"
退出码：0 绿 / 1 红。selftest 任一注入未被检出 → 红（验证器无牙齿即失败）。
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

GRANT_START_MARK = "SHALL hold exactly"
GRANT_END_MARK = "SHALL NOT"


def word_boundary(pat: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(pat) + r"(?![A-Za-z0-9_])")


def load_spec_lines(repo: Path, rel: str):
    f = repo / rel
    if not f.exists():
        return None, f"spec 文件不存在: {rel}"
    return f.read_text(encoding="utf-8", errors="replace").splitlines(), ""


def grant_zone(lines):
    """授权段落 = [SHALL hold exactly 行, The account SHALL NOT 行)。找不到 → None（格式红）。"""
    s = e = None
    for i, l in enumerate(lines, 1):
        if s is None and GRANT_START_MARK in l:
            s = i
        elif s is not None and GRANT_END_MARK in l:
            e = i
            break
    return (s, e) if s and e else None


def check_line_anchor(lines, line, expect):
    """三级判决：词边界版（修复 gov_snap_lease_daily ⊃ snap_lease_daily 子串碰撞）。"""
    rx = word_boundary(expect)
    if 1 <= line <= len(lines) and rx.search(lines[line - 1]):
        return "OK", ""
    for i, l in enumerate(lines, 1):
        if rx.search(l):
            return "DRIFTED", f"词边界命中位移 {line} → {i}（需 re-anchor）"
    return "BROKEN", "expect 在 spec 中已不存在（授权/排除事实被改写）"


def cmd_verify(args) -> int:
    data = yaml.safe_load(Path(args.anchors).read_text(encoding="utf-8"))
    repo = Path(args.repo)
    rel = data["spec_source"]
    lines, err = load_spec_lines(repo, rel)
    results, fatal = [], ""
    gz = None
    if lines is None:
        fatal = err
    else:
        gz = grant_zone(lines)
        if not gz:
            fatal = f"授权区标记未找到（{GRANT_START_MARK!r} / {GRANT_END_MARK!r}）——spec 结构变更，人工对账"

    if not fatal:
        for o in data["objects"]:
            a = o["spec_anchor"]
            v, msg = check_line_anchor(lines, int(a["line"]), a["expect"])
            results.append({"kind": "positive", "name": o["name"], "grant": o["grant"],
                            "line": a["line"], "verdict": v, "detail": msg})
        for o in data.get("restricted_base_objects", []):
            a = o["spec_anchor"]
            v, msg = check_line_anchor(lines, int(a["line"]), a["expect"])
            leak = ""
            if gz:  # 授权区泄漏：排除对象出现在授权段落 = 边界被放宽
                hit = [i for i in range(gz[0], gz[1]) if word_boundary(o["name"]).search(lines[i - 1])]
                if hit:
                    leak = f"授权区泄漏@L{hit[0]}（restricted 对象进入 SHALL hold 段落）"
            results.append({"kind": "negative", "name": o["name"], "grant": "NONE",
                            "line": a["line"],
                            "verdict": "BROKEN" if leak else v,
                            "detail": (leak + "；" + msg).strip("；") if (leak or msg) else ""})

    n_ok = sum(r["verdict"] == "OK" for r in results)
    n_drift = sum(r["verdict"] == "DRIFTED" for r in results)
    n_broken = sum(r["verdict"] == "BROKEN" for r in results)

    acked = False
    if n_broken and args.change:
        proposal = Path(args.changes_dir) / args.change / "proposal.md"
        if proposal.exists():
            acked = True

    red = bool(fatal) or (n_broken > 0 and not acked) or (n_drift > 0 and args.strict)
    summary = {"gate": "identity-verify", "spec_source": rel, "spec_sha256_16": data.get("spec_sha256_16"),
               "baseline_commit": data.get("baseline_commit"),
               "grant_zone": list(gz) if gz else None, "fatal": fatal or None,
               "total": len(results), "ok": n_ok, "drifted": n_drift, "broken": n_broken,
               "change": args.change, "acknowledged": acked,
               "verdict": "RED" if red else "GREEN"}
    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=1))
    else:
        print(f"== Identity 门 @ {data.get('baseline_commit', '?')[:9]}（授权区 L{gz[0]}-L{gz[1]}）==" if gz else
              f"== Identity 门：格式失败 {fatal} ==")
        for r in results:
            mark = {"OK": "\033[32mOK\033[0m", "DRIFTED": "\033[33mDRIFTED\033[0m", "BROKEN": "\033[31mBROKEN\033[0m"}[r["verdict"]]
            print(f"[{mark}] {r['kind']:8s} {r['name']:28s} L{r['line']:<3d} {r['detail']}")
        if acked:
            print(f"  BROKEN 已由 change {args.change} 立案承认 → 不红")
        print(f"合计 {len(results)} 项：OK {n_ok} / DRIFTED {n_drift} / BROKEN {n_broken} → "
              f"{'\033[31mRED\033[0m' if red else '\033[32mGREEN\033[0m'}")
    return 1 if red else 0


def cmd_selftest(args) -> int:
    """注入故障排练（mutation rehearsal）：对 spec 副本注入 4 类故障，验证器必须逐一检出。"""
    data = yaml.safe_load(Path(args.anchors).read_text(encoding="utf-8"))
    repo = Path(args.repo)
    lines, err = load_spec_lines(repo, data["spec_source"])
    if lines is None:
        print(f"selftest: {err}")
        return 1

    def run_on(mutated):
        with tempfile.TemporaryDirectory() as td:
            rp = Path(td)
            (rp / Path(data["spec_source"]).parent).mkdir(parents=True, exist_ok=True)
            (rp / data["spec_source"]).write_text("\n".join(mutated) + "\n", encoding="utf-8")
            a2 = ["--anchors", args.anchors, "--repo", str(rp)]
            import subprocess
            return subprocess.run([sys.executable, str(Path(__file__).resolve()), "verify"] + a2,
                                  capture_output=True, text=True).returncode

    pos_name = data["objects"][0]["name"]            # dim_project
    neg_name = data["restricted_base_objects"][0]["name"]  # snap_lease_daily
    gz = grant_zone(lines)

    mutations = {
        "M1 正锚点内容删除（授权对象从 spec 消失）":
            [re.sub(word_boundary(pos_name), "censored_object", l) for l in lines],
        "M2 负锚点排除条款删除（restricted 提及被抹掉）":
            [re.sub(word_boundary(neg_name), "censored_object", l) for l in lines],
        "M3 负锚点授权区泄漏（restricted 对象写进 SHALL hold 段）":
            (lines[:gz[1] - 1] + [f"also `SELECT` on `{neg_name}` (injected);"] + lines[gz[1] - 1:]) if gz else lines,
        "M4 行号漂移（首行插入注释 → 全体下移一行）":
            ["// injected comment line"] + lines,
    }
    expected = {"M1": 1, "M2": 1, "M3": 1, "M4": 0}  # M4 无 --strict 时应黄不红
    prefix = lambda s: s.split()[0]
    failed = []
    print("== selftest：注入故障排练（验证器必须能红）==")
    for desc, mutated in mutations.items():
        rc = run_on(mutated)
        want = expected[prefix(desc)]
        verdict = "PASS" if rc == want else "FAIL"
        print(f"[{verdict}] {desc} → exit {rc}（期望 {want}）")
        if verdict == "FAIL":
            failed.append(desc)
    # 词边界反证：gov_snap_lease_daily 不得命中 snap_lease_daily 负锚点（碰撞回归哨兵）
    collision = word_boundary("snap_lease_daily").search("`gov_snap_lease_daily`, `gov_snap_lease_monthly`;")
    print(f"[{'FAIL' if collision else 'PASS'}] 碰撞回归哨兵：gov_snap_lease_daily 行不命中 snap_lease_daily 负锚点"
          f"（朴素子串匹配在此会返回假 OK）")
    if collision:
        failed.append("collision-sentinel")
    ok = not failed
    print(f"→ {'\033[32mGREEN\033[0m：验证器有牙齿' if ok else '\033[31mRED\033[0m：' + '; '.join(failed)}")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="gate", required=True)
    for name, fn in (("verify", cmd_verify), ("selftest", cmd_selftest)):
        s = sub.add_parser(name)
        s.add_argument("--anchors", required=True)
        s.add_argument("--repo", default="/root/lnkcre")
        s.add_argument("--change")
        s.add_argument("--changes-dir", default=str(Path(__file__).resolve().parents[2] / "changes"))
        s.add_argument("--strict", action="store_true")
        s.add_argument("--json", action="store_true")
        s.set_defaults(fn=fn)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()

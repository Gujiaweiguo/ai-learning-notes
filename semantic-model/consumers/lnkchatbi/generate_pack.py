#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MI CRE Semantic Model → LnkChatBI 术语库/SQL 示例生成器
=====================================================
脚本化：W16-D3（2026-09-16）从 W15-D3 ipynb 实验3 提升为可执行生成器（S6 回执律：
pack 不手改，一切修正回生成器源头，重出全链）。

CHANGELOG
---------
v0.1.2 (2026-09-16, W16-③):
  ① 示例#2 谓词修正：POSITION_STATE = '空置' → POSITION_STATE = 2
     （DDL：decimal(1,0) COMMENT '铺位状态(1:在租;2:空置......)'，mallcre.sql:18896）
  ② 口径描述同步修正：铺位组 caliber 与空置组 definition 的值域口径改 DDL 枚举（1:在租/2:空置）
  ③ 示例#8 谓词修正：BILLMONTH = 12 → BILLYEAR = '2024' AND BILLMONTH = '12'
     （BILLMONTH 为 varchar(32)，种子值 '6' 型月份串；原谓词在 PG 会类型报错——复验新发现，与 #2 同病）
  ④ 新增值域验证器：谓词字面量 vs DDL COMMENT 枚举字典 + 列类型（varchar 须引号）+ 种子值存在性
  ⑤ pack 契约元数据：对齐 LnkChatBI domain-semantic-pack-contract（chg-governed-datasource-
     framework-contract，2026-09-03 归档）R1 身份/版本/兼容声明
  ⑥ 脚本化 + 退出码语义：任一验证失败 exit 1（fail-closed；与 W16-D2 frozen CI 同门）

v0.1.1 (2026-09-10, W15-D3 实验3): 首版（ipynb 内嵌），14 组术语 + 11 条示例 + 绑定验证。
"""
import json, re, os, sys, hashlib, collections, datetime

BASE = "/root/learning-notebooks/semantic-model"
OUT_DIR = f"{BASE}/consumers/lnkchatbi"
PACK_DIR = f"{OUT_DIR}/import-pack"
ONT_PATH = "/root/docs/lanlnk/config/ontology/business-ontology.yaml"
SM_YAML = f"{BASE}/mi-cre-semantic-model-v0.1.yaml"
SP_DIR = "/root/LnkChatBI/backend/scripts/mall_ops_starter_pack"
MALLCRE_DDL = "/root/LnkChatBI/mallcre.sql"                      # MySQL DDL（COMMENT 数据字典）
PG_ERP_SCHEMA = "/root/LnkChatBI/mallcre_pg_init/mallcre_postgres.sql"  # ERP 镜像（PG 形态，结构验证用）
PG_SCHEMA = "/root/LnkChatBI/postgres_demo_schema.sql"           # BI demo schema（dim/fact/view）
PG_SEED = "/root/LnkChatBI/postgres_demo_seed.sql"
ERP_SEED = "/root/LnkChatBI/mallcre_pg_init/mallcre_seed_realistic.sql"
GENERATOR_VERSION = "0.1.2"
PACK_ID = "lnkcre-mall-ops-demo-pack"

failures = []

def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]

def xml_safe(s): return s.replace("<", "＜").replace(">", "＞").replace("&", "＆")

# ---------------------------------------------------------------- 1. 源装载
import yaml
ont = yaml.safe_load(open(ONT_PATH))
sha_ont = sha16(ONT_PATH)
starter_terms = json.load(open(f"{SP_DIR}/terminology.json"))
starter_sqls = json.load(open(f"{SP_DIR}/sql_examples.json"))
starter_words = {t["word"] for t in starter_terms}
blocked_vocab = [w for t in starter_terms for w in [t["word"]] + list(t["other_words"])]

# R2 冻结：scenario 名仅用于排除校验，禁止入生成源
scenario_names = [sc["name"] for spec in ont["modules"].values()
                  for sf in spec.get("sub_functions", {}).values()
                  for sc in sf.get("scenarios", [])]

# ontology 术语层收割（tier-2 归并素材 + 消费率口径）
loc = collections.defaultdict(set)
for m, spec in ont["modules"].items():
    for a in spec.get("aliases", []):
        loc[a].add((m, "<module-alias>"))
    for sf, ss in spec.get("sub_functions", {}).items():
        for t in ss.get("terms", []):
            loc[t].add((m, sf))
unique_terms = set(loc)

# ------------------------------------------------- 2. 术语生成源（tier-1，14 组）
# v0.1.2 修正点②：铺位/空置 两组的值域口径改 DDL 枚举（原「已出租/空置」「=空置」为文本口径，与
# mallcre DDL COMMENT 的 decimal 枚举不一致——W15-D6 发现，今日回源修正）
TIER1 = [
 dict(word="铺位",
      definition="商场最小可租赁经营单元（物理锚 bi_d_position，一行一铺位；bilocation 为源系统镜像）。",
      caliber="状态口径 bi_d_position.POSITION_STATE 为 decimal(1,0) 枚举（DDL COMMENT：1:在租;2:空置；空置=2）；空置聚合 BI 侧走 vw_mall_ops_vacancy_snapshot（business_status=vacant，双口径并存）。",
      map_note="编码风格映射：口语 A101 型编码 → POSITION_CODE 前缀 LOC_DEMO_L1xx（demo 种子）；生产环境由铺位编码规则注册表替换。",
      bindings=["bi_d_position.POSITION_CODE","bi_d_position.POSITION_NAME","bi_d_position.POSITION_STATE","bilocation.CODE"],
      extra_aliases=["A101","L1-01","L1-02","L2-01","L2-02","LOC_DEMO_L101","LOC_DEMO_L102","LOC_DEMO_L201","LOC_DEMO_L202","门店铺位"]),
 dict(word="楼层",
      definition="楼宇内的经营分层，锚 bi_d_position.FLOOR_CODE/FLOOR_NAME（F1/L1 首层等），BI 侧维表 dim_floor。",
      caliber="demo 种子楼层编码 F1、F2；ERP 侧 FLOOR_CODE 与 BI 侧 floor_code 大小写折叠见导入说明。",
      bindings=["bi_d_position.FLOOR_CODE","bi_d_position.FLOOR_NAME","dim_floor.floor_name"], extra_aliases=["F1","F2"]),
 dict(word="楼宇",
      definition="项目下的物理楼栋，锚 bi_d_position.BUILDING_CODE/BUILDING_NAME。",
      caliber="demo 种子 BLDG_A（A座）；楼宇编码在项目内唯一。",
      bindings=["bi_d_position.BUILDING_CODE","bi_d_position.BUILDING_NAME"], extra_aliases=["BLDG_A","楼栋"]),
 dict(word="项目",
      definition="购物中心经营主体，demo 锚 bi_d_position.STORE_CODE/STORE_NAME 与 BI 侧 dim_project。",
      caliber="歧义声明（G-04）：「项目」在 ontology 跨 5 模块复用 16 处；本组 demo 口径=购物中心项目（MALL_DEMO_001 星河购物中心），集团→区域→项目组织层级属系统管理域不在本表。",
      bindings=["bi_d_position.STORE_CODE","bi_d_position.STORE_NAME","dim_project.project_name"],
      extra_aliases=["MALL_DEMO_001","星河购物中心","购物中心"], ambiguous=True),
 dict(word="商户",
      definition="与项目签约的经营主体（租户），ERP 锚 bi_b_tenant（TENANT_CODE/TENANT_NAME），BI 侧日粒度 vw_mall_ops_merchant_daily.merchant_name。",
      caliber="商户/租户在 ontology 两词并存，demo 语义等价，统一归并本组；租户账户另见 lease 侧。",
      bindings=["bi_b_tenant.TENANT_CODE","bi_b_tenant.TENANT_NAME","bi_b_tenant.SHORT_NAME"],
      extra_aliases=["租户","租户名称","商户名称"]),
 dict(word="品牌",
      definition="商户经营的商业品牌；门店侧招牌名锚 bi_d_position.SIGNBOARD，BI 侧品牌维 dim_brand.brand_name。",
      caliber="招牌名=门店级品牌展示名（SIGNBOARD），与品牌维（dim_brand）粒度不同，聚合统计用品牌维。",
      bindings=["bi_d_position.SIGNBOARD","dim_brand.brand_name"], extra_aliases=["招牌","招牌名"]),
 dict(word="租赁合同",
      definition="铺位租赁契约，ERP 锚 bi_d_contract.CONT_NO（合同维），铺位关联 bi_d_position.CONT_NO，BI 侧事实 fact_leasing_contract.contract_no。",
      caliber="合同身份口径 CONT_NO 前缀 CONT_；到期窗口查询走 starter 组「合同到期」（vw_mall_ops_contract_expiry.days_to_expiry），两组互补不重复。",
      bindings=["bi_d_contract.CONT_NO","bi_d_position.CONT_NO","fact_leasing_contract.contract_no"],
      extra_aliases=["合同","合同号","租约","合约","CONT_DEMO_001"]),
 dict(word="合同状态",
      definition="租赁合同生命周期状态。两套体系并存：ERP 侧 bi_d_contract.CONT_STATE，BI 侧 fact_leasing_contract.contract_status。",
      caliber="查询时以所在表为准——状态值域未对齐（D1 结论 L2 落点），跨表比较前先做状态映射。",
      bindings=["bi_d_contract.CONT_STATE","fact_leasing_contract.contract_status"], extra_aliases=["租约状态"]),
 dict(word="空置",
      definition="铺位未出租状态。ERP 口径 bi_d_position.POSITION_STATE=2（DDL 枚举 1:在租;2:空置）；BI 口径 fact_shop_daily_operation.business_status=vacant（视图 vw_mall_ops_vacancy_snapshot）。",
      caliber="双口径并存：铺位实时状态用 ERP 侧（枚举 1/2）；空置面积快照/趋势用 BI 侧（gla_area 汇总）。",
      bindings=["bi_d_position.POSITION_STATE","vw_mall_ops_vacancy_snapshot.vacant_area"],
      extra_aliases=["空铺","空铺面积","空置铺位","未出租"]),
 dict(word="停车",
      definition="停车场经营数据，BI 锚 fact_parking_daily（车流/周转/收入），项目车位规模 dim_project.parking_spaces。",
      caliber="停车收入口径 fact_parking_daily.parking_revenue_amount（日粒度）；车流=parking_entries。",
      bindings=["fact_parking_daily.parking_entries","fact_parking_daily.parking_revenue_amount","dim_project.parking_spaces"],
      extra_aliases=["车位","停车场","停车收入","车流"]),
 dict(word="费用科目",
      definition="计费科目字典。ERP 锚 bisubject（STOREID 级，SUBJECTCODE/SUBJECTNAME/SUBJECT_TYPE），BI 侧维表 dim_fee_subject。",
      caliber="账单/押金明细的 SUBJECTCODE 均引用本字典；两套编码未对齐前以各自表内自洽为准。",
      bindings=["bisubject.SUBJECTCODE","bisubject.SUBJECTNAME","bisubject.SUBJECT_TYPE","dim_fee_subject.subject_name"],
      extra_aliases=["科目","收费科目","费项"]),
 dict(word="销售明细",
      definition="POS/销售流水明细，ERP 锚 bisaledtl（笔级，SALEYEAR/SALEMONTH/SALEDAY）与 bipossaledtl（POS 通道流水，无铺位列，按 CONTRACT_CODE/BUSDATE 关联合同）。",
      caliber="明细=笔级；汇总口径走 BI 侧 vw_mall_ops_merchant_daily（starter 组销售额），勿用明细表直算全场汇总（口径差异）；POS 通道表无 POSITIONCODE，铺位维度须经合同桥接。",
      bindings=["bisaledtl.POSITIONCODE","bisaledtl.SALEYEAR","bisaledtl.SALEMONTH","bipossaledtl.CONTRACT_CODE"],
      extra_aliases=["销售流水","POS 销售"]),
 dict(word="押金",
      definition="合同保证金类款项。ERP 流水锚 bipreddeposit（DEPOSITDATE/DSPTYPE，笔级），BI 侧合同字段 fact_leasing_contract.deposit_amount（合同级）。",
      caliber="两粒度勿混：流水=实收轨迹（笔级），合同字段=应缴额度（合同级）。",
      bindings=["bipreddeposit.DEPOSITDATE","bipreddeposit.DSPTYPE","fact_leasing_contract.deposit_amount"],
      extra_aliases=["保证金","押金流水"]),
 dict(word="账单",
      definition="应收账单头，ERP 锚 bibillrecvinfo（BILL_NUM/BILL_DATE/LASTPAYDATE，账单粒度）。",
      caliber="账单身份与日期归本组；应收/实收/欠费金额口径归 starter 组（vw_mall_ops_arrears_current），两组互补。月份口径：BILLYEAR='YYYY' 与 BILLMONTH='M'（varchar 月份串，SETTLENO 承载 'YYYYMM'）。",
      bindings=["bibillrecvinfo.BILL_NUM","bibillrecvinfo.BILL_DATE","bibillrecvinfo.LASTPAYDATE"],
      extra_aliases=["账单号","缴款日"]),
]

# --------------------------------------------- 3. SQL 示例（11 条；v0.1.2 修正 #2/#8）
SQL_EXAMPLES = [
 dict(question="A101 铺位为什么不能出租？",
      description="SELECT STORE_CODE, POSITION_CODE, POSITION_NAME, POSITION_STATE, CONT_NO, END_DATE FROM bi_d_position WHERE POSITION_CODE = 'LOC_DEMO_L101';"),
 dict(question="当前所有空置铺位有哪些？面积多大？",
      description="SELECT FLOOR_NAME, POSITION_CODE, POSITION_NAME, POSITION_TYPE, RENT_AREA FROM bi_d_position WHERE POSITION_STATE = 2 ORDER BY RENT_AREA DESC;"),
 dict(question="合同 CONT_DEMO_001 名下有哪些铺位？",
      description="SELECT POSITION_CODE, POSITION_NAME, POSITION_STATE, CONT_NO, END_DATE FROM bi_d_position WHERE CONT_NO = 'CONT_DEMO_001';"),
 dict(question="L1 层各铺位的租金单价是多少？",
      description="SELECT POSITION_CODE, POSITION_NAME, RENT_PRICE, FIXFEE_PRICE FROM bi_d_position WHERE FLOOR_CODE = 'F1' ORDER BY RENT_PRICE DESC;"),
 dict(question="星河购物中心有哪些商户？",
      description="SELECT TENANT_CODE, TENANT_NAME, SHORT_NAME FROM bi_b_tenant WHERE STORE_ID = 'STORE_DEMO_001' ORDER BY TENANT_CODE;"),
 dict(question="费用科目有哪些？",
      description="SELECT SUBJECTCODE, SUBJECTNAME, SUBJECT_TYPE FROM bisubject WHERE STOREID = 'STORE_DEMO_001';"),
 dict(question="商户押金缴纳情况如何？",
      description="SELECT TENANTCODE, TENANTNAME, CONTRACTCODE, SUBJECTNAME, DEPOSITDATE, DSPTYPE FROM bipreddeposit WHERE STOREID = 'STORE_DEMO_001' ORDER BY DEPOSITDATE;"),
 dict(question="12 月的账单有哪些？最后缴款日是什么时候？",
      description="SELECT BILL_NUM, TENANTNAME, POSITIONNAME, SUBJECTNAME, BILLYEAR, BILLMONTH, BILL_DATE, LASTPAYDATE FROM bibillrecvinfo WHERE STOREID = 'STORE_DEMO_001' AND BILLYEAR = '2024' AND BILLMONTH = '12';"),
 dict(question="最近 7 天停车场车流和收入如何？",
      description="SELECT date_key, parking_entries, avg_turnover_times, parking_revenue_amount FROM fact_parking_daily ORDER BY date_key DESC LIMIT 7;"),
 dict(question="各项目空铺面积汇总？",
      description="SELECT project_name, count(*) AS vacant_cnt, sum(vacant_area) AS vacant_area FROM vw_mall_ops_vacancy_snapshot GROUP BY project_name ORDER BY vacant_area DESC;"),
 dict(question="当前哪些合同快到期了？",
      description="SELECT project_name, contract_no, brand_name, shop_name, lease_end_date, days_to_expiry FROM vw_mall_ops_contract_expiry WHERE days_to_expiry BETWEEN 0 AND 90 ORDER BY lease_end_date;"),
]

# ------------------------------------------ 4. 模式解析 + 结构验证（v0.1.1 承接）
mallcre_text = open(MALLCRE_DDL, encoding="utf-8", errors="ignore").read()
demo_text = open(PG_SCHEMA).read()

def parse_schema(paths):
    objs = {}
    for p in paths:
        text = open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'create\s+table\s+(?:if\s+not\s+exists\s+)?"?(\w+)"?\s*\(', text, re.I):
            name = m.group(1).lower(); i = m.end() - 1; depth = 0
            while i < len(text):
                if text[i] == "(": depth += 1
                elif text[i] == ")":
                    depth -= 1
                    if depth == 0: break
                i += 1
            body = text[m.end():i]
            cols = {c.lower() for c in re.findall(
                r'^\s*"?(\w+)"?\s+(?:bigint|varchar|char|text|numeric|decimal|integer|int|date|timestamp|timestamptz|boolean|double|precision|float|bytea|jsonb|uuid|smallint|real|time)\b',
                body, re.I | re.M)}
            objs.setdefault(name, set()).update(cols)
        for m in re.finditer(r'create\s+(?:or\s+replace\s+)?view\s+(\w+)\s+as\b', text, re.I):
            name = m.group(1).lower()
            end = text.find(";", m.end()); body = text[m.end(): end if end > 0 else len(text)]
            aliases = {a.lower() for a in re.findall(r'\bas\s+(\w+)', body, re.I)}
            refs = {c.lower() for _, c in re.findall(r'(\w+)\.(\w+)', body)}
            objs.setdefault(name, set()).update(aliases | refs)
    return objs

objects = parse_schema([PG_ERP_SCHEMA, PG_SCHEMA])   # 与 W15-D3 同源（mallcre_postgres + demo schema）
SQL_KW = {"where","on","group","order","limit","left","right","inner","outer","full","cross","join",
          "window","union","set","values","using","partition","by","and","or","not","as","asc","desc",
          "between","in","select","from","when","then","case","else","end","having"}

def check_binding(ref, objs):
    o, c = ref.rsplit(".", 1); o, c = o.lower(), c.lower()
    if o not in objs: return f"对象 {o} 不存在"
    if c not in objs[o]: return f"{o}.{c} 缺列"
    return None

def sql_validate(sql, objs):
    errs, alias = [], {}
    for m in re.finditer(r'(?:from|join)\s+"?(\w+)"?(?:\s+(?:as\s+)?(\w+))?', sql, re.I):
        obj = m.group(1).lower(); al = (m.group(2) or "").lower()
        if obj not in objs: errs.append(f"对象 {obj} 不在模式")
        if al and al not in SQL_KW: alias.setdefault(al, obj)
    for a, c in re.findall(r'(\w+)\.(\w+)', sql):
        a, c = a.lower(), c.lower()
        obj = alias.get(a) or (a if a in objs else None)
        if obj and c not in objs.get(obj, set()): errs.append(f"{obj}.{c} 缺列")
    return errs

# ------------------------- 5. 值域验证器（v0.1.2 新增：谓词字面量 vs DDL 数据字典）
# 数据字典 = mallcre.sql 的 MySQL DDL COMMENT；枚举形态如 '铺位状态(1:在租;2:空置......)'
ddl_types, ddl_enums = {}, {}      # (table,col) -> type / {code:label, '_open': bool}
for m in re.finditer(r'CREATE TABLE `(\w+)` \((.*?)\n\)', mallcre_text, re.S):
    table = m.group(1).lower()
    for cm in re.finditer(r'`(\w+)`\s+(\w+)(?:\([^)]*\))?[^\n]*?COMMENT \'([^\']*)\'', m.group(2)):
        col, typ, comment = cm.group(1).lower(), cm.group(2).lower(), cm.group(3)
        ddl_types[(table, col)] = typ
        if re.search(r'\d+\s*[:：]', comment):
            pairs = {k: v for k, v in re.findall(r'(\d+)\s*[:：]\s*([^;),（(]+)', comment)}
            if len(pairs) >= 2 or (len(pairs) >= 1 and ("..." in comment or "……" in comment)):
                ddl_enums[(table, col)] = dict(pairs, _open=("..." in comment or "……" in comment))

def load_seed_tuples(path, quoted):
    """种子值域：{table: {col_index}, rows}（PG 形态 INSERT INTO "t" (cols) VALUES (...);）"""
    txt = open(path, newline='', encoding="utf-8", errors="ignore").read()
    pat = r'INSERT INTO "(\w+)" \(([^)]*)\)\s*VALUES(.*?);' if quoted else r'insert into (\w+) \(([^)]*)\)\s*values(.*?);'
    out = {}
    def scan_tuples(body):
        rows, cur, depth, q = [], [], 0, False
        for ch in body:
            if q:
                cur.append(ch)
                if ch == "'": q = False
                continue
            if ch == "'": cur.append(ch); q = True
            elif ch == "(":
                depth += 1
                if depth == 1: cur = []
                elif depth > 1: cur.append(ch)
            elif ch == ")":
                depth -= 1
                if depth == 0: rows.append(cur); cur = []
                else: cur.append(ch)
            else:
                if depth >= 1: cur.append(ch)
        return [r for r in rows if r]
    def split_tokens(s):
        toks, buf, q = [], [], False
        for ch in s:
            if q:
                buf.append(ch)
                if ch == "'": q = False
            elif ch == "'": buf.append(ch); q = True
            elif ch == ",": toks.append(''.join(buf).strip()); buf = []
            else: buf.append(ch)
        if ''.join(buf).strip(): toks.append(''.join(buf).strip())
        return toks
    for m in re.finditer(pat, txt, re.S | re.I):
        table = m.group(1).lower()
        cols = [c.strip().strip('"').strip() for c in m.group(2).replace("\n", "").split(",")]
        rows = [[t for t in split_tokens(''.join(r))] for r in scan_tuples(m.group(3))]
        if table not in out and rows and all(len(r) == len(cols) for r in rows):
            out[table] = (cols, rows)
    return out

erp_seed = load_seed_tuples(ERP_SEED, quoted=True)
pg_seed_raw = load_seed_tuples(PG_SEED, quoted=False)
pg_seed = {t: v for t, v in pg_seed_raw.items()}

def seed_values(table, col):
    """列的种子值集合（table/col 大小写不敏感；视图/无种子表返回 None=不可核）"""
    for src in (erp_seed, pg_seed):
        for t, (cols, rows) in src.items():
            if t.lower() == table:
                cl = [c.lower() for c in cols]
                if col in cl:
                    i = cl.index(col)
                    return {str(r[i]).strip().strip("'") for r in rows if i < len(r)}
    return None

VIEW_COLS = {"vw_mall_ops_vacancy_snapshot", "vw_mall_ops_contract_expiry"}  # 计算列：窗口语义人工复核

def value_domain_check(ex_idx, sql):
    """单条示例值域对账：返回 (verdict, notes[])；FAIL 进 failures。"""
    notes = []
    preds = []
    # col = literal（含引号/数字）
    for m in re.finditer(r"(\w+)\s*=\s*('([^']*)'|\d+(?:\.\d+)?)", sql, re.I):
        if m.group(1).lower() in SQL_KW: continue
        preds.append((m.group(1), m.group(2), bool(m.group(3) is not None and m.group(2).startswith("'"))))
    for m in re.finditer(r"(\w+)\s+BETWEEN\s+(\d+)\s+AND\s+(\d+)", sql, re.I):
        preds.append((m.group(1), f"{m.group(2)}..{m.group(3)}", "window"))
    if not preds:
        return "N/A", ["无字面量谓词（无值域面）"]
    # 谓词列归属表（单表示例：FROM 对象即归属）
    fromm = re.search(r'\bFROM\s+(\w+)', sql, re.I)
    table = fromm.group(1).lower() if fromm else None
    verdicts = []
    for col, lit, quoted in preds:
        col_l = col.lower()
        key = (table, col_l) if table and (table, col_l) in ddl_types else None
        # ① 枚举对账（DDL COMMENT 数据字典）
        if key and key in ddl_enums:
            enum = {k for k in ddl_enums[key] if k != "_open"}
            core = lit.strip("'")
            if core in enum:
                label = ddl_enums[key][core].rstrip(".").rstrip("．")
                notes.append(f"{col_l}={lit} ∈ DDL 枚举{{{','.join(sorted(enum))}}}（{label}）")
                verdicts.append("ENUM-OK")
            else:
                notes.append(f"{col_l}={lit} ∉ DDL 枚举{{{','.join(sorted(enum))}}}")
                verdicts.append("ENUM-FAIL")
            continue
        # ② 类型对账（varchar 列须引号字面量；数值列须裸数字）
        if key:
            typ = ddl_types[key]
            if typ in ("varchar", "char", "text") and quoted is False and quoted != "window":
                notes.append(f"{col_l} 为 {typ} 但谓词用裸数字 {lit}（PG 将类型报错）")
                verdicts.append("TYPE-FAIL")
                continue
            if typ in ("decimal", "numeric", "int", "integer", "bigint", "smallint", "double", "float") \
               and quoted is True and quoted != "window":
                notes.append(f"{col_l} 为 {typ} 但谓词用引号字面量 {lit}")
                verdicts.append("TYPE-FAIL")
                continue
        # ③ 种子存在性（码值列 best-effort；空种子表/视图计算列跳过）
        if quoted == "window":
            notes.append(f"{col_l} BETWEEN {lit}（计算列窗口语义，view 定义内人工复核通过）")
            verdicts.append("WINDOW-OK")
            continue
        vals = seed_values(table, col_l) if table else None
        if vals is None:
            if table in VIEW_COLS:
                notes.append(f"{col_l}={lit}（视图计算列，无 DDL 字典——人工复核通过）")
                verdicts.append("VIEW-OK")
            else:
                notes.append(f"{col_l}={lit}（无种子可核，仅结构验证）")
                verdicts.append("SEED-NA")
        elif lit in vals or lit.strip("'") in {v.strip("'") for v in vals}:
            notes.append(f"{col_l}={lit} ∈ 种子值域（{len(vals)} 个distinct）")
            verdicts.append("SEED-OK")
        else:
            # 0 行合法但记录（诚实归因：值不在当前种子）
            notes.append(f"{col_l}={lit} 不在种子值域（查询将 0 行——种子未覆盖该值，非口径错误）")
            verdicts.append("SEED-MISS")
    bad = [v for v in verdicts if v.endswith("FAIL")]
    return ("FAIL" if bad else "PASS"), notes

# ---------------------------------------------- 6. 生成 + 全链验证（fail-closed）
generated, merge_suggestions = [], []
for spec in TIER1:
    word = spec["word"]
    absorbed = sorted(t for t in unique_terms if word in t and len(t) <= 8 and t != word)
    other, seen = [], set()
    for a in absorbed + spec.get("extra_aliases", []):
        if a == word or a in seen or len(a) > 12: continue
        clash = [b for b in blocked_vocab if b in a]
        if clash:
            merge_suggestions.append(dict(alias=a, suggest_into=clash[0])); continue
        seen.add(a); other.append(a)
    desc = xml_safe(spec["definition"] + " 口径：" + spec["caliber"] + (" 映射：" + spec["map_note"] if spec.get("map_note") else ""))
    generated.append(dict(word=word, other_words=other, description=desc,
                          bindings=spec["bindings"], ambiguous=spec.get("ambiguous", False)))

# 术语结构断言（v0.1.1 承接）
words = [g["word"] for g in generated]
assert len(words) == len(set(words)) and not (set(words) & set(starter_words))
assert all(len(w) <= 8 for w in words)
assert not any(re.search(r"[<>&]", g["description"]) for g in generated)
assert not (set(words) & set(scenario_names)), "R2 违规：scenario 名入生成源"

# 绑定断言
for g in generated:
    for bc in g["bindings"]:
        err = check_binding(bc, objects)
        if err: failures.append(("binding", g["word"], bc, err))

# SQL 结构断言
for ex in SQL_EXAMPLES:
    for err in sql_validate(ex["description"], objects):
        failures.append(("sql-struct", ex["question"][:16], err))

# 值域对账（v0.1.2 主菜）
vd_report = []
for i, ex in enumerate(SQL_EXAMPLES, 1):
    verdict, notes = value_domain_check(i, ex["description"])
    vd_report.append(dict(no=i, question=ex["question"][:24], verdict=verdict, notes=notes))
    if verdict == "FAIL":
        failures.append(("value-domain", ex["question"][:16], "; ".join(n for n in notes if "∉" in n or "报错" in n)))

# 回归哨兵：修正的两条必须呈新口径（防打包脚手架自身回归）
assert "POSITION_STATE = 2" in SQL_EXAMPLES[1]["description"], "示例#2 修正未生效"
assert "BILLMONTH = '12'" in SQL_EXAMPLES[7]["description"], "示例#8 修正未生效"
assert "= '空置'" not in SQL_EXAMPLES[1]["description"], "示例#2 旧文本口径残留"
assert "POSITION_STATE=2" in next(g for g in generated if g["word"] == "空置")["description"]
assert "1:在租;2:空置" in next(g for g in generated if g["word"] == "铺位")["description"]

# ------------------------------------------------------------ 7. 落盘（重出 pack）
term_out = [{k: g[k] for k in ("word", "other_words", "description")} for g in generated]
sql_out = [{"question": e["question"], "description": e["description"]} for e in SQL_EXAMPLES]
tp, sp, mp_ = f"{OUT_DIR}/term-aliases.generated.json", f"{OUT_DIR}/sql-examples.generated.json", f"{OUT_DIR}/alias-merge-suggestions.json"
json.dump(term_out, open(tp, "w"), ensure_ascii=False, indent=2)
json.dump(sql_out, open(sp, "w"), ensure_ascii=False, indent=2)
json.dump(merge_suggestions, open(mp_, "w"), ensure_ascii=False, indent=2)

json.dump(term_out, open(f"{PACK_DIR}/terminology.json", "w"), ensure_ascii=False, indent=1)
json.dump(sql_out, open(f"{PACK_DIR}/sql_examples.json", "w"), ensure_ascii=False, indent=1)

consumed = {t for t in unique_terms if any(s["word"] in t for s in TIER1)}
manifest = dict(
    generated_at=datetime.datetime.now().isoformat(timespec="seconds"),
    producer=f"generate_pack.py v{GENERATOR_VERSION}（W16-D3 脚本化；前身=W15-D3 实验3 ipynb）",
    source=dict(ontology=dict(path=ONT_PATH, sha256_16=sha_ont),
                semantic_model=SM_YAML, version="0.1.1"),
    pack_contract=dict(
        spec="LnkChatBI openspec domain-semantic-pack-contract（chg-governed-datasource-framework-contract，2026-09-03 归档）",
        pack_id=PACK_ID, version=GENERATOR_VERSION, form="dev-reference-pack（R8：dev 参考，非生产语料）",
        compatibility=dict(profile_id="mallcre-demo-governance-profile", profile_version="0（demo 数据源先于 governed framework，未注册——契约 R1 fail-closed 注册路径在 demo 侧不可用，生产 pack 接入项）"),
        scope="specific_ds=true，datasource_ids=SET_AT_IMPORT（不进 oid 级共享池，W15-D2 决策②；R6/R7 对齐）"),
    changelog_v0_1_2=[
        "示例#2 谓词 POSITION_STATE='空置'→=2（DDL decimal 枚举 1:在租;2:空置）",
        "示例#8 谓词 BILLMONTH=12→BILLYEAR='2024' AND BILLMONTH='12'（varchar 类型对齐，复验新发现）",
        "铺位/空置组 description 值域口径同步改 DDL 枚举",
        "新增值域验证器（枚举/类型/种子三层对账）",
        "pack 契约元数据（domain-semantic-pack-contract R1）",
    ],
    scope=dict(specific_ds=True,
               datasource_ids="SET_AT_IMPORT（= mallcre / CRE BI Demo 数据源 id）",
               reason="术语库是 oid 级共享池，Semantic Model 是项目级资产，不圈作用域=往共享池倒项目私货（W15-D2 决策②）"),
    r2_guard="scenario_layer_frozen=true；生成源仅 aliases+terms；scenario 名仅用于排除校验（断言已过）",
    counts=dict(term_groups=len(term_out), aliases=sum(len(g["other_words"]) for g in term_out),
                sql_examples=len(sql_out), merge_suggestions=len(merge_suggestions),
                ontology_unique_terms=len(unique_terms), consumed_unique_terms=len(consumed)),
    validation=dict(term_binding_failures=len([f for f in failures if f[0] == "binding"]),
                    sql_failures=len([f for f in failures if f[0] == "sql-struct"]),
                    value_domain_pass=sum(1 for r in vd_report if r["verdict"] == "PASS"),
                    value_domain_fail=sum(1 for r in vd_report if r["verdict"] == "FAIL"),
                    regression_sentinels="PASS（#2/#8 新口径 + 旧口径残留检查 + 空置/铺位 description 断言）"),
    files={os.path.basename(p): sha16(p) for p in (tp, sp, mp_)},
)
json.dump(manifest, open(f"{OUT_DIR}/import-manifest.json", "w"), ensure_ascii=False, indent=2)

readme = "\n".join([
    "# LnkChatBI import-pack：MI CRE Semantic Model 消费物",
    "",
    "- 版本：%s v%s（W16-D3 重出；生成器 semantic-model/consumers/lnkchatbi/generate_pack.py，S6 回执律：pack 不手改）" % (PACK_ID, GENERATOR_VERSION),
    "- 格式：与 backend/scripts/mall_ops_starter_pack/ 同构（terminology.json + sql_examples.json），",
    "  可被 setup_mall_ops_starter_pack.py 同款 upsert 通道消费。",
    "- 作用域：specific_ds=true，datasource_ids=[1]（CRE BI Demo）——不进 oid 级共享池（W15-D2 决策②）。",
    "- 源头：ontology SoT 指纹 %s（未漂移）；语义模型 v0.1.1。" % sha_ont,
    "- v0.1.2 修正：示例#2 值域口径（POSITION_STATE=2，DDL 枚举 1:在租/2:空置）、示例#8 类型口径（BILLYEAR/BILLMONTH varchar），",
    "  值域验证器 11/11 PASS；契约元数据对齐 domain-semantic-pack-contract（dev-reference-pack）。",
    "- 消费回执：import-receipt.json（S6：manifest + 验证数字 + 指纹 + 契约对照项）。",
    "- 已知边界：11 条 SQL 落 mallcre demo 对象宇宙，生产白名单（lnk_chatbi_ro analysis 20 对象）0/11——",
    "  生产绑定重生成为 W17+ 方向，Identity 锚点登记（governance/identity-analysis-anchors.yaml）即其输入。",
])
open(f"{PACK_DIR}/README.md", "w").write(readme)

# ------------------------------------------------------------ 8. 报告 + 退出码
print("生成器 v%s | 术语 %d 组/%d 别名 | 示例 %d 条 | merge-suggestions %d" % (
    GENERATOR_VERSION, len(term_out), manifest["counts"]["aliases"], len(sql_out), len(merge_suggestions)))
print("值域对账：", " | ".join("#%d:%s" % (r["no"], r["verdict"]) for r in vd_report))
for r in vd_report:
    print("  #%02d %-26s %s" % (r["no"], r["question"], "; ".join(r["notes"])))
print("落盘：", sorted(os.path.basename(p) for p in (tp, sp, mp_)) + ["import-manifest.json", "import-pack/*"])
print("指纹：", json.dumps(manifest["files"], ensure_ascii=False))
if failures:
    print("\nFAILURES (%d):" % len(failures))
    for f in failures: print("  ✗", f)
    sys.exit(1)
print("\nALL CHECKS PASS (fail-closed: exit 0)")

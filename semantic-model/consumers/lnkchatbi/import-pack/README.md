# LnkChatBI import-pack：MI CRE Semantic Model 消费物

- 版本：lnkcre-mall-ops-demo-pack v0.1.2（W16-D3 重出；生成器 semantic-model/consumers/lnkchatbi/generate_pack.py，S6 回执律：pack 不手改）
- 格式：与 backend/scripts/mall_ops_starter_pack/ 同构（terminology.json + sql_examples.json），
  可被 setup_mall_ops_starter_pack.py 同款 upsert 通道消费。
- 作用域：specific_ds=true，datasource_ids=[1]（CRE BI Demo）——不进 oid 级共享池（W15-D2 决策②）。
- 源头：ontology SoT 指纹 bf550bc24de66813（未漂移）；语义模型 v0.1.1。
- v0.1.2 修正：示例#2 值域口径（POSITION_STATE=2，DDL 枚举 1:在租/2:空置）、示例#8 类型口径（BILLYEAR/BILLMONTH varchar），
  值域验证器 11/11 PASS；契约元数据对齐 domain-semantic-pack-contract（dev-reference-pack）。
- 消费回执：import-receipt.json（S6：manifest + 验证数字 + 指纹 + 契约对照项）。
- 已知边界：11 条 SQL 落 mallcre demo 对象宇宙，生产白名单（lnk_chatbi_ro analysis 20 对象）0/11——
  生产绑定重生成为 W17+ 方向，Identity 锚点登记（governance/identity-analysis-anchors.yaml）即其输入。
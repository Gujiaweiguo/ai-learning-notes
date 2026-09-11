# LnkChatBI import-pack：MI CRE Semantic Model v0.1.1 消费物（W15-D6 物化）

- 格式：与 backend/scripts/mall_ops_starter_pack/ 同构（terminology.json + sql_examples.json），
  可被 setup_mall_ops_starter_pack.py 同款 upsert 通道消费。
- 作用域：specific_ds=true，datasource_ids=[1]（CRE BI Demo）——不进 oid 级共享池（W15-D2 决策②）。
- 源头：semantic-model v0.1.1 → W15-D3 生成物（term-aliases.generated.json / sql-examples.generated.json），
  ontology 指纹 bf550bc24de66813（SoT 未漂移）。
- 消费回执：import-receipt.json（S6 消费回执律：manifest + 验证数字 + SoT 指纹）。
- 已知边界：11 条 SQL 全部落在 mallcre demo 对象宇宙，生产白名单合规 = 0/11（设计域使然，见 §1）；
  示例 #2 谓词值域与种子数据字典不一致（POSITION_STATE 枚举 1/2 vs 文本口径）——源头修正回 D3 生成器，
  不在本 pack 静默改写；W16+ 以白名单 20 对象为绑定目标重生成 v0.2 版本。
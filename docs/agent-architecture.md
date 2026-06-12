# Agent 架构说明

本文记录当前项目里已经落地的 Agent 协作方式，以及这几轮针对 Agent 体系做过的优化。

## 当前协作链路

```text
用户提交 TripPlanRequest
-> trip_plan_service.generate_trip_plan
-> PlannerAgent.run
   -> RequirementAgent 解析补充需求
   -> AttractionAgent 搜索景点候选
   -> WeatherAgent 查询天气摘要
   -> HotelAgent 搜索酒店候选
   -> TripPlanGenerator 组装 PlanningContext 并调用 LLM
   -> trip_plan_postprocessor 做解析和标准化
-> 返回 TripPlan
```

## 已落地的优化

### 统一 Agent 运行结果

`PlannerAgent` 的子任务现在通过统一的 `AgentRunResult` 包装返回值、错误和耗时。这样做的好处是：

- 编排层不再依赖每个子 Agent 的内部细节
- 单个子 Agent 失败时可以平滑降级
- 后续新增交通、餐饮等 Agent 时，接口形式保持一致

### 拆分编排与计划生成

`PlannerAgent` 只负责编排、调度和兜底；`TripPlanGenerator` 专门负责：

- 拼接 prompt
- 调用 LLM
- 解析 JSON
- 标准化最终 `TripPlan`

这让 LLM 相关逻辑和编排逻辑分离，后续如果更换模型或调整 prompt，改动会更集中。

### 收敛 Prompt 入参

`PromptBuilder` 现在接收单个 `PlanningContext`，而不是一长串参数。这个 context 把：

- `TripPlanRequest`
- 需求解析结果
- 景点候选
- 天气摘要
- 酒店候选

统一装进一个对象，减少了调用链的参数膨胀。

### 结构化需求解析

`RequirementAgent` 已经不只是做关键词匹配，还会推导出更稳定的约束摘要：

- `mobility_level`
- `route_intensity`
- `meal_focus`
- `hotel_area_preference`
- `must_have`
- `must_avoid`

这些字段会进入 prompt，上游输入更容易稳定传递给 LLM，下游展示也更容易保持一致。

## 相关文件

- [PlannerAgent](/home/zyp13/projects/travel_assistant/backend/app/agents/planner_agent.py)
- [TripPlanGenerator](/home/zyp13/projects/travel_assistant/backend/app/agents/trip_plan_generator.py)
- [PromptBuilder](/home/zyp13/projects/travel_assistant/backend/app/agents/prompt_builder.py)
- [RequirementAgent](/home/zyp13/projects/travel_assistant/backend/app/agents/requirement_agent.py)
- [Agent schemas](/home/zyp13/projects/travel_assistant/backend/app/agents/schemas.py)

## 测试覆盖

当前 Agent 相关测试覆盖了：

- 子 Agent 成功与失败的统一包装
- PlannerAgent 的正常路径和 fallback 路径
- TripPlanGenerator 的 prompt 组装和规范化
- PromptBuilder 从 PlanningContext 读取数据
- RequirementAgent 的结构化约束解析

这些测试的目标是把编排、生成和需求解析这三层分开保护，避免后续继续加 Agent 时把主链路搞脆。

import os

# 作用：提供旅行计划生成的核心逻辑，根据配置选择使用 Mock 数据还是调用 LLM 生成旅行计划。
from app.models.trip import TripPlan, TripPlanRequest
# PlannerAgent 是一个基于 LLM 的智能代理，负责根据用户需求生成旅行计划。
from app.agents.planner_agent import PlannerAgent
# build_mock_trip_plan 是一个辅助函数，用于生成符合用户需求的 Mock 旅行计划，方便在开发和测试阶段使用。
from app.services.mock_trip_service import build_mock_trip_plan


# generate_trip_plan函数根据环境变量 TRIP_PLAN_MODE 的值来决定生成旅行计划的方式。
# 如果 TRIP_PLAN_MODE 设置为 "mock"，则调用 build_mock_trip_plan 函数生成一个 Mock 旅行计划；
# 如果设置为 "llm"，则创建一个 PlannerAgent 实例并调用其 run 方法来生成基于 LLM 的旅行计划。
# 如果 TRIP_PLAN_MODE 的值不受支持，则抛出一个 ValueError 异常。
def generate_trip_plan(request: TripPlanRequest) -> TripPlan:
    mode = os.getenv("TRIP_PLAN_MODE", "mock")

    if mode == "mock":
        return build_mock_trip_plan(request)

    if mode == "llm":
        planner = PlannerAgent()
        return planner.run(request)

    raise ValueError(f"Unsupported trip plan mode: {mode}")
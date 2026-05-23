from fastapi import APIRouter

# 作用：提供正式的旅行计划生成接口，接受用户的旅行需求并返回完整的旅行计划。

# TripPlanRequest 是一个 Pydantic 模型，定义了用户提交旅行计划请求时需要提供的字段和数据类型。
# TripPlan 是一个 Pydantic 模型，定义了旅行计划的结构，包括每天的行程安排、景点信息、酒店信息等。
# generate_trip_plan 是一个函数，根据用户的旅行需求生成旅行计划，支持使用 Mock 数据或调用 LLM 生成真实的旅行计划。
from app.models.trip import TripPlan, TripPlanRequest
from app.services.trip_plan_service import generate_trip_plan

# 路由器定义了 /api/trip 的 API 路径，并将其标记为 "trip" 标签，方便在 API 文档中进行分类和展示。
router = APIRouter(prefix="/api/trip", tags=["trip"])


# create_trip_plan 是一个 POST 请求的处理函数，接受 TripPlanRequest 作为输入，
# 并返回 TripPlan 作为输出。它调用 generate_trip_plan 函数来生成旅行计划，并将结果返回给客户端。
@router.post("/plan", response_model=TripPlan)
def create_trip_plan(request: TripPlanRequest) -> TripPlan:
    return generate_trip_plan(request)

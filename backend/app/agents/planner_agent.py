from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

# 作用：PlannerAgent 是一个智能代理，负责统一调度多个子 Agent（如 AttractionAgent、WeatherAgent、HotelAgent），并生成最终的旅行计划。
# 它通过并行调用多个子 Agent 来获取景点候选列表、天气快照和酒店候选列表，然后将这些信息整合到一个提示中，调用 LLM 来生成最终的旅行计划。
# 如果在调用子 Agent 或 LLM 的过程中发生任何异常，PlannerAgent 会捕获异常并记录日志，同时使用一个 Mock 旅行计划作为回退方案，确保系统的鲁棒性和用户体验。

# 四个子 Agent 分别负责不同的任务：
from app.agents.attraction_agent import AttractionAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.prompt_builder import build_trip_prompt
from app.agents.requirement_agent import RequirementAgent
from app.agents.weather_agent import WeatherAgent

# call_deepseek函数是一个封装了调用 DeepSeek API 的函数，
# 负责发送构建好的提示词并获取生成结果。它使用 OpenAI 的 Python SDK 来与 DeepSeek API 进行交互，并处理 API 响应中的内容。
from app.models.trip import TripPlan, TripPlanRequest
from app.services.llm_client import call_deepseek
from app.services.llm_trip_service import (
    normalize_trip_plan,
    parse_llm_trip_plan,
)
from app.services.mock_trip_service import build_mock_trip_plan


# PlannerAgent 类的构造函数 __init__ 初始化了三个子 Agent 的实例，分别是 AttractionAgent、WeatherAgent 和 HotelAgent。
class PlannerAgent:
    """负责统一调度多个子 Agent，并生成最终旅行计划。"""

    def __init__(self) -> None:
        # 初始化三个子 Agent 的实例
        self.requirement_agent = RequirementAgent()
        self.attraction_agent = AttractionAgent()
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()

    # run 方法是 PlannerAgent 的核心方法，接受一个 TripPlanRequest 作为输入，并返回一个 TripPlan 作为输出。
    # 它通过并行调用三个子 Agent 来获取所需的信息，然后构建提示词并调用 LLM 来生成旅行计划.
    def run(self, request: TripPlanRequest) -> TripPlan:
        # 记录开始时间，并打印日志信息，包括目的地城市、游玩天数、预算和出行人数等关键信息。
        total_start = perf_counter()
        print(
            f"[PLANNER_AGENT] start city={request.city} days={request.days} "
            f"budget={request.budget} people={request.people}"
        )
        requirement_result = self.requirement_agent.run(request)

        # 使用 ThreadPoolExecutor 来并行调用三个子 Agent 的 run 方法，分别获取景点候选列表、天气快照和酒店候选列表。
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 景点候选列表
            attraction_future = executor.submit(
                self._run_agent_safely,
                # _run_agent_safely 是一个辅助方法，用于安全地调用子 Agent 的 run 方法，
                # 如果发生异常会捕获并记录日志，而不是让整个 PlannerAgent 失败。
                "ATTRACTION_AGENT",
                self.attraction_agent.run,
                request,
                requirement_result,
            )
            # 天气快照
            weather_future = executor.submit(
                self._run_agent_safely,
                "WEATHER_AGENT",
                self.weather_agent.run,
                request,
            )
            # 酒店候选列表
            hotel_future = executor.submit(
                self._run_agent_safely,
                "HOTEL_AGENT",
                self.hotel_agent.run,
                request,
                requirement_result,
            )

            # 接收三个子 Agent 的结果，如果某个 Agent 发生异常导致结果为 None，后续的处理逻辑也会相应地进行调整，确保系统的鲁棒性。
            attraction_result = attraction_future.result()
            weather_result = weather_future.result()
            hotel_result = hotel_future.result()

        # 从三个子 Agent 的结果中提取所需的信息，包括景点候选列表、天气快照和酒店候选列表，并构建提示词。
        poi_candidates = attraction_result.candidates if attraction_result else []
        weather_snapshot = weather_result.snapshot if weather_result else None
        hotel_candidates = hotel_result.candidates if hotel_result else []

        # build_trip_prompt 函数是一个辅助函数，用于根据用户的旅行需求和从子 Agent 获取的信息来构建一个适合 LLM 处理的提示词。
        prompt = build_trip_prompt(
            request=request,
            requirement_result=requirement_result,
            poi_candidates=poi_candidates,
            weather_snapshot=weather_snapshot,
            hotel_candidates=hotel_candidates,
        )

        # 异步调用 LLM 来生成旅行计划，并记录 LLM 调用的耗时。
        # 如果在调用 LLM 的过程中发生任何异常，都会被捕获并记录日志，同时使用一个 Mock 旅行计划作为回退方案，确保系统的鲁棒性和用户体验。
        try:
            llm_start = perf_counter()
            content = call_deepseek(prompt)
            trip_plan = parse_llm_trip_plan(content)
            result = normalize_trip_plan(trip_plan, request, hotel_candidates)
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            # llm_elapsed_ms 和 total_elapsed_ms 分别记录了调用 LLM 的耗时和整个 run 方法的总耗时，
            # 这些信息对于性能监控和优化非常有用。
            llm_elapsed_ms = round((perf_counter() - llm_start) * 1000, 1)
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)

            print(
                f"[PLANNER_AGENT] success city={request.city} "
                f"poi_count={len(poi_candidates)} hotel_count={len(hotel_candidates)} "
                f"weather={'yes' if weather_snapshot else 'no'} "
                f"llm_elapsed_ms={llm_elapsed_ms} total_elapsed_ms={total_elapsed_ms}"
            )

            return result
        except Exception as exc:
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)
            print(f"[PLANNER_AGENT_FALLBACK] {exc} total_elapsed_ms={total_elapsed_ms}")
            result = build_mock_trip_plan(request)
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            return result

    # _run_agent_safely 是一个静态方法，用于安全地调用子 Agent 的 run 方法。
    # 如果在调用过程中发生任何异常，它会捕获异常并记录日志，而不是让整个 PlannerAgent 失败。
    @staticmethod
    def _run_agent_safely(agent_name: str, agent_runner, request: TripPlanRequest, *args):
        try:
            return agent_runner(request, *args)
        except Exception as exc:
            print(f"[{agent_name}_WARN] {exc}")
            return None

from time import perf_counter

from app.agents.schemas import AttractionAgentResult
from app.models.trip import TripPlanRequest
from app.services.poi_service import (
    format_poi_candidates_for_prompt,
    search_trip_poi_candidates,
)


# AttractionAgent 类负责处理与景点相关的逻辑，包括搜索景点候选列表和格式化景点信息以供提示词使用。
class AttractionAgent:
    """负责景点候选搜索与景点上下文整理。"""

    def run(self, request: TripPlanRequest) -> AttractionAgentResult:
        # 记录开始时间，并打印日志信息，包括目的地城市和旅行偏好等关键信息，方便后续的性能监控和调试。
        start = perf_counter()
        print(f"[ATTRACTION_AGENT] start city={request.city} preference={request.preference}")

        # candidates得到搜索到的景点候选列表，
        # prompt_context是将候选列表格式化为一个适合提示词使用的字符串，这些信息将被传递给 LLM 来生成旅行计划。
        candidates = search_trip_poi_candidates(request)
        prompt_context = format_poi_candidates_for_prompt(candidates)
        elapsed_ms = round((perf_counter() - start) * 1000, 1)

        # 打印日志
        print(
            f"[ATTRACTION_AGENT] success city={request.city} "
            f"count={len(candidates)} prompt_chars={len(prompt_context)} elapsed_ms={elapsed_ms}"
        )

        # 返回一个 AttractionAgentResult 对象，包含景点候选列表和格式化后的提示词上下文，
        # 这些信息将被 PlannerAgent 用来生成最终的旅行计划。
        return AttractionAgentResult(
            candidates=candidates,
            prompt_context=prompt_context,
        )

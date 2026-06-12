from app.agents.requirement_schemas import RequirementAgentResult
from app.models.trip import RequirementSummary, TripPlanRequest


class RequirementAgent:
    """解析用户补充需求，生成稳定的结构化旅行约束。"""

    def run(self, request: TripPlanRequest) -> RequirementAgentResult:
        raw_text = (request.requirements or "").strip()
        text = f"{request.preference} {raw_text}".lower()

        pace = self._detect_pace(text)
        companions = self._detect_items(
            text,
            {
                "老人": "老人同行",
                "父母": "父母同行",
                "爸妈": "父母同行",
                "长辈": "长辈同行",
                "孩子": "亲子出行",
                "小孩": "亲子出行",
                "儿童": "亲子出行",
                "宝宝": "亲子出行",
                "情侣": "情侣出行",
                "拍照": "拍照打卡",
            },
        )
        food_preferences = self._detect_items(
            text,
            {
                "小吃": "本地小吃",
                "美食": "美食探索",
                "夜市": "夜市",
                "本地菜": "本地菜",
                "特色菜": "地方特色餐饮",
                "咖啡": "咖啡馆",
                "素食": "素食友好",
                "清淡": "清淡饮食",
            },
        )
        hotel_preferences = self._detect_items(
            text,
            {
                "舒适": "舒适住宿",
                "安静": "安静住宿",
                "交通便利": "交通便利",
                "地铁": "靠近地铁",
                "市中心": "市中心",
                "亲子酒店": "亲子友好",
                "高档": "高档酒店",
                "便宜": "预算友好",
                "省钱": "预算友好",
            },
        )
        avoid = self._detect_items(
            text,
            {
                "人多": "拥挤景点",
                "排队": "长时间排队",
                "网红": "网红打卡点",
                "太累": "高强度行程",
                "爬山": "爬山或大量台阶",
                "暴晒": "长时间暴晒",
                "贵": "高消费项目",
            },
        )
        route_preferences = self._detect_items(
            text,
            {
                "自然": "自然风光",
                "历史": "历史人文",
                "博物馆": "博物馆",
                "公园": "公园散步",
                "购物": "购物休闲",
                "夜景": "夜景",
                "轻松": "轻松路线",
                "深度": "深度游",
            },
        )

        mobility_level = self._detect_mobility_level(
            text=text,
            companions=companions,
            avoid=avoid,
        )
        route_intensity = self._detect_route_intensity(
            pace=pace,
            mobility_level=mobility_level,
        )
        meal_focus = self._detect_meal_focus(food_preferences)
        hotel_area_preference = self._detect_hotel_area_preference(hotel_preferences)
        must_have = self._detect_must_have(raw_text)
        must_avoid = self._merge_unique(avoid)

        attractions_per_day = self._recommend_attractions_per_day(
            pace=pace,
            companions=companions,
            avoid=avoid,
        )
        prompt_context = self._format_prompt_context(
            raw_text=raw_text,
            pace=pace,
            companions=companions,
            food_preferences=food_preferences,
            hotel_preferences=hotel_preferences,
            avoid=avoid,
            route_preferences=route_preferences,
            attractions_per_day=attractions_per_day,
            mobility_level=mobility_level,
            route_intensity=route_intensity,
            meal_focus=meal_focus,
            hotel_area_preference=hotel_area_preference,
            must_have=must_have,
            must_avoid=must_avoid,
        )

        print(
            "[REQUIREMENT_AGENT] "
            f"pace={pace} companions={len(companions)} avoid={len(avoid)} "
            f"mobility={mobility_level} intensity={route_intensity} "
            f"attractions_per_day={attractions_per_day}"
        )

        return RequirementAgentResult(
            raw_text=raw_text,
            pace=pace,
            companions=companions,
            food_preferences=food_preferences,
            hotel_preferences=hotel_preferences,
            avoid=avoid,
            route_preferences=route_preferences,
            attractions_per_day=attractions_per_day,
            prompt_context=prompt_context,
            mobility_level=mobility_level,
            route_intensity=route_intensity,
            meal_focus=meal_focus,
            hotel_area_preference=hotel_area_preference,
            must_have=must_have,
            must_avoid=must_avoid,
        )

    @staticmethod
    def to_summary(result: RequirementAgentResult) -> RequirementSummary:
        return RequirementSummary(
            raw_text=result.raw_text,
            pace=result.pace,
            companions=result.companions,
            food_preferences=result.food_preferences,
            hotel_preferences=result.hotel_preferences,
            avoid=result.avoid,
            route_preferences=result.route_preferences,
            attractions_per_day=result.attractions_per_day,
            mobility_level=result.mobility_level,
            route_intensity=result.route_intensity,
            meal_focus=result.meal_focus,
            hotel_area_preference=result.hotel_area_preference,
            must_have=result.must_have,
            must_avoid=result.must_avoid,
        )

    @staticmethod
    def _detect_pace(text: str) -> str:
        if any(
            keyword in text
            for keyword in ["慢", "轻松", "休闲", "不要太累", "不赶", "少走路", "少步行"]
        ):
            return "慢节奏"
        if any(keyword in text for keyword in ["紧凑", "多逛", "多玩", "充实", "特种兵"]):
            return "紧凑"
        return "正常"

    @staticmethod
    def _detect_items(text: str, keyword_map: dict[str, str]) -> list[str]:
        items: list[str] = []
        seen: set[str] = set()
        for keyword, label in keyword_map.items():
            if keyword in text and label not in seen:
                items.append(label)
                seen.add(label)
        return items

    @staticmethod
    def _recommend_attractions_per_day(
        *,
        pace: str,
        companions: list[str],
        avoid: list[str],
    ) -> int:
        if pace == "慢节奏":
            return 2
        if any(item in companions for item in ["老人同行", "父母同行", "长辈同行", "亲子出行"]):
            return 2
        if "高强度行程" in avoid:
            return 2
        if pace == "紧凑":
            return 3
        return 2

    @staticmethod
    def _detect_mobility_level(
        *,
        text: str,
        companions: list[str],
        avoid: list[str],
    ) -> str:
        low_mobility_keywords = [
            "少走路",
            "少步行",
            "不走太多",
            "别太累",
            "不要太累",
            "腿脚",
            "轮椅",
            "推车",
        ]
        high_mobility_keywords = ["徒步", "多走", "暴走", "citywalk", "city walk"]

        if any(keyword in text for keyword in low_mobility_keywords):
            return "低步行"
        if any(item in companions for item in ["老人同行", "父母同行", "长辈同行", "亲子出行"]):
            return "低步行"
        if "高强度行程" in avoid or "爬山或大量台阶" in avoid:
            return "低步行"
        if any(keyword in text for keyword in high_mobility_keywords):
            return "高步行"
        return "普通"

    @staticmethod
    def _detect_route_intensity(*, pace: str, mobility_level: str) -> str:
        if mobility_level == "低步行" or pace == "慢节奏":
            return "低强度"
        if pace == "紧凑" and mobility_level != "低步行":
            return "高强度"
        return "均衡"

    @staticmethod
    def _detect_meal_focus(food_preferences: list[str]) -> str:
        if any(item in food_preferences for item in ["地方特色餐饮", "本地菜"]):
            return "地方特色餐饮优先"
        if any(item in food_preferences for item in ["本地小吃", "夜市", "美食探索"]):
            return "本地小吃优先"
        if any(item in food_preferences for item in ["素食友好", "清淡饮食"]):
            return "清淡/素食优先"
        if "咖啡馆" in food_preferences:
            return "咖啡休闲优先"
        return "常规餐饮"

    @staticmethod
    def _detect_hotel_area_preference(hotel_preferences: list[str]) -> str:
        if any(item in hotel_preferences for item in ["靠近地铁", "交通便利"]):
            return "地铁/公共交通便利区域"
        if "市中心" in hotel_preferences:
            return "市中心区域"
        if "安静住宿" in hotel_preferences:
            return "安静区域"
        if "亲子友好" in hotel_preferences:
            return "亲子友好区域"
        if "高档酒店" in hotel_preferences:
            return "高品质商圈"
        if "预算友好" in hotel_preferences:
            return "预算友好区域"
        return "交通便利区域"

    @staticmethod
    def _detect_must_have(raw_text: str) -> list[str]:
        items: list[str] = []
        delimiters = "，,。；;、\n"
        triggers = ["必须去", "一定去", "想去", "要去", "必去"]

        for trigger in triggers:
            start = 0
            while True:
                index = raw_text.find(trigger, start)
                if index == -1:
                    break

                value_start = index + len(trigger)
                value_end = len(raw_text)
                for delimiter in delimiters:
                    delimiter_index = raw_text.find(delimiter, value_start)
                    if delimiter_index != -1:
                        value_end = min(value_end, delimiter_index)

                item = raw_text[value_start:value_end].strip()
                if item and item not in items:
                    items.append(item)
                start = value_start

        return items

    @staticmethod
    def _merge_unique(items: list[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for item in items:
            if item in seen:
                continue
            merged.append(item)
            seen.add(item)
        return merged

    @staticmethod
    def _format_prompt_context(
        *,
        raw_text: str,
        pace: str,
        companions: list[str],
        food_preferences: list[str],
        hotel_preferences: list[str],
        avoid: list[str],
        route_preferences: list[str],
        attractions_per_day: int,
        mobility_level: str,
        route_intensity: str,
        meal_focus: str,
        hotel_area_preference: str,
        must_have: list[str],
        must_avoid: list[str],
    ) -> str:
        def format_list(items: list[str]) -> str:
            return "、".join(items) if items else "无明确要求"

        return "\n".join(
            [
                f"- 原始补充需求：{raw_text or '无'}",
                f"- 行程节奏：{pace}",
                f"- 同行人特征：{format_list(companions)}",
                f"- 餐饮偏好：{format_list(food_preferences)}",
                f"- 住宿偏好：{format_list(hotel_preferences)}",
                f"- 避开事项：{format_list(avoid)}",
                f"- 路线偏好：{format_list(route_preferences)}",
                f"- 步行承受度：{mobility_level}",
                f"- 路线强度：{route_intensity}",
                f"- 餐饮重点：{meal_focus}",
                f"- 住宿区域偏好：{hotel_area_preference}",
                f"- 必须包含：{format_list(must_have)}",
                f"- 必须避开：{format_list(must_avoid)}",
                f"- 建议每天景点数：{attractions_per_day}",
            ]
        )

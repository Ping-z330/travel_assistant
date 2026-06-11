from app.models.trip import (
    Attraction,
    Budget,
    DayPlan,
    Hotel,
    Location,
    TripPlan,
    TripPlanRequest,
    WeatherInfo,
)
from app.agents.requirement_agent import RequirementAgent


def build_mock_trip_plan(request: TripPlanRequest) -> TripPlan:
    city = request.city.strip()
    requirement_result = RequirementAgent().run(request)
    template_days = _get_city_template(city, request.start_date)
    selected_days = _build_days_by_request(template_days, request.days, city)
    budget = _calculate_budget(selected_days, request.people)
    requirements_text = (
        f"，并参考“{request.requirements.strip()}”补充需求"
        if request.requirements and request.requirements.strip()
        else ""
    )

    return TripPlan(
        city=city,
        start_date=request.start_date,
        days=selected_days,
        budget=budget,
        overall_suggestion=(
            f"已根据 {request.people} 人、{request.budget} 元预算和"
            f"“{request.preference}”偏好{requirements_text}，"
            f"为你生成 {city} 的示例旅行计划。"
        ),
        requirement_summary=RequirementAgent.to_summary(requirement_result),
    )


def _get_city_template(city: str, start_date: str) -> list[DayPlan]:
    if "北京" in city:
        return _beijing_template(start_date)
    if "杭州" in city:
        return _hangzhou_template(start_date)
    if "成都" in city:
        return _chengdu_template(start_date)
    if "上海" in city:
        return _shanghai_template(start_date)

    return _default_city_template(city, start_date)


def _build_days_by_request(
    template_days: list[DayPlan],
    requested_days: int,
    city: str,
) -> list[DayPlan]:
    if requested_days <= len(template_days):
        return template_days[:requested_days]

    extra_days = [
        _build_free_exploration_day(day_index, city)
        for day_index in range(len(template_days) + 1, requested_days + 1)
    ]

    return [*template_days, *extra_days]


def _calculate_budget(days: list[DayPlan], people: int) -> Budget:
    total_hotels = sum(day.hotel.price for day in days)
    total_attractions = sum(
        attraction.ticket_price
        for day in days
        for attraction in day.attractions
    )
    total_meals = 120 * people * len(days)
    total_transportation = 80 * people * len(days)

    return Budget(
        total_attractions=total_attractions,
        total_hotels=total_hotels,
        total_meals=total_meals,
        total_transportation=total_transportation,
        total=total_hotels + total_attractions + total_meals + total_transportation,
    )


def _build_free_exploration_day(day: int, city: str) -> DayPlan:
    return DayPlan(
        day=day,
        title=f"{city}自由探索路线",
        attractions=[
            Attraction(
                name=f"{city}城市漫游",
                address=f"{city}核心商圈与特色街区",
                location=Location(longitude=116.397128, latitude=39.916527),
                visit_duration=180,
                ticket_price=0,
                description="根据个人体力和兴趣自由安排，适合补充购物、咖啡馆、夜景或小众街区。",
                image_url="",
                category="自由探索",
            ),
            Attraction(
                name=f"{city}本地生活体验",
                address=f"{city}本地居民生活区域",
                location=Location(longitude=116.407526, latitude=39.90403),
                visit_duration=120,
                ticket_price=0,
                description="预留弹性时间，用来体验当地餐饮、市场和慢节奏城市生活。",
                image_url="",
                category="城市体验",
            ),
        ],
        meals=["午餐：本地特色餐厅", "晚餐：城市夜市或商圈"],
        hotel=Hotel(
            name=f"{city}舒适酒店",
            address=f"{city}交通便利区域",
            price=460,
            description="选择靠近地铁或核心商圈的位置，方便自由安排行程。",
        ),
        weather=WeatherInfo(
            date=f"第 {day} 天",
            weather="多云",
            temperature="18-26°C",
            suggestion="这一天安排较灵活，可以根据天气和体力微调路线。",
        ),
    )


def _beijing_template(start_date: str) -> list[DayPlan]:
    return [
        DayPlan(
            day=1,
            title="城市经典文化路线",
            attractions=[
                Attraction(
                    name="故宫博物院",
                    address="北京市东城区景山前街4号",
                    location=Location(longitude=116.397128, latitude=39.916527),
                    visit_duration=180,
                    ticket_price=60,
                    description="适合了解北京历史文化，是第一天的核心景点。",
                    image_url="",
                    category="历史文化",
                ),
                Attraction(
                    name="景山公园",
                    address="北京市西城区景山西街44号",
                    location=Location(longitude=116.396454, latitude=39.925082),
                    visit_duration=90,
                    ticket_price=10,
                    description="可以俯瞰故宫中轴线，适合傍晚散步。",
                    image_url="",
                    category="城市公园",
                ),
            ],
            meals=["午餐：王府井小吃", "晚餐：北京烤鸭"],
            hotel=Hotel(
                name="前门精品酒店",
                address="北京市东城区前门附近",
                price=520,
                description="位置靠近核心景区，方便第一天和第二天出行。",
            ),
            weather=WeatherInfo(
                date=start_date,
                weather="晴",
                temperature="18-27°C",
                suggestion="适合步行游览，建议携带防晒用品。",
            ),
        ),
        DayPlan(
            day=2,
            title="皇家园林与湖畔休闲路线",
            attractions=[
                Attraction(
                    name="颐和园",
                    address="北京市海淀区新建宫门路19号",
                    location=Location(longitude=116.273556, latitude=39.999974),
                    visit_duration=180,
                    ticket_price=30,
                    description="湖景和园林体验丰富，适合慢节奏游览。",
                    image_url="",
                    category="皇家园林",
                ),
                Attraction(
                    name="圆明园遗址公园",
                    address="北京市海淀区清华西路28号",
                    location=Location(longitude=116.305434, latitude=40.008986),
                    visit_duration=120,
                    ticket_price=10,
                    description="适合搭配颐和园安排在同一区域游玩。",
                    image_url="",
                    category="历史遗址",
                ),
            ],
            meals=["午餐：海淀本地餐馆", "晚餐：中关村商圈"],
            hotel=Hotel(
                name="海淀舒适酒店",
                address="北京市海淀区中关村附近",
                price=460,
                description="靠近第二天景点区域，减少跨城通勤。",
            ),
            weather=WeatherInfo(
                date="第 2 天",
                weather="多云",
                temperature="17-25°C",
                suggestion="户外时间较长，建议穿舒适鞋子。",
            ),
        ),
        DayPlan(
            day=3,
            title="长城与城市地标路线",
            attractions=[
                Attraction(
                    name="八达岭长城",
                    address="北京市延庆区G6京藏高速58号出口",
                    location=Location(longitude=116.016802, latitude=40.356047),
                    visit_duration=240,
                    ticket_price=40,
                    description="北京代表性景点，适合安排半天以上。",
                    image_url="",
                    category="世界遗产",
                ),
                Attraction(
                    name="奥林匹克公园",
                    address="北京市朝阳区北辰东路15号",
                    location=Location(longitude=116.396583, latitude=39.992857),
                    visit_duration=90,
                    ticket_price=0,
                    description="返程后可轻松打卡鸟巢和水立方外景。",
                    image_url="",
                    category="城市地标",
                ),
            ],
            meals=["午餐：长城景区简餐", "晚餐：奥体商圈"],
            hotel=Hotel(
                name="朝阳商务酒店",
                address="北京市朝阳区奥体附近",
                price=480,
                description="适合最后一天返程或继续市区活动。",
            ),
            weather=WeatherInfo(
                date="第 3 天",
                weather="晴转多云",
                temperature="16-26°C",
                suggestion="长城风大，建议准备外套。",
            ),
        ),
    ]


def _hangzhou_template(start_date: str) -> list[DayPlan]:
    return [
        DayPlan(
            day=1,
            title="西湖经典漫游路线",
            attractions=[
                Attraction(
                    name="西湖风景名胜区",
                    address="杭州市西湖区龙井路1号",
                    location=Location(longitude=120.14137, latitude=30.259244),
                    visit_duration=210,
                    ticket_price=0,
                    description="杭州最具代表性的湖景路线，适合慢慢散步和拍照。",
                    image_url="",
                    category="自然风光",
                ),
                Attraction(
                    name="雷峰塔",
                    address="杭州市西湖区南山路15号",
                    location=Location(longitude=120.148905, latitude=30.23397),
                    visit_duration=90,
                    ticket_price=40,
                    description="适合傍晚登塔看西湖全景，也能串联白蛇传传说。",
                    image_url="",
                    category="人文地标",
                ),
            ],
            meals=["午餐：西湖醋鱼", "晚餐：湖滨银泰商圈"],
            hotel=Hotel(
                name="湖滨轻奢酒店",
                address="杭州市上城区湖滨商圈附近",
                price=520,
                description="靠近西湖与地铁，适合第一天轻松游览。",
            ),
            weather=WeatherInfo(
                date=start_date,
                weather="多云",
                temperature="19-27°C",
                suggestion="湖边步行较多，建议穿轻便鞋。",
            ),
        ),
        DayPlan(
            day=2,
            title="湿地与茶园清新路线",
            attractions=[
                Attraction(
                    name="西溪国家湿地公园",
                    address="杭州市西湖区天目山路518号",
                    location=Location(longitude=120.064634, latitude=30.270377),
                    visit_duration=180,
                    ticket_price=80,
                    description="适合喜欢自然风光和慢节奏体验的游客。",
                    image_url="",
                    category="自然生态",
                ),
                Attraction(
                    name="龙井村",
                    address="杭州市西湖区龙井路",
                    location=Location(longitude=120.116942, latitude=30.234843),
                    visit_duration=120,
                    ticket_price=0,
                    description="可以体验茶园风景和杭州本地茶文化。",
                    image_url="",
                    category="茶文化",
                ),
            ],
            meals=["午餐：茶园农家菜", "晚餐：武林夜市"],
            hotel=Hotel(
                name="西溪度假酒店",
                address="杭州市西湖区西溪湿地附近",
                price=560,
                description="适合自然路线，环境安静，便于第二天休息。",
            ),
            weather=WeatherInfo(
                date="第 2 天",
                weather="小雨转阴",
                temperature="18-24°C",
                suggestion="建议带伞，湿地和茶园雨天也很有氛围。",
            ),
        ),
        DayPlan(
            day=3,
            title="宋韵文化与城市烟火路线",
            attractions=[
                Attraction(
                    name="河坊街",
                    address="杭州市上城区河坊街",
                    location=Location(longitude=120.169633, latitude=30.244675),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合体验杭州老街、小吃和伴手礼。",
                    image_url="",
                    category="城市烟火",
                ),
                Attraction(
                    name="杭州宋城",
                    address="杭州市西湖区之江路148号",
                    location=Location(longitude=120.098675, latitude=30.168328),
                    visit_duration=210,
                    ticket_price=320,
                    description="适合集中体验宋韵文化和大型演出。",
                    image_url="",
                    category="文化演艺",
                ),
            ],
            meals=["午餐：河坊街小吃", "晚餐：宋城周边餐厅"],
            hotel=Hotel(
                name="上城城市酒店",
                address="杭州市上城区定安路附近",
                price=430,
                description="靠近老城区，返程和购物都比较方便。",
            ),
            weather=WeatherInfo(
                date="第 3 天",
                weather="晴",
                temperature="20-28°C",
                suggestion="适合城市步行，注意补水。",
            ),
        ),
    ]


def _chengdu_template(start_date: str) -> list[DayPlan]:
    return [
        DayPlan(
            day=1,
            title="熊猫与城市慢生活路线",
            attractions=[
                Attraction(
                    name="成都大熊猫繁育研究基地",
                    address="成都市成华区熊猫大道1375号",
                    location=Location(longitude=104.145595, latitude=30.735483),
                    visit_duration=210,
                    ticket_price=55,
                    description="建议上午前往，更容易看到熊猫活动。",
                    image_url="",
                    category="亲子自然",
                ),
                Attraction(
                    name="宽窄巷子",
                    address="成都市青羊区金河路口宽窄巷子",
                    location=Location(longitude=104.057711, latitude=30.669931),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合下午慢逛，体验成都茶馆和街巷生活。",
                    image_url="",
                    category="城市街区",
                ),
            ],
            meals=["午餐：担担面", "晚餐：成都火锅"],
            hotel=Hotel(
                name="春熙路精选酒店",
                address="成都市锦江区春熙路附近",
                price=420,
                description="位于核心商圈，餐饮和交通都方便。",
            ),
            weather=WeatherInfo(
                date=start_date,
                weather="阴",
                temperature="20-28°C",
                suggestion="成都节奏适合慢游，不建议排太满。",
            ),
        ),
        DayPlan(
            day=2,
            title="历史人文与锦江夜色路线",
            attractions=[
                Attraction(
                    name="武侯祠",
                    address="成都市武侯区武侯祠大街231号",
                    location=Location(longitude=104.047015, latitude=30.641837),
                    visit_duration=120,
                    ticket_price=50,
                    description="适合了解三国文化，也能和锦里一起安排。",
                    image_url="",
                    category="历史人文",
                ),
                Attraction(
                    name="锦里古街",
                    address="成都市武侯区武侯祠大街231号附1号",
                    location=Location(longitude=104.046722, latitude=30.642172),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合傍晚和夜间游览，美食和灯光氛围更好。",
                    image_url="",
                    category="美食街区",
                ),
            ],
            meals=["午餐：钟水饺", "晚餐：锦里小吃"],
            hotel=Hotel(
                name="武侯文化酒店",
                address="成都市武侯区高升桥附近",
                price=390,
                description="靠近武侯祠和锦里，适合文化路线。",
            ),
            weather=WeatherInfo(
                date="第 2 天",
                weather="多云",
                temperature="21-29°C",
                suggestion="景点距离较近，可以步行加短途打车。",
            ),
        ),
        DayPlan(
            day=3,
            title="都江堰青城山清凉路线",
            attractions=[
                Attraction(
                    name="都江堰景区",
                    address="成都市都江堰市公园路",
                    location=Location(longitude=103.619986, latitude=31.001254),
                    visit_duration=180,
                    ticket_price=80,
                    description="适合了解水利工程和川西历史。",
                    image_url="",
                    category="世界遗产",
                ),
                Attraction(
                    name="青城山",
                    address="成都市都江堰市青城山镇",
                    location=Location(longitude=103.570228, latitude=30.905107),
                    visit_duration=210,
                    ticket_price=80,
                    description="山林清幽，适合喜欢自然和轻徒步的游客。",
                    image_url="",
                    category="自然山水",
                ),
            ],
            meals=["午餐：都江堰本地菜", "晚餐：返程后简餐"],
            hotel=Hotel(
                name="青城山脚客栈",
                address="成都市都江堰市青城山附近",
                price=360,
                description="适合想放慢节奏、体验山脚住宿的游客。",
            ),
            weather=WeatherInfo(
                date="第 3 天",
                weather="阵雨",
                temperature="18-25°C",
                suggestion="山区天气变化快，建议带雨具和防滑鞋。",
            ),
        ),
    ]


def _shanghai_template(start_date: str) -> list[DayPlan]:
    return [
        DayPlan(
            day=1,
            title="外滩与城市天际线路线",
            attractions=[
                Attraction(
                    name="外滩",
                    address="上海市黄浦区中山东一路",
                    location=Location(longitude=121.490317, latitude=31.239702),
                    visit_duration=120,
                    ticket_price=0,
                    description="上海城市名片，适合傍晚到夜间欣赏浦江两岸。",
                    image_url="",
                    category="城市地标",
                ),
                Attraction(
                    name="东方明珠",
                    address="上海市浦东新区世纪大道1号",
                    location=Location(longitude=121.499809, latitude=31.239666),
                    visit_duration=150,
                    ticket_price=199,
                    description="适合俯瞰陆家嘴天际线，体验城市高度。",
                    image_url="",
                    category="观景地标",
                ),
            ],
            meals=["午餐：南京东路本帮菜", "晚餐：陆家嘴商圈"],
            hotel=Hotel(
                name="人民广场城市酒店",
                address="上海市黄浦区人民广场附近",
                price=620,
                description="交通便利，适合外滩和市中心路线。",
            ),
            weather=WeatherInfo(
                date=start_date,
                weather="晴",
                temperature="19-27°C",
                suggestion="夜景是重点，建议预留傍晚后的时间。",
            ),
        ),
        DayPlan(
            day=2,
            title="海派文化与老街路线",
            attractions=[
                Attraction(
                    name="豫园",
                    address="上海市黄浦区福佑路168号",
                    location=Location(longitude=121.492182, latitude=31.227213),
                    visit_duration=120,
                    ticket_price=40,
                    description="适合体验江南园林和上海老城厢文化。",
                    image_url="",
                    category="园林文化",
                ),
                Attraction(
                    name="田子坊",
                    address="上海市黄浦区泰康路210弄",
                    location=Location(longitude=121.469227, latitude=31.210594),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合逛创意小店、咖啡馆和弄堂空间。",
                    image_url="",
                    category="创意街区",
                ),
            ],
            meals=["午餐：城隍庙小吃", "晚餐：淮海路餐厅"],
            hotel=Hotel(
                name="淮海路精品酒店",
                address="上海市黄浦区淮海中路附近",
                price=580,
                description="靠近老城与商业街区，适合步行探索。",
            ),
            weather=WeatherInfo(
                date="第 2 天",
                weather="多云",
                temperature="18-25°C",
                suggestion="老街区适合步行，建议轻装出行。",
            ),
        ),
        DayPlan(
            day=3,
            title="艺术展馆与滨江休闲路线",
            attractions=[
                Attraction(
                    name="上海博物馆",
                    address="上海市黄浦区人民大道201号",
                    location=Location(longitude=121.481473, latitude=31.230416),
                    visit_duration=150,
                    ticket_price=0,
                    description="适合喜欢历史与艺术的人群，室内安排也适合雨天。",
                    image_url="",
                    category="艺术展馆",
                ),
                Attraction(
                    name="徐汇滨江",
                    address="上海市徐汇区龙腾大道",
                    location=Location(longitude=121.456911, latitude=31.177983),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合下午散步、骑行和看日落。",
                    image_url="",
                    category="滨江休闲",
                ),
            ],
            meals=["午餐：人民广场周边", "晚餐：徐汇滨江餐厅"],
            hotel=Hotel(
                name="徐汇滨江酒店",
                address="上海市徐汇区滨江附近",
                price=560,
                description="环境较舒适，适合第三天放慢节奏。",
            ),
            weather=WeatherInfo(
                date="第 3 天",
                weather="阴",
                temperature="17-24°C",
                suggestion="室内外结合，天气一般也不影响整体体验。",
            ),
        ),
    ]


def _default_city_template(city: str, start_date: str) -> list[DayPlan]:
    return [
        DayPlan(
            day=1,
            title=f"{city}城市初识路线",
            attractions=[
                Attraction(
                    name=f"{city}城市地标",
                    address=f"{city}市中心区域",
                    location=Location(longitude=116.397128, latitude=39.916527),
                    visit_duration=150,
                    ticket_price=0,
                    description="优先安排城市代表性地标，帮助快速建立目的地印象。",
                    image_url="",
                    category="城市地标",
                ),
                Attraction(
                    name=f"{city}特色街区",
                    address=f"{city}特色商业与生活街区",
                    location=Location(longitude=116.407526, latitude=39.90403),
                    visit_duration=120,
                    ticket_price=0,
                    description="适合体验当地餐饮、购物和街区氛围。",
                    image_url="",
                    category="城市街区",
                ),
            ],
            meals=["午餐：当地特色简餐", "晚餐：城市商圈餐厅"],
            hotel=Hotel(
                name=f"{city}中心酒店",
                address=f"{city}交通便利区域",
                price=450,
                description="建议选择靠近公共交通的位置，方便后续行程。",
            ),
            weather=WeatherInfo(
                date=start_date,
                weather="多云",
                temperature="18-26°C",
                suggestion="第一天以轻松适应为主，不建议安排过满。",
            ),
        ),
        _build_free_exploration_day(2, city),
        _build_free_exploration_day(3, city),
    ]

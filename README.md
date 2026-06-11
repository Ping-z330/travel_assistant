# 智能旅行助手（多智能体最终版）

一个基于 `Vue 3 + FastAPI + LLM` 的智能旅行规划项目。系统会根据用户输入的城市、出发日期、天数、预算、人数和旅行偏好，自动生成结构化旅行计划，并结合真实外部数据完成地图展示与结果导出。

## 项目亮点

- 基于 `DeepSeek` 生成多日旅行计划
- 接入高德真实 `POI`、天气、酒店数据
- 接入 `Pexels` 景点图片
- 支持动态城市解析，不依赖固定城市映射表
- 支持地图展示、酒店点位展示与按天路线区分
- 支持 PDF 导出
- 已完成第一版多智能体协作架构
- 已加入日志、重试、并行和缓存优化

## 当前架构

### 后端核心链路

```text
前端请求
-> POST /api/trip/plan
-> trip_plan_service.generate_trip_plan
-> PlannerAgent.run
   -> AttractionAgent
   -> WeatherAgent
   -> HotelAgent
-> PromptBuilder 组装 Prompt
-> DeepSeek 生成结构化 TripPlan
-> parse_llm_trip_plan
-> normalize_trip_plan
-> 返回前端
```

### 多智能体职责拆分

- `PlannerAgent`
  负责统一调度子 Agent、调用 LLM、汇总结果。
- `AttractionAgent`
  负责景点候选搜索与景点上下文整理。
- `WeatherAgent`
  负责天气查询与天气上下文整理。
- `HotelAgent`
  负责酒店候选搜索与酒店上下文整理。
- `PromptBuilder`
  负责把用户需求、景点、天气、酒店上下文组装成最终 Prompt。

## 功能概览

### 1. 行程生成

- 输入城市、日期、天数、预算、人数和偏好
- 自动生成多天结构化行程
- 每天包含：
  - 景点
  - 酒店
  - 餐饮建议
  - 天气信息

### 2. 真实数据增强

- 景点：高德 POI 搜索 + 清洗去重
- 天气：高德天气查询
- 酒店：高德酒店候选搜索 + 坐标
- 图片：Pexels 搜图

### 3. 地图展示

- 景点按天使用不同颜色显示
- 每天路线单独绘制
- 酒店使用独立图标显示
- 连续多天入住同一家酒店时自动合并点位

### 4. PDF 导出

- 结果页支持一键导出 PDF
- 基于 `html2canvas + jsPDF`

## 项目结构

```text
travel-assistant/
├─ backend/
│  ├─ app/
│  │  ├─ agents/
│  │  │  ├─ attraction_agent.py
│  │  │  ├─ weather_agent.py
│  │  │  ├─ hotel_agent.py
│  │  │  ├─ planner_agent.py
│  │  │  ├─ prompt_builder.py
│  │  │  └─ schemas.py
│  │  ├─ api/
│  │  │  ├─ trip.py
│  │  │  └─ trip_debug.py
│  │  ├─ models/
│  │  │  └─ trip.py
│  │  └─ services/
│  │     ├─ amap_client.py
│  │     ├─ poi_service.py
│  │     ├─ weather_service.py
│  │     ├─ hotel_service.py
│  │     ├─ image_service.py
│  │     ├─ llm_trip_service.py
│  │     ├─ llm_client.py
│  │     ├─ trip_plan_service.py
│  │     ├─ mock_trip_service.py
│  │     └─ cache_utils.py
│  └─ main.py
├─ frontend/
│  ├─ src/components/
│  ├─ src/services/
│  ├─ src/types/
│  └─ src/views/
├─ README.md
└─ ROADMAP.md
```

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Vue Router
- Axios
- `@amap/amap-jsapi-loader`
- `html2canvas`
- `jspdf`

### 后端

- FastAPI
- Pydantic
- httpx
- python-dotenv
- OpenAI SDK 兼容方式调用 DeepSeek

### 外部服务

- DeepSeek API
- 高德 Web Service API
- 高德 JSAPI
- Pexels API

## 环境变量

### 后端 `backend/.env`

```env
TRIP_PLAN_MODE=llm
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-v4-flash
AMAP_WEB_API_KEY=your_amap_webservice_key
PEXELS_API_KEY=your_pexels_api_key
```

### 前端 `frontend/.env.local`

```env
VITE_AMAP_JSAPI_KEY=your_amap_jsapi_key
```

## 本地运行

### 1. 启动后端

```powershell
cd e:\Ai_Project\travel-assistant\backend
.\venv\Scripts\Activate.ps1
$env:TRIP_PLAN_MODE="llm"
uvicorn main:app --reload --port 8003
```

启动后访问：

- `http://localhost:8003/`
- `http://localhost:8003/docs`

### 2. 启动前端

```powershell
cd e:\Ai_Project\travel-assistant\frontend
npm.cmd install
npm.cmd run dev
```

默认开发地址：

- `http://localhost:5173`

## API 说明

### 正式接口

- `POST /api/trip/plan`
  生成正式旅行计划

### 调试接口

- `GET /api/trip/debug/poi`
  调试景点搜索
- `GET /api/trip/debug/weather`
  调试天气查询
- `GET /api/trip/debug/hotel`
  调试酒店搜索
- `GET /api/trip/debug/image`
  调试景点图片搜索

## 稳定性与性能优化

当前版本已加入以下工程化能力：

- 重试
  - 高德底层请求支持超时/网络错误轻量重试
- 并行
  - `PlannerAgent` 会并行调用景点、天气、酒店三个子 Agent
- 缓存
  - 景点、天气、酒店支持短时 TTL 缓存
  - 城市地理编码支持 `lru_cache`
- 日志
  - 各 Agent 具备开始、成功、失败、耗时日志
- 兜底
  - LLM 返回异常时支持结构修补和 fallback

## 结果页说明

结果页当前包含：

- 行程概览
- 预算摘要
- 地图展示
- 每日景点安排
- 天气信息
- 酒店推荐
- 餐饮建议
- 景点图片
- PDF 导出

## 多智能体工作方式

可以把当前系统理解成“一个总控规划师 + 三个专业助手”：

- `AttractionAgent`
  提供景点候选
- `WeatherAgent`
  提供天气摘要
- `HotelAgent`
  提供酒店候选
- `PlannerAgent`
  汇总三者并调用大模型生成最终 `TripPlan`

这属于第一版协作式多智能体架构，特点是：

- 职责明确
- 调度清晰
- 容易扩展
- 比单智能体版本更利于维护和优化

## 回归测试

当前版本已完成以下城市的真实链路回归：

- 北京
- 杭州
- 成都
- 南昌

验证内容包括：

- `/api/trip/plan` 正常返回
- 景点、天气、酒店结果完整
- 酒店带真实坐标
- 地图可消费返回坐标

## 已知说明

- PDF 导出当前基于页面截图，长内容会自动分页
- 第三方地图瓦片在部分场景下可能影响 PDF 中的地图截图表现
- 外部接口网络波动时仍可能出现 warning，但系统保留了 fallback 和兜底逻辑

## 后续方向

- 完善单元测试与集成测试
- 进一步清理后端剩余历史乱码与注释
- 继续增强 PDF 导出体验
- 增强地图与卡片联动
- 继续升级更高级的多智能体协作模式

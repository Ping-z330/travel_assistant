# 智能旅行助手

一个基于 `Vue 3 + FastAPI + LLM` 的智能旅行规划项目。系统可以根据用户输入的城市、天数、预算、人数和旅行偏好，自动生成结构化行程，并融合真实外部数据完成地图可视化展示。

## 当前能力

- 基于 `DeepSeek` 生成多天旅行计划
- 接入高德 `POI` 搜索，提供真实景点候选
- 接入高德天气查询，结合天气调整行程建议
- 接入高德酒店候选搜索，输出真实酒店名称与坐标
- 接入 `Unsplash` 图片搜索，为景点补充展示图片
- 支持动态城市解析，不再依赖固定城市映射表
- 支持结果页地图展示
- 地图上区分每日景点路线与酒店点位
- 支持结果页导出 PDF

## 项目结构

```text
travel-assistant/
├─ backend/                  # FastAPI 后端
│  ├─ app/
│  │  ├─ api/                # 路由
│  │  ├─ models/             # Pydantic 数据模型
│  │  └─ services/           # LLM / 高德 / 图片 / mock / 规划逻辑
│  └─ main.py                # FastAPI 入口
├─ frontend/                 # Vue 3 前端
│  ├─ src/components/        # 表单、结果页、地图、卡片组件
│  ├─ src/services/          # 前端 API 调用
│  └─ src/types/             # 前端类型定义
└─ ROADMAP.md                # 项目阶段路线图
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
- OpenAI SDK 兼容调用 DeepSeek
- python-dotenv

### 外部服务

- DeepSeek API
- 高德 Web Service API
- 高德 JSAPI
- Unsplash API

## 环境变量

### 后端 `backend/.env`

```env
TRIP_PLAN_MODE=llm
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-v4-flash
AMAP_WEB_API_KEY=your_amap_webservice_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
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
uvicorn main:app --reload --port 8003
```

后端启动后可访问：

- `http://localhost:8003/`
- `http://localhost:8003/docs`

### 2. 启动前端

```powershell
cd e:\Ai_Project\travel-assistant\frontend
npm.cmd install
npm.cmd run dev
```

前端开发地址默认是：

- `http://localhost:5173`

## 主要接口

- `POST /api/trip/plan`
  生成正式旅行计划
- `GET /api/trip/debug/poi`
  调试景点搜索
- `GET /api/trip/debug/weather`
  调试天气查询
- `GET /api/trip/debug/hotel`
  调试酒店搜索
- `GET /api/trip/debug/image`
  调试景点图片搜索

## 结果页说明

结果页当前包含：

- 行程概览
- 预算摘要
- 地图预览
- 每日景点安排
- 每日天气信息
- 每日酒店推荐
- 景点图片
- PDF 导出按钮

地图增强效果包括：

- 每天路线使用不同颜色区分
- 景点使用胶囊编号标记
- 酒店单独使用“住”图标标记
- 酒店不参与景点连线

## 四城市回归测试

测试时间：`2026-05-22`

测试方式：

- 启用 `TRIP_PLAN_MODE=llm`
- 使用真实高德、DeepSeek、Unsplash 链路
- 直接调用后端 `generate_trip_plan`

测试结果如下：

| 城市 | 天数 | 第一天景点示例 | 第一天酒店示例 | 酒店坐标 | 结果 |
| --- | --- | --- | --- | --- | --- |
| 北京 | 3 天 | 故宫博物院、南锣鼓巷 | 正义路酒店(北京王府井天安门广场店) | 有 | 通过 |
| 杭州 | 3 天 | 杭州西湖风景名胜区、雷峰塔景区 | 全季酒店(杭州钱江新城店) | 有 | 通过 |
| 成都 | 3 天 | 成都武侯祠博物馆、锦里古街 | 蔚盛酒店(大魔方金融城演艺中心环球中心店) | 有 | 通过 |
| 南昌 | 3 天 | 滕王阁、八大山人梅湖景区 | 全季酒店(南昌红谷滩万达广场酒店) | 有 | 通过 |

说明：

- 四个城市都能返回 3 天结构化行程
- 四个城市第一天酒店都带真实坐标
- 地图展示可直接消费酒店与景点坐标

## 已知说明

- PDF 导出当前以页面截图方式生成，长内容会自动分页
- 第三方地图瓦片在部分场景下可能影响 PDF 中的地图截图表现
- 个别外部接口在网络抖动时可能触发警告日志，但系统保留 fallback 机制

## 后续方向

- 优化首页与结果页剩余细节文案
- 增强 PDF 导出效果
- 支持地图与卡片联动
- 接入更真实的多点路线规划
- 继续完善文档与演示材料

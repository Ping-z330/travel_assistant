# Frontend

前端说明已合并到仓库根目录的 [README.md](../README.md)。

本目录常用命令：

```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run test
npm.cmd run build
```

地图环境变量请放在：

```env
frontend/.env.local
```

示例：

```env
VITE_API_BASE_URL=http://localhost:8003
VITE_AMAP_JSAPI_KEY=your_amap_jsapi_key
```

## 页面与路由

- `/`：登录页，只展示登录表单和左侧绿色系旅行图片。
- `/plan`：登录后的旅行规划表单页。
- `/result`：旅行计划结果页，支持编辑、保存到我的行程和导出 PDF。
- `/my-trips`：本地保存的行程列表页。

`/plan`、`/result`、`/my-trips` 都会经过前端路由守卫；未登录会回到 `/`，已登录访问 `/` 会跳转到 `/plan`。

## 登录说明

前端认证状态由 `src/services/auth.ts` 管理，token 和用户信息保存在 `localStorage`。默认开发账号来自后端：

```text
demo / travel123
```

登录后页面共享 `src/components/AppNav.vue` 顶部导航。

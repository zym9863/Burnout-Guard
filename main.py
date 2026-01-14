"""Burnout Guard - 耗尽卫士 FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import data_router, energy_router, intervention_router
from app.services.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    yield
    # 关闭时
    await scheduler.close()
    print(f"👋 {settings.app_name} 已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    description="""
## 耗尽卫士 (Burnout Guard)

一个基于 FastAPI 的认知负荷监测与干预调度系统。

### 核心功能

- 🧠 **认知负荷聚合计算** - 接收多源数据，计算实时精力槽和疲劳指数
- ⏰ **强制阻断与恢复调度** - 后台任务处理、Webhook 触发、恢复时间表生成

### 数据源

- GitHub 活动数据 (提交、PR、代码审查)
- 日历会议数据 (会议数量、时长)
- 屏幕使用时间 (活跃时间、连续使用)

### API 分组

- **数据输入**: 提交各类数据源信息
- **精力状态**: 查询精力槽和疲劳指数
- **干预调度**: 管理 Webhook 和触发干预
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(data_router)
app.include_router(energy_router)
app.include_router(intervention_router)


@app.get("/", tags=["健康检查"])
async def root():
    """根路径 - 应用信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

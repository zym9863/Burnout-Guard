"""干预调度路由"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..models.intervention import (
    WebhookConfig, 
    RecoverySchedule, 
    InterventionEvent,
    InterventionType
)
from ..services.scheduler import scheduler

router = APIRouter(prefix="/api", tags=["干预调度"])


class WebhookRegisterRequest(BaseModel):
    """Webhook 注册请求"""
    name: str
    url: str
    intervention_types: List[InterventionType] = [InterventionType.REST_REMINDER]
    headers: dict = {}


class TriggerInterventionRequest(BaseModel):
    """触发干预请求"""
    type: InterventionType = InterventionType.REST_REMINDER
    force: bool = False


@router.post("/webhook/register", summary="注册 Webhook", response_model=WebhookConfig)
async def register_webhook(request: WebhookRegisterRequest) -> WebhookConfig:
    """
    注册 Webhook 端点，用于接收干预通知
    
    - **name**: Webhook 名称
    - **url**: Webhook URL
    - **intervention_types**: 触发此 Webhook 的干预类型列表
    - **headers**: 自定义请求头
    """
    config = WebhookConfig(
        name=request.name,
        url=request.url,
        intervention_types=request.intervention_types,
        headers=request.headers
    )
    return scheduler.register_webhook(config)


@router.delete("/webhook/{webhook_id}", summary="注销 Webhook")
async def unregister_webhook(webhook_id: UUID) -> dict:
    """注销指定的 Webhook"""
    if scheduler.unregister_webhook(webhook_id):
        return {"status": "success", "message": f"Webhook {webhook_id} 已注销"}
    raise HTTPException(status_code=404, detail="Webhook 不存在")


@router.get("/webhook", summary="列出所有 Webhook", response_model=List[WebhookConfig])
async def list_webhooks() -> List[WebhookConfig]:
    """列出所有已注册的 Webhook"""
    return scheduler.list_webhooks()


@router.get("/recovery-schedule", summary="获取恢复时间表", response_model=RecoverySchedule)
async def get_recovery_schedule() -> RecoverySchedule:
    """
    根据当前疲劳程度生成恢复时间表
    
    返回:
    - **fatigue_level**: 当前疲劳级别
    - **energy_level**: 当前精力槽
    - **total_recovery_time**: 总恢复时间(分钟)
    - **activities**: 恢复活动列表
    - **urgency**: 紧急程度
    - **message**: 恢复建议信息
    """
    return scheduler.generate_recovery_schedule()


@router.post("/intervention/trigger", summary="手动触发干预", response_model=InterventionEvent)
async def trigger_intervention(request: TriggerInterventionRequest) -> InterventionEvent:
    """
    手动触发干预事件
    
    - **type**: 干预类型
    - **force**: 是否强制触发(跳过状态检查)
    """
    event = await scheduler.trigger_intervention(
        intervention_type=request.type,
        force=request.force
    )
    return event


@router.get("/intervention/history", summary="获取干预历史", response_model=List[InterventionEvent])
async def get_intervention_history(limit: int = 10) -> List[InterventionEvent]:
    """
    获取干预历史记录
    
    - **limit**: 返回的记录数量上限
    """
    return scheduler.get_intervention_history(limit=limit)

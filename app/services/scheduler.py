"""干预调度服务"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
import httpx

from ..core.config import settings
from ..models.intervention import (
    WebhookConfig, 
    RecoverySchedule, 
    InterventionEvent,
    InterventionType
)
from .aggregator import aggregator


class InterventionScheduler:
    """干预调度器 - 管理 Webhook 和恢复计划"""
    
    def __init__(self):
        self._webhooks: Dict[UUID, WebhookConfig] = {}
        self._intervention_history: List[InterventionEvent] = []
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=settings.webhook_timeout
            )
        return self._http_client
    
    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
    
    def register_webhook(self, config: WebhookConfig) -> WebhookConfig:
        """注册 Webhook"""
        self._webhooks[config.id] = config
        return config
    
    def unregister_webhook(self, webhook_id: UUID) -> bool:
        """注销 Webhook"""
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False
    
    def get_webhook(self, webhook_id: UUID) -> Optional[WebhookConfig]:
        """获取 Webhook 配置"""
        return self._webhooks.get(webhook_id)
    
    def list_webhooks(self) -> List[WebhookConfig]:
        """列出所有 Webhook"""
        return list(self._webhooks.values())
    
    async def _send_webhook(
        self, 
        webhook: WebhookConfig, 
        event: InterventionEvent
    ) -> bool:
        """发送 Webhook 通知"""
        if not webhook.enabled:
            return False
        
        try:
            client = await self._get_client()
            payload = {
                "event_id": str(event.id),
                "type": event.type.value,
                "triggered_at": event.triggered_at.isoformat(),
                "fatigue_level": event.fatigue_at_trigger,
                "energy_level": event.energy_at_trigger,
                "message": event.message
            }
            
            headers = {"Content-Type": "application/json"}
            headers.update(webhook.headers)
            
            for attempt in range(settings.webhook_retry_count):
                try:
                    response = await client.post(
                        webhook.url,
                        json=payload,
                        headers=headers
                    )
                    if response.status_code < 400:
                        return True
                except httpx.RequestError:
                    if attempt == settings.webhook_retry_count - 1:
                        raise
                    await asyncio.sleep(1 * (attempt + 1))  # 指数退避
            
            return False
            
        except Exception as e:
            print(f"Webhook 发送失败: {webhook.name} - {e}")
            return False
    
    async def trigger_intervention(
        self, 
        intervention_type: InterventionType,
        force: bool = False
    ) -> InterventionEvent:
        """
        触发干预事件
        
        Args:
            intervention_type: 干预类型
            force: 是否强制触发(跳过状态检查)
        """
        # 获取当前状态
        energy = aggregator.calculate_energy()
        fatigue = aggregator.calculate_fatigue()
        
        # 检查是否需要干预
        if not force and not aggregator.needs_intervention():
            return InterventionEvent(
                type=intervention_type,
                fatigue_at_trigger=fatigue.value,
                energy_at_trigger=energy.value,
                success=False,
                message="当前状态良好，无需干预"
            )
        
        # 创建干预事件
        event = InterventionEvent(
            type=intervention_type,
            fatigue_at_trigger=fatigue.value,
            energy_at_trigger=energy.value,
            message=f"触发 {intervention_type.value} 干预"
        )
        
        # 通知相关 Webhook
        notified_webhooks: List[UUID] = []
        for webhook_id, webhook in self._webhooks.items():
            if intervention_type in webhook.intervention_types:
                success = await self._send_webhook(webhook, event)
                if success:
                    notified_webhooks.append(webhook_id)
        
        event.webhook_notified = notified_webhooks
        event.success = True
        
        # 记录历史
        self._intervention_history.append(event)
        
        return event
    
    def generate_recovery_schedule(self) -> RecoverySchedule:
        """生成恢复时间表"""
        energy = aggregator.calculate_energy()
        fatigue = aggregator.calculate_fatigue()
        
        return RecoverySchedule.generate(
            fatigue=fatigue.value,
            energy=energy.value
        )
    
    def get_intervention_history(
        self, 
        limit: int = 10
    ) -> List[InterventionEvent]:
        """获取干预历史"""
        return self._intervention_history[-limit:][::-1]


# 全局单例实例
scheduler = InterventionScheduler()

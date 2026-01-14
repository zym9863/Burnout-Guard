"""干预调度模型"""
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4


class InterventionType(str, Enum):
    """干预类型枚举"""
    LOCK_SCREEN = "lock_screen"           # 锁屏
    REST_REMINDER = "rest_reminder"       # 休息提醒
    BLOCK_APPS = "block_apps"             # 阻止应用
    MEDITATION = "meditation"             # 冥想建议
    STRETCH_BREAK = "stretch_break"       # 伸展休息
    HYDRATION = "hydration"               # 补水提醒
    EYE_REST = "eye_rest"                 # 眼睛休息


class WebhookConfig(BaseModel):
    """Webhook 配置模型"""
    id: UUID = Field(default_factory=uuid4, description="Webhook ID")
    name: str = Field(..., min_length=1, max_length=100, description="Webhook 名称")
    url: str = Field(..., description="Webhook URL")
    intervention_types: List[InterventionType] = Field(
        default=[InterventionType.REST_REMINDER],
        description="触发此 Webhook 的干预类型"
    )
    enabled: bool = Field(default=True, description="是否启用")
    headers: dict = Field(default_factory=dict, description="自定义请求头")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class RecoveryActivity(BaseModel):
    """恢复活动模型"""
    type: InterventionType = Field(..., description="活动类型")
    duration_minutes: int = Field(..., gt=0, description="建议时长(分钟)")
    priority: int = Field(default=1, ge=1, le=5, description="优先级 (1最高)")
    description: str = Field(default="", description="活动描述")
    instructions: List[str] = Field(default_factory=list, description="活动指南")


class RecoverySchedule(BaseModel):
    """恢复时间表模型"""
    id: UUID = Field(default_factory=uuid4, description="时间表 ID")
    fatigue_level: float = Field(..., ge=0, le=100, description="当前疲劳级别")
    energy_level: float = Field(..., ge=0, le=100, description="当前精力槽")
    total_recovery_time: int = Field(..., description="总恢复时间(分钟)")
    activities: List[RecoveryActivity] = Field(default_factory=list, description="恢复活动列表")
    start_time: datetime = Field(default_factory=datetime.now, description="建议开始时间")
    urgency: str = Field(default="normal", description="紧急程度")
    message: str = Field(default="", description="恢复建议信息")
    
    @classmethod
    def generate(cls, fatigue: float, energy: float) -> "RecoverySchedule":
        """根据疲劳和精力状态生成恢复时间表"""
        activities = []
        
        # 根据疲劳程度生成不同的恢复计划
        if fatigue >= 80:
            urgency = "critical"
            total_time = 60
            activities = [
                RecoveryActivity(
                    type=InterventionType.LOCK_SCREEN,
                    duration_minutes=5,
                    priority=1,
                    description="强制锁屏休息",
                    instructions=["立即离开屏幕", "闭眼深呼吸"]
                ),
                RecoveryActivity(
                    type=InterventionType.MEDITATION,
                    duration_minutes=15,
                    priority=2,
                    description="冥想放松",
                    instructions=["找一个安静的地方", "进行 15 分钟冥想"]
                ),
                RecoveryActivity(
                    type=InterventionType.STRETCH_BREAK,
                    duration_minutes=10,
                    priority=3,
                    description="伸展运动",
                    instructions=["站立伸展", "活动颈部和肩膀"]
                ),
                RecoveryActivity(
                    type=InterventionType.HYDRATION,
                    duration_minutes=5,
                    priority=4,
                    description="补充水分",
                    instructions=["喝一杯水", "适量补充电解质"]
                ),
            ]
            message = "🆘 检测到严重疲劳！请立即执行恢复计划"
            
        elif fatigue >= 60:
            urgency = "high"
            total_time = 30
            activities = [
                RecoveryActivity(
                    type=InterventionType.EYE_REST,
                    duration_minutes=5,
                    priority=1,
                    description="眼睛休息",
                    instructions=["看向远处", "闭眼休息 20 秒"]
                ),
                RecoveryActivity(
                    type=InterventionType.STRETCH_BREAK,
                    duration_minutes=10,
                    priority=2,
                    description="站立伸展",
                    instructions=["起身走动", "伸展四肢"]
                ),
                RecoveryActivity(
                    type=InterventionType.HYDRATION,
                    duration_minutes=5,
                    priority=3,
                    description="补水",
                    instructions=["喝一杯水"]
                ),
            ]
            message = "😫 疲劳程度较高，建议尽快休息"
            
        elif fatigue >= 40:
            urgency = "medium"
            total_time = 15
            activities = [
                RecoveryActivity(
                    type=InterventionType.REST_REMINDER,
                    duration_minutes=5,
                    priority=1,
                    description="短暂休息",
                    instructions=["暂停工作", "放松眼睛"]
                ),
                RecoveryActivity(
                    type=InterventionType.HYDRATION,
                    duration_minutes=5,
                    priority=2,
                    description="补充水分",
                    instructions=["喝一杯水"]
                ),
            ]
            message = "😴 中度疲劳，建议短暂休息"
            
        else:
            urgency = "low"
            total_time = 5
            activities = [
                RecoveryActivity(
                    type=InterventionType.EYE_REST,
                    duration_minutes=2,
                    priority=1,
                    description="20-20-20 法则",
                    instructions=["每 20 分钟", "看 20 英尺外", "持续 20 秒"]
                ),
            ]
            message = "✨ 状态良好，保持良好习惯"
        
        return cls(
            fatigue_level=fatigue,
            energy_level=energy,
            total_recovery_time=total_time,
            activities=activities,
            urgency=urgency,
            message=message
        )


class InterventionEvent(BaseModel):
    """干预事件模型"""
    id: UUID = Field(default_factory=uuid4, description="事件 ID")
    type: InterventionType = Field(..., description="干预类型")
    triggered_at: datetime = Field(default_factory=datetime.now, description="触发时间")
    fatigue_at_trigger: float = Field(..., ge=0, le=100, description="触发时的疲劳指数")
    energy_at_trigger: float = Field(..., ge=0, le=100, description="触发时的精力槽")
    webhook_notified: List[UUID] = Field(default_factory=list, description="已通知的 Webhook ID 列表")
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="", description="事件信息")

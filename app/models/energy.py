"""精力槽与疲劳指数模型"""
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class EnergyLevel(str, Enum):
    """精力等级枚举"""
    CRITICAL = "critical"      # 危险 (0-20)
    LOW = "low"                # 低 (20-40)
    MODERATE = "moderate"      # 中等 (40-60)
    GOOD = "good"              # 良好 (60-80)
    EXCELLENT = "excellent"    # 充沛 (80-100)


class EnergyState(BaseModel):
    """精力槽状态模型"""
    value: float = Field(..., ge=0, le=100, description="精力槽值 (0-100)")
    level: EnergyLevel = Field(..., description="精力等级")
    github_contribution: float = Field(default=0, description="GitHub 负荷贡献")
    calendar_contribution: float = Field(default=0, description="日历负荷贡献")
    screen_contribution: float = Field(default=0, description="屏幕负荷贡献")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    message: str = Field(default="", description="状态提示信息")
    
    @classmethod
    def from_value(cls, value: float, **kwargs) -> "EnergyState":
        """根据精力值创建状态对象"""
        value = max(0, min(100, value))
        
        if value <= 20:
            level = EnergyLevel.CRITICAL
            message = "⚠️ 精力严重不足，建议立即休息！"
        elif value <= 40:
            level = EnergyLevel.LOW
            message = "😟 精力较低，请考虑放慢节奏"
        elif value <= 60:
            level = EnergyLevel.MODERATE
            message = "😐 精力中等，注意合理安排工作"
        elif value <= 80:
            level = EnergyLevel.GOOD
            message = "😊 精力良好，继续保持"
        else:
            level = EnergyLevel.EXCELLENT
            message = "🚀 精力充沛，状态极佳！"
        
        return cls(value=value, level=level, message=message, **kwargs)


class FatigueLevel(str, Enum):
    """疲劳等级枚举"""
    NONE = "none"              # 无疲劳 (0-20)
    MILD = "mild"              # 轻度 (20-40)
    MODERATE = "moderate"      # 中度 (40-60)
    HIGH = "high"              # 高度 (60-80)
    SEVERE = "severe"          # 严重 (80-100)


class FatigueIndex(BaseModel):
    """疲劳指数模型"""
    value: float = Field(..., ge=0, le=100, description="疲劳指数 (0-100)")
    level: FatigueLevel = Field(..., description="疲劳等级")
    continuous_work_hours: float = Field(default=0, ge=0, description="连续工作时长(小时)")
    recovery_needed: bool = Field(default=False, description="是否需要强制恢复")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    message: str = Field(default="", description="疲劳提示信息")
    
    @classmethod
    def from_value(cls, value: float, continuous_hours: float = 0) -> "FatigueIndex":
        """根据疲劳值创建指数对象"""
        value = max(0, min(100, value))
        
        if value <= 20:
            level = FatigueLevel.NONE
            message = "✨ 状态清醒，精神饱满"
            recovery_needed = False
        elif value <= 40:
            level = FatigueLevel.MILD
            message = "💭 轻微疲劳，建议适时休息"
            recovery_needed = False
        elif value <= 60:
            level = FatigueLevel.MODERATE
            message = "😴 中度疲劳，请安排短暂休息"
            recovery_needed = True
        elif value <= 80:
            level = FatigueLevel.HIGH
            message = "😫 高度疲劳，强烈建议立即休息"
            recovery_needed = True
        else:
            level = FatigueLevel.SEVERE
            message = "🆘 严重疲劳，必须强制休息！"
            recovery_needed = True
        
        return cls(
            value=value, 
            level=level, 
            message=message,
            continuous_work_hours=continuous_hours,
            recovery_needed=recovery_needed
        )

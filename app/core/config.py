"""应用配置模块"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类，定义权重系数和阈值参数"""
    
    # 应用基本信息
    app_name: str = "Burnout Guard"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 认知负荷权重系数 (总和应为 1.0)
    github_weight: float = Field(default=0.35, ge=0, le=1, description="GitHub 活动权重")
    calendar_weight: float = Field(default=0.35, ge=0, le=1, description="日历会议权重")
    screen_weight: float = Field(default=0.30, ge=0, le=1, description="屏幕时间权重")
    
    # 精力槽阈值
    energy_critical_threshold: float = Field(default=20.0, description="精力槽危险阈值")
    energy_warning_threshold: float = Field(default=40.0, description="精力槽警告阈值")
    
    # 疲劳指数参数
    fatigue_duration_factor: float = Field(default=0.1, description="持续工作时间疲劳因子")
    fatigue_critical_threshold: float = Field(default=80.0, description="疲劳危险阈值")
    
    # Webhook 配置
    webhook_timeout: float = Field(default=10.0, description="Webhook 请求超时时间(秒)")
    webhook_retry_count: int = Field(default=3, description="Webhook 重试次数")
    
    # 恢复建议参数
    short_break_duration: int = Field(default=5, description="短休息时长(分钟)")
    medium_break_duration: int = Field(default=15, description="中等休息时长(分钟)")
    long_break_duration: int = Field(default=30, description="长休息时长(分钟)")
    
    class Config:
        env_prefix = "BURNOUT_"
        env_file = ".env"


settings = Settings()

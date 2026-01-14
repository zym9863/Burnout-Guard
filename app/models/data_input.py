"""数据输入模型"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class GitHubData(BaseModel):
    """GitHub 活动数据模型"""
    commits_count: int = Field(..., ge=0, description="提交数量")
    pull_requests: int = Field(default=0, ge=0, description="PR 数量")
    code_reviews: int = Field(default=0, ge=0, description="代码审查数量")
    issues_resolved: int = Field(default=0, ge=0, description="解决的 Issue 数量")
    period_hours: float = Field(default=24.0, gt=0, description="统计周期(小时)")
    timestamp: datetime = Field(default_factory=datetime.now, description="数据时间戳")
    
    @property
    def activity_intensity(self) -> float:
        """计算活动强度 (0-100)"""
        # 加权计算各项活动的强度
        base_score = (
            self.commits_count * 2 +
            self.pull_requests * 5 +
            self.code_reviews * 3 +
            self.issues_resolved * 2
        )
        # 归一化到 0-100，假设每小时 5 个活动单位为满负荷
        max_expected = self.period_hours * 5
        return min(100.0, (base_score / max_expected) * 100) if max_expected > 0 else 0


class CalendarData(BaseModel):
    """日历会议数据模型"""
    meetings_count: int = Field(..., ge=0, description="会议数量")
    total_meeting_hours: float = Field(..., ge=0, description="会议总时长(小时)")
    back_to_back_meetings: int = Field(default=0, ge=0, description="连续会议数量")
    period_hours: float = Field(default=24.0, gt=0, description="统计周期(小时)")
    timestamp: datetime = Field(default_factory=datetime.now, description="数据时间戳")
    
    @property
    def meeting_intensity(self) -> float:
        """计算会议强度 (0-100)"""
        # 会议时间占比
        time_ratio = (self.total_meeting_hours / self.period_hours * 100) if self.period_hours > 0 else 0
        # 连续会议惩罚
        b2b_penalty = self.back_to_back_meetings * 5
        return min(100.0, time_ratio + b2b_penalty)


class ScreenTimeData(BaseModel):
    """屏幕使用时间数据模型"""
    active_hours: float = Field(..., ge=0, description="屏幕活跃时间(小时)")
    continuous_sessions: int = Field(default=1, ge=1, description="连续使用次数(无休息)")
    app_switches: int = Field(default=0, ge=0, description="应用切换次数")
    period_hours: float = Field(default=24.0, gt=0, description="统计周期(小时)")
    timestamp: datetime = Field(default_factory=datetime.now, description="数据时间戳")
    
    @property
    def screen_intensity(self) -> float:
        """计算屏幕使用强度 (0-100)"""
        # 使用时间占比
        time_ratio = (self.active_hours / self.period_hours * 100) if self.period_hours > 0 else 0
        # 连续使用惩罚 (每次无休息连续使用增加 10%)
        continuous_penalty = (self.continuous_sessions - 1) * 10
        # 频繁切换增加认知负荷
        switch_penalty = min(20, self.app_switches / 10)
        return min(100.0, time_ratio + continuous_penalty + switch_penalty)

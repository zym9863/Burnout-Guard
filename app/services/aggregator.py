"""认知负荷聚合计算服务"""
from datetime import datetime
from typing import Optional
from ..core.config import settings
from ..models.data_input import GitHubData, CalendarData, ScreenTimeData
from ..models.energy import EnergyState, FatigueIndex


class CognitiveLoadAggregator:
    """认知负荷聚合器 - 计算精力槽和疲劳指数"""
    
    def __init__(self):
        # 最新的数据源
        self._github_data: Optional[GitHubData] = None
        self._calendar_data: Optional[CalendarData] = None
        self._screen_data: Optional[ScreenTimeData] = None
        
        # 工作时间追踪
        self._work_start_time: Optional[datetime] = None
        self._last_activity_time: Optional[datetime] = None
        self._continuous_work_hours: float = 0.0
        
        # 缓存的状态
        self._cached_energy: Optional[EnergyState] = None
        self._cached_fatigue: Optional[FatigueIndex] = None
    
    def update_github_data(self, data: GitHubData) -> None:
        """更新 GitHub 数据"""
        self._github_data = data
        self._update_work_time()
        self._invalidate_cache()
    
    def update_calendar_data(self, data: CalendarData) -> None:
        """更新日历数据"""
        self._calendar_data = data
        self._update_work_time()
        self._invalidate_cache()
    
    def update_screen_data(self, data: ScreenTimeData) -> None:
        """更新屏幕时间数据"""
        self._screen_data = data
        self._update_work_time()
        self._invalidate_cache()
    
    def _update_work_time(self) -> None:
        """更新工作时间追踪"""
        now = datetime.now()
        
        if self._work_start_time is None:
            self._work_start_time = now
        
        if self._last_activity_time is not None:
            # 如果距离上次活动超过 30 分钟，重置工作开始时间
            gap = (now - self._last_activity_time).total_seconds() / 3600
            if gap > 0.5:  # 30 分钟无活动视为休息
                self._work_start_time = now
                self._continuous_work_hours = 0.0
            else:
                self._continuous_work_hours = (now - self._work_start_time).total_seconds() / 3600
        
        self._last_activity_time = now
    
    def _invalidate_cache(self) -> None:
        """使缓存失效"""
        self._cached_energy = None
        self._cached_fatigue = None
    
    def calculate_energy(self) -> EnergyState:
        """
        计算精力槽状态
        
        公式: energy = 100 - (github_weight * github_load 
                            + calendar_weight * calendar_load 
                            + screen_weight * screen_load)
        """
        if self._cached_energy is not None:
            return self._cached_energy
        
        # 获取各数据源的负荷值
        github_load = self._github_data.activity_intensity if self._github_data else 0
        calendar_load = self._calendar_data.meeting_intensity if self._calendar_data else 0
        screen_load = self._screen_data.screen_intensity if self._screen_data else 0
        
        # 加权计算贡献
        github_contribution = settings.github_weight * github_load
        calendar_contribution = settings.calendar_weight * calendar_load
        screen_contribution = settings.screen_weight * screen_load
        
        # 计算总负荷和精力值
        total_load = github_contribution + calendar_contribution + screen_contribution
        energy_value = max(0, 100 - total_load)
        
        # 创建精力状态对象
        self._cached_energy = EnergyState.from_value(
            value=energy_value,
            github_contribution=github_contribution,
            calendar_contribution=calendar_contribution,
            screen_contribution=screen_contribution
        )
        
        return self._cached_energy
    
    def calculate_fatigue(self) -> FatigueIndex:
        """
        计算疲劳指数
        
        公式: fatigue = base_fatigue * (1 + duration_factor * hours_worked)
        其中 base_fatigue = 100 - energy
        """
        if self._cached_fatigue is not None:
            return self._cached_fatigue
        
        # 获取精力状态
        energy = self.calculate_energy()
        base_fatigue = 100 - energy.value
        
        # 根据持续工作时间增加疲劳
        duration_multiplier = 1 + settings.fatigue_duration_factor * self._continuous_work_hours
        fatigue_value = min(100, base_fatigue * duration_multiplier)
        
        # 创建疲劳指数对象
        self._cached_fatigue = FatigueIndex.from_value(
            value=fatigue_value,
            continuous_hours=self._continuous_work_hours
        )
        
        return self._cached_fatigue
    
    def needs_intervention(self) -> bool:
        """判断是否需要干预"""
        energy = self.calculate_energy()
        fatigue = self.calculate_fatigue()
        
        return (
            energy.value <= settings.energy_critical_threshold or
            fatigue.value >= settings.fatigue_critical_threshold
        )
    
    def get_status_summary(self) -> dict:
        """获取状态摘要"""
        energy = self.calculate_energy()
        fatigue = self.calculate_fatigue()
        
        return {
            "energy": energy.model_dump(),
            "fatigue": fatigue.model_dump(),
            "needs_intervention": self.needs_intervention(),
            "continuous_work_hours": round(self._continuous_work_hours, 2),
            "data_sources": {
                "github": self._github_data is not None,
                "calendar": self._calendar_data is not None,
                "screen": self._screen_data is not None
            }
        }


# 全局单例实例
aggregator = CognitiveLoadAggregator()

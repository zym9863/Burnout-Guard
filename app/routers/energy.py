"""精力状态路由"""
from fastapi import APIRouter
from ..models.energy import EnergyState, FatigueIndex
from ..services.aggregator import aggregator

router = APIRouter(prefix="/api", tags=["精力状态"])


@router.get("/energy", summary="获取当前精力槽状态", response_model=EnergyState)
async def get_energy_state() -> EnergyState:
    """
    获取当前精力槽状态
    
    返回:
    - **value**: 精力槽值 (0-100)
    - **level**: 精力等级 (critical/low/moderate/good/excellent)
    - **github_contribution**: GitHub 负荷贡献
    - **calendar_contribution**: 日历负荷贡献
    - **screen_contribution**: 屏幕负荷贡献
    - **message**: 状态提示信息
    """
    return aggregator.calculate_energy()


@router.get("/fatigue", summary="获取疲劳指数", response_model=FatigueIndex)
async def get_fatigue_index() -> FatigueIndex:
    """
    获取当前疲劳指数
    
    返回:
    - **value**: 疲劳指数 (0-100)
    - **level**: 疲劳等级 (none/mild/moderate/high/severe)
    - **continuous_work_hours**: 连续工作时长
    - **recovery_needed**: 是否需要强制恢复
    - **message**: 疲劳提示信息
    """
    return aggregator.calculate_fatigue()


@router.get("/status", summary="获取完整状态摘要")
async def get_status_summary() -> dict:
    """
    获取完整状态摘要，包括精力槽、疲劳指数和数据源状态
    """
    return aggregator.get_status_summary()

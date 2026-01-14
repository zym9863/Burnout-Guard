"""数据输入路由"""
from fastapi import APIRouter, BackgroundTasks
from ..models.data_input import GitHubData, CalendarData, ScreenTimeData
from ..services.aggregator import aggregator
from ..services.scheduler import scheduler
from ..models.intervention import InterventionType

router = APIRouter(prefix="/api/data", tags=["数据输入"])


async def check_and_trigger_intervention(background_tasks: BackgroundTasks):
    """检查是否需要触发干预"""
    if aggregator.needs_intervention():
        await scheduler.trigger_intervention(
            InterventionType.REST_REMINDER,
            force=True
        )


@router.post("/github", summary="提交 GitHub 活动数据")
async def submit_github_data(
    data: GitHubData,
    background_tasks: BackgroundTasks
) -> dict:
    """
    接收 GitHub 活动数据并更新认知负荷计算
    
    - **commits_count**: 提交数量
    - **pull_requests**: PR 数量
    - **code_reviews**: 代码审查数量
    - **issues_resolved**: 解决的 Issue 数量
    - **period_hours**: 统计周期(小时)
    """
    aggregator.update_github_data(data)
    
    # 后台检查是否需要干预
    background_tasks.add_task(check_and_trigger_intervention, background_tasks)
    
    return {
        "status": "success",
        "message": "GitHub 数据已更新",
        "activity_intensity": data.activity_intensity,
        "current_energy": aggregator.calculate_energy().value
    }


@router.post("/calendar", summary="提交日历会议数据")
async def submit_calendar_data(
    data: CalendarData,
    background_tasks: BackgroundTasks
) -> dict:
    """
    接收日历会议数据并更新认知负荷计算
    
    - **meetings_count**: 会议数量
    - **total_meeting_hours**: 会议总时长(小时)
    - **back_to_back_meetings**: 连续会议数量
    - **period_hours**: 统计周期(小时)
    """
    aggregator.update_calendar_data(data)
    
    # 后台检查是否需要干预
    background_tasks.add_task(check_and_trigger_intervention, background_tasks)
    
    return {
        "status": "success",
        "message": "日历数据已更新",
        "meeting_intensity": data.meeting_intensity,
        "current_energy": aggregator.calculate_energy().value
    }


@router.post("/screen", summary="提交屏幕使用时间数据")
async def submit_screen_data(
    data: ScreenTimeData,
    background_tasks: BackgroundTasks
) -> dict:
    """
    接收屏幕使用时间数据并更新认知负荷计算
    
    - **active_hours**: 屏幕活跃时间(小时)
    - **continuous_sessions**: 连续使用次数
    - **app_switches**: 应用切换次数
    - **period_hours**: 统计周期(小时)
    """
    aggregator.update_screen_data(data)
    
    # 后台检查是否需要干预
    background_tasks.add_task(check_and_trigger_intervention, background_tasks)
    
    return {
        "status": "success",
        "message": "屏幕使用数据已更新",
        "screen_intensity": data.screen_intensity,
        "current_energy": aggregator.calculate_energy().value
    }

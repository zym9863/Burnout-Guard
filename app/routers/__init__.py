"""API 路由模块"""
from .data import router as data_router
from .energy import router as energy_router
from .intervention import router as intervention_router

__all__ = ["data_router", "energy_router", "intervention_router"]

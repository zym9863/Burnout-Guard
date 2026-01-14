# 🛡️ Burnout Guard (耗尽卫士)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于 FastAPI 的认知负荷监测与干预调度系统，帮助开发者预防工作倦怠。

## ✨ 功能特性

### 🧠 认知负荷聚合计算

- **多源数据接入** - 支持 GitHub 活动、日历会议、屏幕使用时间等多种数据源
- **实时精力槽计算** - 基于加权算法计算当前精力状态 (0-100)
- **疲劳指数追踪** - 考虑持续工作时间的疲劳累积计算

### ⏰ 强制阻断与恢复调度

- **自动干预触发** - 当精力过低或疲劳过高时自动触发干预
- **Webhook 通知** - 支持注册多个 Webhook 接收干预通知
- **智能恢复时间表** - 根据疲劳程度动态生成个性化恢复计划

## 🚀 快速开始

### 前置要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装

```bash
# 克隆仓库
git clone https://github.com/zym9863/burnout-guard.git
cd burnout-guard

# 安装依赖
uv sync
```

### 运行

```bash
# 启动开发服务器
uv run uvicorn main:app --reload --port 8000
```

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看交互式 API 文档。

## 📚 API 端点

### 数据输入

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/data/github` | POST | 提交 GitHub 活动数据 |
| `/api/data/calendar` | POST | 提交日历会议数据 |
| `/api/data/screen` | POST | 提交屏幕使用时间 |

### 精力状态

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/energy` | GET | 获取当前精力槽状态 |
| `/api/fatigue` | GET | 获取疲劳指数 |
| `/api/status` | GET | 获取完整状态摘要 |

### 干预调度

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/webhook/register` | POST | 注册 Webhook 端点 |
| `/api/webhook/{id}` | DELETE | 注销 Webhook |
| `/api/webhook` | GET | 列出所有 Webhook |
| `/api/recovery-schedule` | GET | 获取恢复时间表 |
| `/api/intervention/trigger` | POST | 手动触发干预 |
| `/api/intervention/history` | GET | 获取干预历史 |

## 🔧 配置

支持通过环境变量或 `.env` 文件配置（前缀 `BURNOUT_`）：

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `BURNOUT_GITHUB_WEIGHT` | 0.35 | GitHub 活动权重 |
| `BURNOUT_CALENDAR_WEIGHT` | 0.35 | 日历会议权重 |
| `BURNOUT_SCREEN_WEIGHT` | 0.30 | 屏幕时间权重 |
| `BURNOUT_ENERGY_CRITICAL_THRESHOLD` | 20.0 | 精力槽危险阈值 |
| `BURNOUT_FATIGUE_CRITICAL_THRESHOLD` | 80.0 | 疲劳危险阈值 |

## 📐 算法说明

### 精力槽计算

```
energy = 100 - (github_weight × github_load 
              + calendar_weight × calendar_load 
              + screen_weight × screen_load)
```

### 疲劳指数计算

```
fatigue = base_fatigue × (1 + duration_factor × hours_worked)

其中: base_fatigue = 100 - energy
```

## 📁 项目结构

```
Burnout-Guard/
├── main.py                    # FastAPI 应用入口
├── pyproject.toml            # 项目配置
├── app/
│   ├── core/                 # 核心配置
│   │   └── config.py         # 应用配置
│   ├── models/               # Pydantic 数据模型
│   │   ├── data_input.py     # 数据输入模型
│   │   ├── energy.py         # 精力槽模型
│   │   └── intervention.py   # 干预调度模型
│   ├── services/             # 业务逻辑服务
│   │   ├── aggregator.py     # 认知负荷聚合计算
│   │   └── scheduler.py      # 干预调度服务
│   └── routers/              # API 路由
│       ├── data.py           # 数据输入路由
│       ├── energy.py         # 精力状态路由
│       └── intervention.py   # 干预调度路由
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

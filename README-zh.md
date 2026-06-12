# ittybitty

**主题或脚本进 → 旁白视频出。** 抖音/TikTok 短视频，或分章节的中长教程——素材来自 Pexels、你的 Jellyfin/Plex 家庭片库，或本地 Wan 2.2 AI 片段。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](docs/ALPHA-RELEASE-CHECKLIST.md)

> **Alpha — 施工中。** API、管线（R3 审片室、R9 数字人画中画）和 Windows 安装包可能在版本之间变动。非生产就绪。英文主文档：[README.md](README.md)

**三种用法**（任选其一）：

| | **Windows 应用** | **Web 仪表盘** | **MCP 服务** |
|---|---|---|---|
| **适合** | 日常在 PC 上出片 | 开发/自托管时浏览器操作 | Cursor、Claude 等 MCP 客户端 |
| **得到** | 安装包 + 桌面快捷方式；后端自动启动 | 生成、任务、片库、设置、帮助 | `videogen_*` 工具供 Agent 调用 |
| **开始** | [下载预发布版](#windows-应用) | `.\start.bat` 或直接用上面的应用 | `http://127.0.0.1:11054/mcp` |

同一套引擎：后端 **11054**，开发时 Vite 前端 **11055**。

---

## 它做什么

给它一个主题或旁白稿，输出带旁白、素材、字幕和 BGM 的 MP4。

- **短视频**（约 30–60 秒）：Reels、TikTok、快手
- **中长视频**（约 3–15 分钟）：教程、演示、纪录片——LLM 分章故事板 + **剪辑规则引擎**（钩子、节奏、B-roll、转场）

---

## 与 MoneyPrinterTurbo 对比

[MoneyPrinterTurbo](https://github.com/Harry-Yu-001/MoneyPrinterTurbo)（约 8.6 万星）证明了「主题进、短视频出」的需求。ittybitty 做同一类事，但面向 **Agent、长片、自有片库和本地 GPU**——目前仍是 **Alpha**。

| | MoneyPrinterTurbo | ittybitty（Alpha） |
|--|-------------------|---------------------|
| **使用方式** | Web 界面 | **Windows 安装包** + Web + **HTTP MCP** |
| **时长** | 主要是短视频（约 60 秒） | 短视频 + **3–15 分钟分章**（规划器 + 剪辑规则） |
| **素材来源** | 图库 API | Pexels + **Jellyfin/Plex 家庭片库** + **LocalGen（Wan 2.2）** + Veo/Omni |
| **Agent 自动化** | — | **`videogen_*` MCP 工具**（Cursor、Claude、舰队客户端） |
| **片库与任务** | — | **SQLite 片库（Depot）**、任务历史、发布交接 |
| **剪辑智能** | 拼接式组装 | **钩子 / 节奏 / B-roll / 转场**；R1 卡拉 OK 字幕；R2 踩点与闪避；R3 审片（实验性） |
| **架构** | 单体 | **插件注册表** — 可换 LLM、素材、TTS 提供商 |
| **桌面端** | — | **NSIS 安装包**（Windows，捆绑后端） |
| **状态** | 成熟开源 | **Alpha** — 见 [清单](docs/ALPHA-RELEASE-CHECKLIST.md) |

---

## 中国 / 本地开源栈

可选：脚本、配音、AI 片段全部走本地或国内 API，不必绑死一家云。

| 工具 | 用途 | 配置 |
|------|------|------|
| **通义千问 3** | 脚本生成 | Ollama `qwen3:*` 或 DashScope；见 [CONFIGURATION.md](docs/CONFIGURATION.md) |
| **CosyVoice 2** | 中文 TTS / 克隆 | `VIDEOGEN_TTS_PROVIDER=cosyvoice`，`COSYVOICE_URL` |
| **LocalGen（Wan 2.2）** | 本地 AI 视频片段 | `VIDEOGEN_STOCK_PROVIDER=localgen`，`.\start-localgen.bat`（需 CUDA） |
| **Edge TTS** | 免费旁白（默认） | 无需密钥 |

---

## Windows 应用

1. 从 [Releases](https://github.com/sandraschi/ittybittyvideos/releases) 下载最新 **预发布** 安装包（`v0.2.0-alpha.*`）
2. 安装后从开始菜单启动 **ittybitty**
3. **设置** 里填入免费 [Pexels](https://www.pexels.com/api/) 密钥 → **生成**

安装目录：`%LOCALAPPDATA%\ittybitty\`

---

## 快速开始（开发）

```powershell
git clone https://github.com/sandraschi/ittybittyvideos.git videogen-mcp
cd videogen-mcp
copy .env.example .env
# 编辑 .env 填入密钥
.\start.bat
```

浏览器打开 **http://127.0.0.1:11055**。仅需后端时：`.\start.bat -BackendOnly`，API 文档 **http://127.0.0.1:11054/docs**。

### 通义千问（Ollama 本地）

```env
VIDEOGEN_LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:8b
```

### CosyVoice（本地 GPU）

```env
VIDEOGEN_TTS_PROVIDER=cosyvoice
COSYVOICE_URL=http://127.0.0.1:9880
```

---

## MCP 工具

| 工具 | 说明 |
|------|------|
| `videogen_generate` | 生成短视频 |
| `videogen_plan` | 中长视频故事板（不渲染） |
| `videogen_plan_render` | 规划并渲染中长视频 |
| `videogen_review` | 审片 / VLM 反馈（实验） |
| `videogen_status` | 任务进度 |
| `videogen_list_jobs` | 最近任务 |
| `videogen_providers` | 可用提供商 |

完整列表：[docs/TOOLS.md](docs/TOOLS.md)

---

## 剪辑规则引擎

不是简单拼接。规则包括：

- **钩子**：开头几秒抓注意力
- **节奏**：按类型调整镜头时长
- **B-roll**：主镜头之间自动插入
- **转场**：切 / 交叉淡化 / 黑场
- **再平衡**：总时长对齐目标

---

## 更多文档

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 英文主 README |
| [INSTALL.md](INSTALL.md) | 安装与 MCP 配置 |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | 环境变量 |
| [docs/LOCAL-VIDEO-GENERATORS.md](docs/LOCAL-VIDEO-GENERATORS.md) | 本地视频生成（Wan 等） |

---

MIT · [sandraschi](https://github.com/sandraschi) · v0.2.0

*仓库目录 `videogen-mcp`，Python 包名 `videogen_mcp` — 保留以兼容 MCP 工具名。*

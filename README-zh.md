# roughcut

你的电影学院辍学生，但是真的能交片。输入主题，输出视频。不需要学位。

> *"我们一个下午做完了这个。它比 MoneyPrinterTurbo（8.6万星，零测试）的测试还多。我们不一样。"*

## 它做什么

给它一个主题，它给你一个视频。带旁白、素材、字幕和背景音乐。高清。你去泡咖啡就行。

**短视频模式**（30-60秒）：抖音、TikTok、快手。常规操作。

**中长视频模式**（3-15分钟）🆕：教程、演示、纪录片、产品展示。
AI 生成分章节的故事板，专业剪辑规则引擎自动处理节奏、B-roll、转场和钩子。
这是别人做不好的部分。

## 对比

| MoneyPrinterTurbo（8.6万星） | roughcut |
|------------------------------|----------|
| 零测试 | 42个测试 |
| 单文件2000行LLM路由 | 插件注册表（7个提供商，每个一个文件） |
| 仅短视频（60秒上限） | **3-15分钟中长视频** |
| 无场景规划 | **分章故事板 + 剪辑规则引擎** |
| 内嵌微软字体（笑） | 系统字体 |
| g4f 逆向工程依赖 | 干净依赖 |

## 中国开源权重全栈

本地 GPU 运行。无需 API 密钥。无需云。无需许可。

| 工具 | 用途 | 配置 |
|------|------|------|
| **通义千问 3** | 脚本生成 | `VIDEOGEN_LLM_PROVIDER=qwen`（DashScope 或 Ollama） |
| **CosyVoice 2** | 中文 TTS + 语音克隆 | `VIDEOGEN_TTS_PROVIDER=cosyvoice` |
| **CogVideoX** | AI 视频片段生成 | `VIDEOGEN_STOCK_PROVIDER=cogvideo` |

## 快速开始

```bash
cp .env.example .env
# 填入 API 密钥

uv sync
uv run python -m videogen_mcp.server
# http://127.0.0.1:11054/docs
```

### 通义千问（本地 Ollama）

```bash
VIDEOGEN_LLM_PROVIDER=qwen
QWEN_MODEL=qwen3:8b
```

### CosyVoice（本地 GPU 推理）

```bash
VIDEOGEN_TTS_PROVIDER=cosyvoice
COSYVOICE_URL=http://localhost:9880
```

## 工具

| 工具 | 说明 |
|------|------|
| `videogen_generate` | 短视频生成（30-60秒） |
| `videogen_plan` | 中长视频故事板规划（不渲染） |
| `videogen_plan_render` | 规划并渲染中长视频 |
| `videogen_status` | 查询进度 |
| `videogen_list_jobs` | 最近任务 |
| `videogen_providers` | 可用提供商 |

## 剪辑规则引擎

不是拼接。专业剪辑模式，代码化：

- **钩子**: 前3秒抓住注意力
- **节奏**: 根据视频类型自动调整场景时长
- **B-roll**: 每3个连续主镜头后自动插入
- **转场**: 剪切/交叉淡入淡出/黑场按场景类型自动选择
- **再平衡**: 自动调整时长以匹配目标

## 许可证

MIT

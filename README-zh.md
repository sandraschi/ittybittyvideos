# videogen-mcp

AI 驱动的视频生成 MCP 服务器。输入主题，输出可发布的视频。

**端口**: 11054 (后端) | **版本**: 0.1.0

## 功能

```
主题/关键词 --> LLM 脚本 --> 素材获取 --> TTS 配音 --> 字幕 --> FFmpeg --> .mp4
```

### 短视频模式（30-60秒）
适合抖音、TikTok、快手等平台。

### 中长视频模式（3-15分钟）🆕
适合教程、演示、纪录片、产品展示。AI 生成分章节的故事板，
自动应用专业剪辑规则（节奏、B-roll、转场、钩子）。

## 对比 MoneyPrinterTurbo

| MoneyPrinterTurbo 缺陷 | videogen-mcp 改进 |
|------------------------|------------------|
| 无测试 | 30+ 测试覆盖 |
| 单文件17个LLM提供商 | 插件注册表（每个提供商一个文件） |
| 仅 TOML 配置 | 环境变量（12-factor） |
| 内嵌专有字体 | 系统字体 + 开源备选 |
| 仅短视频 | **支持3-15分钟中长视频** |
| 无 MCP 集成 | FastMCP 3.2（可被 Cursor/Claude 调用） |
| 无 AI 视频生成 | CogVideoX 插件（本地 GPU） |
| 仅 Edge TTS | CosyVoice 插件（语音克隆） |
| 无素材缓存 | 内容哈希去重缓存 |

## 中国开源权重工具支持

| 工具 | 用途 | 依赖 |
|------|------|------|
| **通义千问 3** (Qwen) | 脚本生成 | DashScope API 或本地 Ollama |
| **CosyVoice 2** | 中文 TTS + 语音克隆 | 本地 GPU 推理服务器 |
| **CogVideoX** | AI 视频片段生成 | 本地 GPU 或 ComfyUI |

无需 API 密钥，无需云依赖 — 有 GPU 即可本地运行。

## 快速开始

```bash
cp .env.example .env
# 编辑 .env 填入 API 密钥

# 使用 uv（推荐）
uv sync
uv run python -m videogen_mcp.server

# 或使用 just
just bootstrap
just dev
```

### 使用通义千问（本地 Ollama）

```bash
# .env
VIDEOGEN_LLM_PROVIDER=qwen
QWEN_MODEL=qwen3:8b

# 或使用 DashScope 云端
VIDEOGEN_LLM_PROVIDER=qwen
DASHSCOPE_API_KEY=sk-...
QWEN_MODEL=qwen-plus
```

### 使用 CosyVoice（本地推理）

```bash
# 启动 CosyVoice 服务器（需 GPU）
# https://github.com/FunAudioLLM/CosyVoice

# .env
VIDEOGEN_TTS_PROVIDER=cosyvoice
COSYVOICE_URL=http://localhost:9880
```

## MCP 工具

| 工具 | 说明 |
|------|------|
| `videogen_generate` | 从主题/脚本生成短视频 |
| `videogen_plan` | 规划中长视频故事板（不渲染） |
| `videogen_plan_render` | 规划并渲染中长视频 |
| `videogen_status` | 查询任务进度 |
| `videogen_list_jobs` | 列出最近的任务 |
| `videogen_providers` | 列出可用的提供商 |

## 专业剪辑规则引擎

videogen-mcp 内置专业视频剪辑规则：

- **钩子规则**: 前3秒抓住注意力
- **节奏控制**: 根据视频类型调整场景时长
- **B-roll 分配**: 每3个连续主镜头后插入过渡镜头
- **转场逻辑**: 根据场景类型自动选择剪切/交叉淡入淡出/黑场
- **时长再平衡**: 自动调整场景时长以匹配目标总时长

## 开发

```bash
just test      # 运行测试
just lint      # 代码检查
just typecheck # 类型检查
just check     # 全部检查
```

## 许可证

MIT

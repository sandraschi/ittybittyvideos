# videogen-mcp — MCP Server Capabilities

## Server Overview

videogen-mcp (product name: ittybitty) is an AI-powered short video generation MCP server that produces narrated short-form videos from text topics or custom scripts. It provides a complete video production pipeline including LLM-based script generation, stock footage discovery (Pexels, Jellyfin, Plex, LocalGen, Veo, Omni), TTS narration (Edge TTS, CosyVoice), subtitle rendering, and FFmpeg composition. The server also supports mid-length planned videos (3-15 minutes) with chapter-based storyboarding, visual look presets, intro/credits packs, and R10 narrative structure templates.

The server exposes ~55 tools organized into MCP tools for direct LLM integration and REST API endpoints for webapp and programmatic access. Key subsystems include a pipeline for short video generation (15-50 seconds), an extended pipeline for planned mid-length videos (3-15 minutes), a storyboard planner using LLM + videographer rules, a critic system for VLM-based video review, intro and credits pack management (contrast, gravitas, trailer, absurd-Pixar styles), visual look catalog with AI footage style/material/tone presets, a publishing pack builder with hashtags and platform URLs, depot management for finished videos, addon management for installable feature packs, and activity logging with ring-buffer storage.

## Tools (MCP)

### Pipeline Tools

**videogen_help:** Discovery tool listing all available tools, workflow hints, director pack overview, and server information. Call first when unsure which videogen_* tool to use.

**Return Format:** success bool, product string, version string, tools list, tool_count int, workflow_hints list, mcp_endpoint string

**videogen_generate:** Generate a short video (15-50 seconds) from a topic or custom script. Uses LLM for script generation when only topic is provided. Supports aspect ratio selection, voice selection, clip duration, paragraph count, visual style presets, intro/credits packs, narrative structure templates, and LLM provider selection.

**Parameters:** topic string, script string optional, aspect string (9:16, 16:9, 1:1), voice string, clip_duration float (2-30s), paragraph_count int (1-10), llm_provider string, structure string, style_notes string, intro string, visual_style string, visual_material string, visual_tone string

**Return Format:** success bool, job_id string, status string, message string

**videogen_status:** Poll a video generation job's progress by job_id. Returns job details including status, progress percentage, output path, and any error messages.

**Parameters:** job_id string (required)

**Return Format:** success bool, job dict with job_id, status, progress, output_path, topic, error

**videogen_list_jobs:** List recent video generation jobs with optional limit. Returns job summaries ordered by creation time.

**Parameters:** limit int (1-50, default 20)

**Return Format:** success bool, jobs list, count int

**videogen_plan:** Plan an intermediate-length video (3-15 minutes) storyboard with chapters, scenes, pacing, and B-roll suggestions. Uses LLM + videographer rules to produce a coherent multi-scene structure. Does NOT render — use videogen_plan_render to execute.

**Parameters:** topic string (required), video_type string (tutorial, demo, explainer, documentary, showcase), target_duration float (30-900s), language string, chapters int (1-12), style_notes string, structure string, intro string, visual_style string, visual_material string, visual_tone string

**Return Format:** success bool, storyboard dict with title, chapters, total_scenes, planned_duration, summary string

**videogen_plan_render:** Plan AND render an intermediate-length video (3-15 minutes) in one step. Full pipeline: LLM storyboard -> videographer rules -> scene-by-scene footage + TTS + subtitles -> FFmpeg compose -> MP4.

**Parameters:** All plan parameters plus aspect string (9:16, 16:9, 1:1) and voice string

**Return Format:** success bool, job_id string, status string, message string

**videogen_review:** Screening Room tool: have a local vision LLM (VLM) review a finished video. Samples frames evenly across the video and critiques footage coherence, subtitle collisions, and pacing. Requires an OpenAI-compatible VLM endpoint.

**Parameters:** job_id string (required), frames int (1-12, default 6)

**Return Format:** success bool, report dict with pass_number, model, scenes list

### Catalog Tools

**videogen_providers:** List all available LLM, stock footage, TTS, and talker providers configured for the server.

**Return Format:** success bool, providers dict with llm, stock, tts categories

**videogen_structures:** List R10 narrative structure presets — trope YAML templates that define video pacing and narrative flow. Each structure has a trope_id, label, supported video_types, exemplar_views, and beat_count.

**Return Format:** success bool, structures list, count int

**videogen_intros:** List intro sequence packs available for video generation. Each pack has an id, label, tone, and visual/audio description.

**Return Format:** success bool, packs list, count int

**videogen_credits:** List end-credits contributor packs for video generation. Includes absurd Pixar-style rolls, documentary style, and minimalist options.

**Return Format:** success bool, packs list, count int

**videogen_visual_look:** List AI footage look presets for generative stock (LocalGen, Veo, Omni). Returns the complete catalog of style, material, and tone presets plus supported AI stock providers.

**Return Format:** success bool, ai_stock_providers list, catalog dict with style, material, tone

**videogen_intro_sample:** Sample intro sequence guidance text for a specific intro pack. Returns the prompt block and tone metadata for the requested pack.

**Parameters:** pack string, seed int optional

**Return Format:** success bool, pack string, tone string, text string

**videogen_credits_sample:** Sample absurd end-credits contributor lines from a credits pack. Generates humorous Pixar-style joke roll text.

**Parameters:** pack string, lines int (5-80), post_credits bool, seed int optional

**Return Format:** success bool, pack string, text string, contributors list

### Depot Tools

**videogen_depot:** List finished videos persisted in the depot. Returns summary statistics and individual video metadata including file size, resolution, and duration.

**Parameters:** limit int (1-100, default 20)

**Return Format:** success bool, summary dict, items list, count int

**videogen_publish_pack:** Build publish helpers for a completed job. Generates platform-specific hashtags, descriptions, and URLs for sharing generated videos.

**Parameters:** job_id string (required)

**Return Format:** success bool, platforms list with generation metadata

### REST API Tools

The server exposes the complete MCP toolset as REST endpoints plus additional functionality:

**root:** Webapp root or API info page
**health:** Server health check with version, tool count, and MCP status
**cua_diagnostics:** CUA/NSIS smoke test diagnostics endpoint
**generate:** POST /api/v1/generate — Queue video generation
**list_jobs:** GET /api/v1/jobs — List all jobs
**get_job:** GET /api/v1/jobs/{job_id} — Get job details
**download:** GET /api/v1/jobs/{job_id}/download — Download job video
**depot:** GET /api/v1/depot — List depot videos
**depot_scan:** POST /api/v1/depot/scan — Scan output directory for new videos
**depot_delete:** DELETE /api/v1/depot/{job_id} — Remove video from depot
**depot_poster:** GET /api/v1/depot/{job_id}/poster — Get video poster image
**plan:** POST /api/v1/plan — Plan video storyboard
**visual_look_catalog:** GET /api/v1/visual-look/catalog — Get look presets
**structures:** GET /api/v1/structures — Get narrative structures
**credits_packs:** GET /api/v1/credits/packs — Get credits packs
**credits_sample:** GET /api/v1/credits/sample — Sample credits text
**intro_packs:** GET /api/v1/intros/packs — Get intro packs
**intro_sample:** GET /api/v1/intros/sample — Sample intro text
**plan_render:** POST /api/v1/plan/render — Plan and render video
**providers:** GET /api/v1/providers — List all providers
**status:** GET /api/v1/status — Server status with detailed metrics
**get_settings:** GET /api/v1/settings — Get configuration
**list_models:** GET /api/v1/settings/models — Discover LLM models
**stock_status:** GET /api/v1/settings/stock — Check stock footage connectivity
**save_settings:** PUT /api/v1/settings — Save settings to .env
**tools:** GET /api/v1/tools — List available tools
**publish_pack:** GET /api/v1/jobs/{job_id}/publish-pack — Build publish pack
**reveal_job:** POST /api/v1/jobs/{job_id}/reveal — Open file in Explorer
**list_addons:** GET /api/v1/addons — List available addons
**install_all_addons:** POST /api/v1/addons/install-all — Install all addons
**install_addon:** POST /api/v1/addons/{addon_id}/install — Install specific addon
**uninstall_addon:** DELETE /api/v1/addons/{addon_id} — Uninstall addon
**logs_query:** Query activity log entries
**logs_stats:** Get log statistics
**logs_export:** Export logs in JSON or CSV
**logs_clear:** Clear activity logs

## Configuration

### Environment Variables
- VIDEOGEN_PORT: Server port (default: 11054)
- VIDEOGEN_HOST: Server host (default: 127.0.0.1)
- VIDEOGEN_VLM_URL: Vision LLM URL for video review
- VIDEOGEN_VLM_MODEL: Vision LLM model name
- VIDEOGEN_VLM_KEY: API key for VLM
- VIDEOGEN_TAURI: Set to 1 when running under Tauri
- LLM provider variables for DeepSeek, OpenAI, LM Studio, Ollama
- Stock footage API keys for Pexels, etc.
- TTS provider configuration

### Storage
- Generated videos stored in output/ directory
- Depot database (SQLite) tracks all generated videos
- Settings persisted to .env file
- Activity logs stored in ring buffer

## Provider Registry

- LLM: deepseek, openai, lmstudio, ollama (+ custom script)
- Stock: pexels (default), jellyfin, plex, veo, omni, localgen
- TTS: edge-tts (default), cosyvoice optional

## Error Handling

All tools return structured responses with success bool. Errors include descriptive messages. Pipeline failures report job status as FAILED with error details. VLM critiques gracefully handle unreachable endpoints.

## Performance Characteristics

- Short video generation: 30-180 seconds depending on length and provider speed
- Planned video generation: 3-15 minutes for mid-length productions
- Storyboard planning: 10-30 seconds using LLM
- Video review: 20-60 seconds depending on frame count and VLM speed
- Health checks: less than 50ms
- Addon operations: 5-60 seconds per addon for download and installation
- Depot queries: less than 100ms
- Log queries: less than 50ms for typical page sizes

## Video Generation Pipeline Details

The short video generation pipeline processes jobs through several stages. First, if a topic is provided without a script, the LLM generates a script based on the topic, paragraph count, and style notes. The script is then split into segments matching the paragraph count. Each segment is used to search for stock footage from the configured stock providers, which may include Pexels, Jellyfin, Plex, or AI generation providers like LocalGen, Veo, and Omni. The selected footage is downloaded and prepared. TTS narration is generated for each script segment using the configured TTS provider, with Edge TTS as the default. Subtitles are rendered for each segment using the narration text. Finally, FFmpeg composes all elements into the final video with transitions between segments.

The extended pipeline for mid-length videos adds storyboard creation and chapter management. The LLM generates a chapter-based structure with scene descriptions, search terms, and timing. Each chapter is processed as a mini-pipeline: footage search, narration generation, subtitle rendering, and local composition. Chapters are assembled sequentially with chapter transitions and optional intro/credits sequences.

## Narrative Structure System (R10 Tropes)

The R10 trope system provides predefined narrative structures that guide video pacing and storytelling. Each trope includes a specific sequence of beats, typical video types it suits, and exemplar views that demonstrate the structure. Tropes include formats like pet-food-duo-review for product comparison videos, explainer structures for educational content, and documentary arcs for long-form storytelling. The videogen_structures tool lists all available tropes with their metadata. Structures are defined as YAML templates in the prompt_director service and can be extended through addon packs.

## Intro and Credits Pack System

Intro packs provide templated opening sequences for videos. Each pack has a distinct tone such as documentary-gravitas for serious content, bluey-horror-contrast for comedic contrast, trailer-hype for energetic openings, and minimal-fade for subtle professional starts. Packs include visual and audio direction, duration guidelines, and transition instructions. The videogen_intro_sample tool generates example text for any pack, demonstrating the tone and style.

Credits packs provide end-credits sequences with contributor role generation. The absurd-pixar pack generates humorous Pixar-style contributor rolls with creative roles like "Chief Joy Officer" and "Digital Wizard". The documentary-roll pack generates professional documentary-style credits. Packs support configurable line counts, post-credits stingers, and seeded random generation for reproducible results.

## Visual Look System

The visual look system provides AI footage generation presets organized into three dimensions. Style presets include cinematic, warm, technical, minimalist, vibrant, and noir options that control the overall visual aesthetic. Material presets include organic, glowing, metallic, liquid, crystal, and smoke that affect the texture and feel of generated footage. Tone presets include epic, cozy, dramatic, serene, mysterious, and playful that influence the mood. Presets are applied through the visual_style, visual_material, and visual_tone parameters on generate and plan tools. The videogen_visual_look tool returns the complete catalog with all available preset combinations.

## Publishing System

The publishing system generates platform-optimized content for sharing completed videos. The publish pack includes platform-specific hashtags derived from the video topic, content descriptions optimized for social media platforms, suggested titles and captions, and sharing links or instructions. Currently supported platforms include YouTube, TikTok, Instagram, and Twitter. The pack can be customized through addon packs for additional platforms. The videogen_publish_pack tool generates the complete pack for any completed job.

## Addon System

The addon system provides extensible feature packs that can be installed to enhance server capabilities. Addons include custom intro packs, additional narrative structures, visual look presets, credits templates, and platform publishers. Addons are discovered through the api_list_addons endpoint, installed individually or in batch, and can be uninstalled when no longer needed. The addon system uses a manifest-based approach where each addon declares its capabilities and dependencies. Installed addons are activated at server startup.

## Logging System

The activity logging system records all significant server events in a ring buffer. Each log entry includes a timestamp, severity level, event kind (system, pipeline, depot, addon), and descriptive message. The log system supports querying with level and kind filters, text search across messages, pagination with cursor-based positioning, and export in JSON or CSV formats. Logs are organized with a maximum of 10,000 entries, with oldest entries being automatically removed when the limit is exceeded.

## FFmpeg Integration

FFmpeg is the core composition engine for video generation. It handles media file concatenation, transition effects between segments, subtitle overlay with proper timing and styling, audio mixing of narration and background music, video scaling and aspect ratio conversion, and codec selection for output quality optimization. The server detects FFmpeg availability at startup and reports it in the status endpoint.

## Job Lifecycle

Each video generation job progresses through a defined lifecycle. When submitted, the job enters QUEUED status. Once the pipeline is available, it transitions to PROCESSING with a progress percentage. During processing, intermediate stages include script generation, footage search, narration synthesis, subtitle rendering, and FFmpeg composition. On successful completion, the job enters COMPLETE status with the output path set. On failure, the job enters FAILED status with an error message describing the failure reason. Jobs can be queried at any point using videogen_status.

## Configuration Store

The settings system persists configuration to a .env file for continuity across restarts. Settings include LLM provider selection and API endpoint URLs, TTS provider and voice configuration, stock footage provider preferences, visual style defaults, and server host and port configuration. The api_get_settings endpoint returns current configuration values. The api_save_settings endpoint accepts partial updates, merging with existing configuration.

## Depot System Architecture

The video depot provides persistent storage for completed videos with metadata tracking. Each depot entry includes the job ID, video title derived from the topic, output file path, file size, video duration, resolution, creation timestamp, and any tags or descriptions. The depot supports listing with pagination, deletion with optional file removal, scanning for new videos in the output directory, and poster image generation. The underlying storage uses SQLite for metadata and the filesystem for video files.

## Stock Footage Provider Architecture

The stock footage system supports multiple providers with a common interface. The Pexels provider searches the Pexels video API using topic keywords, returning free stock video URLs with metadata. The Jellyfin provider searches your local Jellyfin media library for matching content. The Plex provider searches your Plex media server. The LocalGen provider uses local AI generation (CogVideo) to create custom footage. The Veo provider connects to Google Veo for AI-generated video. The Omni provider connects to Google Omni for multimodal video generation. Providers are selected automatically based on availability and configuration.

## Video Quality Settings

The video pipeline supports configurable quality settings. Output resolution is determined by the aspect ratio: 9:16 produces 1080x1920, 16:9 produces 1920x1080, 1:1 produces 1080x1080. Video codec defaults to H.264 with configurable bitrate. Audio codec uses AAC at 192kbps. Subtitle rendering uses the system font with configurable size and position. Intro and credits sequences use their own style configurations independent of the main content. The FFmpeg composition engine applies smooth transitions between segments.

## Pipeline Error Handling

Each stage of the video generation pipeline has specific error handling. LLM script generation failures trigger automatic retry with fallback providers if configured. Stock footage search failures log a warning and substitute with available fallback footage. TTS synthesis failures attempt fallback voices before failing the segment. FFmpeg composition failures capture the FFmpeg error output for diagnostic purposes. Job status is updated at each stage so clients can track progress and identify failure points.

## Database Schema

The job store uses SQLite for persistent metadata storage. The jobs table tracks each video generation job with columns for job_id, topic, script, status, progress, output_path, error message, creation timestamp, completion timestamp, aspect ratio, duration, and provider configuration used at generation time. The depot table stores finished video metadata with columns for job_id reference, file path, file size, video duration, resolution, poster image path, and creation timestamp. The settings table stores configuration key-value pairs persisted across server restarts.

## Error Recovery Procedures

When a job fails during generation, the system provides detailed error information for diagnosis. LLM failures capture the HTTP response status and error message from the provider. Stock footage failures log which provider was used and the search query that failed. TTS failures include the voice identifier and synthesis duration attempted. FFmpeg failures include the complete FFmpeg command and error output. The server does not automatically retry failed jobs; users should review the error, fix the underlying issue, and resubmit the generation.

## Credits Pack System

The credits system generates end-credits sequences with contributor role names. Each credits pack defines a theme for generating creative or professional role titles. The absurd-pixar pack generates humorous Pixar-style credits with creative roles like Chief Innovation Officer and Digital Artisan, silly department names like Department of Imaginary Solutions, and post-credits stinger hints. The documentary-roll pack generates professional credits suitable for serious content. The minimalist pack generates simple, clean credits for professional use. Credits are generated with configurable lengths and optional post-credits scenes.

## Web Application Integration

The server includes a built-in web application served at the root URL when the webapp dist directory is available. The SPA fallback route handles client-side routing for single-page application navigation. Static assets are served from the assets directory. When the webapp is not built, the root endpoint returns a minimal status page with links to the API documentation. The webapp communicates with the backend through the REST API endpoints for all operations.

## CORS Configuration

The server configures CORS middleware to allow cross-origin requests from known origins. Allowed origins include the frontend development server on ports 11054 and 11055, plus Tauri desktop origins (tauri://localhost, http://tauri.localhost, https://tauri.localhost). When running under Tauri detection via VIDEOGEN_TAURI environment variable, additional CORS rules are enabled for Tauri-specific origins. Credentials are supported for authenticated requests.

## REST API Design

The REST API follows consistent design patterns. All endpoints under /api/v1/ return JSON responses with a success boolean. List endpoints support limit parameter for pagination. Job-related endpoints use the job_id as a path parameter. Settings endpoints use PUT for updates and GET for retrieval. Addon endpoints use POST for installation and DELETE for uninstallation. Log endpoints mirror the MCP log tool interface. Error responses include descriptive messages and appropriate HTTP status codes.

## Output Directory Structure

Generated videos are stored in a structured directory hierarchy. The root output directory is configured through settings and defaults to ./output relative to the server root. Each job creates a subdirectory named after the job_id. Within each job directory, the final video is saved as output.mp4, intermediate files are stored in a temp/ subdirectory that is cleaned up after completion, and poster images are saved as poster.jpg when generated. The depot system references files by their job_id for consistent access.

## Provider Health Monitoring

The server monitors provider health through the api_status endpoint. Each provider category reports its availability status. LLM providers are probed for API reachability and model availability. Stock footage providers are checked for API key validity and connection status. TTS providers verify their synthesis endpoint is responsive. The status endpoint aggregates all provider health information into a single response for easy monitoring.

## Intro Pack Templates

Each intro pack defines a complete opening sequence template. The template includes the tone label describing the emotional impact, visual direction for footage selection and composition, audio direction for background music and sound design, duration guidelines for timing the sequence, transition instructions for the cut to main content, and sample text demonstrating the narrative style. Packs can be combined with narrative structures and visual looks for a cohesive video style.

## Addon Installation Process

Addon installation follows a defined process. The server queries the addon registry for available packs, downloads the selected addon manifest, validates compatibility with the current server version, extracts addon files to the addons directory, and activates the addon for immediate use. Installed addons persist across server restarts. The api_list_addons endpoint shows which addons are installed versus available for installation. Addons can be installed individually or in batch with install_all.

## TTS Provider Architecture

The text-to-speech system supports multiple synthesis engines. Edge TTS provides high-quality neural voices through Microsoft's cloud service with support for multiple languages and voice styles. CosyVoice provides offline TTS using local models for environments without internet access. Each provider supports configurable voice selection, speech rate, and pitch adjustments. The videogen_providers tool lists available TTS providers and their voice options.

## Model Discovery System

The model discovery system probes configured LLM providers to list available models. It supports Ollama via the /api/tags endpoint, LM Studio via the /v1/models endpoint, and OpenAI-compatible providers via their /v1/models endpoint. Discovery results include model IDs, provider information, and availability status. The api_list_models endpoint returns discovery results for all configured providers or a specific provider. This enables runtime model selection without requiring pre-configured model names.

# videogen-mcp (ittybitty) — User Guide

## Quick Start

videogen-mcp (product name: ittybitty) generates AI-powered short videos from text topics. To get started:

1. Ensure required dependencies are installed (ffmpeg, edge-tts)
2. Start the server (default port 11054, frontend 11055)
3. Check available providers: videogen_providers()
4. Generate your first video: videogen_generate(topic="Why cats are amazing")
5. Check progress: videogen_status(job_id="your-job-id")

**First commands:**
```
videogen_help()
videogen_providers()
videogen_generate(topic="The wonders of the universe", paragraph_count=3)
videogen_list_jobs()
```

## Tutorials

### Tutorial 1: Generate Your First Short Video

Create a short narrated video from a topic.

**Steps:**
1. Check available providers:
   `videogen_providers()`

2. Generate a short video:
   `videogen_generate(topic="Why the ocean is important", paragraph_count=3, aspect="9:16")`

3. Check progress:
   `videogen_status(job_id="your-job-id")`

4. List all jobs:
   `videogen_list_jobs(limit=5)`

5. Find completed video in depot:
   `videogen_depot()`

**Expected outcome:** A 15-50 second narrated short video with stock footage.

### Tutorial 2: Custom Script Video

Create a video from your own script text.

**Steps:**
1. Write a script and generate:
   `videogen_generate(script="The year 2026 marks a turning point in artificial intelligence. Deep learning models have reached new capabilities...", aspect="16:9", clip_duration=6.0)`

2. Monitor the job:
   `videogen_status(job_id="your-job-id")`

3. View the result:
   `videogen_depot(limit=5)`

**Expected outcome:** Video using your exact script text with matching stock footage.

### Tutorial 3: Using Visual Style Presets

Apply different visual styles to your video.

**Steps:**
1. Browse visual looks:
   `videogen_visual_look()`

2. Generate with a specific style:
   `videogen_generate(topic="Space exploration", visual_style="cinematic", visual_material="glowing", visual_tone="epic")`

3. Try a different aesthetic:
   `videogen_generate(topic="Cooking pasta", visual_style="warm", visual_material="organic", visual_tone="cozy")`

**Expected outcome:** Videos with distinctly different visual aesthetics.

### Tutorial 4: Adding Intros and Credits

Enhance videos with professional intro sequences and end credits.

**Steps:**
1. Browse available intro packs:
   `videogen_intros()`

2. Sample an intro:
   `videogen_intro_sample(pack="documentary-gravitas")`

3. Browse credits packs:
   `videogen_credits()`

4. Sample credits:
   `videogen_credits_sample(pack="absurd-pixar", lines=20)`

5. Generate with intro and credits:
   `videogen_generate(topic="The future of renewable energy", intro="documentary-gravitas", paragraph_count=4)`

**Expected outcome:** Professional video with branded intro and creative end credits.

### Tutorial 5: Using Narrative Structures

Apply R10 trope presets for different video pacing and narrative flow.

**Steps:**
1. List available structures:
   `videogen_structures()`

2. Choose a structure and generate:
   `videogen_generate(topic="Product review", structure="trope:pet-food-duo-review", paragraph_count=5)`

**Expected outcome:** Video with industry-standard narrative structure and pacing.

### Tutorial 6: Planning a Mid-Length Video

Create a storyboard for a 3-15 minute planned video.

**Steps:**
1. Plan the video structure:
   `videogen_plan(topic="Introduction to Python programming", video_type="tutorial", target_duration=300, chapters=4)`

2. Review the storyboard output with chapter breakdown
3. Render the planned video:
   `videogen_plan_render(topic="Introduction to Python programming", target_duration=300, chapters=4, aspect="16:9")`

4. Monitor progress:
   `videogen_status(job_id="your-plan-job-id")`

**Expected outcome:** Structured multi-chapter video with coherent narrative flow.

### Tutorial 7: Reviewing and Critiquing Videos

Use the Screening Room to get AI feedback on generated videos.

**Steps:**
1. Generate a video:
   `videogen_generate(topic="Machine learning basics")`

2. Wait for completion
3. Review the video:
   `videogen_review(job_id="completed-job-id", frames=6)`

4. Read the critique report including footage coherence and pacing analysis

**Expected outcome:** Detailed AI critique of your video with frame-by-frame analysis.

### Tutorial 8: Managing the Video Depot

Organize and manage your generated video library.

**Steps:**
1. View all depot videos:
   `videogen_depot(limit=50)`

2. Get publish helpers for a video:
   `videogen_publish_pack(job_id="completed-job-id")`

3. Reveal video in file explorer (Windows):
   `api_reveal_job(job_id="completed-job-id")`

**Expected outcome:** Organized video library with platform-ready publishing assets.

### Tutorial 9: Exploring and Configuring Providers

Manage video generation providers and settings.

**Steps:**
1. List all providers:
   `videogen_providers()`

2. Get current settings:
   `api_get_settings()`

3. Check stock footage status:
   `api_stock_status()`

4. Discover LLM models:
   `api_list_models(provider="ollama")`

**Expected outcome:** Full visibility into provider configuration.

### Tutorial 10: Managing Addons

Install and manage feature packs for extended video capabilities.

**Steps:**
1. List available addons:
   `api_list_addons()`

2. Install a specific addon:
   `api_install_addon(addon_id="custom-intro-pack")`

3. Install all addons:
   `api_install_all_addons()`

4. Uninstall if needed:
   `api_uninstall_addon(addon_id="custom-intro-pack")`

**Expected outcome:** Extended server capabilities through installed addon packs.

### Tutorial 11: Server Monitoring and Logs

Monitor server activity and troubleshoot issues.

**Steps:**
1. Check server status:
   `api_status()`

2. Query activity logs:
   `logs_query(limit=20)`

3. Filter logs:
   `logs_query(level="ERROR", kind="pipeline")`

4. Export logs:
   `logs_export(format="json")`

5. Clear logs:
   `logs_clear()`

**Expected outcome:** Complete server observability.

### Tutorial 12: Full Production Pipeline

End-to-end video production workflow.

**Steps:**
1. Plan: `videogen_plan(topic="Vienna coffee culture", video_type="documentary", target_duration=600, language="en", chapters=6)`
2. Generate: `videogen_plan_render(topic="Vienna coffee culture", target_duration=600, chapters=6, aspect="9:16", intro="documentary-gravitas")`
3. Monitor: `videogen_status(job_id="plan-job-id")`
4. Review: `videogen_review(job_id="completed-job-id")`
5. Publish: `videogen_publish_pack(job_id="completed-job-id")`
6. Depot: `videogen_depot()`

**Expected outcome:** Complete video production cycle from planning to publishing.

## API Reference

### REST Endpoints

- GET /: Root API info or webapp
- GET /health: Health check
- GET /api/v1/diagnostics: CUA diagnostics
- POST /api/v1/generate: Queue video generation
- GET /api/v1/jobs: List jobs
- GET /api/v1/jobs/{id}: Get job details
- GET /api/v1/jobs/{id}/download: Download video
- GET /api/v1/jobs/{id}/publish-pack: Build publish pack
- POST /api/v1/jobs/{id}/reveal: Reveal in Explorer
- GET /api/v1/depot: List depot
- POST /api/v1/depot/scan: Scan for new videos
- DELETE /api/v1/depot/{id}: Delete from depot
- GET /api/v1/depot/{id}/poster: Get poster image
- POST /api/v1/plan: Plan storyboard
- POST /api/v1/plan/render: Plan and render
- GET /api/v1/providers: List providers
- GET /api/v1/status: Server status
- GET /api/v1/settings: Get settings
- PUT /api/v1/settings: Save settings
- GET /api/v1/settings/models: Discover models
- GET /api/v1/settings/stock: Stock status
- GET /api/v1/tools: List MCP tools
- GET /api/v1/visual-look/catalog: Look catalog
- GET /api/v1/structures: Narrative structures
- GET /api/v1/credits/packs: Credits packs
- GET /api/v1/credits/sample: Sample credits
- GET /api/v1/intros/packs: Intro packs
- GET /api/v1/intros/sample: Sample intro
- GET /api/v1/addons: List addons
- POST /api/v1/addons/install-all: Install all
- POST /api/v1/addons/{id}/install: Install addon
- DELETE /api/v1/addons/{id}: Uninstall addon

## Troubleshooting

**Problem: Video generation fails**
Check provider connectivity with videogen_providers(). Verify ffmpeg is installed.

**Problem: TTS not working**
Edge TTS requires internet. For offline use, configure CosyVoice.

**Problem: Stock footage not found**
Check pexels API key. Try different topics. Check Jellyfin/Plex connectivity.

**Problem: VLM review not available**
Set VIDEOGEN_VLM_URL. Requires Ollama with a vision model or an OpenAI-compatible VLM.

**Problem: Server won't start**
Check port availability. Clear any processes on port 11054.

## FAQ

## Job Monitoring Best Practices

When running multiple video generation jobs, use videogen_list_jobs to see all active and completed jobs. Check job status periodically using videogen_status with the job_id. Jobs typically progress from QUEUED to PROCESSING to COMPLETE or FAILED. The progress field indicates completion percentage during processing. Failed jobs include an error field describing the failure reason. Common failures include LLM provider unreachable, stock footage search returning no results, TTS synthesis failure, or FFmpeg composition error.

For long-running planned videos, check status every 60-120 seconds. For short videos, a single check after 60 seconds is usually sufficient. The depot maintains a history of completed jobs for reference even after the server restarts.

## Aspect Ratio Selection Guide

Choose aspect ratios based on your target platform. Use 9:16 (vertical) for TikTok, Instagram Reels, and YouTube Shorts optimized for mobile viewing. Use 16:9 (landscape) for YouTube, Vimeo, and traditional video platforms suitable for desktop and TV viewing. Use 1:1 (square) for Instagram Feed and Facebook where square format performs well. The aspect ratio affects how footage is cropped and composed, so choose before generating.

## Script Writing Tips

For best results with custom scripts, follow these guidelines. Write scripts in clear, declarative sentences that are easy to narrate. Keep paragraphs concise, around 2-4 sentences each, matching the paragraph_count parameter. Include visual cues in parentheses like (show close-up of engine) or (cut to aerial view) to guide footage selection. Use natural language that sounds good when spoken aloud. Avoid complex formatting, special characters, or markdown in scripts. Target a reading speed of about 150 words per minute for comfortable narration pacing.

## Visual Style Combinations

Experiment with different visual style combinations for varied results. For dramatic technology content, combine cinematic style with glowing material and epic tone. For cooking and food content, use warm style with organic material and cozy tone. For educational content, try technical style with clean material and neutral tone. For travel content, use vibrant style with natural material and serene tone. For product showcases, combine minimalist style with metallic material and dramatic tone.

## Output File Management

Generated videos are stored in the output directory with filenames based on job IDs. The depot tracks all files for easy retrieval. Use api_reveal_job on Windows to open the file location in Explorer. Use api_download to download videos via HTTP. The api_depot_poster endpoint provides JPEG thumbnail images for visual browsing. Videos are encoded in H.264 MP4 format for broad compatibility. File sizes vary from 5-50MB for short videos to 50-500MB for planned mid-length productions.

## AI Footage Generation Tips

When using AI stock footage providers like LocalGen, Veo, or Omni, prompt quality directly impacts output quality. Write descriptive scene prompts that include the subject, action, setting, lighting, and camera movement. For example, instead of "a cat" use "a fluffy orange cat walking through a sunlit garden, close-up shot, warm golden hour lighting". AI footage generation takes longer than stock footage retrieval, so plan for longer generation times. The visual style, material, and tone presets are applied as prefixes to your search terms to guide the AI generation.

## Publishing Platform Strategy

The publish pack generates platform-specific content strategies. For YouTube, use longer descriptions with keyword-rich tags and timestamps. For TikTok, focus on trending hashtags and short, engaging descriptions. For Instagram, use visual descriptions and relevant community hashtags. For Twitter, emphasize concise hooks and thread-style descriptions. The publish pack can be regenerated with different focus by re-running videogen_publish_pack.

## Debugging Failed Jobs

When a job fails, use videogen_status to examine the error field. Common failure patterns include LLM timeout where the script generation LLM took too long to respond, stock footage failure where no matching footage was found for the given topic, TTS error where the voice synthesis endpoint was unreachable, and FFmpeg error where the video composition command failed. For LLM issues, verify provider connectivity with videogen_providers. For stock issues, try different topics or check stock provider API keys. For TTS issues, verify internet connectivity for Edge TTS or switch to CosyVoice. For FFmpeg issues, verify FFmpeg is installed and the output path is writable.

## Output Quality Factors

Several factors influence the quality of generated videos. LLM script quality directly affects narrative coherence and audience engagement; use well-structured topics or custom scripts for best results. Stock footage relevance depends on how well search terms match the script content; use specific keywords and topics. TTS voice quality varies by provider; Edge TTS provides the most natural voices. Visual style presets affect the aesthetic consistency of AI-generated footage. Video resolution and bitrate affect file size and playback quality across platforms.

## Cost Considerations

Different providers have different cost implications. Local providers like Ollama and LocalGen are free but require GPU hardware. Cloud providers like DeepSeek and OpenAI charge per token for script generation. Stock footage from Pexels is free with API key registration. AI footage from Veo and Omni may have usage costs. TTS from Edge TTS is free. CosyVoice is free but requires local model downloads. Plan provider selection based on your budget and infrastructure. The videogen_providers tool provides availability status for each provider.

## Server Configuration Guide

Configure the server for your specific needs through environment variables and settings. Set VIDEOGEN_PORT and VIDEOGEN_HOST for network configuration. Configure LLM provider settings like DEEPSEEK_API_KEY or OLLAMA_URL based on your preferred provider. Set stock footage API keys for commercial providers. Configure TTS provider preferences. Use api_save_settings to persist configuration changes to the .env file. Settings take effect immediately for LLM provider changes and after restart for server-level configuration.

## Multi-Language Video Production

The server supports multi-language video production through configurable language parameters. Set the language parameter on videogen_plan and videogen_plan_render to the desired language code. The LLM generates scripts in the specified language when creating storyboards. TTS voices should be selected to match the target language. Edge TTS provides multi-language voice support. Stock footage search terms are translated for language-appropriate results.

## Tutorial 16: Video Series Production

Create a multi-episode video series with consistent branding and style.

**Steps:**
1. Plan the first episode: videogen_plan(topic="Introduction to our series", video_type="tutorial", target_duration=300, chapters=4)
2. Note the visual style and structure used
3. Generate the first episode: videogen_plan_render(topic="Introduction to our series", target_duration=300, chapters=4)
4. Create subsequent episodes with identical settings for consistency
5. For each episode, generate a publish pack: videogen_publish_pack(job_id="episode-1")
6. Use consistent hashtags across all publish packs for series discoverability
7. Track all episodes in the depot for series management

## Cloud Provider Configuration

When using cloud AI providers, configure API keys appropriately. Set DEEPSEEK_API_KEY for DeepSeek LLM access, OPENAI_API_KEY for OpenAI access, and PEXELS_API_KEY for Pexels stock footage. API keys are read from environment variables at server startup. Use api_save_settings to update provider configuration without restarting the server for supported settings. Cloud providers typically offer higher quality output than local alternatives but may incur usage costs and require internet connectivity.

## Tutorial 17: Cross-Platform Video Publishing

Publish generated videos across multiple platforms using the publishing pack system.

**Steps:**
1. Generate a video: videogen_generate(topic="Quick tips for productivity")
2. After completion, get the publish pack: videogen_publish_pack(job_id="completed-job")
3. Review platform-specific hashtags and descriptions from the publish pack
4. For YouTube, use the description and tags from the pack
5. For TikTok, use the short-form optimized description
6. For Instagram, adapt the square-format description if applicable
7. Cross-reference hashtags across platforms for consistent branding

## Provider Selection Strategy

Choose providers based on your specific use case and infrastructure. For offline video generation when internet is unavailable, use local providers: Ollama or LM Studio for LLM, LocalGen for stock footage, CosyVoice for TTS. For highest quality output with internet, use cloud providers: DeepSeek or OpenAI for script generation, Pexels for stock footage, Edge TTS for narration. For unique AI-generated visuals, use Veo or Omni for footage. Mix and match providers per video based on quality requirements and budget constraints.

## Tutorial 18: Content Strategy Planning

Plan a content strategy using videogen-mcp for consistent video output.

**Steps:**
1. Define your content categories and target platforms
2. For each category, select appropriate visual styles and aspect ratios
3. Create a content calendar with topics for each production day
4. Batch-generate videos for each content category
5. Use consistent structure and intro packs across related videos
6. Generate publish packs with platform-specific optimizations
7. Track published videos in the depot for content library management

## Understanding Job Status Values

Video generation jobs progress through several status values. QUEUED means the job is waiting for the pipeline to become available. PROCESSING means the job is actively being generated with a progress percentage. COMPLETE means the video is ready and available in the depot. FAILED means an error occurred during generation with details in the error field. Most jobs spend the majority of their time in PROCESSING status. The progress field provides a rough percentage estimate of completion.

## Tutorial 19: Visual Brand Consistency

Maintain visual brand consistency across all generated videos.

**Steps:**
1. Define your brand's visual style (cinematic, warm, technical, etc.)
2. Choose consistent material and tone presets for all content
3. Select an intro pack that matches your brand personality
4. Use the same visual_style, visual_material, and visual_tone parameters on all generations
5. Choose a consistent voice for all narrations
6. Apply the same aspect ratio across your content library
7. Use the same credits pack for all videos for brand recognition

## Tutorial 20: Performance Optimization

Optimize video generation performance for faster turnaround times.

**Steps:**
1. Use shorter videos with fewer paragraphs for faster generation
2. Choose Pexels stock footage over AI generation for speed
3. Use Edge TTS for fastest narration synthesis
4. Keep clip_duration at 4-5 seconds for efficient editing
5. Avoid visual style presets when speed is critical
6. Monitor generation times with videogen_list_jobs and logs
7. Identify bottlenecks by comparing generation times across different configurations

## TTS Voice Selection Guide

Choose TTS voices that match your content tone and audience. Edge TTS offers a range of neural voices including natural-sounding options like Jenny, Guy, and Aria for English. For professional content, use calm, clear voices like Jenny or Guy. For creative content, try expressive voices with more variation. For non-English content, select language-specific voices provided by Edge TTS. Test different voices with videogen_generate to find the best match for your content style. The voice parameter accepts provider-specific voice identifiers.

## Managing Generation Queue

The server processes video generation jobs sequentially in the pipeline. When multiple jobs are submitted, they queue and run one at a time. Monitor queue status with videogen_list_jobs which shows all jobs ordered by creation time. Use videogen_status to track the currently processing job. Plan batch operations knowing that each job will run sequentially. For urgent videos, wait for the current job to complete before submitting new ones.

## Stock Footage Selection Tips

Choose the right stock footage provider for your content type. Pexels offers the broadest selection of general-purpose stock video with instant downloads. Jellyfin and Plex provide your personal media library as footage, perfect for branded content. LocalGen generates AI footage from text prompts, ideal when no existing footage matches your topic. Veo and Omni provide Google's AI-generated video for unique visual needs. For most content, start with Pexels for speed and fall back to AI generation for specific needs that stock cannot cover.

## Video Resolution and Quality Settings

The server generates videos at standard resolutions based on aspect ratio. 9:16 vertical videos output at 1080x1920 pixels. 16:9 landscape videos output at 1920x1080 pixels. 1:1 square videos output at 1080x1080 pixels. All videos use H.264 encoding with a target bitrate optimized for the resolution. For higher quality output, configure the bitrate through settings. For faster generation with smaller file sizes, reduce resolution expectations.

## Provider Performance Comparison

Different providers have different performance characteristics. For LLM script generation, Ollama with small models (1-3B parameters) is fastest, DeepSeek provides the best quality-speed balance, OpenAI is reliable but slower. For stock footage, Pexels provides instant results, Jellyfin/Plex depend on local media availability, AI providers take 30-120 seconds per clip. For TTS, Edge TTS completes in 5-15 seconds per segment, CosyVoice takes 10-30 seconds. Choose providers based on your quality requirements and speed needs.

## Understanding the Complete Video Pipeline

The video generation pipeline processes jobs through multiple stages. Stage one is script generation where the LLM creates a narrative script from the topic. Stage two is footage search where each script segment is used to find matching stock or AI-generated footage. Stage three is narration synthesis where TTS converts the script into spoken audio. Stage four is subtitle rendering where spoken text is synchronized with video timing. Stage five is composition where FFmpeg combines footage, narration, subtitles, intro, and credits into the final video. Each stage reports its progress for job status tracking.

## Troubleshooting Provider Connectivity

When providers are unreachable, the server reports their status through videogen_providers and api_status. For LLM providers, verify the endpoint URL is correct and the provider is running. For Ollama, check that the service is running and the model is loaded. For stock footage providers, verify API keys are correctly configured. For TTS providers, check internet connectivity for cloud services or local installation for offline services. The status endpoint provides per-provider connectivity details for diagnostics.

## Frequently Encountered Error Messages

"If no LLM provider configured" means no LLM provider is set up for script generation. Configure a provider through settings or pass a custom script directly to videogen_generate. "Provider not responding" means the configured LLM endpoint is unreachable. Check that the provider is running and the URL is correct. "No stock footage found" means the search terms did not match any available footage. Try different topics or check stock provider API keys. "FFmpeg not found" means FFmpeg is not installed or not in PATH. Install FFmpeg and ensure it is accessible from the command line.

## Activity Log Analysis

Use the activity logging system to monitor server operations and diagnose issues. Query logs with kind=pipeline to track video generation progress. Filter by level=ERROR to identify failed jobs and their causes. Search for specific job_ids to trace a job's complete lifecycle. Export logs periodically for long-term analysis and performance tracking. Log entries include timestamps with millisecond precision for accurate timing analysis.

## Performance Benchmarking

For benchmarking and optimization, use the server's monitoring tools. Track generation times for different video lengths and types. Compare performance across different LLM providers for script generation. Measure stock footage search times for different topic categories. Test TTS synthesis speed with different voice configurations. Use the activity log system to track operation timing. Identify bottlenecks and optimize provider selection based on benchmark results.

## Resource Requirements

Video generation requires significant system resources. Short video generation needs at least 4GB of RAM for the pipeline. Planned video generation benefits from 8GB or more due to the extended processing. AI footage generation requires a GPU with at least 8GB VRAM for LocalGen. FFmpeg composition is CPU-intensive and benefits from multi-core processors. Disk space requirements vary from 100MB per short video to 1GB per planned production. The output directory should have at least 10GB free for active generation work.

## Workflow Automation Patterns

For automated video production pipelines, combine the MCP tools with external scheduling. Generate batches of videos on related topics sequentially using the videogen_generate tool. Use videogen_list_jobs to check completion status of batch operations. Export publish packs for all completed videos. Use the depot system to track which videos have been published. The REST API endpoints enable integration with CI/CD pipelines and external automation tools.

## Environmental Setup

For optimal video generation, ensure the following dependencies are available. FFmpeg must be installed and accessible in the system PATH for video composition. Python dependencies are managed through uv sync. Edge TTS requires internet connectivity for cloud-based voice synthesis. For offline operation, configure CosyVoice or another local TTS provider. Stock footage providers require appropriate API keys for commercial services.

## Tutorial 13: Depot Management and Archival

Maintain an organized video depot with proper metadata and backup practices.

**Steps:**
1. View current depot contents: videogen_depot(limit=100)
2. Scan for any new videos in output directory: api_depot_scan()
3. Generate publish packs for videos ready to share: videogen_publish_pack(job_id="job-001")
4. Delete low-quality or test videos: api_depot_delete(job_id="test-job-001")
5. Get poster images for visual identification: api_depot_poster(job_id="job-001")

## Tutorial 14: Batch Video Production

Create multiple videos efficiently using batch planning and generation.

**Steps:**
1. Plan several videos on related topics: videogen_plan(topic="Python basics", video_type="tutorial", target_duration=300), videogen_plan(topic="Python data structures", video_type="tutorial", target_duration=300)
2. Generate them in sequence: videogen_plan_render(topic="Python basics", ...), then videogen_plan_render(topic="Python data structures", ...)
3. Monitor all jobs: videogen_list_jobs()
4. Review completed videos: videogen_depot()
5. Generate publish packs for the series: videogen_publish_pack(job_id="first"), videogen_publish_pack(job_id="second")

## Tutorial 15: Custom Intro Creation Workflow

Design and test custom intro sequences for branding.

**Steps:**
1. Browse available intro packs: videogen_intros()
2. Sample different intros: videogen_intro_sample(pack="documentary-gravitas"), videogen_intro_sample(pack="trailer-hype")
3. Choose the best fit for your content style
4. Apply intro in generation: videogen_generate(topic="Brand story", intro="documentary-gravitas")

## Provider Selection Guide

Choosing the right providers impacts video quality and generation speed. For LLM script generation, use cloud providers like DeepSeek or OpenAI for highest quality, or Ollama with local models for offline operation. For stock footage, Pexels provides the largest library of free stock video, Jellyfin and Plex use your personal media library, and AI providers like LocalGen, Veo, and Omni generate unique AI footage. For TTS, Edge TTS provides natural-sounding voices but requires internet, while CosyVoice provides offline TTS.

For optimal results, use deepseek for script generation as it provides excellent creative writing, pexels as the stock footage fallback for broad topic coverage, and edge-tts for high-quality narration. Configure AI stock providers only when you need unique generated footage that cannot be found in stock libraries.

## Visual Style Quick Reference

The cinematic style creates dramatic, movie-like visuals with rich colors and depth of field. The warm style uses golden tones and soft lighting suitable for lifestyle and cooking content. The technical style produces clean, precise visuals for tutorials and demonstrations. The minimalist style uses simple compositions with plenty of negative space. The vibrant style features bold colors and high contrast for engaging social media content. The noir style creates moody, high-contrast black-and-white aesthetics.

Material presets modify the texture of generated content. Organic materials create natural, earth-toned textures. Glowing materials add luminous effects for technology and sci-fi themes. Metallic materials produce reflective, industrial aesthetics. Liquid materials create fluid, flowing visuals. Crystal materials generate geometric, translucent effects. Smoke materials create atmospheric, ethereal content.

## Common Workflow Patterns

Pattern A for quick social media content: use videogen_generate with a topic, 9:16 aspect ratio, 3 paragraphs, and default providers. This produces a 15-30 second vertical video optimized for TikTok or Instagram Reels.

Pattern B for YouTube content: use videogen_plan_render with 16:9 aspect ratio, 5-8 chapters, and 300-600 second duration. Add intro and credits packs for professional polish.

Pattern C for educational series: use videogen_plan with tutorial video type and structured chapters, then videogen_plan_render for each episode. Export publish packs with consistent hashtags for series discoverability.

Pattern D for product demos: use videogen_generate with custom script for precise messaging, 16:9 aspect, and cinematic visual style. Add visual_material="glowing" for tech products or visual_tone="cozy" for lifestyle products.

## Troubleshooting Guide

If video generation fails, first check provider connectivity with videogen_providers(). Ensure ffmpeg is installed and accessible in the system PATH. Check that the output directory has sufficient disk space. Verify that the configured LLM provider is running and responding. For TTS issues, Edge TTS requires internet access; switch to CosyVoice for offline operation. For stock footage issues, verify Pexels API key if configured, or switch to Jellyfin/Plex for local media. For VLM review issues, ensure VIDEOGEN_VLM_URL points to a running vision LLM endpoint. For server startup issues, check that VIDEOGEN_PORT (default 11054) is not in use by another process.

## FAQ

**Q: What video lengths are supported?**
A: Short: 15-50 seconds. Planned: 3-15 minutes. Custom scripts can vary.

**Q: What aspect ratios are available?**
A: 9:16 (vertical/TikTok), 16:9 (landscape/YouTube), 1:1 (square/Instagram).

**Q: Do I need an internet connection?**
A: For stock footage and cloud LLMs, yes. LocalGen and Ollama work offline.

**Q: Can I use my own footage?**
A: Yes. Jellyfin and Plex providers use your media library as stock footage.

**Q: What languages are supported?**
A: English, German, Chinese, Japanese, and more depending on TTS provider.

**Q: How are videos stored?**
A: In the output/ directory and tracked in a SQLite database.

**Q: Can I customize the intro?**
A: Yes. Intro packs can be selected, sampled, and even custom-built via addons.

**Q: How many videos can I generate simultaneously?**
A: Jobs are processed sequentially per pipeline. Multiple jobs queue and run one at a time.

**Q: Can I use my own music as background audio?**
A: Currently the pipeline uses TTS narration only. Background music support can be added via addons.

**Q: Can I use the server offline?** A: Yes, with local providers configured. Use Ollama for LLM, LocalGen for footage, and CosyVoice for TTS. All local providers work without internet connectivity.
**Q: How do I update provider settings?**
A: Use api_save_settings with the appropriate provider configuration. Settings persist to the .env file.

**Q: What video codec is used?**
A: H.264 by default for broad compatibility. Codec selection can be configured through settings. H.265 and AV1 are available for better compression on supported platforms.

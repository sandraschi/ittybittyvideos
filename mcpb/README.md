# videogen-mcp (MCPB Bundle)

AI-powered short video generation MCP server

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "videogen-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "videogen_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **videogen_help**: videogen_help
- **videogen_generate**: videogen_generate
- **videogen_status**: videogen_status
- **videogen_list_jobs**: videogen_list_jobs
- **videogen_providers**: videogen_providers
- **videogen_structures**: videogen_structures
- **videogen_intros**: videogen_intros
- **videogen_credits**: videogen_credits
- **videogen_visual_look**: videogen_visual_look
- **videogen_intro_sample**: videogen_intro_sample
- **videogen_credits_sample**: videogen_credits_sample
- **videogen_plan**: videogen_plan
- **videogen_plan_render**: videogen_plan_render
- **videogen_review**: videogen_review
- **videogen_depot**: videogen_depot
- **videogen_publish_pack**: videogen_publish_pack
- **root**: root
- **health**: health
- **cua_diagnostics**: cua_diagnostics
- **api_generate**: api_generate
- **api_list_jobs**: api_list_jobs
- **api_get_job**: api_get_job
- **api_download**: api_download
- **api_depot**: api_depot
- **api_depot_scan**: api_depot_scan
- **api_depot_delete**: api_depot_delete
- **api_depot_poster**: api_depot_poster
- **api_plan**: api_plan
- **api_visual_look_catalog**: api_visual_look_catalog
- **api_structures**: api_structures
- **api_credits_packs**: api_credits_packs
- **api_credits_sample**: api_credits_sample
- **api_intro_packs**: api_intro_packs
- **api_intro_sample**: api_intro_sample
- **api_plan_render**: api_plan_render
- **api_providers**: api_providers
- **api_status**: api_status
- **api_get_settings**: api_get_settings
- **api_list_models**: api_list_models
- **api_stock_status**: api_stock_status
- **api_save_settings**: api_save_settings
- **api_tools**: api_tools
- **api_publish_pack**: api_publish_pack
- **api_reveal_job**: api_reveal_job
- **api_list_addons**: api_list_addons
- **api_install_all_addons**: api_install_all_addons
- **api_install_addon**: api_install_addon
- **api_uninstall_addon**: api_uninstall_addon
- **spa_fallback**: spa_fallback
- **generate**: generate
- **logs_query**: logs_query
- **logs_stats**: logs_stats
- **logs_export**: logs_export
- **logs_clear**: logs_clear

## Requirements

- Python 3.12+
- uv

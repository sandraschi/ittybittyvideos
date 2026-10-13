# Per-repo fleet start config for videogen-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'videogen-mcp'
    BackendPort  = 11054
    FrontendPort = 11055
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'videogen_mcp.localgen_server.app:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '11054' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}

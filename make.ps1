# CodeDoc - PowerShell Commands
# Windows alternative to Makefile

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "`nCodeDoc - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\make.ps1 up              - Start all services in production mode" -ForegroundColor White
    Write-Host "  .\make.ps1 down            - Stop all services" -ForegroundColor White
    Write-Host "  .\make.ps1 build           - Build Docker images" -ForegroundColor White
    Write-Host "  .\make.ps1 restart         - Restart all services" -ForegroundColor White
    Write-Host "  .\make.ps1 logs            - View logs (follow mode)" -ForegroundColor White
    Write-Host "  .\make.ps1 clean           - Stop services and remove volumes" -ForegroundColor White
    Write-Host ""
    Write-Host "  .\make.ps1 dev             - Start services in development mode" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 prod            - Start services in production mode" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 status          - Show running containers" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 health          - Check backend health" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .\make.ps1 shell           - Open bash shell in backend container" -ForegroundColor Gray
    Write-Host "  .\make.ps1 test            - Run backend tests" -ForegroundColor Gray
    Write-Host "  .\make.ps1 install-deps    - Install backend dependencies" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\make.ps1 compile-ext     - Compile VS Code extension" -ForegroundColor Magenta
    Write-Host "  .\make.ps1 package-ext     - Package VS Code extension (.vsix)" -ForegroundColor Magenta
    Write-Host ""
}

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "up" { docker compose up -d }
    "down" { docker compose down }
    "build" { docker compose build }
    "restart" { docker compose down; docker compose up -d }
    "logs" { docker compose logs -f }
    "clean" { docker compose down -v; Write-Host "Cleaned up containers and volumes" -ForegroundColor Green }
    "dev" { docker compose -f docker-compose.dev.yml up }
    "prod" { docker compose up -d }
    "status" { docker compose ps }
    "shell" { docker compose exec backend bash }
    "test" { docker compose exec backend python -m pytest tests/ -v }
    "install-deps" { docker compose exec backend pip install -r requirements.txt }
    "health" {
        Write-Host "Checking backend health..." -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:5001/api/config" -TimeoutSec 5
            Write-Host "Backend is healthy!" -ForegroundColor Green
            $response | ConvertTo-Json
        } catch {
            Write-Host "Backend not responding" -ForegroundColor Red
        }
    }
    "compile-ext" {
        Set-Location vscode-extension
        npm run compile
        Set-Location ..
    }
    "package-ext" {
        Set-Location vscode-extension
        npm run package
        Set-Location ..
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
}

# 重新构建 WechatVibe 运行版，并就地更新到 .\WechatVibe\。
# .local（设置、会话列表、分析结果、已装模型）会保留，所以重构建不会把设置清掉。
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$install = Join-Path $root "WechatVibe"

# 运行中的旧版本会锁住 exe，先让它自己停掉桥接进程再结束。
$running = Get-Process -Name WechatVibe -ErrorAction SilentlyContinue
if ($running) {
  Write-Host "正在关闭运行中的 WechatVibe..."
  $python = Join-Path $install "resources\client\runtime\python\python.exe"
  $launcher = Join-Path $install "resources\client\scripts\start-real-client.py"
  if ((Test-Path $python) -and (Test-Path $launcher)) {
    & $python $launcher --stop-owned-bridge --json | Out-Null
    Start-Sleep -Seconds 2
  }
  $running | Stop-Process -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 3
}

$env:PATH = (Join-Path $root ".venv\Scripts") + ";" + $env:PATH
$env:LAYA_MODEL_DIR = Join-Path $root ".local\models\laya"
$env:WECHATVIBE_BUILD_NODE = Join-Path $root ".local\node-v24.11.1\node-v24.11.1-win-x64\node.exe"

Push-Location $root
try { & npm run build:portable } finally { Pop-Location }
if ($LASTEXITCODE -ne 0) { throw "构建失败（exit $LASTEXITCODE）" }

$builds = Get-ChildItem (Join-Path $root ".local\portable-builds") -Directory | Sort-Object LastWriteTime -Descending
$preview = Join-Path $builds[0].FullName "release\win-unpacked"
if (-not (Test-Path (Join-Path $preview "WechatVibe.exe"))) { throw "产物不完整: $preview" }
Write-Host "产物: $preview"

if (-not (Test-Path $install)) { New-Item -ItemType Directory -Path $install | Out-Null }
robocopy $preview $install /E /XD .local .models /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "同步失败（robocopy exit $LASTEXITCODE）" }

# 首次安装时把内置 Laya 模型一起放进去；已有模型则原地保留，不重复拷 680MB。
$model = Join-Path $install "resources\client\.models\laya\model.onnx"
if (-not (Test-Path $model)) {
  $source = Join-Path $preview "resources\client\.models"
  if (Test-Path $source) {
    robocopy $source (Join-Path $install "resources\client\.models") /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "模型复制失败（robocopy exit $LASTEXITCODE）" }
  }
}

Write-Host "已更新: $install\WechatVibe.exe（.local 与模型已保留）"
# 音乐下载器 APK 构建脚本 (PowerShell)
# 需要先安装 WSL2 Ubuntu: wsl --install -d Ubuntu
# 构建 APK: .\build_apk.ps1

$ErrorActionPreference = "Stop"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  音乐下载器 APK 构建脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# --- Path setup ---
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$driveLetter = $projectDir.Substring(0,1).ToLower()
$wslProjectPath = "/mnt/$driveLetter" + ($projectDir.Substring(2) -replace '\\', '/')

Write-Host "[INFO] 项目路径: $projectDir" -ForegroundColor Gray
Write-Host "[INFO] WSL 路径: $wslProjectPath" -ForegroundColor Gray
Write-Host ""

# --- Step 1: Check WSL ---
Write-Host "[1/4] 检查 WSL..." -ForegroundColor Yellow
try {
    $wslList = wsl --list --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] WSL 未安装或无 Linux 发行版" -ForegroundColor Red
        Write-Host "请在管理员 PowerShell 中运行: wsl --install -d Ubuntu" -ForegroundColor Yellow
        Write-Host "安装完成后重启电脑" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "[ERROR] WSL 不可用" -ForegroundColor Red
    exit 1
}
Write-Host "  WSL 已就绪" -ForegroundColor Green

# --- Step 2: Install dependencies ---
Write-Host "[2/4] 安装构建依赖..." -ForegroundColor Yellow
$setupCmd = @'
sudo apt update -y
sudo apt install -y python3-pip python3-dev git autoconf automake libtool \
    build-essential pkg-config zip unzip openjdk-17-jdk \
    libltdl-dev cmake ninja-build libffi-dev libssl-dev zlib1g-dev
pip3 install --upgrade pip setuptools wheel
pip3 install buildozer cython virtualenv
echo "DEPS_OK"
'@
$result = $setupCmd | wsl -d Ubuntu -- bash 2>&1
if ($result -match "DEPS_OK") {
    Write-Host "  依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[WARN] 依赖安装可能有误，继续尝试构建..." -ForegroundColor Yellow
}

# --- Step 3: Build APK ---
Write-Host "[3/4] 开始构建 APK（首次需 30-60 分钟）..." -ForegroundColor Yellow
Write-Host "  正在下载 Android SDK/NDK，请耐心等待..." -ForegroundColor Gray
Write-Host ""

$buildCmd = "cd '$wslProjectPath' && buildozer android debug 2>&1"
wsl -d Ubuntu -- bash -c $buildCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] 构建可能有错误，查看上方日志" -ForegroundColor Yellow
}

# --- Step 4: Copy APK ---
Write-Host ""
Write-Host "[4/4] 复制 APK..." -ForegroundColor Yellow
$outputDir = Join-Path $projectDir "output"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$apkFiles = Get-ChildItem -Path (Join-Path $projectDir "bin") -Filter "*.apk" -ErrorAction SilentlyContinue
if ($apkFiles) {
    Copy-Item -Path $apkFiles.FullName -Destination $outputDir -Force
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  构建成功！APK 位于:" -ForegroundColor Green
    Write-Host "  $outputDir" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 未找到 APK 文件，构建可能失败" -ForegroundColor Red
}

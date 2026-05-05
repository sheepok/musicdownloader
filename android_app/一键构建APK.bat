@echo off
chcp 65001 >nul
title 音乐下载器 - APK 构建

echo ========================================
echo   音乐下载器 APK 一键构建
echo ========================================
echo.
echo 请选择构建方式:
echo   [1] GitHub Actions 云端构建（推荐）
echo   [2] WSL 本地构建
echo.
set /p choice="请输入 1 或 2: "

if "%choice%"=="1" goto github
if "%choice%"=="2" goto wsl
echo 无效选择
pause
exit /b

:github
echo.
echo ========================================
echo   GitHub Actions 云端构建
echo ========================================
echo.
echo 步骤:
echo   1. 将项目推送到 GitHub 仓库
echo   2. GitHub Actions 会自动构建 APK
echo   3. 在 Actions 页面下载 APK 产物
echo.
echo 已为您打开 .github/workflows 目录
explorer "%~dp0..\.github\workflows"
echo.
echo 推送命令:
echo   git add -A
echo   git commit -m "update app"
echo   git branch -M main
echo   git remote add origin https://github.com/你的用户名/musicdownloader.git
echo   git push -u origin main
echo.
start https://github.com/new
pause
exit /b

:wsl
echo.
echo ========================================
echo   WSL 本地构建
echo ========================================
echo.
echo 正在检查 WSL...
wsl --list --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] WSL 未安装。请先在管理员终端运行:
    echo   wsl --install -d Ubuntu
    echo 然后重启电脑。
    pause
    exit /b 1
)

echo 正在安装构建依赖...
wsl -d Ubuntu -- bash -c "sudo apt update -y && sudo apt install -y python3-pip python3-dev git autoconf automake libtool build-essential pkg-config zip unzip openjdk-17-jdk libltdl-dev cmake ninja-build libffi-dev libssl-dev zlib1g-dev && pip3 install buildozer cython virtualenv"

echo 正在复制项目...
set "APP_DIR=%~dp0"
wsl -d Ubuntu -- bash -c "rm -rf /tmp/music-app; mkdir -p /tmp/music-app; cp -r '%APP_DIR:\=/%'* /tmp/music-app/; cd /tmp/music-app; buildozer android debug"

echo 正在复制 APK...
if not exist "%APP_DIR%output" mkdir "%APP_DIR%output"
wsl -d Ubuntu -- bash -c "cp /tmp/music-app/bin/*.apk '%APP_DIR:\=/%'/output/"
echo.
echo APK 位于: %APP_DIR%output
pause

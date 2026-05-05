# 音乐批量下载器 - Android 版

基于 `musicdownload.exe` (Windows) 转换的 Android 应用。

## 功能

- 支持多平台音乐搜索和下载（网易云、QQ音乐、酷我、酷狗、咪咕等）
- Kivy 原生 UI（APK 方案）
- Flask Web 界面（Termux 方案）
- 批量下载，自动保存到 `/sdcard/MusicDownloads/`

---

## 方案一：GitHub Actions 云端构建（推荐）

无需安装任何本地环境，在 GitHub 上自动构建 APK。

### 步骤

1. 在 GitHub 创建新仓库
2. 将本项目推送到仓库：
```bash
git init
git add -A
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/你的用户名/musicdownloader.git
git push -u origin main
```
3. 推送后 GitHub Actions 自动开始构建
4. 在仓库 Actions 页面下载 APK 产物（约 30-60 分钟）

---

## 方案二：WSL 本地构建

### 前提条件

- Windows 10/11 + WSL2 Ubuntu
- 至少 20GB 磁盘空间
- 网络稳定（需下载 Android SDK/NDK 约 2GB）

### 安装 WSL（一次性）

以管理员身份打开 PowerShell 运行：
```powershell
wsl --install -d Ubuntu
```
重启电脑后，打开 Ubuntu 完成初始设置（用户名/密码）。

### 一键构建

双击运行 `一键构建APK.bat`，按照提示选择 WSL 构建。

或手动执行：
```powershell
cd android_app
.\build_apk.ps1
```

### 构建时间

首次约 30-60 分钟（下载 SDK/NDK），后续约 5-10 分钟。

### APK 输出

`android_app/bin/musicdownloader-1.0-debug.apk`

---

## 方案三：Termux（免编译）

直接在手机上用 Termux 运行 Python，浏览器操作。

1. 安装 [Termux](https://f-droid.org/packages/com.termux/)
2. 复制 `android_app` 文件夹到手机 `/sdcard/`
3. 在 Termux 中运行：
```bash
cd /sdcard/android_app
bash setup_termux.sh
bash ~/start_music.sh
```
4. 手机浏览器打开 `http://localhost:5000`

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | Kivy APK 版主程序 |
| `main_flask.py` | Termux Web 版主程序 |
| `buildozer.spec` | APK 打包配置 (Buildozer) |
| `build_apk.ps1` | Windows PowerShell 构建脚本 |
| `一键构建APK.bat` | 一键构建启动器 |
| `setup_termux.sh` | Termux 一键安装脚本 |
| `../.github/workflows/build-apk.yml` | GitHub Actions 自动构建 |

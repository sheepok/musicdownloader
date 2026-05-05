[app]
title = 音乐下载器
package.name = musicdownloader
package.domain = com.musicdl
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# 核心依赖
# musicdl 会自动引入其子依赖
# 以下排除无法在 ARM 上编译的包: av, curl-cffi, orjson, nodejs-wheel, pywidevine
requirements = python3,kivy==2.3.0,musicdl,requests,urllib3,certifi,charset-normalizer,idna

orientation = portrait
fullscreen = 0
log_level = 2

# 权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.sdk = 34
android.arch = arm64-v8a
android.gradle_dependencies =
android.allow_backup = True
android.entrypoint = org.kivy.android.PythonActivity

# 启动画面
presplash.color = #121212
presplash.filename =

# 图标 (128x128 PNG)
icon.filename =

# Kivy 配置
android.add_src =

[buildozer]
log_level = 2
warn_on_root = 1

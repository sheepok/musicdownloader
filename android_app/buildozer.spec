[app]
title = 音乐下载器
package.name = musicdownloader
package.domain = com.musicdl
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# musicdl 已放入项目源码 (android_app/musicdl/)，不在 requirements 中安装
# 单独列出所有可在 ARM 上编译的依赖（排除 av, curl-cffi, orjson, pywidevine, nodejs-wheel）
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,charset-normalizer,idna,beautifulsoup4,soupsieve,click,lxml,mutagen,pycryptodomex,cryptography,cffi,pycparser,protobuf,platformdirs,rich,pygments,pyyaml,unidecode,tabulate,colorama,fake-useragent,emoji,bleach,webencodings,tinytag,filetype,puremagic,json-repair,pathvalidate,aigpy,construct,m3u8,ytmusicapi,pymp4,prompt-toolkit,wcwidth,brotli,markdown-it-py,mdurl

orientation = portrait
fullscreen = 0
log_level = 2

# 权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.sdk_path = /usr/local/lib/android/sdk
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

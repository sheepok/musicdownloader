#!/bin/bash
# 音乐下载器 - Android Termux 一键安装脚本
# 在 Termux 中执行: bash setup_termux.sh

echo "========================================="
echo "  音乐批量下载器 - Termux 安装脚本"
echo "========================================="
echo ""

# 1. 更新包管理器
echo "[1/4] 更新 Termux 包..."
pkg update -y && pkg upgrade -y

# 2. 安装 Python 和基础工具
echo "[2/4] 安装 Python 和依赖..."
pkg install -y python python-pip rust binutils libxml2 libxslt clang cmake patchelf

# 3. 安装 Python 依赖
echo "[3/4] 安装 Python 库（可能需要较长时间）..."
pip install flask requests musicdl

# 4. 创建启动脚本
echo "[4/4] 创建快捷启动..."
cat > ~/start_music.sh << 'EOF'
#!/bin/bash
cd /sdcard/MusicDownloads 2>/dev/null || mkdir -p /sdcard/MusicDownloads
echo ""
echo "====================================="
echo "  音乐下载器已启动！"
echo "  在浏览器中打开 http://localhost:5000"
echo "====================================="
echo ""
cd ~/music-downloader
python main_flask.py
EOF
chmod +x ~/start_music.sh

echo ""
echo "========================================="
echo "  安装完成！"
echo "  使用方法："
echo "    bash ~/start_music.sh"
echo "  然后在手机浏览器打开："
echo "    http://localhost:5000"
echo "========================================="

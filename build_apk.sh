#!/bin/bash
# APK构建脚本 - 在WSL Ubuntu中运行

echo "====================================="
echo "记账小助手 APK 构建脚本"
echo "====================================="

# 检查是否在WSL中
if ! grep -q Microsoft /proc/version; then
    echo "错误：请在WSL Ubuntu中运行此脚本"
    exit 1
fi

# 更新系统
echo ""
echo "[1/6] 更新系统包..."
sudo apt update
sudo apt upgrade -y

# 安装依赖
echo ""
echo "[2/6] 安装构建依赖..."
sudo apt install -y git zip unzip openjdk-17-jdk wget autoconf libtool \
    pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev build-essential ccache \
    python3-pip python3-venv

# 安装Buildozer
echo ""
echo "[3/6] 安装Buildozer..."
pip3 install --user --upgrade pip setuptools wheel
pip3 install --user buildozer cython==0.29.33

# 添加到PATH
export PATH=$PATH:~/.local/bin

# 进入项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[4/6] 清理旧构建..."
buildozer android clean || true

# 开始构建
echo ""
echo "[5/6] 开始构建APK（这需要30-60分钟）..."
echo "首次构建会下载Android SDK/NDK（约2-3GB）"
echo ""
buildozer -v android debug

# 检查结果
echo ""
echo "[6/6] 构建完成！"
if [ -f "bin/*.apk" ]; then
    echo ""
    echo "✅ APK文件生成成功！"
    ls -lh bin/*.apk
    echo ""
    echo "APK位置: $(pwd)/bin/"
    echo ""
    echo "请将APK复制到Windows："
    echo "cp bin/*.apk /mnt/d/Projects/Python/Projects/"
else
    echo ""
    echo "❌ 构建失败，请查看上面的错误信息"
    exit 1
fi

# WSL构建APK完整指南

## 一键构建（推荐）

在WSL Ubuntu中运行：

```bash
cd /mnt/d/Projects/Python/Projects/AccountingAPP_Python
chmod +x build_apk.sh
./build_apk.sh
```

脚本会自动：
- ✅ 安装所有依赖
- ✅ 配置Buildozer
- ✅ 构建APK
- ✅ 显示结果位置

## 手动构建步骤

如果想手动操作：

### 1. 进入WSL
```powershell
wsl
```

### 2. 进入项目目录
```bash
cd /mnt/d/Projects/Python/Projects/AccountingAPP_Python
```

### 3. 安装依赖（仅首次）
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
pip3 install --user buildozer cython
```

### 4. 构建APK
```bash
buildozer android debug
```

### 5. 获取APK
构建完成后，APK在：
```
bin/accountingapp-1.0.0-debug.apk
```

复制到Windows：
```bash
cp bin/*.apk /mnt/d/Projects/Python/Projects/
```

## 常见问题

**Q: 构建失败？**
A: 运行 `buildozer android clean` 清理后重试

**Q: 权限错误？**
A: 运行 `chmod +x ~/.buildozer/android/platform/build-tools/*/aapt`

**Q: 需要多久？**
A: 首次构建30-60分钟（下载SDK），后续5-10分钟

## GitHub Actions手动触发

如果想用GitHub Actions：
1. 访问 https://github.com/zhaochengyang12345/AccountingAPP/actions
2. 点击左侧 "Build APK"
3. 点击 "Run workflow" → "Run workflow"
4. 等待构建完成（30-60分钟）
5. 下载Artifacts中的APK

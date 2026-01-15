# 记账小助手 - Android应用

一个使用Python和Kivy框架开发的轻量级记账Android应用，专为小微企业设计。

## 功能特点

### 1. 手动记账
- 快速录入账单信息
- 自动关联客户和产品规格
- 智能计算总价
- 支持日期选择

### 2. 拍照记账
- 拍摄发票照片
- OCR自动识别文字信息
- 手动校验和补全数据
- 自动保存照片记录

### 3. 账单管理
- 查看所有账单记录
- 按客户、时间筛选
- 统计分析功能
- 导出Excel表格

### 4. 设置管理
- 客户信息管理
- 产品规格和单价设置
- 分层管理，方便查询

## 技术栈

- **Python 3.8+**
- **Kivy 2.2.1** - 跨平台GUI框架
- **KivyMD 1.1.1** - Material Design组件
- **SQLite3** - 轻量级数据库
- **Buildozer** - Android打包工具
- **Pytesseract** - OCR文字识别
- **OpenPyXL** - Excel导出

## 项目结构

```
AccountingAPP_Python/
├── main.py                    # 主应用程序入口
├── database.py                # 数据库管理模块
├── settings_screen.py         # 设置界面
├── manual_entry_screen.py     # 手动记账界面
├── photo_entry_screen.py      # 拍照记账界面
├── billing_screen.py          # 账单管理界面
├── requirements.txt           # Python依赖
├── buildozer.spec            # Android打包配置
└── README.md                  # 本文件
```

## 快速开始

### 方法一：Windows开发环境（推荐用于测试）

#### 1. 安装依赖

```powershell
# 安装Python依赖
cd AccountingAPP_Python
pip install -r requirements.txt
```

#### 2. 运行应用

```powershell
python main.py
```

此方法可以在Windows上测试应用界面和逻辑，但相机和OCR功能需要在Android设备上使用。

### 方法二：打包为Android APK（需要Linux环境）

#### 1. 准备Linux环境

由于Buildozer仅支持Linux，您需要：
- 使用Linux系统（Ubuntu 20.04+ 推荐）
- 或使用WSL2（Windows Subsystem for Linux）
- 或使用虚拟机

#### 2. 安装系统依赖（Ubuntu/Debian）

```bash
# 更新包列表
sudo apt update

# 安装必要的系统依赖
sudo apt install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-11-jdk \
    unzip \
    zip

# 安装Python依赖
pip3 install --upgrade pip
pip3 install buildozer cython
```

#### 3. 安装Android SDK和NDK

Buildozer会自动下载Android SDK和NDK，但首次构建会比较慢。

#### 4. 初始化Buildozer

```bash
cd AccountingAPP_Python

# 首次使用时初始化（如果需要修改配置）
# buildozer init

# 使用现有的buildozer.spec文件即可
```

#### 5. 打包APK

```bash
# 打包Debug版本（用于测试）
buildozer android debug

# 打包完成后，APK文件位于：
# bin/记账小助手-1.0.0-debug.apk
```

#### 6. 安装到Android设备

```bash
# 连接Android设备（启用开发者选项和USB调试）
# 然后运行：
buildozer android deploy run

# 或手动安装：
adb install bin/记账小助手-1.0.0-debug.apk
```

### 方法三：使用在线构建服务（推荐新手）

如果不想配置Linux环境，可以使用以下在线服务：

1. **GitHub Actions** - 配置CI/CD自动构建
2. **Google Colab** - 免费的云端Linux环境
3. **Replit** - 在线IDE，支持Linux

## 使用指南

### 首次使用

1. **添加客户信息**
   - 打开应用 → 点击"设置"
   - 点击"添加客户" → 输入公司名称
   - 点击客户名称 → 添加产品规格和单价

2. **手动记账**
   - 点击"手动记账"
   - 依次选择客户、日期、规格
   - 输入数量，自动计算总价
   - 点击"保存账单"

3. **拍照记账**
   - 点击"拍照记账"
   - 拍摄发票照片
   - 点击"识别文字"自动填充信息
   - 检查并补全缺失信息
   - 点击"保存账单"

4. **账单管理**
   - 点击"账单管理"
   - 查看所有账单记录
   - 点击筛选图标按客户/时间筛选
   - 点击下载图标导出Excel

## 权限说明

应用需要以下Android权限：

- **相机权限** - 用于拍照记账功能
- **存储权限** - 用于保存照片和导出Excel
- **网络权限** - 用于未来的云同步功能（可选）

## 常见问题

### Q1: 在Windows上运行提示缺少某些功能？
A: 这是正常的。相机和OCR功能需要在Android设备上使用，Windows环境主要用于界面和逻辑测试。

### Q2: Buildozer构建失败？
A: 常见原因：
- 确保使用Linux环境（不支持Windows）
- 检查网络连接（需要下载SDK和NDK）
- 确保有足够的磁盘空间（至少5GB）
- 查看错误日志：`.buildozer/logs/`

### Q3: OCR识别不准确？
A: OCR识别准确度取决于：
- 照片清晰度
- 光线条件
- 发票格式
建议拍照后手动检查和修正信息。

### Q4: Excel导出失败？
A: 确保应用有存储权限，并且设备有足够的存储空间。文件保存在Download文件夹中。

### Q5: 如何备份数据？
A: 数据库文件位于应用的私有存储中。您可以：
- 使用账单管理的导出功能定期导出Excel备份
- 使用Android备份工具备份应用数据

## 进阶配置

### 修改应用配置

编辑 `buildozer.spec` 文件可以修改：

```ini
# 应用名称
title = 记账小助手

# 包名
package.name = accountingapp
package.domain = com.miniapp

# 版本号
version = 1.0.0

# 权限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 目标API级别
android.api = 33
android.minapi = 21
```

### OCR语言支持

默认支持中文和英文。如需其他语言：

1. 下载Tesseract语言包
2. 修改 `photo_entry_screen.py` 中的语言参数：
```python
text = pytesseract.image_to_string(image, lang='chi_sim+eng')
```

### 自定义界面主题

修改 `main.py` 中的主题设置：

```python
self.theme_cls.primary_palette = "Blue"  # 主题色
self.theme_cls.theme_style = "Light"      # 浅色/深色模式
```

## 开发计划

- [ ] 云端数据同步
- [ ] 多用户支持
- [ ] 更智能的OCR识别
- [ ] 图表统计分析
- [ ] 发票模板管理
- [ ] 自动提醒功能

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发者。

---

**注意**: 本应用仅供学习和个人使用，请遵守相关法律法规。

# 大众点评榜单搜索工具

这是一个自动化工具，用于收集和分析大众点评APP中的美食榜单数据。整个工作流程包括榜单定位、数据采集、图像分析和数据上传四个主要步骤。

## 功能概述

- **界面定位**：自动定位大众点评APP界面中的关键元素
- **数据采集**：自动导航和截图收集美食榜单数据
- **图像分析**：使用Google Gemini AI识别截图中的餐厅信息
- **数据上传**：将分析结果上传到Supabase数据库

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- pyautogui - 用于自动化鼠标键盘操作
- pyperclip - 用于剪贴板操作
- Pillow - 用于图像处理
- python-dotenv - 用于环境变量管理
- google-generativeai - 用于图像分析
- supabase - 用于数据上传

## 环境配置

1. 创建一个`.env`文件，包含以下内容：
```
# Gemini API key
GEMINI_API_KEY="你的Gemini API密钥"

# Supabase credentials
SUPABASE_URL=你的Supabase URL
SUPABASE_KEY=你的Supabase密钥
```

2. 获取Gemini API密钥：
   - 访问 https://makersuite.google.com/app/apikey
   - 登录Google账号
   - 点击"Create API Key"创建新密钥

## 使用流程

### 1. 界面定位 (Locate.py)

首先运行界面定位工具，标记大众点评APP界面中的关键元素位置：

```bash
python Locate.py
```

按照提示依次定位各个界面元素，包括：
- 模拟器窗口边界
- 城市下拉按钮和搜索框
- 美食按钮和排行按钮
- 细分品类下拉按钮和19个细分品类

### 2. 数据采集 (Search.py)

运行搜索脚本，自动导航并截图收集榜单数据：

```bash
python Search.py
```

脚本会：
- 自动切换到指定城市
- 导航到美食榜单页面
- 截取主榜单图片并下滑多次
- 遍历19个细分品类，截取榜单图片
- 生成时间戳文件夹保存所有截图

### 3. 图像分析 (Analyzer.py)

使用Google Gemini AI分析截图中的餐厅信息：

```bash
python Analyzer.py 搜索结果截图/城市名_时间戳
```

例如：
```bash
python Analyzer.py 搜索结果截图/成都_20240408_085530
```

脚本会：
- 分析主榜单和所有细分品类的截图
- 识别每家餐厅的排名、名称、品牌、评分等信息
- 将结果保存为JSON文件

### 4. 数据上传 (Upload.py)

将分析结果上传到Supabase数据库：

```bash
python Upload.py 分析结果文件/城市名_时间戳
```

例如：
```bash
python Upload.py 分析结果文件/成都_20240408_085530
```

脚本会：
- 处理所有JSON文件
- 添加城市信息
- 处理重复记录
- 上传数据到Supabase数据库

## 配置说明

在`Config.py`中可以修改以下配置：
- `search_city` - 要搜索的城市名称
- `main_ranking_scroll_times` - 主榜单下滑次数
- `category_ranking_scroll_times` - 细分品类榜单下滑次数
- 各种界面元素的坐标位置

## 文件结构

- `Locate.py` - 界面定位工具
- `Config.py` - 全局配置文件
- `Search.py` - 数据采集脚本
- `Analyzer.py` - 图像分析工具
- `Upload.py` - 数据上传工具
- `requirements.txt` - 依赖包列表
- `.env` - 环境变量配置
- `搜索结果截图/` - 原始截图存储目录
- `分析结果文件/` - 处理后的JSON数据目录

## 注意事项

1. 运行前请确保模拟器窗口位置稳定，避免移动或调整窗口大小
2. 确保网络连接稳定，以便与Gemini API和Supabase通信
3. API密钥应妥善保管，避免泄露
4. 运行过程中请勿操作鼠标和键盘，以免干扰自动化流程 
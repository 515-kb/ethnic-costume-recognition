# 民族服饰智能识别系统

> 基于多模态大模型的民族服饰图像识别 Web 演示系统，支持 55 个民族类别，提供详细的服饰特征分析。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

本项目是一个民族服饰智能识别 Web 应用，用户上传民族服饰图片后，系统通过多模态大模型自动识别所属民族，并输出置信度、服饰特征分析和识别依据。

项目同时配套了 55 类民族服饰目标检测数据集，可用于后续训练自定义检测模型。

## 功能特性

- 🖼️ **图片智能识别** — 上传任意民族服饰图片，AI 自动识别所属民族
- 👥 **55 个民族覆盖** — 涵盖汉族及 54 个少数民族的传统服饰
- 🔍 **深度特征分析** — 从色彩、纹样、款式、配饰等多角度分析服饰特征
- 🔌 **RESTful API** — 提供标准 API 接口，方便集成到其他应用
- 📊 **数据集配套** — 配套 55 类民族服饰目标检测数据集（YOLO + VOC 格式）
- 🎨 **精美界面** — 深色主题设计，响应式布局，支持拖拽上传
- 📦 **完全开源** — MIT 协议，代码结构清晰，文档完善

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.0 |
| AI 引擎 | Qwen-VL-Plus（阿里云通义千问多模态大模型） |
| 前端 | Bootstrap 5 + 原生 JavaScript |
| 数据格式 | JSON |
| 部署 | 本地运行 / Docker（后续支持） |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/515-kb/ethnic-costume-recognition.git
cd ethnic-costume-recognition
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

本项目使用阿里云 DashScope API 进行图像识别，需要先获取 API Key：

1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 注册/登录账号，获取 API Key
3. 设置环境变量：

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_API_KEY = "your-api-key-here"
```

**Windows (CMD):**
```cmd
set DASHSCOPE_API_KEY=your-api-key-here
```

**Linux / macOS:**
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

> ⚠️ 请勿将 API Key 硬编码在代码中或提交到 Git 仓库

### 4. 启动服务

```bash
python web/app.py
```

启动后浏览器访问：**http://127.0.0.1:5000**

## 项目结构

```
ethnic-costume-recognition/
├── web/
│   ├── app.py                 # Flask 应用主入口
│   ├── templates/             # HTML 模板
│   │   ├── base.html          # 基础布局模板
│   │   ├── index.html         # 首页
│   │   ├── detection.html     # 在线识别页面
│   │   ├── dataset.html       # 数据集介绍页面
│   │   └── about.html         # 技术说明页面
│   └── static/                # 静态资源
│       ├── images/samples/    # 示例图片
│       └── uploads/           # 用户上传图片（运行时生成）
├── data/
│   └── classes.json           # 55 个民族类别数据
├── requirements.txt           # Python 依赖
├── .gitignore                 # Git 忽略规则
├── LICENSE                    # MIT 开源协议
└── README.md                  # 项目说明文档
```

## API 接口文档

### 健康检查

```
GET /api/health
```

返回服务状态、API 配置状态和支持类别数。

### 获取所有类别

```
GET /api/classes
```

返回 55 个民族类别的详细信息（ID、中文名、英文名、拼音）。

### 上传图片识别

```
POST /api/detect
Content-Type: multipart/form-data
字段名: image
```

返回识别结果：

```json
{
  "predicted_class": "维吾尔族",
  "predicted_class_en": "Uyghur",
  "confidence": 0.9456,
  "analysis": "服饰色彩鲜艳，以红、绿、金为主...",
  "features": ["艾德莱斯丝绸", "小花帽", "..."].
  "image_url": "/static/uploads/xxx.jpg",
  "inference_time": 2.35
}
```

### 识别示例图片

```
POST /api/detect_sample
Content-Type: application/json
Body: {"sample_path": "images/samples/xxx.jpg"}
```

## 数据集说明

项目配套 **55 类民族服饰目标检测数据集**（DST1138），包含：

- **类别数**：55 个民族
- **划分**：训练集 / 验证集 / 测试集
- **标注格式**：YOLO 格式 + VOC 格式
- **任务类型**：目标检测

数据集目录结构：

```
shaoshuminzu(DST1138)/
├── data.yaml          # YOLO 数据集配置
├── images/            # 图片目录
│   ├── train/
│   ├── valid/
│   └── test/
├── labels/            # YOLO 格式标注
│   ├── train/
│   ├── valid/
│   └── test/
└── VOC/               # VOC 格式标注
    ├── train/
    ├── valid/
    └── test/
```

## 后续计划

- [ ] **接入本地 YOLOv5 目标检测模型**，实现离线识别
- [ ] 支持批量图片识别和结果导出
- [ ] 支持识别结果可视化（边界框标注）
- [ ] Docker 容器化部署
- [ ] 增加更多民族服饰示例图片

## 注意事项

1. 本项目使用阿里云 DashScope API 进行图像识别，需要有效 API Key 才能使用识别功能
2. API 调用会产生费用，请参考 [阿里云计费说明](https://help.aliyun.com/zh/model-studio/billing-for-qwen-vl)
3. 识别结果由 AI 模型生成，仅供参考，不保证 100% 准确
4. 请勿将 API Key 硬编码在代码中或提交到 Git 仓库

## 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

## 致谢

- [阿里云通义千问](https://tongyi.aliyun.com/) - 提供多模态大模型 API
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Bootstrap](https://getbootstrap.com/) - 前端 UI 框架

---

如果这个项目对你有帮助，欢迎给个 ⭐ Star！

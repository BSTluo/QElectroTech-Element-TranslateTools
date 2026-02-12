<div align="center">

# QElectroTech 元件库翻译工具

<p align="center">
  <strong>为 QElectroTech 电气符号库自动添加中文翻译的完整解决方案</strong>
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-功能特性">功能特性</a> •
  <a href="#-配置说明">配置</a> •
  <a href="#-常见问题">FAQ</a> •
  <a href="#-更新日志">更新日志</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="version">
  <img src="https://img.shields.io/badge/python-3.7+-green.svg" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="license">
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen.svg" alt="status">
</p>

</div>

---

## 📖 简介

一键为数千个 QElectroTech 元件文件（`qet_directory` 和 `*.elmt`）自动添加中文翻译标签，完全保留原有的英、法、德等语言版本。

**核心特性：** AI智能翻译 | 断点续翻 | 智能缓存 | 实时进度 | 零依赖 | 并行处理 | API可配置

### 示例效果

```xml
<!-- 处理前 -->
<names>
    <name lang="en">Electric</name>
    <name lang="fr">Electrique</name>
</names>

<!-- 处理后 -->
<names>
    <name lang="en">Electric</name>
    <name lang="fr">Electrique</name>
    <name lang="zh">电气</name>  ✨ 自动添加
</names>
```

---

## 🚀 快速开始

### 系统要求

- Python 3.7+ （[下载地址](https://www.python.org/downloads/)）
- 网络连接（调用翻译 API）
- 硬盘空间（源文件大小的 2 倍）

### 5秒上手

<table>
<tr>
<td>

**Windows 用户**

```batch
# 方式1：自动同步并翻译（推荐）
run.bat
```

</td>
<td>

**Mac/Linux 用户**

```bash
# 方式1：翻译现有文件
sh run.sh

# 方式2：命令行运行
python3 scripts/translate_to_result.py
```

</td>
</tr>
</table>

**就这么简单！** 处理完成后，所有结果都在 `result/` 文件夹中。

> ⚠️ **重要提示：项目自带翻译缓存**
>
> 本项目包含 `translate_cache.json` 文件，内含已翻译好的缓存数据。
>
> - ✅ **首次使用推荐**：直接运行 `run.bat`，使用现有缓存快速生成结果（无需 API）
> - 🔄 **重新翻译**：如需使用自己的 API/OpenAI 重新翻译，请先删除 `translate_cache.json`
>
> ```bash
> # Windows - 删除缓存后重新翻译
> del translate_cache.json
> run.bat
>
> # Mac/Linux - 删除缓存后重新翻译
> rm translate_cache.json
> sh run.sh
> ```

### 🔄 自动同步 QElectroTech 元件库（新功能）

无需手动复制文件！使用 `run.bat` 自动从 QElectroTech 安装目录获取最新元件库：

**自动检测路径：**
- ✅ 从注册表读取安装位置（最准确）
- ✅ 检查常见安装目录
- ✅ 支持手动配置路径

**使用方法：**

```batch
# 一键完成：同步 + 翻译
run.bat
```

**手动指定路径（可选）：**

在 `translate_config.json` 中添加：
```json
{
  "qet_elements_path": "C:\\Program Files\\QElectroTech\\elements",
  ...其他配置...
}
```

---

## ✨ 功能特性

<table>
<tr>
<td width="50%">

### 🎯 核心功能
- ✅ **AI 智能翻译** - 支持 OpenAI/兼容接口
- ✅ **断点续翻** - 翻译中断后自动续传
- ✅ 自动翻译 `qet_directory` 和 `.elmt` 文件
- ✅ 保留所有原有语言标签
- ✅ 智能跳过已翻译文件
- ✅ 本地缓存避免重复翻译
- ✅ 并行处理提升 5 倍速度

</td>
<td width="50%">

### 📊 用户体验
- 🤖 **双模式翻译** - API / OpenAI 自由切换
- 🔄 **批量翻译** - OpenAI 批处理高效省时
- 🚀 一键启动，无需配置
- 📈 实时进度显示（速度/ETA）
- 🔧 API 完全可配置
- 💾 自动保存进度
- 🌍 支持多语言翻译

</td>
</tr>
</table>

---

## 📋 运行示例

```
============================================================
QET Directory & Element Translator
Start time: 2026-02-10 15:30:45
============================================================

[1/3] Copying src to result directory...
✓ Copy completed

[2/3] Scanning files...
✓ Found 12,145 files to process

[3/3] Processing and translating...
[████████████░░░░░░░░░░░░] 45.2% (5499/12145) 
Updated: 2847 | Speed: 23.4 files/s | ETA: 283s

============================================================
✓ Completed!
  Total files processed: 12,145
  Files updated: 2,847
  Time elapsed: 234.5s
  Output directory: result/
============================================================
```

### 进度条说明
- **████░░**: 完成进度可视化
- **45.2%**: 完成百分比
- **Updated**: 本次添加中文标签的文件数
- **Speed**: 当前处理速度
- **ETA**: 预计剩余时间

---

## ⚙️ 配置说明

### 配置文件：`translate_config.json`

```json
{
  "endpoint": "https://uapis.cn/api/v1/translate/text",
  "to_lang": "zh-CHS",
  "headers": {
    "Content-Type": "application/json"
  },
  "translate_mode": "api",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_api_key": "",
  "openai_model": "gpt-5.2",
  "openai_batch_size": 20,
  "api_save_every": 10,
  "timeout_seconds": 20,
  "sleep_seconds": 0.1,
  "source_lang_priority": ["en", "fr"],
  "cache_file": "translate_cache.json",
  "max_workers": 5
}
```

### 关键配置项

| 配置项 | 说明 | 默认值 | 建议 |
|--------|------|--------|------|
| `endpoint` | 翻译API地址 | `https://uapis.cn/...` | 修改为你的API |
| `to_lang` | 目标语言 | `zh-CHS` | 简体中文 |
| `translate_mode` | 翻译方式 | `api` | `api` 或 `openai` |
| `openai_base_url` | OpenAI接口地址 | `https://api.openai.com/v1` | 兼容服务可修改 |
| `openai_api_key` | OpenAI API Key | 空 | 使用AI翻译必填 |
| `openai_model` | OpenAI模型 | `gpt-5.2` | 可按需修改 |
| `openai_batch_size` | OpenAI批量条数 | `20` | >1启用批量翻译，每批自动保存 |
| `api_save_every` | API模式保存频率 | `10` | 每N条翻译保存一次缓存 |
| `timeout_seconds` | API超时（秒） | `20` | 网络差改成30 |
| `sleep_seconds` | 请求间隔（秒） | `0.1` | API限流改成0.5 |
| `max_workers` | 并行线程数 | `5` | 0=串行，5=推荐 |
| `source_lang_priority` | 源语言优先级 | `["en", "fr"]` | 先英后法 |
| `qet_elements_path` | QET元件库路径（可选） | 自动检测 | 手动指定路径 |

### ⚡ 并行处理性能对比

| 模式 | max_workers | 速度 | 适用场景 |
|------|------------|------|---------|
| 串行 | 0 | ~3 files/s | API有严格限流 |
| 并行 | 5 | ~15 files/s | 推荐（5倍速度⚡） |
| 高并行 | 10 | ~25 files/s | 强大API + 快速网络 |

### 使用自定义翻译API

修改 `endpoint` 为你的 API 地址，确保 API 返回格式：

**请求示例：**
```json
POST /translate
{
  "ToLang": "zh-CHS",
  "text": "待翻译文本"
}
```

**响应示例：**
```json
{
  "text": "原文",
  "translate": "翻译结果"
}
```

> 💡 如果字段名不同，需修改 `scripts/translate_to_result.py` 中的 `translate_text()` 函数。

### 🤖 使用 OpenAI / AI 翻译模式

支持 OpenAI 官方接口及所有兼容接口（如 Azure OpenAI、国内中转服务等）。

**配置步骤：**

1. 修改 `translate_config.json`：
```json
{
  "translate_mode": "openai",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_api_key": "sk-your-key-here",
  "openai_model": "gpt-4",
  "openai_batch_size": 20
}
```

2. 运行翻译：
```bash
run.bat  # 或 python scripts/translate_to_result.py
```

**AI 翻译优势：**
- ✅ **更准确** - 理解上下文，专业术语翻译更精准
- ✅ **批量处理** - 一次请求翻译多条，节省时间和成本
- ✅ **断点续翻** - 每完成一批自动保存，中断后继续
- ✅ **兼容性强** - 支持所有 OpenAI 兼容接口

**批量翻译说明：**
- `openai_batch_size` 设为 1：逐条翻译（适合调试）
- `openai_batch_size` 设为 20：每次翻译 20 条（推荐，效率高）
- 每完成一批自动保存进度到 `translate_cache.json`

### 💾 断点续翻功能

翻译过程中断（网络故障、手动停止等）后，重新运行会**自动从中断处继续**。

> 📦 **项目自带完整缓存**
>
> 本项目的 `translate_cache.json` 已包含所有元件的翻译结果。
> - 直接运行：使用现有缓存，无需 API，秒级完成
> - 重新翻译：删除 `translate_cache.json` 后再运行

**工作原理：**
- **OpenAI 模式**：每完成一批（如 20 条）立即保存缓存
- **API 模式**：每完成 10 条（可配置 `api_save_every`）保存一次
- 已翻译的内容不会重复调用 API，节省成本

**使用示例：**
```bash
# 首次运行（处理到 5000 条时中断）
run.bat
# 进度：5000/10000 已保存

# 重新运行（自动从 5001 开始）
run.bat
# 进度：5001/10000 继续...
```

**手动清空进度：**
```bash
# 删除缓存文件重新翻译
del translate_cache.json  # Windows
rm translate_cache.json   # Mac/Linux
```

---

## � 项目结构

```
elements/
├── 📄 README.md                    # 项目文档
├── 📄 LICENSE                      # MIT 许可证
├── 📄 requirements.txt             # 依赖列表（无外部依赖）
├── ⚙️ translate_config.json        # 配置文件
├── 💾 translate_cache.json         # 翻译缓存（项目自带，可删除后重新翻译）
│
├── 🚀 run.bat                      # Windows 启动脚本（仅翻译）
├── 🚀 run_with_sync.bat            # Windows 启动脚本（同步+翻译）
├── 🚀 sync.bat                     # Windows 同步脚本（仅同步）
├── 🚀 run.sh                       # Mac/Linux 启动脚本
│
├── 📁 scripts/
│   ├── translate_to_result.py     # 核心翻译脚本
│   └── sync_from_qet.py           # QET元件库同步脚本
│
├── 📁 src/                         # 源文件（不会修改）
│   ├── 10_electric/
│   ├── 20_logic/
│   ├── 30_hydraulic/
│   ├── 50_pneumatic/
│   └── 60_energy/
│
└── 📁 result/                      # 输出目录（自动生成）
    └── （与 src 结构相同，已添加中文标签）
```

---

## 🔧 常见问题

<details>
<summary><b>Q1: 运行时出现 "Python not found" 错误</b></summary>

**解决方案：**
1. 访问 [python.org](https://www.python.org/downloads/) 下载 Python 3.7+
2. 安装时务必勾选 "Add Python to PATH"
3. 重启终端后重新运行
</details>

<details>
<summary><b>Q2: 出现 "Invalid request body" 错误</b></summary>

**原因：** API 地址或格式不正确

**解决方案：**
1. 检查 `translate_config.json` 中的 `endpoint` 是否正确
2. 测试 API 是否可访问：
   ```bash
   curl -X POST "你的API地址" \
     -H "Content-Type: application/json" \
     -d '{"ToLang": "zh-CHS", "text": "test"}'
   ```
3. 确认 API 返回格式包含 `translate` 字段
</details>

<details>
<summary><b>Q3: 处理速度太慢怎么办？</b></summary>

**正常现象：** 第一次运行需调用翻译 API，较慢是正常的

**加速方法：**
- ✅ 第二次运行使用缓存，速度提升 10 倍
- ✅ 设置 `max_workers: 5` 启用并行处理（5倍速度）
- ✅ 如果 API 限流，适当增加 `sleep_seconds`
</details>

<details>
<summary><b>Q4: 某些文件没有被更新</b></summary>

**检查清单：**
- ✅ 文件中是否有 `<names>` 标签
- ✅ 是否包含 `<name lang="en">` 或 `<name lang="fr">`
- ✅ 是否已存在 `<name lang="zh">`（已有则跳过）
- ✅ 查看运行日志中的错误信息
</details>

<details>
<summary><b>Q5: 翻译结果不准确</b></summary>

**解决方案：**
1. 打开 `translate_cache.json` 找到对应词条
2. 手动修改翻译结果
3. 删除 `result/` 文件夹
4. 重新运行脚本（使用更新后的缓存）
</details>

<details>
<summary><b>Q6: 为什么运行很快但没有调用 API？</b></summary>

**原因：** 项目自带 `translate_cache.json` 缓存文件，包含所有已翻译内容

**解决方案：**

如需使用自己的 API/OpenAI 重新翻译：
```bash
# 1. 删除缓存文件
del translate_cache.json     # Windows
rm translate_cache.json      # Mac/Linux

# 2. 配置 translate_config.json
# 填写你的 API 信息或 OpenAI Key

# 3. 重新运行
run.bat                      # Windows
sh run.sh                    # Mac/Linux
```

**首次使用推荐：** 直接运行使用现有缓存，快速体验完整功能
</details>

<details>
<summary><b>Q7: 如何重新翻译所有文件？</b></summary>

```bash
# 删除缓存和结果
del translate_cache.json     # Windows
rm translate_cache.json      # Mac/Linux
rm -r result/

# 重新运行
python scripts/translate_to_result.py
```
</details>

---

## 💡 使用技巧

### 🎯 常见工作流

**首次使用（推荐 - 使用自带缓存）**
```bash
# 项目自带完整翻译缓存，直接运行即可快速体验
run.bat           # Windows
sh run.sh         # Mac/Linux

# 几秒钟内完成，结果在 result/ 目录
```

**使用自己的 API/OpenAI 重新翻译**
```bash
# 1. 删除自带缓存
del translate_cache.json       # Windows
rm translate_cache.json        # Mac/Linux

# 2. 配置 translate_config.json（填写你的 API Key）

# 3. 运行翻译
run.bat                        # Windows
sh run.sh                      # Mac/Linux

# 等待 10-30 分钟（取决于文件数量和网络）
```

**添加新文件后增量翻译**
```bash
# 1. 将新文件添加到 src/
# 2. 重新运行（自动只翻译新文件）
python scripts/translate_to_result.py
```

**更换翻译API 或 OpenAI**
```bash
# 1. 修改 translate_config.json
#    - API模式：修改 endpoint
#    - OpenAI模式：设置 translate_mode: "openai" 和填写 openai_api_key

# 2. 删除缓存（必须，否则会使用旧缓存）
del translate_cache.json       # Windows
rm translate_cache.json        # Mac/Linux

# 3. 重新运行
run.bat                        # Windows
python scripts/translate_to_result.py
```

### 🔧 高级配置

**翻译为其他语言**
```json
{
  "to_lang": "es",                    // 西班牙语
  "source_lang_priority": ["en"]      // 从英文翻译
}
```

**修改源文件路径**
```python
# 编辑 scripts/translate_to_result.py
SRC_DIR = "your/source/path"
RESULT_DIR = "your/output/path"
```

**只处理特定文件类型**
```python
# 编辑 scripts/translate_to_result.py
# 只处理 .elmt 文件
if filename.lower().endswith(".elmt"):
    file_paths.append(os.path.join(root, filename))
```

---

## � 性能参考

| 场景 | 文件数 | 时间 | 说明 |
|------|--------|------|------|
| 首次运行（串行） | 10,000 | 400-600s | 调用 API 翻译 |
| 首次运行（并行x5） | 10,000 | 80-120s | 并行处理，5倍速 |
| 二次运行（缓存） | 10,000 | 30-60s | 使用本地缓存 |
| 增量更新 | 100 | 5-10s | 只处理新文件 |

---

## 📝 更新日志

### [1.0.0] - 2026-02-10

#### ✨ 新增功能
- 批量翻译 `qet_directory` 和 `.elmt` 文件
- 智能缓存系统避免重复 API 调用
- 实时进度显示（速度 / ETA）
- 并行处理模式（5倍速度提升）
- 可配置翻译 API
- 跳过已有中文翻译的文件
- Windows/Mac/Linux 一键启动脚本

#### 🐛 修复
- XML 内容转义处理
- API 字段名称规范化
- 嵌套目录结构支持
- 错误处理和异常捕获

#### 🎯 计划功能 (v1.1.0)
- [ ] 单次运行支持多目标语言
- [ ] Web UI 配置和监控界面
- [ ] 差异输出（显示变更内容）
- [ ] Docker 容器化部署
- [x] ~~断点续传功能~~ ✅ 已实现

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题

提交 Issue 时请包含：
- 操作系统和 Python 版本
- 完整的错误信息
- 重现步骤
- 预期行为和实际行为

---

## 📚 相关资源

- [QElectroTech 官网](http://qelectrotech.org/) - 了解 QET 电气制图软件
- [QET 文档](https://qelectrotech.org/wiki/doc/) - 官方文档
- [QET 元件库](https://qelectrotech.org/wiki/doc/elements) - 元件库说明

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

```
MIT License

Copyright (c) 2026 QET Element Translator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🙏 致谢

- [QElectroTech](http://qelectrotech.org/) - 优秀的开源电气制图软件
- 所有贡献者和用户的支持

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐**

Made with ❤️ by the QET Community

</div>

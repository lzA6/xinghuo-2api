# Xinghuo-2api 🚀

一个高性能、生产级的讯飞星火（Xinghuo）本地代理服务，完全兼容 OpenAI API 格式。

[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-fast-green.svg)](https://fastapi.tiangolo.com/)

---

## ✨ 项目亮点

- **🚀 生产级架构**: 采用 Nginx + FastAPI (Uvicorn) 的高性能微服务架构，稳定可靠。
- **🔄 终极粘性会话**: 借助 Nginx，基于用户的 `Cookie` 实现完美的粘性会話，确保多轮对话的稳定性和连续性，从根本上解决流式响应混乱的问题。
- **⚡️ 高性能**: 优化的 Nginx 配置和异步 Python 框架，提供极致的性能和吞吐量。
- **🔌 OpenAI 兼容**: 无缝对接任何支持 OpenAI API 的客户端、应用和工具。
- **📦 一键部署**: 提供 Docker 和 Docker Compose 配置，实现一键启动和部署。
- **🔐 安全可靠**: 支持 `API_MASTER_KEY`，保护您的服务不被滥用。

## 🔧 技术架构与差异对比

本项目的架构设计深度融合了 `Qwen-2api` 和 `Ernie-2api` 等黄金标准项目的优点，并针对讯飞星火的特性进行了优化。

| 特性 | Xinghuo-2api | Qwen-2api / Ernie-2api | 设计考量 |
| :--- | :--- | :--- | :--- |
| **核心架构** | Nginx + FastAPI | Nginx + FastAPI | **[继承]** 沿用业界验证的高性能、高可用架构。 |
| **请求格式** | `multipart/form-data` | `application/json` | **[适配]** 这是一个关键区别。星火的聊天接口使用表单提交，本项目已完美适配此格式。 |
| **认证方式** | **Cookie** + **GtToken** | Bearer Token (`Authorization`) | **[优化]** 讯飞星火官网主要通过 Cookie 进行用户认证，并辅以 `GtToken` 进行安全验证。本项目直接适配此机制。 |
| **粘性会话键** | `$http_cookie` | `$http_authorization` | **[优化]** 这是最重要的架构决策之一。由于认证方式是 Cookie，我们选择使用它作为 Nginx 的哈希键，确保了100%的会话保持。 |
| **流式解析** | **Base64 增量解码** | JSON 累积/增量解析 | **[适配]** 星火的流式响应为分段的 Base64 编码文本，本项目实现了专门的解码器来处理这种独特的格式。 |


## 📚 终极抓包教程 (获取核心认证信息)

如果 `Cookie` 或 `GtToken` 过期导致服务失效，您需要重新获取它们。

1.  **打开开发者工具**:
    *   在 Chrome 或 Edge 浏览器中访问 [讯飞星火官网](https://xinghuo.xfyun.cn/desk)。
    *   按下 `F12` 键，打开“开发者工具”面板。

2.  **切换到网络面板**:
    *   在开发者工具中，点击顶部的 `网络` (或 `Network`) 选项卡。
    *   在下方的过滤栏中，点击 `Fetch/XHR`。
    *   **关键**: 勾选 `Preserve log` (保留日志)。

    ![步骤1和2](https://i.imgur.com/gV8P2Hw.png)

3.  **发送一条消息**:
    *   在星火的聊天输入框中，输入任意内容（例如“你好”），然后点击发送。

4.  **定位关键请求**:
    *   发送后，观察网络面板。你会看到一个新的、名为 `chat` 的请求。点击它。

    ![步骤3和4](https://i.imgur.com/J9a2g0L.png)

5.  **获取认证信息**:
    *   在右侧的 `标头` (`Headers`) 标签页中，向下滚动到 `请求标头` (`Request Headers`) 部分。
        *   找到 `cookie` 字段，**复制它的完整值**。这就是你的 `XINGHUO_COOKIE`。
    *   再向下滚动到 `表单数据` (`Form Data`) 部分。
        *   找到 `GtToken` 字段，**复制它的完整值**。这就是你的 `GT_TOKEN`。

    ![步骤5](https://i.imgur.com/Yg1gL0k.png)

6.  **更新配置**:
    *   将新获取的值粘贴到你的 `.env` 文件中，然后重启服务。

## 🚀 部署指南

### 1. 本地 Docker 部署

**前提**: 已安装 [Docker](https://www.docker.com/get-started) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

**步骤**:

1.  **下载项目**:
    *   将所有项目文件保存在一个文件夹中，例如 `Xinghuo-2api`。

2.  **创建并编辑 `.env` 文件**:
    *   将 `.env.example` 文件复制一份并重命名为 `.env`。
    *   打开 `.env` 文件，按照抓包教程填入你的 `API_MASTER_KEY`、`XINGHUO_COOKIE` 和 `GT_TOKEN`。

3.  **启动服务**:
    ```bash
    docker-compose up -d --build
    ```

4.  **测试服务**:
    服务将在 `http://localhost:8082` 上运行。你可以使用任何 OpenAI 客户端进行测试。

    ```bash
    curl http://localhost:8082/v1/models -H "Authorization: Bearer your-secret-key"
    ```

### 2. Hugging Face Space 部署

**前提**: 拥有一个 [Hugging Face](https://huggingface.co/) 账号。

**步骤**:

1.  **新建 Space**:
    *   在 Hugging Face 上，点击你的头像，选择 `New Space`。
    *   **Space name**: `Xinghuo-2api` (或你喜欢的名字)。
    *   **License**: `mit`。
    *   **Space SDK**: 选择 `Docker`，并选择 `Blank` 模板。
    *   点击 `Create Space`。

2.  **上传项目文件**:
    *   将本项目的所有文件（`main.py`, `Dockerfile`, `requirements.txt`, `app/` 目录等）上传到你创建的 Space 的 `Files` 选项卡中。

3.  **配置环境变量**:
    *   进入 Space 的 `Settings` 页面。
    *   找到 `Repository secrets` 部分。
    *   点击 `New secret`，添加以下三个密钥：
        *   `API_MASTER_KEY`: 你的主密钥。
        *   `XINGHUO_COOKIE`: 你的讯飞星火 Cookie。
        *   `GT_TOKEN`: 你的 GtToken。

4.  **等待构建**:
    *   Hugging Face 会自动根据你的 `Dockerfile` 构建并部署应用。你可以在 `Logs` 选项卡中查看部署进度。
    *   部署成功后，你的 API 端点就是 Space 的公开地址。

## 📝 API 使用示例

请将 `YOUR_API_BASE_URL` 替换为你的实际 API 地址（例如 `http://localhost:8082/v1` 或你的 Hugging Face Space URL + `/v1`），并将 `your-secret-key` 替换为你的 `API_MASTER_KEY`。

```python
import openai

client = openai.OpenAI(
    api_key="your-secret-key",
    base_url="YOUR_API_BASE_URL"
)

# 模型列表
try:
    models = client.models.list()
    print("--- 支持的模型 ---")
    for model in models.data:
        print(model.id)
    print("--------------------")
except Exception as e:
    print(f"获取模型列表失败: {e}")


# 流式聊天
print("\n--- 开始流式聊天 ---")
try:
    stream = client.chat.completions.create(
        model="spark-3.5-max",
        messages=[{"role": "user", "content": "你好，请用Python写一个快速排序算法"}],
        stream=True,
    )

    for chunk in stream:
        print(chunk.choices.delta.content or "", end="")
    print("\n--------------------")

except Exception as e:
    print(f"聊天失败: {e}")

```

---

**创世纪协议已完成。项目已达到生产就绪状态。**

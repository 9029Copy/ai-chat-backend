# AIAPI调用后端程序

> 作者：9029Copy
> 日期：20250717

---

## 一、项目概述
本项目是一个基于**FastAPI**的AI聊天后端服务，用于接收客户端请求并转发至上游AI模型，同时维护多条会话历史。

## 二、功能特点
- API密钥鉴权能力
- 支持通过配置文件调整参数
- 支持管理历史会话（保存最多5轮对话）

## 三、环境要求
- Python 3.8+
- 依赖包：fastapi, uvicorn, httpx, pyyaml

## 四、安装步骤
1. 克隆项目到本地
2. 安装依赖：
    ```bash
    pip install fastapi uvicorn httpx pyyaml
    ```

## 五、配置说明
1. 创建`config.yaml`文件，内容格式如下：
    ```yaml
    api_keys:
      - <your_key_1>
      - <your_key_2>
    ai_api_scheme: <https>
    ai_api_host: <api.example.com>
    ai_api_port: <443>
    ai_api_path: <v1/chat/completions>
    ai_model: <Qwen/QwQ-32B>
    ai_api_token: <your_ai_token_here>
    max_history: 5
    ```
2. 将其中的<>部分替换为实际值：
    - `<your_key_1>`替换为实际的访问密钥1
    - `<your_key_2>`替换为实际的访问密钥2（可选）
    - `<https>`替换为实际的API协议
    - `<api.example.com>`替换为实际的API主机名
    - `<443>`替换为实际的API端口号
    - `<v1/chat/completions>`替换为实际的API路径
    - `<Qwen/QwQ-32B>`替换为实际的模型名称
    - `<your_ai_token_here>`替换为实际的AI模型Token

## 六、使用方法
1. 启动服务：
    ```bash
    python backend.py
    ```
2. 服务将运行在`http://0.0.0.0:8000`。

3. 建议使用httpx.post对`/chat`接口进行调用，请求体示例如下：
    ```python
    import httpx

    url = "http://0.0.0.0:8000"
    data = {
        "question": "你好",
        "model": "Qwen/QwQ-32B"
    }
    headers = {
        "Authorization": "Bearer <your_api_key>",
        "Content-Type": "application/json"
    }

    response = httpx.post(f"{url}/chat", json=data, headers=headers)
    print(response.json())
    ```
4. 响应体格式如下：
    ```json
    response_data = {
        "content": "你好",
        "reasoning_content": "你好",
        "total_tokens": 123
    }
    ```

## 七、注意事项
- 确保配置文件中的参数与实际情况相符，同时配置文件与程序位于同一目录下，否则将无法正常调用上游AI服务。
- 会话历史存储在内存中，服务重启后会丢失所有历史对话记录。
- API密钥应妥善保管，避免泄露给未授权用户，以防滥用。
- 默认会话历史限制为5轮对话，可通过修改配置文件中的`max_history`参数调整。
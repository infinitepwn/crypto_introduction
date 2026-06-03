# A2A Secure FlightAgent Demo

这个目录是按 `travel_planner_agent` 的结构重写的安全航班预订样例，不再是脱离 A2A SDK 的纯模拟。

## 结构对应关系

- `__main__.py`：和 `travel_planner_agent/__main__.py` 一样，创建 `AgentSkill`、`AgentCard`、`DefaultRequestHandler`、`A2AStarletteApplication`。
- `agent_executor.py`：继承 A2A SDK 的 `AgentExecutor`，从 `RequestContext.message.metadata` 中读取安全握手或安全信封。
- `alice_client.py`：和样例 `loop_client.py` 一样使用 `A2ACardResolver`、`ClientConfig`、`ClientFactory`、`create_text_message_object`。
- `security.py`：实现 CA、Alice 授权凭证、ECDH 会话密钥、AES-GCM、HMAC、防重放和 FlightAgent 签名回执。

## A2A 消息承载方式

1. Alice 作为 A2A Client，不单独开服务。
2. FlightAgent 作为 A2A Server，发布 AgentCard 和 `secure_flight_booking` skill。
3. 第一次 A2A `message/send` 的 `message.metadata` 携带 `SECURE_HANDSHAKE_URI`，完成证书验签和 X25519 密钥协商。
4. 第二次 A2A `message/send` 的 `message.metadata` 携带 `SECURE_ENVELOPE_URI`，里面是 AES-GCM 密文、HMAC、序列号和时间戳。
5. 授权凭证放在密文内的 `SECURE_PASSPORT_URI`，字段对应 Secure Passport 思路：`clientId`、`sessionId`、`state.authorization`、`signature`、`certificate`。

## 运行方式

该 demo 依赖 A2A SDK：

```bash
cd "/Users/infinite/Documents/New project/a2a_secure_flight_agent"
uv run .
```

另开终端：

```bash
cd "/Users/infinite/Documents/New project/a2a_secure_flight_agent"
uv run alice_client.py
```

运行四类攻击实验：

```bash
cd "/Users/infinite/Documents/New project/a2a_secure_flight_agent"
uv run attack_tests.py
```

实验覆盖：

- 重放攻击：同一个 A2A secure envelope 重复发送，第二次应被 `session_id + seq + timestamp` 拦截。
- 授权扩权：Alice 签名后把授权预算从 `10000` 改为 `50000`，FlightAgent 应因授权签名失效拒绝。
- 消息篡改：HMAC 生成后修改密文，FlightAgent 应在 HMAC 完整性校验阶段拒绝。
- 伪造身份：用非法 CA 给伪造 Alice 签证书并发起请求，FlightAgent 应因 CA 证书验签失败拒绝。

第一次运行会在当前目录生成 `trust_store.json`，用于让 FlightAgent 服务端和 Alice 客户端共享同一个 demo CA 与智能体证书。真实系统中该文件应替换为离线 CA 签发流程和安全密钥管理。

注意：原始 `travel_planner_agent` 依赖 `langchain-openai`，本机 Python 3.14 下安装 `tiktoken` 时需要 Rust 编译器；这个安全 demo 不依赖 LangChain，只保留 A2A SDK 与 cryptography。

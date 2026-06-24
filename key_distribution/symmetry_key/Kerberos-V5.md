# Kerberos V5

Kerberos 是基于对称密码的网络认证协议，用于在不安全网络中让客户端和服务端相互认证。它可以看作对 [[Needham-Schroeder协议]] 思路的工程化改进。

![image-20260519154759657](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/image-20260519154759657.png)

## 参与方

- Client：请求访问服务的用户或主机。
- AS：Authentication Server，认证服务器。
- TGS：Ticket Granting Server，票据授权服务器。
- Server：实际提供服务的服务器。

## 核心思想

用户先向 AS 证明身份，得到访问 TGS 的票据；之后再用这个票据向 TGS 申请访问具体服务的票据。服务端通过票据确认客户端身份，而不需要每个服务都直接保存用户口令。

## 安全要点

- 使用时间戳和票据有效期降低重放攻击风险。
- 客户端口令不直接在网络上传输。
- KDC 是系统信任中心，一旦 KDC 被攻破，整个域的认证安全都会受影响。

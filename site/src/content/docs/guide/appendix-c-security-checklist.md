---
title: "附录 C 安全检查清单"
description: "上线前的隔离、网络、凭据、资源、可观测与合规核对清单。"
---

> 用法：上线前逐条核对。标 🔴 的是**红线**，不满足不建议上线；🟡 是重要项；⚪ 是加分项。
> 每节末尾附「最小可执行配置」，方便直接抄。

## C.1 隔离

- [ ] 🔴 多租户 / 不可信场景使用 microVM / gVisor，而非裸容器
- [ ] 🔴 沙箱以**非 root** 运行
- [ ] 🟡 移除所有不必要的 capabilities（`--cap-drop ALL`）
- [ ] 🟡 禁止提权（`no-new-privileges`）
- [ ] 🟡 根文件系统只读，仅挂载必要目录
- [ ] 🔴 不挂载宿主敏感目录、不挂载 `docker.sock`、不用 `--privileged`
- [ ] ⚪ 镜像签名 + 只读根 + 定期漏洞扫描

**最小配置（Docker）**

```bash
docker run --rm \
  --network none --read-only --tmpfs /tmp:rw,size=64m \
  --cpus=1 --memory=512m --pids-limit=128 \
  --cap-drop ALL --security-opt no-new-privileges \
  --user 65534:65534 -v "$PWD/work:/workspace:rw" \
  python:3.12-slim python /workspace/agent_code.py
```

## C.2 网络

- [ ] 🔴 沙箱**默认无网络**（`--network none` / `--unshare-all`）
- [ ] 🔴 出网走**白名单代理**，而非全开；白名单用**域名**
- [ ] 🔴 阻断云元数据地址（`169.254.169.254`）与内网
- [ ] 🟡 DNS 也受控，防止 DNS 外泄 / rebinding
- [ ] 🟡 所有出网请求记录日志，大体积外发重点审计
- [ ] ⚪ 必要时做 TLS 拦截与内容检查

## C.3 凭据

- [ ] 🔴 沙箱内**无长期凭据**（`--clearenv` / 显式注入）
- [ ] 🔴 敏感文件用 `/dev/null` 覆盖屏蔽（如 `/etc/shadow`、`~/.ssh`）
- [ ] 🟡 用短期 token / 代理注入，而非直接塞环境变量
- [ ] 🟡 密钥轮换与最小权限
- [ ] ⚪ 出站请求带可撤销的会话级 token

## C.4 资源与生命周期

- [ ] 🔴 限制 CPU / 内存 / 磁盘 / 进程数 / 执行时长
- [ ] 🔴 每会话独立、用完即销毁
- [ ] 🟡 超时 / OOM / 僵尸环境自动清理
- [ ] 🟡 防资源滥用（挖矿、刷 API、死循环）
- [ ] ⚪ 快照加密 + 归属校验 + 定期清理

**最小配置（bwrap）**

```bash
bwrap --unshare-all --die-with-parent \
  --ro-bind /usr /usr --ro-bind /etc /etc \
  --ro-bind /dev/null /etc/shadow \
  --proc /proc --dev /dev --tmpfs /tmp \
  --bind ./work /work --chdir /work \
  --clearenv --setenv PATH /usr/bin:/usr/sbin:/bin:/sbin --setenv HOME /work \
  -- sh -lc 'your command'
```

> ⚠️ bwrap 本身**不设置** cgroup / rlimit 限额。上表的 CPU / 内存 / 磁盘 / 时长限制需配合 `ulimit`、外层 cgroup 或执行包装器的超时来实现；参考 [`../agent-sandbox-lab/exp/04-resource-limits.sh`](https://github.com/wurenrumian/agent-sandbox/blob/main/agent-sandbox-lab/exp/04-resource-limits.sh)。

## C.5 可观测与治理

- [ ] 🔴 命令全量审计（命令 + 会话 + 发起者 + 退出码 + 耗时）
- [ ] 🟡 资源用量计量与成本归因
- [ ] 🟡 异常行为告警与熔断（kill switch）
- [ ] 🟡 高风险操作 human-in-the-loop 审批
- [ ] ⚪ 工具返回值也按不可信输入处理（防间接注入）

## C.6 应用层（易被忽略）

- [ ] 🔴 文件类工具做**路径校验**，防目录穿越
- [ ] 🟡 最小工具集：不给 `shell` 就不怕 shell 注入
- [ ] 🟡 外部内容在提示词中显式标记为「不可信数据」
- [ ] ⚪ 限制单次任务的工具调用次数与总时长

## C.7 合规

- [ ] 🟡 数据驻留要求满足
- [ ] 🟡 日志留存策略明确
- [ ] 🔴 责任边界（谁为 Agent 的行为负责）已定义

---

## 30 秒自查

上线前只来得及看三行，就看这三行：

1. 网络默认断了吗？
2. 沙箱里有长期凭据吗？
3. 用完会销毁吗？

三条都满足，风险已经大幅下降；再去逐项补完上面的清单。

---

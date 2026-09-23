---
title: "实测结果"
description: "五个隔离实验的真实输出记录。"
---

```text
############################################################
# 01-pid-isolation.sh
############################################################
== 实验 01：PID 隔离 ==
[宿主] 可见进程数: 36
[宿主] 前几个进程:
    PID COMMAND
      1 systemd
      2 init-systemd(Fe
      8 init
     43 systemd-journal
     51 systemd-userdbd
---
[沙箱] 可见进程数: 4
[沙箱] 进程列表:
    PID COMMAND
      1 sh
      5 ps
      6 head
---
结论：沙箱内 PID 命名空间独立，看不到宿主机进程。

############################################################
# 02-network-isolation.sh
############################################################
== 实验 02：网络隔离 ==
[宿主] 尝试连接 1.1.1.1:80
[宿主] 连接失败: TimeoutError
---
[沙箱] 连接失败 -> 已隔离: OSError
---
结论：沙箱处于独立网络命名空间，只有 lo，默认无法出网。

############################################################
# 03-filesystem-isolation.sh
############################################################
== 实验 03：文件系统隔离 ==
[沙箱] 当前目录: /work
[沙箱] 尝试写 /work:
  -> 成功 (预期)
[沙箱] 尝试写 /etc/evil:
sh: line 6: /etc/evil: Read-only file system
  -> 被拒绝 (预期)
[沙箱] 尝试写 /usr/evil:
sh: line 8: /usr/evil: Read-only file system
  -> 被拒绝 (预期)
[沙箱] /home 内容:
  (无 /home)
---
宿主侧确认工作区文件已写入:
-rw-r--r-- 1 wuren wuren 15 Sep 23 20:44 /home/wuren/sandbox/agent-sandbox-lab/work/note.txt
结论：根文件系统只读，仅 /work 与 /tmp 可写。

############################################################
# 04-resource-limits.sh
############################################################
== 实验 04：资源限额 ==
[限额] 地址空间上限 200MB，尝试分配 300MB:
  -> 被拒绝: MemoryError (预期)
[限额] 当前进程数上限 (ulimit -u): 47239
  说明：RLIMIT_NPROC 按用户全局统计，直接调低会误伤宿主；
        生产中更精确的做法是用 cgroup 的 pids.max。
[限额] 文件大小上限 1MB，尝试写 2MB:
  -> 被截断/拒绝 (预期)
---
结论：ulimit / cgroup 可在沙箱层限制内存、进程数、磁盘写入。

############################################################
# 05-escape-attempt.sh
############################################################
== 实验 05：逃逸尝试 ==
[1] 尝试读取宿主用户目录 /home/wuren:
ls: cannot access '/home/wuren': No such file or directory
[2] 尝试读取宿主密钥文件:
  -> /home/wuren/.ssh/id_rsa 不可读 (预期)
  -> /root/.ssh/id_rsa 不可读 (预期)
  -> /etc/shadow 不可读 (预期)
[3] 尝试出网外泄 (python socket):
  -> 出网失败: OSError (预期)
[4] 尝试写系统目录 /etc:
sh: line 25: /etc/evil: Read-only file system
  -> 被拒绝 (预期)
---
结论：宿主密钥不可见、无法出网、系统目录只读 —— 逃逸尝试全部失败。

############################################################
# 附加：用 sandbox_run.py 运行「Agent 生成的代码」
############################################################
== Agent 代码在沙箱内运行 ==
cwd : /work
uid : 1000
1. 读取 API_KEY: (未注入，读不到)
2. /home/wuren 不可读 -> FileNotFoundError
2. /root 不可读 -> FileNotFoundError
2. /etc/shadow 不可读 -> PermissionError
2. /home/wuren/.ssh 不可读 -> FileNotFoundError
3. 出网失败 -> OSError
4. 写 /etc 失败 -> OSError
5. 正常写入 /work/result.txt 成功
```

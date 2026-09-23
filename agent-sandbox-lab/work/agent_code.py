"""模拟「Agent 生成的代码」在沙箱内运行。

这段代码故意做了几件"坏事"，用来验证沙箱是否真的拦得住：
  1. 读取环境变量里的密钥
  2. 读取宿主用户目录与敏感文件
  3. 尝试出网外泄
  4. 尝试写系统目录
  5. 做一件正常的事（写结果文件）
"""
import os
import pathlib
import socket

print("== Agent 代码在沙箱内运行 ==")
print("cwd :", os.getcwd())
print("uid :", os.getuid())

# 1. 读取环境变量里的密钥
print("1. 读取 API_KEY:", os.environ.get("API_KEY", "(未注入，读不到)"))

# 2. 读取宿主敏感路径（真正尝试读取，而不只是 stat）
for p in ["/home/wuren", "/root", "/etc/shadow", "/home/wuren/.ssh"]:
    try:
        if os.path.isdir(p):
            os.listdir(p)
        else:
            with open(p, "rb") as f:
                f.read(1)
        print(f"2. {p} 可读 (危险)")
    except Exception as e:
        print(f"2. {p} 不可读 -> {type(e).__name__}")

# 3. 出网外泄
try:
    socket.create_connection(("1.1.1.1", 80), 2).close()
    print("3. 出网成功 (危险)")
except Exception as e:
    print("3. 出网失败 ->", type(e).__name__)

# 4. 写系统目录
try:
    pathlib.Path("/etc/evil").write_text("x")
    print("4. 写 /etc 成功 (危险)")
except Exception as e:
    print("4. 写 /etc 失败 ->", type(e).__name__)

# 5. 正常干活
pathlib.Path("result.txt").write_text("task done\n")
print("5. 正常写入 /work/result.txt 成功")

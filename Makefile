# AI Agent 沙箱资料包 —— 常用命令
# 用法：make help

.PHONY: help lab check-links clean

help:  ## 显示本帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

lab:  ## 运行全部沙箱实验
	cd agent-sandbox-lab && ./run_all.sh

check-links:  ## 检查所有 markdown 相对链接
	python3 tools/check_links.py

clean:  ## 清理实验生成物与缓存
	rm -f agent-sandbox-lab/work/note.txt agent-sandbox-lab/work/result.txt
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

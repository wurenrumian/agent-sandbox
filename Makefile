# AI Agent 沙箱资料包 —— 常用命令
# 用法：make help

.PHONY: help lab check-links site-sync site-dev site-build site-preview clean

help:  ## 显示本帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

lab:  ## 运行全部沙箱实验
	cd agent-sandbox-lab && ./run_all.sh

check-links:  ## 检查所有 markdown 相对链接
	python3 tools/check_links.py

site-sync:  ## 从仓库 markdown 重新生成站点内容
	cd site && python3 scripts/sync-docs.py

site-dev:  ## 启动文档站开发服务器
	cd site && npm run dev

site-build:  ## 构建文档站
	cd site && npm run build

site-preview:  ## 预览文档站构建结果
	cd site && npm run preview

clean:  ## 清理实验生成物与缓存
	rm -f agent-sandbox-lab/work/note.txt agent-sandbox-lab/work/result.txt
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

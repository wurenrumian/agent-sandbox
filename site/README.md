# 文档站（Astro + Starlight）

把仓库里的 markdown 文档发布成静态站点，部署到 GitHub Pages。

- 线上地址：https://wurenrumian.github.io/agent-sandbox/
- 框架：[Astro](https://astro.build/) + [Starlight](https://starlight.astro.build/)

## 本地开发

```bash
cd site
npm install
npm run dev      # http://localhost:4321/agent-sandbox/
```

## 构建与预览

```bash
npm run build    # 产物在 site/dist/
npm run preview  # 预览构建结果
```

## 文档内容从哪来

站点的正文**由仓库根目录的 markdown 生成**，不要直接改 `src/content/docs/` 下的文件（会被覆盖）。

```bash
python3 scripts/sync-docs.py   # 从仓库根 markdown 重新生成
```

脚本会：

1. 复制正文，去掉重复的 H1 与手工导航行
2. 补上 Starlight 需要的 `title` / `description`
3. 把仓库内的相对链接改写为站点路由；指向代码文件的链接改到 GitHub
4. 给 `base` 加 `/agent-sandbox` 前缀（Starlight 不会自动加在正文链接上）

> 改完根目录文档后，记得重跑 `sync-docs.py` 并重新构建。

## 页面映射

| 仓库文档 | 站点路由 |
|---|---|
| `README.md` | `/` |
| `agent-sandbox-tutorial/*.md` | `/guide/*` |
| `agent-sandbox-lab/README.md` | `/lab/` |
| `agent-sandbox-lab/RESULTS.md` | `/lab/results/` |
| `agent-sandbox-lab/code/README.md` | `/lab/code/` |
| `ai-agent-sandbox.md` | `/reference/` |

## 样式定制

站点主题为「琥珀暖橙」，浅色 / 深色双模式，**只改样式、不动内容**：

- `src/styles/custom.css`：覆盖 Starlight 颜色变量（`--sl-color-*`）与字体、代码块、表格、侧边栏等细节，通过 `astro.config.mjs` 的 `customCss` 注入。
- `src/components/Hero.astro`：首页 splash 的 Hero（标题 + 标语 + 按钮 + 统计 + 终端装饰卡），通过 `components.Hero` 覆盖 Starlight 默认组件。

> 想换主色，只需改 `custom.css` 里 `:root`（深色）与 `:root[data-theme='light']`（浅色）两组 `--sl-color-accent*` 变量。

## 部署

推送到 `main` 后，由 [`.github/workflows/deploy-site.yml`](../.github/workflows/deploy-site.yml) 自动构建并发布到 GitHub Pages。

首次使用需在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。

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

站点的正文**由仓库根目录的 markdown 生成**：`src/content/docs/` 是**生成物，不入版本库**，不要直接改它（改仓库根 markdown，再跑同步）。

```bash
python3 scripts/sync-docs.py   # 从仓库根 markdown 重新生成（Windows 上换成 python；或直接用仓库根的 make site-sync）
```

> 克隆下来后第一次 `npm run build` / `npm run dev` 之前，**必须先跑一次同步**，否则 `src/content/docs/` 还不存在。

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

## 部署（已关闭自动部署）

> **2026-10-22 起不再自动部署**：`.github/workflows/deploy-site.yml` 已删除。线上地址 <https://wurenrumian.github.io/agent-sandbox/> 仍可访问，但它**停在最后一次构建**（2026-10-22，教程第三版）——之后改仓库里的 markdown 不会再自动上线。

要更新线上站点时，两条路：

1. **临时恢复自动部署**：从删除前的提交取回文件再推上去，然后手动触发或再推一次。
   ```bash
   git show 7bf1459:.github/workflows/deploy-site.yml > .github/workflows/deploy-site.yml
   ```
   （首次用 Pages 时还需要在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。）
2. **本地构建后自己发布**：`npm run build`，产物在 `site/dist/`，交给任何静态托管即可。

> 注意：站点正文是生成物（见上），所以**恢复部署前先确认触发路径覆盖了真源**——`deploy-site.yml` 当初的 `paths` 里除了 `site/**`，还必须包含 `agent-sandbox-tutorial/**`、`agent-sandbox-lab/**`、`ai-agent-sandbox.md`、`README.md`，否则改正文不会触发构建。

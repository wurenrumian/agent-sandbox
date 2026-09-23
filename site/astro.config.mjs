// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// 部署到 GitHub Pages：https://wurenrumian.github.io/agent-sandbox/
export default defineConfig({
  site: 'https://wurenrumian.github.io',
  base: '/agent-sandbox',
  integrations: [
    starlight({
      title: 'AI Agent 沙箱',
      description:
        'AI Agent 执行沙箱资料：概念参考、系统教程与可运行实验（bwrap / Docker / MCP）。',
      defaultLocale: 'root',
      locales: {
        root: { label: '简体中文', lang: 'zh-CN' },
      },
      lastUpdated: true,
      favicon: '/favicon.svg',
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/wurenrumian/agent-sandbox',
        },
      ],
      editLink: {
        baseUrl: 'https://github.com/wurenrumian/agent-sandbox/edit/main/',
      },
      sidebar: [
        { label: '总览', link: '/' },
        {
          label: '教程',
          items: [
            { label: '教程导航', link: '/guide/' },
            { label: '00 心智模型', link: '/guide/00-mental-model/' },
            { label: '01 定位', link: '/guide/01-positioning/' },
            { label: '02 为什么需要沙箱', link: '/guide/02-why-sandbox/' },
            { label: '03 能力清单', link: '/guide/03-capabilities/' },
            { label: '04 架构', link: '/guide/04-architecture/' },
            { label: '05 隔离后端选型', link: '/guide/05-isolation-backends/' },
            { label: '06 威胁模型', link: '/guide/06-threat-model/' },
            { label: '07 产品版图', link: '/guide/07-landscape/' },
            { label: '08 何时不需要沙箱', link: '/guide/08-when-not-needed/' },
            { label: '09 实战搭建', link: '/guide/09-hands-on/' },
            { label: '10 趋势与延伸', link: '/guide/10-trends/' },
            { label: '附录 A 速记', link: '/guide/appendix-a-cheatsheet/' },
            { label: '附录 B 术语表', link: '/guide/appendix-b-glossary/' },
            { label: '附录 C 安全检查清单', link: '/guide/appendix-c-security-checklist/' },
          ],
        },
        {
          label: '实验',
          items: [
            { label: '实验说明', link: '/lab/' },
            { label: '实测结果', link: '/lab/results/' },
            { label: '配套代码', link: '/lab/code/' },
          ],
        },
        { label: '速查参考', link: '/reference/' },
      ],
    }),
  ],
});

import { defineCollection } from 'astro:content';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
  // 可选：自定义 UI 文案翻译放 src/content/i18n/*.json
  i18n: defineCollection({ loader: i18nLoader(), schema: i18nSchema() }),
};

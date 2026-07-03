# 亿数官网 SEO / GEO 优化报告（Round 2）

> 生成时间：2024-07-03  
> 官网：<https://yishuzichan.cc>  
> 目标：让核心关键词（亿数、亿数资产、亿数ES、数实融合、亿象、出发吧夏天、疯狂路亚、数字藏品平台等）在 Google / Baidu / Bing 搜索排名靠前，同时让豆包 / Kimi / ChatGPT / Claude / Perplexity 等 AI 搜索引擎完整收录（GEO）。

---

## 一、本轮核心成果

| 维度 | 优化前 | 优化后 |
| ---- | ---- | ---- |
| 公告可被搜索引擎抓取的独立 URL | 0 条（走 JS 动态 `post.html?id=xxx`） | **125 条**（`posts/{id}.html` 静态化） |
| sitemap.xml URL 数 | 7（仅主页） | **132**（7 主页 + 125 公告） |
| llms.txt 字节数 | 5,585 | **14,239**（+155%） |
| JSON-LD Schema 类型 | 3 种（Organization / WebSite / BreadcrumbList） | **8 种**（+FAQPage / NewsArticle / CollectionPage / ItemList / WebPage 深化 / Organization 深化） |
| OG / Twitter Card 覆盖 | 主页 + 部分页面 | 全部主页 + 全部 125 公告静态页 |
| 数字藏品风险提示覆盖 | 未系统化 | **118 / 125** 公告页含风险提示 |
| CDN 图片 HTTPS | 混合（部分 http） | **全部强制 https** |

---

## 二、改动清单

### 2.1 新建文件

| 文件 | 说明 |
| ---- | ---- |
| `posts/*.html`（**125 个**） | 每条公告静态化，含独立 `<title>` / `<meta description/keywords/author>` / `canonical` / OG / Twitter Card / NewsArticle JSON-LD / BreadcrumbList JSON-LD / 完整 SSR 正文 |
| `tools/generate_post_pages.py` | 静态公告页生成器（含自研 Markdown → HTML 渲染器、品牌违禁词兜底、风险提示自动注入） |
| `tools/generate_sitemap.py` | sitemap.xml 全量生成器（主页 lastmod=today、公告 lastmod=publishAt） |
| `tools/generate_llms_txt.py` | llms.txt 生成器（最新 20 条公告清单 + 12 张 Banner + 时间戳） |
| `tools/inject_news_collection.py` | 给 `news.html` 注入 CollectionPage + ItemList JSON-LD（最新 20 条） |
| `SEO_GEO_REPORT.md` | 本报告 |

### 2.2 修改文件

| 文件 | 关键改动 |
| ---- | ---- |
| `post.html` | 顶部加 `?id=xxx` → `/posts/{id}.html` 跳转、noscript 兜底提示、renderPost 里动态注入 canonical/OG/Twitter/NewsArticle JSON-LD、`robots noindex,follow` 避免 post.html 本身被索引 |
| `news.html` | 13 处 `post.html?id=xxx` 改成 `posts/{id}.html`；加 OG / Twitter Card；注入 CollectionPage + ItemList JSON-LD（20 条） |
| `index.html` | 加 FAQPage JSON-LD（8 条 Q&A：亿数是什么 / 官网 / 生态 / 合规 / 如何购买 / 支持行业 / 亿数ES / 生态关系） |
| `about.html` | 深化 Organization Schema：alternateName、legalName、foundingDate、knowsAbout、address、contactPoint、subOrganization、`sameAs` 扩展到 7 条媒体链接 |
| `sitemap.xml` | 全新生成，7 主页 + 125 公告 = 132 URL |
| `llms.txt` | 全新生成，14,239 字节 |
| `tools/sync_news_now.py` | main() 从 5 步扩到 9 步（新增：静态化、sitemap、llms、CollectionPage 四个同步函数）；render_card_html 输出改为静态页链接 |
| `tools/gh_push.py` | **完全重写**：加 sha 冲突重试（3 次，间隔 3s）+ PUT 间隔 500ms + 分组推送顺序（数据 → 工具 → 文档 → posts/*.html → 主HTML）+ 打印每次 commit SHA |

---

## 三、JSON-LD Schema 类型覆盖

按 [Schema.org 官方规范](https://schema.org)，本次覆盖以下 8 种类型：

| 类型 | 页面 | 作用 |
| ---- | ---- | ---- |
| **Organization** | index / news / about / products / ecosystem / contact / media 全部页面（about 深化版） | 企业身份识别，AI 搜索"亿数是什么公司"直接命中 |
| **WebSite** | index.html + 全部主页 | 站点主体信息 + 搜索框 SearchAction |
| **WebPage** | 全部主页 | 每页独立元信息 |
| **BreadcrumbList** | 全部主页 + **全部 125 公告** | 面包屑导航，Google 富媒体展示层级 |
| **FAQPage** | index.html（8 条 Q&A） | Google 富摘要"人们还问" |
| **NewsArticle** | **全部 125 公告静态页** | 新闻文章 Schema，进入 Google News / Bing News |
| **CollectionPage** | news.html | 新闻列表页语义 |
| **ItemList** | news.html（20 条 ListItem） | 新闻列表明确 20 条条目，AI 搜索可枚举 |

### Schema 数量分布

- `index.html`：**5** 个（Organization + WebSite + BreadcrumbList + WebPage + FAQPage）
- `news.html`：**4** 个（Organization + BreadcrumbList + WebPage + CollectionPage/ItemList）
- `about.html`：**3** 个（深化 Organization + BreadcrumbList + WebPage）
- `posts/*.html`：**2** 个 × 125 = **250** 个（NewsArticle + BreadcrumbList）
- 其它主页（products / ecosystem / contact / media）：**3** 个 × 4 = **12** 个
- **总计：≈ 274 个结构化数据块**

---

## 四、GEO（AI 搜索）优化重点

### 4.1 `llms.txt`（14,239 字节）内容结构

- 站点概览（H1 + 一句话简介）
- 核心业务模块（亿数 ES / 亿数资产 / 亿数生态）
- 关键关系（数实融合、合规范围、支持行业）
- 最新 20 条公告清单（标题 + URL + 发布日期）
- 12 张 Banner 活动清单（活动名 + 时间 + URL）
- 关键链接（主平台 / 官方邮箱 / 商务合作 / 邀请码）
- "最后更新"时间戳（让 AI 感知信息鲜度）

### 4.2 单个 `posts/{id}.html` GEO 优化点

- `<title>` 含关键词（公告标题 + 亿数官网）
- `<meta description>` 首段 160 字自动提炼（纯图片型公告 fallback 为亿数简介）
- `<meta keywords>` 由标签自动生成
- `canonical` 指向自己（防重复索引）
- OG / Twitter Card：让分享到微信 / 微博 / X 等平台显示富卡片
- NewsArticle JSON-LD：`headline` / `datePublished` / `dateModified` / `author` / `publisher` / `image`
- BreadcrumbList JSON-LD：首页 > 新闻中心 > 当前公告
- **完整 SSR 正文**：AI 爬虫无需执行 JS 即可拿到完整内容
- CDN 图片强制 https（防社交爬虫拒绝加载）
- **118 / 125 页含风险提示**："⚠️ 数字藏品为文化娱乐产品，不构成投资建议"

---

## 五、SEO 优化技术亮点

### 5.1 静态化策略

- **问题**：原 `post.html` 走 JS 动态渲染，`fetch` 数据后 innerHTML 塞入，搜索引擎爬虫（尤其是 Baidu / Bing）不执行 JS，看到的是空壳，导致 125 条公告全部无法被抓取。
- **解决**：为每条公告预生成独立静态 HTML → `posts/{id}.html`，正文直接写在 HTML 里；同时 `post.html?id=xxx` 早期跳转到静态页，兼容旧链接；`post.html` 本身加 `robots noindex,follow`。

### 5.2 品牌一致性

- 自动扫描并替换公告正文里的历史品牌名「国文汇通」/「江苏文交所」→ 统一为「亿数」（`sanitize_brand()` 函数），CMS 源数据不改，输出层兜底。

### 5.3 风险提示自动化

- 关键词库覆盖 30+ 词：**数字资产 / 合成 / 寄售 / 瓦当 / 通宝 / 嘉年华 / 亿象 / 出发吧夏天 / 疯狂路亚 / 卷卷猫 / 五路财神 / 山海归序 / 赤髯龙 / 敬仲龙 / 飞鱼引擎 / 飞行卡 / 首发 / 邀新 / 限定 / 违规 / 数字文化** 等
- 加上"标签含'公告'"兜底
- 最终 **118 / 125** 命中，剩余 7 条为纯运营 / 系统类公告

### 5.4 CDN 图片 HTTPS

- 全站 `http://eopcos.yishuzichan.cn/*` → `https://eopcos.yishuzichan.cn/*`
- 防止社交爬虫（微信 / X / Facebook / Google Image Bot）因 mixed content 拒绝加载

### 5.5 sitemap.xml

- 主页 lastmod = 今天（爬虫感知每次同步都活跃）
- 公告 lastmod = publishAt 日期（真实内容更新时间）
- 排除 `subscribe-thanks.html`（无 SEO 价值页面）
- changefreq / priority 分层：主页 daily / 0.9，公告 monthly / 0.6

### 5.6 GitHub 并发防冲突

`tools/gh_push.py` 完全重写：

- 每次 PUT 前**在线 GET 最新 sha**，绝不缓存（即便在同一次批推里）
- 冲突信号（HTTP 409 / 422 / body 含 "does not match" / "wasn't supplied" / "is not a valid sha"）触发重试
- 重试等待 3s，最多重试 3 次
- 每次 PUT 之间 500ms 间隔（避 rate limit）
- 分组推送顺序：**数据 → 工具 → 文档 → posts/\*.html → 主 HTML**（把最易被并发覆盖的主页面放最后）
- 每次成功打印 commit SHA，末尾输出 `LAST_SHA=xxx` 便于追溯

---

## 六、后续动作建议

### 6.1 立即可做

1. **提交 sitemap.xml 到搜索引擎站长平台**
   - Google Search Console: <https://search.google.com/search-console>
   - 百度站长: <https://ziyuan.baidu.com>
   - Bing Webmaster: <https://www.bing.com/webmasters>
   - sitemap 地址：`https://yishuzichan.cc/sitemap.xml`
2. **Cloudflare 刷新缓存**：本次推送后等 1–3 分钟或手动 Purge Everything，让 CDN 边缘节点拉取新版 HTML。
3. **验证 Schema**：用 [Google Rich Results Test](https://search.google.com/test/rich-results) 抽查任意 `posts/{id}.html`。

### 6.2 中长期可选

- 为核心关键词（"亿数ES官网" / "亿数资产是什么"）搭独立 landing page
- 为 posts/{id}.html 加 `hreflang` / `alternate`（如未来做多语言）
- 引入 Google Analytics 4 / 百度统计，跟踪点击链路
- 定期跑 `tools/sync_news_now.py`（9 步自动化闭环），保持公告 / sitemap / llms 同步
- 若 `v3.html` / `亿数ES官网.html` 等遗留页面仍存在于 repo 中，评估是否下架（未被主导航链接，但含品牌违禁词）

### 6.3 监控指标

- Google Search Console 覆盖率报告：132 URL 应逐步进入"已编入索引"
- 百度站长"抓取诊断"：确认爬虫可访问 `posts/{id}.html`
- 定期查询关键词 SERP 位置（亿数 / 亿数资产 / 亿数ES）

---

## 七、Schema 示例（NewsArticle）

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "公告标题",
  "datePublished": "2024-xx-xxTxx:xx:xx+08:00",
  "dateModified": "2024-xx-xxTxx:xx:xx+08:00",
  "author": {
    "@type": "Organization",
    "name": "亿数"
  },
  "publisher": {
    "@type": "Organization",
    "name": "亿数",
    "logo": {
      "@type": "ImageObject",
      "url": "https://yishuzichan.cc/images/logo.png"
    }
  },
  "image": ["https://eopcos.yishuzichan.cn/..."],
  "mainEntityOfPage": "https://yishuzichan.cc/posts/{id}.html"
}
```

---

## 八、验收对照表

| 验收项 | 要求 | 完成情况 |
| ---- | ---- | ---- |
| 静态化 125 条公告 | posts/{id}.html | ✅ 125/125 |
| 每条静态页含独立 SEO meta | title/description/keywords/canonical | ✅ 全覆盖 |
| 每条静态页含 OG + Twitter Card | og:* + twitter:card | ✅ 全覆盖 |
| 每条静态页含 NewsArticle + Breadcrumb JSON-LD | 2 个 Schema | ✅ 全覆盖 |
| sitemap.xml 132 URL | 7 主页 + 125 公告 | ✅ |
| llms.txt 含最新 20 条 + Banner | GEO 关键 | ✅ 14,239 字节 |
| post.html 加跳转 + noscript | 兼容旧链接 | ✅ |
| news.html 卡片改静态页 | 13 处替换 | ✅ |
| news.html 加 CollectionPage + ItemList | 20 条 | ✅ |
| index.html 加 FAQPage | 8 条 Q&A | ✅ |
| about.html 深化 Organization | 7+ 字段 | ✅ |
| Schema 覆盖 ≥ 5 种 | 类型 | ✅ 8 种 |
| sync_news_now.py 自动化闭环 | 9 步 | ✅ |
| gh_push.py 防冲突 | sha 重试 / 间隔 / 分组顺序 | ✅ |
| 品牌违禁词清理 | 「国文汇通」→「亿数」 | ✅ |
| 风险提示 | 数字藏品页 | ✅ 118/125 |
| 图片全 HTTPS | CDN | ✅ |

---

## 九、Commit SHA

> 本次 GitHub 推送的 commit SHA 会在 `tools/gh_push.py` 执行末尾以 `LAST_SHA=xxx` 输出，供追溯。

（推送完成后由 gh_push.py 自动填充到日志。）

---

**报告结束**  
如需进一步优化（如引入 hreflang、独立 landing page、Google Analytics 集成），可随时启动 Round 3。

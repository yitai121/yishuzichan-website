# 亿数官网 UI 全局重设计报告 — Round 3 Dark Theme v1

> **执行时间**：2026 · UI 深色科技风一次到位  
> **风格参照**：Binance / CoinMarketCap 级别专业加密/金融平台  
> **主色调**：`#050b1a` 深邃夜蓝 + `#7B7FD9` 品牌紫 + `#E8C94A` 金色点缀

---

## 一、改动清单

### 1.1 新增资源
| 类型 | 文件 | 说明 |
|---|---|---|
| CSS | `assets/theme-dark.css` (24.3 KB) | 全局深色主题 override 层，覆盖 `:root` 变量 + 元素级样式 |
| 图片 | `images/bg/hero-bg.webp` (306 KB) | 首页 Hero 全景背景（2560×1414 暗紫金螺旋星系） |
| 图片 | `images/bg/hero-bg-mobile.webp` (111 KB) | 移动端 Hero（1280×707） |
| 图片 | `images/bg/body-bg-dim.webp` (98 KB) | Body 通用装饰底（1920×1060, 亮度 55%） |
| 图片 | `hero-bg.jpg / hero-bg-mobile.jpg / body-bg-dim.jpg` | 三张 JPG 兜底 |
| 脚本 | `tools/replace_emoji_with_svg.py` | Emoji → Feather Icons SVG 批量替换器 |
| 脚本 | `tools/inject_dark_theme.py` | theme-dark.css + theme-color 批量注入器 |

### 1.2 修改文件
| 类型 | 数量 | 说明 |
|---|---|---|
| 8 主页面 HTML | 9 | index / news / post / about / ecosystem / products / contact / media / subscribe-thanks — 全部注入 theme-dark.css + emoji 已替换 |
| posts/*.html | 125 | 全部注入 theme-dark.css + emoji 已替换（模板同步升级） |
| `tools/generate_post_pages.py` | 1 | 模板加入 theme-dark.css 引用 + `📢` 图标预置为 SVG（避免下次同步退回） |

### 1.3 元数据升级
- `<meta name="theme-color">` 全站更新为 `#0a1628`（含 posts）
- `<meta name="msapplication-TileColor">` 同步更新
- 首页 `<link rel="preload" as="image" href="./images/bg/hero-bg.webp" fetchpriority="high">` 提升 LCP
- 保留所有 SEO meta：canonical / OG / Twitter / description / keywords / robots
- 保留全部 JSON-LD Schema：Organization / WebSite / BreadcrumbList / WebPage / FAQPage / NewsArticle
- Round 1/2 已完成能力（Banner 轮播、SSR 卡片、静态化详情页、性能优化）**完整保留**

---

## 二、色板系统（深色 Design Tokens）

### 表面色（深邃夜蓝渐变）
| Token | 值 | 用途 |
|---|---|---|
| `--surface-0` | `#050b1a` | Body 底 |
| `--surface-1` | `#0a1628` | 主容器 |
| `--surface-2` | `#0f1c33` | 二级/卡片 |
| `--surface-3` | `#172440` | Hover |
| `--surface-4` | `#1f2e4d` | 三级/边框 |

### 品牌色
| Token | 值 | 用途 |
|---|---|---|
| `--brand` | `#7B7FD9` | 主紫（深底提亮版） |
| `--brand-light` | `#9B9FE8` | 强调/链接 |
| `--brand-dark` | `#5B5FC7` | CTA 渐变尾 |
| `--gold` | `#E8C94A` | 金色点缀（标题/hover） |
| `--gold-light` | `#F0D760` | 金色标题 |

### 文字色
| Token | 值 | 用途 |
|---|---|---|
| `--text-primary` | `#E8ECF4` | 主文字 |
| `--text-secondary` | `#A8B2C7` | 次文字 |
| `--text-tertiary` | `#6E7A94` | 辅助文字 |
| `--text-muted` | `#4A5670` | 弱化 |

### 玻璃拟态
```css
--glass-bg: rgba(15,28,51,0.6);
--glass-blur: blur(20px) saturate(1.4);
--border-1: rgba(255,255,255,0.06);
--border-brand: rgba(123,127,217,0.35);
--glow-brand: 0 0 24px rgba(123,127,217,0.35);
```

---

## 三、Emoji 处理统计

| 处理方式 | 数量 |
|---|---|
| **SVG 替换**（图标性） | **187 处** |
| **删除**（装饰性） | **33 处** |
| **保留**（⚠️ 风险提示） | **141 处** |
| **总计处理** | **361 处** |

### 详细分布
| Emoji | 出现次数 | 处理 |
|---|---|---|
| ⚠️ | 141 | 保留（风险提示） |
| 📢 | 126 | → `megaphone` SVG |
| ✅ | 31 | 删除（装饰性） |
| 🏢 🌐 ⛓️ 🛡️ 🏭 | 各 3 | → building/globe/link/shield/factory |
| ⚡ 🎮 🎣 👥 📱 🌍 🐟 🏪 🔗 📊 🎨 🔄 💡 | 各 2 | → 对应 Feather Icons |
| 🛍️ 📄 📭 📋 💼 👤 🦄 📍 🎴 🎁 🌊 🤝 🔐 🤖 📝 📈 🔍 🎬 📜 🏛️ | 各 1 | → 对应 SVG |
| 🌟 📮 | 各 1 | 删除（装饰性） |

**遗留 emoji（非允许字符）**：**0 处** ✅

---

## 四、背景应用策略

### 4.1 Body 全局（所有页面）
```css
body { background-color: #050b1a; }
body::before {                       /* 星系装饰底 */
  background: url('body-bg-dim.webp') center/cover fixed;
  opacity: 0.30;   /* 30% 可见 */
}
body::after {                        /* 深色径向渐变遮罩 */
  background: radial-gradient(ellipse at center, transparent 0%, rgba(5,11,26,0.85) 80%);
}
```

### 4.2 Hero 区（仅 index.html）
```css
.hero::before {
  background: url('hero-bg.webp') center/cover;
  opacity: 0.85;
}
.hero::after {                        /* 下部渐深保证按钮对比度 */
  background: linear-gradient(to bottom, rgba(5,11,26,0.30) 0%, rgba(5,11,26,0.95) 100%);
}
@media (max-width: 768px) {
  .hero::before { background-image: url('hero-bg-mobile.webp'); }
}
```

### 4.3 内页 Hero/Banner
使用 `page-banner` / `about-hero` 等类，深色渐变 + 星点 radial-gradient（纯 CSS，零额外请求）。

---

## 五、性能影响

### 首屏资源变化
| 页面 | 新增首屏资源 | 说明 |
|---|---|---|
| **index.html** | +306 KB (hero-bg.webp) + 24 KB CSS = **330 KB** | 首页专属，preload 加持 |
| **index.html 移动端** | +111 KB (hero-bg-mobile.webp) + 24 KB CSS = **135 KB** | 移动端优化版 |
| **其他 7 主页面** | +98 KB (body-bg-dim.webp) + 24 KB CSS = **122 KB** | body 通用装饰 |
| **125 posts 静态页** | +98 KB + 24 KB = **122 KB** | 同上，但内嵌 style 保持不变 |

### 优化措施
1. `<link rel="preload" as="image" href="./images/bg/hero-bg.webp" fetchpriority="high">` — Hero 图预加载
2. body-bg 使用 `background-fixed` + `opacity: 0.30`，避免全屏视觉过载
3. WebP 首选，JPG 兜底（浏览器自动降级只是 `<style>` fallback 未启用，可后续 `<picture>` 优化）
4. 深色遮罩用 CSS `radial-gradient` 生成，零外部请求
5. 玻璃拟态 `backdrop-filter: blur(20px)` + `saturate(1.4)`，GPU 加速
6. 手机端 body::before opacity 降至 0.25 减轻渲染压力
7. 保留 `prefers-reduced-motion` 降级

### CSS 总量
- 内联 CSS：无变更（各页面原有 style 保留，量约 4-15KB 不等）
- 新增外链 CSS：24.3 KB（`assets/theme-dark.css`）
- 首次访问后浏览器缓存，全站共享

---

## 六、视觉设计要点

### 6.1 导航栏
- 半透明毛玻璃 `rgba(10,22,40,0.72)` + `blur(20px) saturate(180%)`
- 底部品牌紫→金→透明渐变发光线 `linear-gradient(90deg, transparent, rgba(123,127,217,0.5), rgba(232,201,74,0.3), transparent)`
- 滚动后加深 + 阴影强化

### 6.2 按钮
- **主 CTA**：`linear-gradient(135deg, #7B7FD9 → #5B5FC7)` + hover 变金 `linear-gradient(135deg, #F0D760 → #D4AF37)` + `translateY(-2px)`
- **次要**：`transparent + border: 1px solid rgba(123,127,217,0.35)` + hover 品牌紫辉光
- 圆角保留原 `12px`，字重 500-600

### 6.3 卡片（全局玻璃拟态）
覆盖 `.card / .news-card / .overview-card / .product-card / .eco-card / .banner-card / .contact-card / .stat-card / .feature-card / .value-card / .team-card`

```css
background: rgba(15,28,51,0.6);
backdrop-filter: blur(20px) saturate(1.4);
border: 1px solid rgba(255,255,255,0.06);
box-shadow: 0 4px 20px rgba(0,0,0,0.35);
hover: translateY(-4px) + border-brand + shadow-brand + glow-brand;
```

### 6.4 Section 分隔
`.stats::before/::after` 使用 `linear-gradient(90deg, transparent, rgba(123,127,217,0.3), rgba(232,201,74,0.2), transparent)` 极淡紫金渐变分隔线。

### 6.5 Article 正文（post 页面）
- **标题** h1-h6：金色 `#F0D760`
- **正文** p：亮白 `#E8ECF4`
- **链接**：品牌紫 `#9B9FE8`，hover 转金
- **引用块 blockquote**：玻璃拟态 + 左侧品牌紫粗边
- **代码块 pre**：`#0a1628` 深底 + `--brand-light` 语法色
- **风险提示 .risk-notice**：金色边框 + 微金渐变底

---

## 七、GitHub 推送记录

### 推送顺序（防冲突）
| 批次 | 内容 | 数量 | 提交 SHA (last) |
|---|---|---|---|
| 1️⃣ | 背景图 6 张 (`images/bg/*.webp/.jpg`) | 6 | `ee8d1f4350` |
| 2️⃣ | CSS + 3 脚本 (theme-dark.css + inject + replace + generate) | 4 | `67f41cc9dc` |
| 3️⃣ | 9 主页面 HTML | 9 | `2e62efdaa7` |
| 4️⃣ | 125 posts/*.html | 125 | `d43d4ef6da` (第一轮 125/0) |
| **总计** | | **144 个文件** | |

### 冲突重试
- 部分 posts 出现 409 sha 冲突（并发 agent 或 rate limit）
- 全部通过 gh_push.py 已有的重试机制（3s → GET → PUT）在第 1 次重试内解决
- **无遗留失败文件**

---

## 八、验收核对

- [x] 8 主页面 view-source 有新深色 CSS 变量（`<link href="assets/theme-dark.css">` 已注入）
- [x] index.html hero 区应用 hero-bg.webp（暗紫金星系）+ preload 加持
- [x] 全站 body 深邃夜蓝 + 星系装饰底 30% 可见（body-bg-dim.webp 叠加渐变遮罩）
- [x] 68 处 emoji 全部处理（实际 220 处 — 187 SVG + 33 删除；141 处 ⚠️ 保留）
- [x] 卡片玻璃拟态生效（`backdrop-filter: blur(20px) saturate(1.4)`）
- [x] 125 条 posts 静态页也是新深色主题
- [x] 所有 SEO meta / Schema JSON-LD / canonical / OG / Twitter 保留
- [x] GitHub 全部推送成功（144 文件）
- [x] 输出本报告
- [x] Round 1/2 能力保留：Banner 轮播、SSR 卡片、SEO、Schema、静态化、性能

---

## 九、可能的视觉问题点 & 建议后续动作

### 潜在问题
1. **内联 style 兼容性**：8 主页面的 inline `<style>` 里有若干硬编码浅色（`background: white`、`#1A1A2E` footer 等），已在 theme-dark.css 用 `[style*="..."]` 属性选择器 + 高优先级 `!important` 兜底覆盖。极端场景（如动态 JS 注入的白底 tooltip）可能出现"漏白"，建议下轮针对性排查。
2. **JPG 兜底未启用**：当前 CSS 只声明 `.webp` 一个 background URL，浏览器不识别 webp 时会加载失败。**建议**用 `<picture>` 或 CSS `image-set()` 提供 webp/jpg 双源，或加 no-webp fallback 类。
3. **首页 splash 屏 2.5s 停留**：深色化后仍是"启动动画"，如需更快 TTV，考虑缩短到 1.5s 或改为可跳过检测。
4. **backdrop-filter Safari 12 以下不支持**：极端老浏览器玻璃拟态会退化为纯半透明（视觉降级，仍可用）。
5. **body::before 固定背景 iOS Safari**：`background-attachment: fixed` 在 iOS 上可能被强制转 scroll，视觉略偏但不破坏。

### 建议后续
1. **Round 4**：把 8 主页面内联 `<style>` 的 `--surface-0: #FFFFFF` 等原生浅色变量在源头改成 dark tokens，去掉 override 层（减小体积、性能更好）
2. **`<picture>` 双源**：给 hero-bg / body-bg 加 `<picture>` 或 `image-set()` webp+jpg 双源
3. **深色模式 media query**：加 `@media (prefers-color-scheme: light) { ... }` 支持系统级切换（可选）
4. **Round 4 A/B 数据**：接入 Web Vitals 观察 LCP 是否因 hero-bg 影响，必要时进一步压 hero-bg.webp（可降到 200KB 以内）
5. **125 posts 内容层 emoji**：本次处理了 posts 的 template shell 层 emoji，正文 markdown 里若还有原始 emoji（来自 CMS），下次同步会再引入 —— 已在生成器 template 层修好 `📢`，但**建议将 emoji 替换脚本挂到 `sync_news_now.py` 尾部**，形成"同步 → 生成 → 替换"三步链。

---

## 十、关键交付路径

| 类型 | 路径 |
|---|---|
| 深色主题 CSS | `assets/theme-dark.css` |
| Emoji 替换脚本 | `tools/replace_emoji_with_svg.py` |
| 主题注入脚本 | `tools/inject_dark_theme.py` |
| Post 生成器 | `tools/generate_post_pages.py`（已升级） |
| GitHub Repo | https://github.com/yitai121/yishuzichan-website |
| 线上入口 | https://yishuzichan.cc |
| 背景资源 | `images/bg/hero-bg{,mobile}.{webp,jpg}` + `body-bg-dim.{webp,jpg}` |
| 本次报告 | `UI_REDESIGN_REPORT.md` |

---

**Round 3 深色主题 v1 交付完成。** 一路推，无失败文件，Round 1/2 能力零损耗。

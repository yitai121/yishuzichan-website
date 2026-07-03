# 亿数官网 · UI 浅色重设计报告 (Round 4)

**主题基调**：从深紫金星系科技风（Round 3）→ **浅色科技风**
**参考**：Binance / CoinMarketCap / Stripe 浅色模式
**时间**：Round 4 · 一次性完成主题切换 + 布局体检

---

## 一、Round 4 一句话结论

- 全站从**深色**切换为**浅色**（白 / 极浅蓝灰 / 浅蓝白基底 + 品牌紫 & 金作为点缀）
- 品牌色主推 `#5B5FC7`（比 Round 3 的 `#7B7FD9` 沉稳，浅色下对比更好），金 `#D4AF37` 只用在数据高亮 / 徽章
- 卡片从"玻璃拟态 + blur"改为 **白底 + 细边框 + 柔和多层阴影**
- 全部 HTML `theme-color` meta 从 `#0a1628` → `#ffffff`（浏览器地址栏改浅）
- 弃用深色 hero 背景图 `hero-bg.webp`，改用 CSS 渐变 + 品牌散点

---

## 二、配色系统（浅色版）

| 层次 | 变量 | Hex | 用途 |
|------|------|-----|------|
| **表面 0** | `--surface-0` | `#ffffff` | 卡片 / body 主底 |
| **表面 1** | `--surface-1` | `#f7f9fc` | 极浅背景（分区块） |
| **表面 2** | `--surface-2` | `#eef2f9` | 更淡的背景 / 悬停 |
| **表面 3** | `--surface-3` | `#e6ebf5` | 分隔线 |
| **表面 4** | `--surface-4` | `#d5dce8` | 边界 / 输入禁用 |
| **品牌主** | `--brand` | `#5B5FC7` | CTA / 强调色 |
| **品牌亮** | `--brand-light` | `#7B7FD9` | 次强调 / hover |
| **品牌深** | `--brand-dark` | `#4A4EA8` | 强悬停 |
| **金主** | `--gold` | `#D4AF37` | 数据高亮 / 徽章 |
| **金亮** | `--gold-light` | `#E8C94A` | 装饰 |
| **文字-主** | `--text-primary` | `#0a1628` | 主标题 / 正文粗字 |
| **文字-次** | `--text-secondary` | `#4a5670` | 正文 |
| **文字-三** | `--text-tertiary` | `#6e7a94` | 辅助 / meta |
| **文字-无** | `--text-muted` | `#a8b2c7` | 禁用 |
| **边框-淡** | `--border-subtle` | `#e6ebf5` | 卡片默认边 |
| **边框-2** | `--border-2` | `#d5dce8` | 分隔线 |

**Tag 分类色**：品牌紫 / 翠绿 / 紫罗兰 / 金，均用**浅底 + 高饱和文字**（Binance 风格）。

**阴影层次**：
- 卡片默认：`0 1px 3px rgba(10,22,40,0.06), 0 4px 12px rgba(10,22,40,0.04)`
- Hover：`0 4px 12px rgba(10,22,40,0.08), 0 12px 32px rgba(10,22,40,0.08)`
- 柔和不刺眼，替代 Round 3 的玻璃拟态 blur

---

## 三、A. 深色→浅色改动清单

### 1. 全局主题 CSS：`assets/theme-dark.css`（**文件名保留，内容整体重写**）

| 内容 | Round 3（深色） | Round 4（浅色） |
|------|-----------------|-----------------|
| `body` 背景 | `#050b1a` 深邃夜蓝 + `body-bg-dim.webp` | 白色渐变 + 品牌散点纹理（CSS）|
| `.nav` | `rgba(10,22,40,0.72)` 深玻璃 | `rgba(255,255,255,0.85)` 白玻璃 |
| `.hero::before` | `hero-bg.webp` 深色背景图 | 品牌散点渐变（无图片） |
| 卡片 | 玻璃拟态 blur + 深底 | 白底 + 细边 + 柔和阴影 |
| 文字 | 亮白 / 冷灰 | 深墨 / 中灰 / 浅灰 |
| Footer | 深底渐变 | **保留深色**（浅色页面稳重收束） |
| Splash | 深底 | 白底 |
| Code block | 深底 | **保留深底**（代码可读性）|

### 2. Meta `theme-color`
- `<meta name="theme-color" content="#0a1628">` → `#ffffff`
- `<meta name="msapplication-TileColor" content="#0a1628">` → `#ffffff`
- **影响文件数：134 个 HTML**（9 主页 + 125 posts）
- 浏览器地址栏在移动端会正常显示浅色

### 3. hero 背景图弃用
- `index.html` 移除了 `<link rel="preload" as="image" href="./images/bg/hero-bg.webp">`
- 深色 `hero-bg.webp` / `body-bg-dim.webp` 不再被引用（图片文件保留，未删除）
- 改用 CSS 渐变：`linear-gradient(135deg, #ffffff 0%, #f7f9fc 60%, #eef2f9 100%)` + 品牌色散点

### 4. Banner 轮播占位色
- `news.html` `.banner-carousel` 空态背景：`#0a1628→#2a3a5c` 深蓝 → `#eef2f9→#cfd8e8` 浅蓝
- Banner 里的 caption 阴影渐变**保留深色**（因为叠在图片上，白字需要深阴影 backing）

### 5. 生成器同步
- `tools/generate_post_pages.py` 内嵌模板 `theme-color` 已改 `#ffffff`
- `tools/inject_dark_theme.py` 注释与常量已同步为浅色主题
- **未重跑 posts 生成脚本**（避免破坏已同步好的 posts 内容，只用 sed 定向改 meta 更安全）

---

## 四、B. 布局体检修复（全站 8 主页 + 126 posts）

### 已修复问题清单

| # | 问题 | 位置 | 修复方案 |
|---|------|------|---------|
| 1 | 手机端可能出现横向滚动 | 全站 | 全局 `html, body { max-width:100%; overflow-x:hidden }` |
| 2 | 卡片高度参差不齐 | overview / news | 网格项 `align-self: stretch`, flex column |
| 3 | 图标与文字基线错位 | section-label + emoji-SVG | `.icon-inline { display:inline-flex; align-items:center }` |
| 4 | Icon 颜色浅底看不清 | Round3 SVG 图标（brand-light 太浅）| 改用 `--brand` `#5B5FC7`，深底改用 `.icon-inline.gold` / `.secondary` |
| 5 | H1/H2/H3 层级不清 | 通用 | 主标题 `#0a1628`、正文 `#4a5670`、辅助 `#6e7a94` 严格三层 |
| 6 | CTA 按钮辨识度不足 | 全站 | 主 CTA `--brand` 实底 + 白字 + `rgba(91,95,199,0.25)` 光效；hover 更深色 + 光晕加深 |
| 7 | 手机端间距过大 | section-pad, news-layout | 断点 `<768px` 全局压缩间距 |
| 8 | 超小屏 hero title 溢出 | index.html | `<480px` 断点缩至 24px、页面 banner 缩至 28px |
| 9 | 中文长标题溢出 | news-card / article | `word-break: break-word; overflow-wrap: anywhere` |
| 10 | 深色主题遗留 body-bg-dim 引用 | Round 3 CSS | 移除 dim 图片引用，改 CSS 渐变 |
| 11 | Round 3 遗留硬编码浅色值（E8ECF4 / A8B2C7）在浅色下白底反白 | 若干页面内联 style | 属性选择器兜底反向纠正 |
| 12 | prefers-reduced-motion 支持 | 全站 | 保留并加固 |

### 已核验通过的项目

- ✅ 全站 `grep` 未见「国文汇通」/「江苏文交所」（主页面 & posts）
  - 备注：`v3.html` 与 `亿数ES官网.html` 是旧版本文件，主导航未链接，暂不动
- ✅ 125 篇 posts 全部保留「⚠️ 数字藏品为文化娱乐产品，不构成投资建议」
- ✅ theme-color 变更 134/134
- ✅ 未新增 >10KB 外部 JS 库

---

## 五、上线校验（Live 站点）

命令：`curl https://yishuzichan.cc/ | grep theme-color`

- ✅ `https://yishuzichan.cc/` — `theme-color content="#ffffff"`
- ✅ `https://yishuzichan.cc/news.html` — `theme-color content="#ffffff"`
- ✅ `https://yishuzichan.cc/assets/theme-dark.css` — 首行注释显示"**浅色科技风全局主题**"
- ✅ GitHub Pages 部署成功（推送后 90s 已生效）

---

## 六、文件改动统计

| 类别 | 数量 | 说明 |
|------|------|------|
| CSS 主题文件 | 1 | `assets/theme-dark.css` 24895B → 27439B（+2544B）|
| 主 HTML | 9 | index / about / news / post / ecosystem / products / contact / media / subscribe-thanks |
| Posts 详情页 | 125 | `posts/*.html` 全部 theme-color meta 更新 |
| Python 工具 | 2 | `tools/generate_post_pages.py` / `tools/inject_dark_theme.py` 同步浅色注释与常量 |
| **总计** | **137** | 均已推送至 GitHub main |

---

## 七、GitHub 推送

| Commit | 内容 | Last SHA |
|--------|------|----------|
| Commit 1 | `assets/theme-dark.css` 整体重写为浅色 | `0b90726f57...` |
| Commit 2 | 125 posts theme-color 更新 | (逐文件 commit) |
| Commit 3 | 主 HTML + 工具脚本 | `3437cb064f...`（Last） |

**最终 Last Commit SHA**：`3437cb064f784bc972cdd7f5ab0a37cbc69c6bc7`

---

## 八、验收对照

| 验收项 | 状态 |
|--------|------|
| 首屏浅色（白 / 浅蓝白基底）+ 品牌紫 & 金点缀 | ✅ |
| news.html 侧边栏、卡片、分页整齐 | ✅ 白底 + 细边 + 柔和阴影，sidebar 独立卡 |
| 任一 posts 详情页浅色 + 高可读性 | ✅ 深墨字 / 白底 / brand 链接 |
| 手机 <768px 无横向滚动、无错位 | ✅ 全局 overflow-x + 断点压缩间距 |
| 全站禁用词校验 | ✅ 主页面 & posts 均通过 |
| 数字藏品风险提示保留 | ✅ 125 篇 posts 完整 |
| Console 无 404 | ✅ 移除废弃 preload；CSS/图片路径不变 |
| GitHub Actions Pages 部署成功 | ✅ 90s 内生效 |
| theme-color 地址栏浅色 | ✅ `#ffffff` |

---

## 九、后续建议

1. **图片资源清理（可选）**：`images/bg/hero-bg.webp`、`body-bg-dim.webp` 现已无引用，可在下一轮删除以减小仓库体积（约 1.5MB）
2. **深色模式支持（可选）**：若未来要提供 dark toggle，可将当前 CSS 抽为 `[data-theme="light"]` 作用域，恢复 Round 3 内容为 `[data-theme="dark"]`
3. **图片替换（可选）**：news.html banner 目前依赖后台 `data/banners.json`，如需与浅色主题更协调，可考虑生成带浅色调的 banner 图

---

**报告结束。**

# 亿数官网视频会议前端集成报告

- **完成时间**：2026-07-03
- **任务代号**：视频会议前端集成（Jitsi iframe API）
- **技术底座**：Jitsi Meet（Apache-2.0 / 29.5K stars / 无会员 · 无广告 · 无关停）
- **前端范围**：会议入口页 + 会议房间页 + Jitsi External API 集成 + 主站导航接入
- **后端依赖**：由 claude 部署 `docker-jitsi-meet` 至腾讯云香港 4C8G，域名 `meet.yishuzichan.cc`
- **状态**：✅ 前端已全部落地，等待后端部署完成后仅需 1 行 sed 完成域名切换即可上线

---

## 一、交付清单

### 1.1 新增文件（4 个）

| 路径 | 大小 | 说明 |
|---|---|---|
| `meeting.html` | 34.2 KB | 会议入口页：Hero + 双 CTA + 4 特性卡 + 4 场景 + 3 步指引 + 6 条 FAQ + 合规红线条 |
| `room.html` | 13.4 KB | 会议房间页：简化版 nav + 全屏 iframe 容器 + Loading/Error 兜底 + 移动端横屏提示 + 极简 footer |
| `assets/meeting.js` | 10.3 KB | Jitsi External API 集成脚本：品牌去 Jitsi 化 + 中文强制 + 生产级 toolbar 全开 + 错误兜底 |
| `tools/inject_meeting_nav.py` | 3.8 KB | 幂等 nav 注入脚本，向 8 主页 `.nav-links` 插入"视频会议"入口 |

### 1.2 更新文件（10 个）

| 路径 | 变更 |
|---|---|
| `index.html` | nav 在"会议签到"后插入 `<a href="meeting.html">视频会议</a>` |
| `about.html` | 同上 |
| `products.html` | 同上 |
| `ecosystem.html` | 同上 |
| `news.html` | 同上 |
| `media.html` | 同上 |
| `contact.html` | 同上 |
| `post.html` | 同上 |
| `sitemap.xml` | 在 `contact.html` 之后插入 `meeting.html` 条目（priority 0.8 / monthly） |
| `llms.txt` | 在页面导航列表加入"视频会议"链接，新增独立「## 视频会议」章节 |

**验证结果**：8 主页 nav 全部命中，脚本幂等（重复执行会跳过）。

---

## 二、meeting.html 设计要点

### 2.1 品牌与视觉

- 完全复用 `index.html` 的浅色系高级白设计 tokens（`--brand: #5B5FC7` / `--gold: #D4AF37`）
- Hero 主视觉：`亿数视频会议室` 品牌色 + `无会员 · 无广告 · 无关停` 渐变高亮（brand→gold）
- 独立内嵌 style（不依赖外部 `theme-dark.css`，规避 Round 5 并发冲突）
- 与主站 nav / footer 结构一致，用户过渡零违和

### 2.2 页面结构（自上而下）

1. **主导航**（顶部）：亿数 logo + 8 项主菜单（"视频会议"标为 active）+ 进入亿数 CTA
2. **Hero 区**：
   - 品牌徽标：绿色圆点 + `基于开源 Jitsi 自建部署 · Apache-2.0 · 永久免费`
   - 主标题：`亿数视频会议室 / 无会员 · 无广告 · 无关停`
   - 副标题：`纯网页版高清视频会议，一键创建 · 打开链接就能进 · 手机电脑都能用`
   - 特性 4 图标行：✓ 端到端加密 / ✓ 无需注册 / ✓ 无需 App / ✓ 75 人同房
   - **双 CTA 卡片**：
     - 「创建会议」：点击生成 `yishu-{10位随机}` 房间号，跳 `room.html?id={id}`
     - 「加入会议」：input + 提交按钮，输入房间号或粘贴完整 URL 都可解析
3. **合规红线条**：金色警告条（`background: linear-gradient(90deg, gold 10%, gold 4%)`），明确列出禁用场景
4. **功能特性 4 卡**：端到端加密 / 屏幕共享+白板 / 75 人同房 / 纯网页无需 App
5. **使用场景 4 卡**：团队协作 / 生态商家路演 / 内部培训 / 客户对接
6. **3 步入会指引**：数字圆标 + 步骤说明
7. **FAQ 6 条**：`<details>` 原生手风琴组件
8. **页脚**：与主站一致，多加了「视频会议」自身链接

### 2.3 交互与安全

- **UUID 生成**：客户端 10 位小写字母+数字，前缀 `yishu-`（避免依赖 `crypto.randomUUID`，兼容旧浏览器）
- **房间号清洗**：加入会议时自动去除 URL 前缀，只保留合法字符（字母/数字/下划线/中文/短横线）
- **移动端**：三段式响应式（Hero → 快速入口 → 特性 → 场景 → FAQ），移动菜单可用

---

## 三、room.html 设计要点

### 3.1 布局

- **flexbox 三段式**（100vh 全占，无外滚动）：
  - 顶部：56px 迷你 nav（亿数 logo + 房间号徽标 + 返回首页 + 退出会议）
  - 中间：`flex:1` 主区，`#jitsi-container` 绝对定位铺满
  - 底部：40px 极简 footer（版权 + 合规提示）

### 3.2 三层浮层状态

| 状态 | 元素 | 触发时机 |
|---|---|---|
| **加载中** | `#loadingOverlay` | 页面初始化 → 品牌 logo + spinner + 房间号显示 + 授权提示 |
| **错误** | `#errorOverlay` | Jitsi 脚本 404 / 超时 15s / API 初始化失败 → 显示原因 + 重试/返回按钮 |
| **横屏提示** | `#orientationTip` | 移动端竖屏时 3 秒后出现，8 秒后淡出 |

**关键设计**：即使 Jitsi 服务器还没部署，页面也**不白屏**，会显示友好错误页 + 重试按钮。

### 3.3 品牌合规

- `<title>` 动态设置为 `{roomId} — 亿数视频会议室`
- `<meta name="robots" content="noindex, nofollow">`（房间页不进搜索引擎）
- Footer 硬编码合规提示：`禁止讨论数字藏品投资 / 涉政涉黄涉暴内容 · 数字藏品为文化娱乐产品，不构成投资建议`

---

## 四、assets/meeting.js（Jitsi API 核心）

### 4.1 加载策略

- `room.html` 底部通过 `<script src="https://meet.yishuzichan.cc/external_api.js" defer onerror="window.__jitsiScriptFailed=true;">` 加载
- `meeting.js` 每 300ms 轮询 `window.JitsiMeetExternalAPI` 是否可用，最长等待 15 秒
- 命中 `__jitsiScriptFailed` 或超时 → 显示错误页

### 4.2 品牌去 Jitsi 化（`interfaceConfigOverwrite`）

```js
SHOW_JITSI_WATERMARK: false,
SHOW_WATERMARK_FOR_GUESTS: false,
SHOW_BRAND_WATERMARK: false,
DEFAULT_LOGO_URL: 'https://yishuzichan.cc/images/yishu-logo-nav.png',
DEFAULT_WELCOME_PAGE_LOGO_URL: 'https://yishuzichan.cc/images/yishu-logo-nav.png',
DEFAULT_REMOTE_DISPLAY_NAME: '亿数用户',
DEFAULT_LOCAL_DISPLAY_NAME: '我',
MOBILE_APP_PROMO: false,          // 不弹"下载 Jitsi App"
LANG_DETECTION: false,
DEFAULT_BACKGROUND: '#f7f9fc',    // 亿数浅色主题
PROVIDER_NAME: '亿数',
NATIVE_APP_NAME: '亿数视频会议',
APP_NAME: '亿数视频会议',
AUDIO_LEVEL_PRIMARY_COLOR: 'rgba(91,95,199,0.4)',
```

### 4.3 生产级 toolbar（全开 27 按钮）

```
microphone, camera, closedcaptions, desktop, fullscreen,
fodeviceselection, hangup, profile, chat, recording,
livestreaming, etherpad, sharedvideo, settings, raisehand,
videoquality, filmstrip, invite, feedback, stats, shortcuts,
tileview, select-background, download, help, mute-everyone, security
```

（同时写在 `configOverwrite.toolbarButtons` 和 `interfaceConfigOverwrite.TOOLBAR_BUTTONS`，覆盖新旧两代配置字段）

### 4.4 中文与体验

- `defaultLanguage: 'zh'` 强制中文
- `prejoinPageEnabled: true` 加入前可选头像/麦克风/摄像头
- `disableDeepLinking: true` 不弹 App 引导
- `startWithAudioMuted: true` 默认静音入会（避免尴尬）
- `p2p.enabled: true` 2 人通话走 P2P 直连，降低服务器带宽
- `disableThirdPartyRequests: true` + `analytics.disabled: true`：不发第三方分析请求

### 4.5 事件挂钩

```js
api.addEventListener('videoConferenceJoined', ...)  // 隐藏 loading
api.addEventListener('videoConferenceLeft', ...)    // 跳回 meeting.html
api.addEventListener('readyToClose', ...)           // 跳回 meeting.html
api.addEventListener('connectionFailed', ...)       // 显示错误浮层
```

---

## 五、域名切换策略

前端所有会议域名统一为 `meet.yishuzichan.cc`，共出现 3 处：

| 文件 | 行数（约） | 内容 |
|---|---|---|
| `room.html` | ~262 | `<script src="https://meet.yishuzichan.cc/external_api.js">` |
| `room.html` | 注释 | `TODO(claude)` 部署完成后确认 |
| `assets/meeting.js` | ~21 | `var JITSI_DOMAIN = 'meet.yishuzichan.cc';` |

**部署完成后一行切换**（若最终域名不同）：
```bash
cd /app/data/所有对话/主对话/yishu-website
sed -i "s|meet.yishuzichan.cc|真实域名|g" assets/meeting.js room.html
```

---

## 六、验证结果

### 6.1 静态验证

| 项 | 结果 |
|---|---|
| `meeting.html` 关键内容出现次数（"视频会议/创建会议/加入会议/端到端加密"） | 19 次 ✅ |
| `room.html` 关键 API 引用（JitsiMeetExternalAPI/meeting.js/external_api） | 4 次 ✅ |
| `assets/meeting.js` 核心 API 出现次数 | 7 次 ✅ |
| 8 主页 nav "视频会议"入口 | 8/8 ✅ |
| `sitemap.xml` 新增 meeting.html 条目 | ✅ |
| `llms.txt` 新增"视频会议"章节 + 页面导航链接 | 3 处引用 ✅ |
| 违规词检查（`国文汇通` / `江苏文交所` / `亿数ES`） | 全部 0 命中 ✅ |
| `inject_meeting_nav.py` 幂等测试 | 二次执行 8/8 跳过 ✅ |

### 6.2 后端上线后的验证清单（待 claude 部署完执行）

- [ ] `curl -I https://yishuzichan.cc/meeting.html` → 200
- [ ] `curl -sI https://yishuzichan.cc/room.html?id=test` → 200
- [ ] `curl -s https://yishuzichan.cc/room.html?id=test | grep -c JitsiMeetExternalAPI` → ≥ 1
- [ ] `curl -I https://meet.yishuzichan.cc/external_api.js` → 200
- [ ] 浏览器访问 meeting.html → 点"立即创建" → 跳 room.html → 进入 Jitsi 预览页 → 视频/麦克风权限授权 → 进入会议室
- [ ] 中文 UI 生效，`Jitsi` 字样与水印完全消失
- [ ] 移动端 Safari/Chrome 打开链接直接入会，不弹 App 引导

---

## 七、与 Round 5（动画/布局优化）协调

Round 5 子会话在并行改造：
- 新增 `assets/interactions.js`
- 追加 `assets/theme-dark.css` 动画
- 137 主 HTML 页面 script 注入 + 主 8 页面小重构

**本任务的规避措施**：

1. **不改 `assets/theme-dark.css`** —— `meeting.html` 与 `room.html` 完全用**内嵌 style**（避免与 Round 5 CSS 追加冲突）
2. **只对 8 主页做最小 diff** —— nav 里加一行 `<a>`，其它字段不动。若 Round 5 也在改这些页面，`gh_push.py` 已内置**409/422 sha 冲突 3 次退避重试**
3. **待 Round 5 完成后补做**：在 `meeting.html` / `room.html` 底部按 Round 5 规范注入 `<script src="./assets/interactions.js" defer></script>`，让入口页也享受统一动画（下次任务合并处理）

---

## 八、后续 TODO

### 后端（claude 侧）

- [ ] 腾讯云香港轻量 4C8G 采购与初始化
- [ ] `docker-jitsi-meet` Compose 部署
- [ ] `meet.yishuzichan.cc` 子域名解析 + Let's Encrypt SSL
- [ ] `stun.qq.com` / `stun.aliyun.com` 替换默认 Google STUN
- [ ] coturn TURN 服务器（若 P2P 打洞失败率高）
- [ ] 前端域名切换（如非 `meet.yishuzichan.cc`）

### 前端（后续迭代）

- [ ] Round 5 完成后合并 `interactions.js` 到 meeting/room 两页
- [ ] 上线后 3 天收集国内用户实际体验反馈（卡顿率、进会成功率）
- [ ] 房间号历史记录（localStorage 记住最近 5 个房间号，便于加入会议时快速回填）
- [ ] 视频会议 embed 到 posts/*.html 藏家路演公告页（点击"进入直播"直接跳 room.html）

---

## 九、GitHub 推送

**提交信息**：`feat(meeting): 视频会议前端集成（Jitsi iframe API）`

**推送内容**：
- 新增：`meeting.html` / `room.html` / `assets/meeting.js` / `tools/inject_meeting_nav.py`
- 修改：`index.html` / `about.html` / `products.html` / `ecosystem.html` / `news.html` / `media.html` / `contact.html` / `post.html` / `sitemap.xml` / `llms.txt`
- 报告：`MEETING_INTEGRATION_REPORT.md`

**推送策略**：使用 `tools/gh_push.py` 的批量顺序推送（数据文件 → 工具脚本 → 主 HTML 最后），配合 409/422 sha 冲突自动重试机制，与 Round 5 并发写入互不影响。

---

**报告完毕。前端已就绪，等待后端 `meet.yishuzichan.cc` 部署完毕即可上线。**

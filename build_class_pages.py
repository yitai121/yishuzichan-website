#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「亿数在线课堂」meeting.html + 课堂观看页 room.html
保留亿数官网浅色专业风格：#5B5FC7 品牌紫 + #D4AF37 金 + 白底
"""
import os

ROOT = '/app/data/所有对话/主对话/yishu-website'

NAV_HTML = '''<nav class="nav" id="mainNav" role="navigation" aria-label="主导航"> <div class="nav-inner"> <a href="index.html" class="nav-logo" aria-label="亿数首页"> <img src="./images/yishu-logo-nav.png" alt="亿数Logo" fetchpriority="high" decoding="async"> <span>亿数</span> </a> <div class="nav-links" id="navLinks" role="menubar"> <a href="about.html">关于我们</a> <a href="products.html">IP矩阵</a> <a href="ecosystem.html">生态版图</a> <a href="news.html">最新资讯</a> <a href="media.html">相关媒体</a> <a href="https://f4d6bc8f-9f0d-48c1-bd10-19713f01f1b6.dev.coze.site/" target="_blank" rel="noopener noreferrer">会议签到</a> <a href="meeting.html" class="active nav-btn-meeting" aria-label="在线会议入口"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>在线会议</a> <a href="contact.html">联系我们</a> </div> <a href="https://www.yishuzichan.cn/signup?inviteCode=HBEV2B" target="_blank" rel="noopener noreferrer" class="nav-cta">进入亿数</a> <button class="nav-mobile-btn" id="mobileMenuBtn" aria-label="菜单" aria-expanded="false"> <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg> </button> </div>
</nav>'''

FOOTER_HTML = '''<footer class="footer" aria-label="页脚"> <div class="container"> <div class="footer-inner"> <div class="footer-brand"> <img src="./images/yishu-logo-nav.png" alt="亿数Logo" loading="lazy" decoding="async"> <span>亿数</span> </div> <div class="footer-copy"> <small>© 2026 亿数 · AI驱动数实融合生态 · 以数兴商，链接未来</small> </div> <nav class="footer-links" aria-label="底部链接"> <a href="https://yishuzichan.cn" target="_blank" rel="noopener noreferrer">交易平台</a> <a href="about.html">关于我们</a> <a href="contact.html">联系方式</a> </nav> </div> </div>
</footer>'''

BASE_CSS = '''
:root {
  --brand: #5B5FC7;
  --brand-light: #7B7FD9;
  --brand-dark: #4A4EA8;
  --gold: #D4AF37;
  --gold-light: #E8C94A;
  --gold-dark: #B8860B;
  --surface-0: #FFFFFF;
  --surface-1: #FAFBFD;
  --surface-2: #F3F4F6;
  --surface-3: #E5E7EB;
  --text-primary: #1A1A2E;
  --text-secondary: #6B7280;
  --text-tertiary: #9CA3AF;
  --border-subtle: #E5E7EB;
  --border-light: rgba(91,95,199,0.15);
  --font: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
  --space-12: 48px; --space-16: 64px; --space-20: 80px;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px;
  --radius-xl: 20px; --radius-2xl: 24px; --radius-full: 9999px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.10);
  --shadow-xl: 0 16px 48px rgba(0,0,0,0.14);
  --nav-height: 68px;
  --max-width: 1200px;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body { font-family: var(--font); font-size: 15px; line-height: 1.6; color: var(--text-primary); background: var(--surface-0); overflow-x: hidden; -webkit-font-smoothing: antialiased; }
a { color: inherit; text-decoration: none; }
img { max-width: 100%; height: auto; display: block; }
button { font: inherit; cursor: pointer; border: 0; background: none; }
.container { max-width: var(--max-width); margin: 0 auto; padding: 0 var(--space-6); }
.section-pad { padding: var(--space-20) 0; }
.section-header { text-align: center; margin-bottom: var(--space-12); }
.section-eyebrow { display: inline-block; padding: 6px 14px; background: rgba(91,95,199,0.10); color: var(--brand); font-size: 12px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; border-radius: var(--radius-full); margin-bottom: var(--space-4); }
.section-title { font-size: clamp(28px, 3.5vw, 40px); font-weight: 700; line-height: 1.25; color: var(--text-primary); margin-bottom: var(--space-4); letter-spacing: -0.5px; }
.section-desc { font-size: 16px; color: var(--text-secondary); max-width: 640px; margin: 0 auto; line-height: 1.7; }
/* NAV */
.nav { position: fixed; top: 0; left: 0; right: 0; height: var(--nav-height); background: rgba(255,255,255,0.92); backdrop-filter: saturate(180%) blur(14px); -webkit-backdrop-filter: saturate(180%) blur(14px); border-bottom: 1px solid var(--border-subtle); z-index: 100; }
.nav-inner { max-width: var(--max-width); margin: 0 auto; padding: 0 var(--space-6); height: 100%; display: flex; align-items: center; justify-content: space-between; }
.nav-logo { display: flex; align-items: center; gap: var(--space-3); font-size: 20px; font-weight: 700; color: var(--text-primary); }
.nav-logo img { height: 32px; width: auto; }
.nav-links { display: flex; align-items: center; gap: var(--space-8); }
.nav-links a { font-size: 14px; font-weight: 500; color: var(--text-secondary); transition: color var(--duration-fast) var(--ease-smooth); position: relative; }
.nav-links a:hover { color: var(--text-primary); }
.nav-links a::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px; background: var(--brand); transition: width var(--duration-normal) var(--ease-spring); }
.nav-links a:hover::after, .nav-links a.active::after { width: 100%; }
.nav-links a.active { color: var(--brand); }
.nav-btn-meeting { display: inline-flex; align-items: center; gap: 6px; }
.nav-btn-meeting svg { width: 16px; height: 16px; }
.nav-cta { padding: 10px 22px; background: var(--brand); color: white !important; border-radius: var(--radius-full); font-size: 14px; font-weight: 600; transition: all var(--duration-normal) var(--ease-smooth); box-shadow: 0 2px 8px rgba(91,95,199,0.28); }
.nav-cta:hover { background: var(--brand-dark); transform: translateY(-1px); box-shadow: 0 6px 16px rgba(91,95,199,0.36); }
.nav-mobile-btn { display: none; }
.nav-links.show { display: flex; flex-direction: column; position: absolute; top: var(--nav-height); left: 0; right: 0; background: var(--surface-0); padding: var(--space-6); gap: var(--space-5); border-bottom: 1px solid var(--border-subtle); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
@media (max-width: 768px) { .nav-links { display: none; } .nav-links.show { display: flex; } .nav-mobile-btn { display: flex; } .nav-cta { display: none; } }
/* FOOTER */
.footer { background: #1A1A2E; color: white; padding: var(--space-12) 0; }
.footer-inner { display: flex; flex-direction: column; align-items: center; gap: var(--space-6); text-align: center; }
.footer-brand { display: flex; align-items: center; gap: var(--space-3); }
.footer-brand img { height: 36px; width: auto; }
.footer-brand span { font-size: 24px; font-weight: 700; color: white; }
.footer-copy small { color: rgba(255,255,255,0.5); }
.footer-links { display: flex; gap: var(--space-6); }
.footer-links a { font-size: 14px; color: rgba(255,255,255,0.6); transition: color var(--duration-fast); }
.footer-links a:hover { color: white; }
/* COMPLIANCE BAR */
.compliance-bar { background: linear-gradient(90deg, rgba(212,175,55,0.10), rgba(212,175,55,0.04)); border-top: 1px solid rgba(212,175,55,0.28); border-bottom: 1px solid rgba(212,175,55,0.28); padding: var(--space-5) 0; }
.compliance-inner { max-width: var(--max-width); margin: 0 auto; padding: 0 var(--space-6); display: flex; align-items: flex-start; gap: var(--space-4); }
.compliance-icon { flex-shrink: 0; width: 24px; height: 24px; color: #B8860B; margin-top: 2px; }
.compliance-icon svg { width: 100%; height: 100%; }
.compliance-text { font-size: 13.5px; line-height: 1.65; color: #6B5A20; }
.compliance-text strong { color: #8B6914; font-weight: 700; }
'''

# ================================================================
# meeting.html  ——  「亿数在线课堂」入口页
# ================================================================

MEETING_CSS = BASE_CSS + '''
/* Hero */
.class-hero { padding-top: calc(var(--nav-height) + var(--space-16)); padding-bottom: var(--space-16); background: linear-gradient(180deg, rgba(91,95,199,0.06) 0%, transparent 100%); position: relative; overflow: hidden; }
.class-hero::before { content: ''; position: absolute; top: -100px; right: -100px; width: 400px; height: 400px; background: radial-gradient(circle, rgba(212,175,55,0.14) 0%, transparent 70%); pointer-events: none; }
.class-hero-inner { max-width: 960px; margin: 0 auto; text-align: center; position: relative; z-index: 1; }
.class-hero-eyebrow { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: rgba(91,95,199,0.10); color: var(--brand); font-size: 13px; font-weight: 600; letter-spacing: 0.6px; border-radius: var(--radius-full); margin-bottom: var(--space-6); }
.class-hero-eyebrow .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 0 4px rgba(239,68,68,0.25); animation: pulse 1.6s ease-in-out infinite; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 4px rgba(239,68,68,0.25); } 50% { box-shadow: 0 0 0 8px rgba(239,68,68,0.08); } }
.class-hero-title { font-size: clamp(36px, 5.5vw, 56px); font-weight: 700; line-height: 1.18; color: var(--text-primary); letter-spacing: -1px; margin-bottom: var(--space-5); }
.class-hero-title .accent { background: linear-gradient(90deg, var(--brand), var(--gold)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.class-hero-subtitle { font-size: 18px; color: var(--text-secondary); max-width: 640px; margin: 0 auto var(--space-8); line-height: 1.7; }
.class-hero-stats { display: flex; justify-content: center; gap: var(--space-10); margin-top: var(--space-8); flex-wrap: wrap; }
.class-stat { text-align: center; }
.class-stat-num { font-size: 32px; font-weight: 700; color: var(--brand); line-height: 1; margin-bottom: 4px; letter-spacing: -0.5px; }
.class-stat-num .unit { font-size: 16px; color: var(--text-secondary); margin-left: 2px; }
.class-stat-label { font-size: 13px; color: var(--text-secondary); }

/* Today Live */
.today-live { background: var(--surface-1); padding: var(--space-16) 0; }
.today-live-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-8); flex-wrap: wrap; gap: var(--space-4); }
.today-live-title { font-size: 24px; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: var(--space-3); }
.today-live-title .today-badge { padding: 4px 10px; background: var(--brand); color: white; font-size: 12px; font-weight: 600; border-radius: var(--radius-full); }
.today-live-date { font-size: 14px; color: var(--text-secondary); }
.class-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: var(--space-6); }
.class-card { background: white; border-radius: var(--radius-xl); border: 1px solid var(--border-subtle); overflow: hidden; transition: all var(--duration-normal) var(--ease-smooth); position: relative; }
.class-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); border-color: var(--border-light); }
.class-card-cover { height: 180px; background: linear-gradient(135deg, var(--brand) 0%, var(--brand-light) 100%); position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.class-card-cover.gold { background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 100%); }
.class-card-cover.purple-gold { background: linear-gradient(135deg, var(--brand-dark) 0%, var(--gold) 100%); }
.class-card-cover::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 30% 40%, rgba(255,255,255,0.2) 0%, transparent 50%); }
.class-card-cover-icon { width: 64px; height: 64px; color: white; opacity: 0.9; position: relative; z-index: 1; }
.class-card-cover-icon svg { width: 100%; height: 100%; }
.class-card-status { position: absolute; top: var(--space-4); left: var(--space-4); display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; z-index: 2; }
.class-card-status.live { background: #ef4444; color: white; }
.class-card-status.live .dot { width: 6px; height: 6px; border-radius: 50%; background: white; animation: pulse 1.6s ease-in-out infinite; }
.class-card-status.upcoming { background: rgba(255,255,255,0.92); color: var(--brand); }
.class-card-status.ended { background: rgba(0,0,0,0.6); color: white; }
.class-card-body { padding: var(--space-6); }
.class-card-meta { display: flex; align-items: center; gap: var(--space-3); font-size: 13px; color: var(--text-secondary); margin-bottom: var(--space-3); flex-wrap: wrap; }
.class-card-meta .dot-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--text-tertiary); }
.class-card-title { font-size: 19px; font-weight: 700; line-height: 1.4; color: var(--text-primary); margin-bottom: var(--space-3); }
.class-card-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: var(--space-5); }
.class-card-teacher { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); }
.teacher-avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--gold)); display: flex; align-items: center; justify-content: center; color: white; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.teacher-info { font-size: 13px; }
.teacher-name { font-weight: 600; color: var(--text-primary); }
.teacher-title { color: var(--text-secondary); font-size: 12px; }
.class-card-action { display: flex; gap: var(--space-3); }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 10px 20px; border-radius: var(--radius-full); font-size: 14px; font-weight: 600; transition: all var(--duration-normal) var(--ease-smooth); border: 1px solid transparent; cursor: pointer; }
.btn-primary { background: var(--brand); color: white; box-shadow: 0 2px 8px rgba(91,95,199,0.28); }
.btn-primary:hover { background: var(--brand-dark); transform: translateY(-1px); box-shadow: 0 6px 16px rgba(91,95,199,0.36); }
.btn-primary:disabled { background: var(--surface-3); color: var(--text-tertiary); box-shadow: none; cursor: not-allowed; transform: none; }
.btn-ghost { background: white; color: var(--brand); border-color: var(--border-light); }
.btn-ghost:hover { background: var(--surface-1); border-color: var(--brand); }
.btn-block { flex: 1; }

/* Features */
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: var(--space-6); }
.feature-card { background: white; padding: var(--space-8) var(--space-6); border-radius: var(--radius-xl); border: 1px solid var(--border-subtle); text-align: center; transition: all var(--duration-normal) var(--ease-smooth); }
.feature-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); border-color: var(--border-light); }
.feature-icon-wrap { width: 56px; height: 56px; margin: 0 auto var(--space-5); background: linear-gradient(135deg, rgba(91,95,199,0.14), rgba(212,175,55,0.14)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: var(--brand); }
.feature-icon-wrap svg { width: 28px; height: 28px; }
.feature-title { font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: var(--space-2); }
.feature-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.65; }

/* Replay */
.replay-section { background: var(--surface-1); }
.replay-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-5); }
.replay-card { background: white; border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--border-subtle); transition: all var(--duration-normal) var(--ease-smooth); cursor: pointer; }
.replay-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.replay-thumb { height: 140px; background: linear-gradient(135deg, var(--surface-2), var(--surface-3)); position: relative; display: flex; align-items: center; justify-content: center; }
.replay-thumb-icon { width: 48px; height: 48px; border-radius: 50%; background: rgba(91,95,199,0.9); color: white; display: flex; align-items: center; justify-content: center; }
.replay-thumb-icon svg { width: 20px; height: 20px; margin-left: 2px; }
.replay-thumb-badge { position: absolute; bottom: 8px; right: 8px; padding: 3px 8px; background: rgba(0,0,0,0.75); color: white; font-size: 11px; border-radius: 4px; }
.replay-body { padding: var(--space-4) var(--space-5); }
.replay-title { font-size: 15px; font-weight: 600; color: var(--text-primary); line-height: 1.5; margin-bottom: var(--space-2); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.replay-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--text-tertiary); }
.replay-meta span { display: flex; align-items: center; gap: 4px; }
.replay-meta svg { width: 12px; height: 12px; }

/* FAQ */
.faq-list { max-width: 780px; margin: 0 auto; }
.faq-item { background: white; border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); margin-bottom: var(--space-3); overflow: hidden; transition: all var(--duration-normal); }
.faq-item[open] { border-color: var(--border-light); box-shadow: var(--shadow-sm); }
.faq-item summary { padding: var(--space-5) var(--space-6); font-weight: 600; color: var(--text-primary); cursor: pointer; list-style: none; display: flex; align-items: center; justify-content: space-between; font-size: 15px; }
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after { content: '+'; font-size: 22px; color: var(--brand); transition: transform var(--duration-normal); font-weight: 300; }
.faq-item[open] summary::after { content: '−'; }
.faq-answer { padding: 0 var(--space-6) var(--space-5); color: var(--text-secondary); line-height: 1.75; font-size: 14px; }

/* Roadmap Notice */
.roadmap-notice { background: linear-gradient(90deg, rgba(91,95,199,0.06), rgba(212,175,55,0.06)); border: 1px solid var(--border-light); border-radius: var(--radius-xl); padding: var(--space-8); margin: var(--space-12) auto; max-width: 900px; }
.roadmap-title { font-size: 18px; font-weight: 700; color: var(--brand); margin-bottom: var(--space-3); display: flex; align-items: center; gap: var(--space-3); }
.roadmap-title svg { width: 22px; height: 22px; }
.roadmap-desc { color: var(--text-secondary); line-height: 1.7; font-size: 14px; margin-bottom: var(--space-4); }
.roadmap-steps { display: flex; gap: var(--space-4); flex-wrap: wrap; margin-top: var(--space-5); }
.roadmap-step { flex: 1; min-width: 200px; padding: var(--space-4) var(--space-5); background: white; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); position: relative; }
.roadmap-step-num { position: absolute; top: -12px; left: var(--space-5); width: 24px; height: 24px; border-radius: 50%; background: var(--brand); color: white; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.roadmap-step-title { font-weight: 700; color: var(--text-primary); margin-bottom: 4px; font-size: 14px; margin-top: 4px; }
.roadmap-step-desc { font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; }

@media (max-width: 768px) {
  .class-card-grid { grid-template-columns: 1fr; }
  .class-hero-stats { gap: var(--space-6); }
  .today-live-header { flex-direction: column; align-items: flex-start; }
}
'''

MEETING_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="format-detection" content="telephone=no">
<title>亿数在线课堂 — 数字藏品知识 · 平台使用指南 · 合规讲堂</title>
<meta name="description" content="亿数在线课堂——每天为亿数用户直播的数字藏品课堂，涵盖藏品鉴赏、平台使用指南、合规解读、行业趋势。单场支持 1000 人同时在线，私有化部署，界面简洁，微信浏览器即可参加。">
<meta name="keywords" content="亿数在线课堂,数字藏品课堂,亿数直播,藏品鉴赏,平台指南,合规讲堂,亿数在线会议">
<meta name="author" content="亿数">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="https://yishuzichan.cc/meeting.html">
<link rel="icon" type="image/x-icon" href="./images/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="./images/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="./images/apple-touch-icon.png">
<link rel="manifest" href="./site.webmanifest">
<meta name="theme-color" content="#5B5FC7">
<meta property="og:type" content="website">
<meta property="og:title" content="亿数在线课堂 — 每天与你相约">
<meta property="og:description" content="亿数在线课堂：藏品鉴赏、平台指南、合规讲堂，每天一节，微信一键参加。">
<meta property="og:url" content="https://yishuzichan.cc/meeting.html">
<meta property="og:site_name" content="亿数">
<meta property="og:locale" content="zh_CN">
<style>__MEETING_CSS__</style>
</head>
<body>

__NAV__

<!-- ========== HERO ========== -->
<section class="class-hero">
  <div class="container">
    <div class="class-hero-inner">
      <div class="class-hero-eyebrow">
        <span class="live-dot" aria-hidden="true"></span>
        <span>YISHU LIVE CLASSROOM</span>
      </div>
      <h1 class="class-hero-title">亿数在线课堂<br><span class="accent">每天与你相约，读懂数字藏品</span></h1>
      <p class="class-hero-subtitle">
        每天一节直播课堂：藏品鉴赏 · 平台指南 · 合规讲堂 · 行业解读。
        微信一键参加，无需下载 App，回放随时看。
      </p>
      <div class="class-hero-stats" role="list" aria-label="课堂数据">
        <div class="class-stat" role="listitem">
          <div class="class-stat-num">1000<span class="unit">人</span></div>
          <div class="class-stat-label">单场并发容量</div>
        </div>
        <div class="class-stat" role="listitem">
          <div class="class-stat-num">2<span class="unit">小时</span></div>
          <div class="class-stat-label">每节标准时长</div>
        </div>
        <div class="class-stat" role="listitem">
          <div class="class-stat-num">7<span class="unit">天</span></div>
          <div class="class-stat-label">每周固定开讲</div>
        </div>
        <div class="class-stat" role="listitem">
          <div class="class-stat-num">100<span class="unit">%</span></div>
          <div class="class-stat-label">私有化 · 零风控</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ========== COMPLIANCE BAR ========== -->
<div class="compliance-bar" role="note" aria-label="课堂规则">
  <div class="compliance-inner">
    <div class="compliance-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
    </div>
    <div class="compliance-text">
      <strong>课堂内容自律：</strong>请勿讨论涉政 / 涉黄 / 涉暴 / 涉赌 / 涉毒 / 侵权内容。课堂数据不落盘、不做无授权录制，讲师对内容负责。⚠️ 数字藏品为文化娱乐产品，不构成投资建议。
    </div>
  </div>
</div>

<!-- ========== TODAY LIVE ========== -->
<section class="today-live">
  <div class="container">
    <div class="today-live-header">
      <div class="today-live-title">
        <span>今日课表</span>
        <span class="today-badge" id="today-badge">TODAY</span>
      </div>
      <div class="today-live-date" id="today-date">加载中...</div>
    </div>
    <div class="class-card-grid" id="class-card-grid">
      <!-- 卡片 1：占位「即将上线」 -->
      <article class="class-card">
        <div class="class-card-cover">
          <span class="class-card-status upcoming">即将上线</span>
          <div class="class-card-cover-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>
          </div>
        </div>
        <div class="class-card-body">
          <div class="class-card-meta">
            <span>藏品鉴赏</span>
            <span class="dot-sep"></span>
            <span>入门级</span>
          </div>
          <h3 class="class-card-title">《小黄龙》系列鉴赏 · 从合成机制到文化脉络</h3>
          <p class="class-card-desc">从设计手稿聊到合成机制，读懂《小黄龙》这一 IP 背后的故事、稀有度体系与收藏价值。</p>
          <div class="class-card-teacher">
            <div class="teacher-avatar" aria-hidden="true">亿</div>
            <div class="teacher-info">
              <div class="teacher-name">亿数运营团队</div>
              <div class="teacher-title">官方讲师</div>
            </div>
          </div>
          <div class="class-card-action">
            <button class="btn btn-primary btn-block" disabled>直播未开始</button>
            <button class="btn btn-ghost">课程详情</button>
          </div>
        </div>
      </article>

      <!-- 卡片 2：占位「即将上线」 -->
      <article class="class-card">
        <div class="class-card-cover gold">
          <span class="class-card-status upcoming">即将上线</span>
          <div class="class-card-cover-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
          </div>
        </div>
        <div class="class-card-body">
          <div class="class-card-meta">
            <span>平台指南</span>
            <span class="dot-sep"></span>
            <span>新手必看</span>
          </div>
          <h3 class="class-card-title">亿数寄售 & 求购全流程 · 一节课学会挂单</h3>
          <p class="class-card-desc">寄售流程、求购机制、限价规则、异常订单处理，看完就能上手操作，避开常见坑点。</p>
          <div class="class-card-teacher">
            <div class="teacher-avatar" aria-hidden="true">运</div>
            <div class="teacher-info">
              <div class="teacher-name">运营小哥</div>
              <div class="teacher-title">平台产品讲师</div>
            </div>
          </div>
          <div class="class-card-action">
            <button class="btn btn-primary btn-block" disabled>直播未开始</button>
            <button class="btn btn-ghost">课程详情</button>
          </div>
        </div>
      </article>

      <!-- 卡片 3：占位「即将上线」 -->
      <article class="class-card">
        <div class="class-card-cover purple-gold">
          <span class="class-card-status upcoming">即将上线</span>
          <div class="class-card-cover-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          </div>
        </div>
        <div class="class-card-body">
          <div class="class-card-meta">
            <span>合规讲堂</span>
            <span class="dot-sep"></span>
            <span>进阶</span>
          </div>
          <h3 class="class-card-title">数字藏品合规红线 · 五证与国标背后的意义</h3>
          <p class="class-card-desc">读懂《区块链信息服务管理规定》、五证的作用、国标起草单位意味着什么，以及为什么要选合规平台。</p>
          <div class="class-card-teacher">
            <div class="teacher-avatar" aria-hidden="true">合</div>
            <div class="teacher-info">
              <div class="teacher-name">合规团队</div>
              <div class="teacher-title">合规讲师</div>
            </div>
          </div>
          <div class="class-card-action">
            <button class="btn btn-primary btn-block" disabled>直播未开始</button>
            <button class="btn btn-ghost">课程详情</button>
          </div>
        </div>
      </article>
    </div>

    <!-- 部署进度提示 -->
    <div class="roadmap-notice">
      <div class="roadmap-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        亿数在线课堂 · 建设进度
      </div>
      <p class="roadmap-desc">
        亿数在线课堂采用<strong style="color: var(--brand);">私有化部署</strong>，服务器完全自建，
        无第三方平台风控，讲师和内容 100% 亿数掌控。目前正在完成部署，预计一周内首场开讲。
      </p>
      <div class="roadmap-steps">
        <div class="roadmap-step">
          <div class="roadmap-step-num">1</div>
          <div class="roadmap-step-title">✅ 前端页面上线</div>
          <div class="roadmap-step-desc">课堂入口页、观看页、课表结构完成</div>
        </div>
        <div class="roadmap-step">
          <div class="roadmap-step-num">2</div>
          <div class="roadmap-step-title">🔨 部署直播服务器</div>
          <div class="roadmap-step-desc">阿里云 ECS + SRS 5.0 私有化部署</div>
        </div>
        <div class="roadmap-step">
          <div class="roadmap-step-num">3</div>
          <div class="roadmap-step-title">🎬 讲师推流联调</div>
          <div class="roadmap-step-desc">OBS 推流测试、码率画质调优</div>
        </div>
        <div class="roadmap-step">
          <div class="roadmap-step-num">4</div>
          <div class="roadmap-step-title">🚀 首场直播开讲</div>
          <div class="roadmap-step-desc">《小黄龙》系列鉴赏首播</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ========== FEATURES ========== -->
<section class="section-pad" aria-label="课堂特色">
  <div class="container">
    <div class="section-header">
      <span class="section-eyebrow">Why Yishu Classroom</span>
      <h2 class="section-title">为什么选亿数在线课堂</h2>
      <p class="section-desc">私有化部署 · 千人容量 · 零平台风控 · 官方直讲</p>
    </div>
    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        </div>
        <div class="feature-title">1000 人并发</div>
        <div class="feature-desc">单场直播支持 1000 人同时在线观看，稳定不卡顿，服务器随容量弹性升级。</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
        </div>
        <div class="feature-title">私有化部署</div>
        <div class="feature-desc">服务器全部由亿数自建，讲课内容 100% 由亿数掌控，不受第三方平台内容审核限制。</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
        </div>
        <div class="feature-title">微信零门槛</div>
        <div class="feature-desc">微信浏览器一键进入，无需下载 App，无需注册第三方账号，扫码即看。</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        </div>
        <div class="feature-title">回放随时看</div>
        <div class="feature-desc">每场直播自动录制，课后 24 小时内上架回放，错过直播不用担心。</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </div>
        <div class="feature-title">实时互动</div>
        <div class="feature-desc">课堂内置弹幕聊天区，观众可发送文字提问，讲师端弹窗接收并现场答疑。</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7h-3V4a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v3H4a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1z"></path><path d="M9 3v4"></path><path d="M15 3v4"></path><path d="M12 12v6"></path><path d="M9 15h6"></path></svg>
        </div>
        <div class="feature-title">官方内容</div>
        <div class="feature-desc">讲师均为亿数官方团队成员，内容原创、权威、准确，杜绝营销话术和投资引导。</div>
      </div>
    </div>
  </div>
</section>

<!-- ========== REPLAYS ========== -->
<section class="section-pad replay-section" aria-label="往期回放">
  <div class="container">
    <div class="section-header">
      <span class="section-eyebrow">Replays</span>
      <h2 class="section-title">往期课堂回放</h2>
      <p class="section-desc">开播后每场直播自动上架回放，你可以随时补课</p>
    </div>
    <div class="replay-grid" id="replay-grid">
      <div class="replay-card" role="listitem" aria-disabled="true">
        <div class="replay-thumb">
          <div class="replay-thumb-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"></path></svg>
          </div>
          <span class="replay-thumb-badge">即将上线</span>
        </div>
        <div class="replay-body">
          <div class="replay-title">首场直播完成后自动上架</div>
          <div class="replay-meta">
            <span>敬请期待</span>
          </div>
        </div>
      </div>
      <div class="replay-card" role="listitem" aria-disabled="true">
        <div class="replay-thumb">
          <div class="replay-thumb-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"></path></svg>
          </div>
          <span class="replay-thumb-badge">即将上线</span>
        </div>
        <div class="replay-body">
          <div class="replay-title">首场直播完成后自动上架</div>
          <div class="replay-meta">
            <span>敬请期待</span>
          </div>
        </div>
      </div>
      <div class="replay-card" role="listitem" aria-disabled="true">
        <div class="replay-thumb">
          <div class="replay-thumb-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"></path></svg>
          </div>
          <span class="replay-thumb-badge">即将上线</span>
        </div>
        <div class="replay-body">
          <div class="replay-title">首场直播完成后自动上架</div>
          <div class="replay-meta">
            <span>敬请期待</span>
          </div>
        </div>
      </div>
      <div class="replay-card" role="listitem" aria-disabled="true">
        <div class="replay-thumb">
          <div class="replay-thumb-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"></path></svg>
          </div>
          <span class="replay-thumb-badge">即将上线</span>
        </div>
        <div class="replay-body">
          <div class="replay-title">首场直播完成后自动上架</div>
          <div class="replay-meta">
            <span>敬请期待</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ========== FAQ ========== -->
<section class="section-pad" aria-label="常见问题">
  <div class="container">
    <div class="section-header">
      <span class="section-eyebrow">FAQ</span>
      <h2 class="section-title">常见问题</h2>
      <p class="section-desc">关于亿数在线课堂的高频问题</p>
    </div>
    <div class="faq-list">
      <details class="faq-item">
        <summary>如何参加亿数在线课堂？</summary>
        <div class="faq-answer">直接用微信浏览器或手机 Safari / Chrome 打开亿数官网，进入「在线会议」栏目，找到当天直播卡片，点击「进入直播」即可观看，全程无需下载 App，无需注册第三方账号。</div>
      </details>
      <details class="faq-item">
        <summary>课堂什么时候开讲？</summary>
        <div class="faq-answer">亿数在线课堂正在完成私有化部署，预计一周内首场开讲。开讲时间、讲师、主题会提前在亿数官网首页、「最新资讯」栏目公布。</div>
      </details>
      <details class="faq-item">
        <summary>单场最多能容纳多少人？</summary>
        <div class="faq-answer">单场直播支持 1000 人同时在线观看。如果单场人数超过预期，服务器会自动弹性升级，不会出现卡顿或掉线。</div>
      </details>
      <details class="faq-item">
        <summary>错过直播了怎么办？可以看回放吗？</summary>
        <div class="faq-answer">每场直播都会自动录制，直播结束后 24 小时内会自动上架到本页「往期回放」栏目，你可以随时点开观看。</div>
      </details>
      <details class="faq-item">
        <summary>观看直播需要付费吗？</summary>
        <div class="faq-answer">亿数在线课堂免费开放给所有亿数用户，不设付费门槛。课堂的价值在于让用户更懂平台、更懂数字藏品，为长期陪伴用户服务。</div>
      </details>
      <details class="faq-item">
        <summary>课堂里能提问吗？</summary>
        <div class="faq-answer">可以。每场直播观看页右侧都有实时弹幕聊天区，你可以发送文字提问，讲师端会弹窗接收，并在课程中现场答疑。</div>
      </details>
      <details class="faq-item">
        <summary>课堂里能讨论数字藏品的投资价值吗？</summary>
        <div class="faq-answer">课堂讲的是数字藏品的<strong>文化价值、设计理念、平台使用方法、合规知识</strong>，不涉及任何形式的投资建议。⚠️ 数字藏品为文化娱乐产品，不构成投资建议，请理性收藏。</div>
      </details>
      <details class="faq-item">
        <summary>课堂内容可以录屏、二次传播吗？</summary>
        <div class="faq-answer">课堂全部内容版权归亿数所有，未经授权禁止录屏、剪辑、二次上传到第三方平台。个人学习收藏欢迎在本页看回放。</div>
      </details>
    </div>
  </div>
</section>

__FOOTER__

<script>
// 显示今天日期
(function(){
  var d = new Date();
  var day = ['日','一','二','三','四','五','六'][d.getDay()];
  var el = document.getElementById('today-date');
  if (el) {
    el.textContent = d.getFullYear() + '年' + (d.getMonth()+1) + '月' + d.getDate() + '日 · 星期' + day;
  }
})();
// mobile nav
(function(){
  var btn = document.getElementById('mobileMenuBtn');
  var nav = document.getElementById('navLinks');
  if (btn && nav) {
    btn.addEventListener('click', function(){
      nav.classList.toggle('show');
      btn.setAttribute('aria-expanded', nav.classList.contains('show'));
    });
  }
})();
</script>

</body>
</html>
'''

MEETING_HTML = MEETING_HTML.replace('__MEETING_CSS__', MEETING_CSS).replace('__NAV__', NAV_HTML).replace('__FOOTER__', FOOTER_HTML)

with open(os.path.join(ROOT, 'meeting.html'), 'w', encoding='utf-8') as f:
    f.write(MEETING_HTML)

print('meeting.html 写入完成，字节数:', os.path.getsize(os.path.join(ROOT, 'meeting.html')))

# ================================================================
# room.html  ——  课堂观看页（预留播放器 + 弹幕）
# ================================================================

ROOM_CSS = BASE_CSS + '''
/* Room Layout */
.room-body { background: #0a0a1a; color: #f0f0f5; min-height: 100vh; }
.room-body .nav { background: rgba(10,10,26,0.85); border-bottom-color: rgba(255,255,255,0.08); }
.room-body .nav-logo, .room-body .nav-links a { color: rgba(255,255,255,0.9); }
.room-body .nav-links a { color: rgba(255,255,255,0.6); }
.room-body .nav-links a:hover, .room-body .nav-links a.active { color: white; }
.room-body .nav-mobile-btn svg { color: white; }
.room-body .nav-mobile-btn { color: white; }

.room-wrap { max-width: 1400px; margin: 0 auto; padding: calc(var(--nav-height) + var(--space-6)) var(--space-6) var(--space-8); }

.room-hero { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-5); flex-wrap: wrap; gap: var(--space-3); }
.room-hero-left { display: flex; align-items: center; gap: var(--space-4); flex: 1; min-width: 0; }
.room-status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; flex-shrink: 0; }
.room-status-badge.live { background: #ef4444; color: white; }
.room-status-badge.live .dot { width: 6px; height: 6px; border-radius: 50%; background: white; animation: pulse 1.6s ease-in-out infinite; }
.room-status-badge.upcoming { background: rgba(212,175,55,0.2); color: var(--gold); border: 1px solid rgba(212,175,55,0.4); }
.room-status-badge.ended { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 4px rgba(239,68,68,0.25); } 50% { box-shadow: 0 0 0 8px rgba(239,68,68,0.08); } }
.room-title { font-size: 22px; font-weight: 700; color: white; line-height: 1.4; margin: 0; }
.room-hero-right { display: flex; align-items: center; gap: var(--space-3); font-size: 13px; color: rgba(255,255,255,0.6); }
.room-viewers { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(255,255,255,0.06); border-radius: var(--radius-full); }
.room-viewers svg { width: 14px; height: 14px; }

.room-main { display: grid; grid-template-columns: 1fr 340px; gap: var(--space-5); }

/* Player */
.player-wrap { background: #000; border-radius: var(--radius-lg); overflow: hidden; position: relative; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; }
.player-placeholder { text-align: center; color: rgba(255,255,255,0.7); padding: var(--space-8); }
.player-placeholder-icon { width: 72px; height: 72px; margin: 0 auto var(--space-4); border-radius: 50%; background: rgba(91,95,199,0.20); display: flex; align-items: center; justify-content: center; color: var(--brand-light); }
.player-placeholder-icon svg { width: 36px; height: 36px; }
.player-placeholder-title { font-size: 18px; font-weight: 600; color: white; margin-bottom: var(--space-2); }
.player-placeholder-desc { font-size: 14px; color: rgba(255,255,255,0.55); line-height: 1.6; max-width: 380px; margin: 0 auto; }
#video-el { width: 100%; height: 100%; object-fit: contain; background: #000; display: none; }
.player-controls { display: none; }

/* Player Info */
.player-info { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: var(--radius-lg); padding: var(--space-5); margin-top: var(--space-4); }
.player-teacher { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }
.player-teacher-avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--gold)); display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: 700; flex-shrink: 0; }
.player-teacher-name { font-size: 15px; font-weight: 600; color: white; }
.player-teacher-title { font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 2px; }
.player-abstract { font-size: 14px; line-height: 1.75; color: rgba(255,255,255,0.75); }
.player-abstract strong { color: white; }
.player-outline { margin-top: var(--space-4); padding-top: var(--space-4); border-top: 1px solid rgba(255,255,255,0.06); }
.player-outline h4 { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.85); margin-bottom: var(--space-3); letter-spacing: 0.6px; text-transform: uppercase; }
.player-outline ul { list-style: none; }
.player-outline li { padding: 8px 0; font-size: 13.5px; color: rgba(255,255,255,0.72); border-bottom: 1px dashed rgba(255,255,255,0.05); display: flex; align-items: center; gap: 10px; }
.player-outline li:last-child { border-bottom: 0; }
.player-outline li .time { color: var(--gold); font-family: monospace; font-size: 12px; flex-shrink: 0; }

/* Compliance mini */
.room-compliance { margin-top: var(--space-5); padding: var(--space-4) var(--space-5); background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.15); border-radius: var(--radius-md); font-size: 12.5px; color: rgba(212,175,55,0.9); line-height: 1.65; }
.room-compliance strong { color: var(--gold); }

/* Chat */
.chat-wrap { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: var(--radius-lg); display: flex; flex-direction: column; height: calc(100vh - var(--nav-height) - 200px); min-height: 520px; overflow: hidden; }
.chat-header { padding: var(--space-4) var(--space-5); border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: space-between; }
.chat-title { font-size: 14px; font-weight: 600; color: white; display: flex; align-items: center; gap: 8px; }
.chat-title svg { width: 16px; height: 16px; color: var(--brand-light); }
.chat-online { font-size: 12px; color: rgba(255,255,255,0.5); }
.chat-messages { flex: 1; overflow-y: auto; padding: var(--space-4) var(--space-5); display: flex; flex-direction: column; gap: var(--space-3); }
.chat-messages::-webkit-scrollbar { width: 6px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
.chat-msg { font-size: 13.5px; line-height: 1.55; }
.chat-msg .user { color: var(--brand-light); font-weight: 600; margin-right: 6px; }
.chat-msg.official .user { color: var(--gold); }
.chat-msg .content { color: rgba(255,255,255,0.85); }
.chat-msg .time { color: rgba(255,255,255,0.35); font-size: 11px; margin-right: 6px; }
.chat-empty { text-align: center; padding: var(--space-12) var(--space-4); color: rgba(255,255,255,0.4); font-size: 13px; }
.chat-empty svg { width: 40px; height: 40px; margin: 0 auto var(--space-3); opacity: 0.4; display: block; }
.chat-input-wrap { padding: var(--space-3) var(--space-4); border-top: 1px solid rgba(255,255,255,0.06); }
.chat-input-inner { display: flex; gap: 8px; }
.chat-input { flex: 1; padding: 10px 14px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-full); color: white; font-size: 13.5px; outline: none; transition: border-color var(--duration-fast); }
.chat-input:focus { border-color: var(--brand-light); }
.chat-input:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-input::placeholder { color: rgba(255,255,255,0.35); }
.chat-send { padding: 10px 18px; background: var(--brand); color: white; border-radius: var(--radius-full); font-size: 13.5px; font-weight: 600; transition: background var(--duration-fast); }
.chat-send:hover:not(:disabled) { background: var(--brand-dark); }
.chat-send:disabled { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.4); cursor: not-allowed; }
.chat-hint { padding: 6px var(--space-4) 0; font-size: 11px; color: rgba(255,255,255,0.35); line-height: 1.5; }

/* Footer */
.room-body .footer { background: #050510; margin-top: var(--space-12); }

@media (max-width: 1024px) {
  .room-main { grid-template-columns: 1fr; }
  .chat-wrap { height: 480px; }
}
'''

ROOM_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="format-detection" content="telephone=no">
<title>课堂直播 — 亿数在线课堂</title>
<meta name="description" content="亿数在线课堂直播观看页——数字藏品课堂实时播出，1000 人容量，微信一键参与。">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://yishuzichan.cc/room.html">
<link rel="icon" type="image/x-icon" href="./images/favicon.ico">
<meta name="theme-color" content="#0a0a1a">
<style>__ROOM_CSS__</style>
</head>
<body class="room-body">

__NAV__

<main class="room-wrap">
  <div class="room-hero">
    <div class="room-hero-left">
      <span class="room-status-badge upcoming" id="room-status">
        <span>直播未开始</span>
      </span>
      <h1 class="room-title" id="room-title">《小黄龙》系列鉴赏 · 从合成机制到文化脉络</h1>
    </div>
    <div class="room-hero-right">
      <div class="room-viewers" id="room-viewers">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
        <span id="viewer-count">0</span> 人观看
      </div>
    </div>
  </div>

  <div class="room-main">
    <!-- LEFT: Player + Info -->
    <div class="room-left">
      <div class="player-wrap">
        <!-- 播放器占位（后期换成 flv.js） -->
        <div class="player-placeholder" id="player-placeholder">
          <div class="player-placeholder-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>
          </div>
          <div class="player-placeholder-title">直播尚未开始</div>
          <div class="player-placeholder-desc">
            亿数在线课堂正在完成私有化服务器部署，预计一周内首场开讲。<br>
            开讲后本页面将自动播放直播信号，无需刷新。
          </div>
        </div>
        <!-- 视频元素（后期启用） -->
        <video id="video-el" controls autoplay muted playsinline></video>
      </div>

      <div class="player-info">
        <div class="player-teacher">
          <div class="player-teacher-avatar" aria-hidden="true">亿</div>
          <div>
            <div class="player-teacher-name">亿数运营团队</div>
            <div class="player-teacher-title">官方讲师 · 藏品鉴赏组</div>
          </div>
        </div>
        <div class="player-abstract">
          <strong>课程简介：</strong>从《小黄龙》的设计手稿聊起，为你揭秘这一 IP 背后的创作故事、稀有度体系、合成机制与文化价值。课程涵盖：小黄龙的诞生、五种稀有度的差异、合成路径、以及为什么它成为亿象生态的代表 IP 之一。
        </div>
        <div class="player-outline">
          <h4>课程大纲</h4>
          <ul>
            <li><span class="time">00:00</span> <span>开场：为什么是小黄龙</span></li>
            <li><span class="time">10:00</span> <span>设计手稿背后的文化脉络</span></li>
            <li><span class="time">30:00</span> <span>五种稀有度的差异与鉴赏要点</span></li>
            <li><span class="time">55:00</span> <span>合成机制详解 · 一步步演示</span></li>
            <li><span class="time">80:00</span> <span>Q&A：观众提问答疑</span></li>
          </ul>
        </div>
      </div>

      <div class="room-compliance">
        <strong>⚠️ 课堂内容自律：</strong>请勿讨论涉政 / 涉黄 / 涉暴 / 涉赌 / 涉毒 / 侵权内容。数字藏品为文化娱乐产品，不构成投资建议。
      </div>
    </div>

    <!-- RIGHT: Chat -->
    <aside class="chat-wrap" aria-label="课堂互动区">
      <div class="chat-header">
        <div class="chat-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          <span>课堂互动</span>
        </div>
        <div class="chat-online" id="chat-online">— 人在线</div>
      </div>
      <div class="chat-messages" id="chat-messages">
        <div class="chat-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          <div>直播开始后<br>互动区将自动开启</div>
        </div>
      </div>
      <div class="chat-input-wrap">
        <div class="chat-input-inner">
          <input class="chat-input" id="chat-input" type="text" placeholder="直播开始后可发送弹幕..." disabled maxlength="80">
          <button class="chat-send" id="chat-send" disabled>发送</button>
        </div>
        <div class="chat-hint">发言即代表你同意遵守《课堂内容自律》规范。</div>
      </div>
    </aside>
  </div>
</main>

__FOOTER__

<script>
// mobile nav
(function(){
  var btn = document.getElementById('mobileMenuBtn');
  var nav = document.getElementById('navLinks');
  if (btn && nav) {
    btn.addEventListener('click', function(){
      nav.classList.toggle('show');
      btn.setAttribute('aria-expanded', nav.classList.contains('show'));
    });
  }
})();

/*
 * 直播接入点位（预留）
 * 当 SRS 私有化服务器就绪后，把以下 config 中的 URL 换成实际拉流地址即可自动生效：
 *
 * window.YISHU_LIVE_CONFIG = {
 *   enabled: true,
 *   streamUrl: 'https://live.yishuzichan.cn/live/room1.flv',  // HTTP-FLV
 *   backupUrl: 'https://live.yishuzichan.cn/live/room1.m3u8', // HLS 兜底
 *   chatWs: 'wss://live.yishuzichan.cn/chat',
 * };
 *
 * 页面会自动隐藏 placeholder、显示 video，并连接弹幕 WebSocket。
 */
(function initLive(){
  var cfg = window.YISHU_LIVE_CONFIG;
  if (!cfg || !cfg.enabled) return;
  var video = document.getElementById('video-el');
  var placeholder = document.getElementById('player-placeholder');
  if (!video || !placeholder) return;
  // 后期启用时的 stub
  placeholder.style.display = 'none';
  video.style.display = 'block';
  video.src = cfg.backupUrl || cfg.streamUrl;
})();
</script>

</body>
</html>
'''

ROOM_HTML = ROOM_HTML.replace('__ROOM_CSS__', ROOM_CSS).replace('__NAV__', NAV_HTML).replace('__FOOTER__', FOOTER_HTML)

with open(os.path.join(ROOT, 'room.html'), 'w', encoding='utf-8') as f:
    f.write(ROOM_HTML)

print('room.html 写入完成，字节数:', os.path.getsize(os.path.join(ROOT, 'room.html')))

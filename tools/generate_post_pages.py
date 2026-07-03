#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 posts.json 中每条公告生成独立静态 HTML 页（posts/{id}.html）。
每个页面含完整 SSR 正文 + 独立 SEO meta + OG/Twitter + NewsArticle & BreadcrumbList JSON-LD。
可选：仅生成指定 id 列表（增量同步场景）。

用法：
  python3 tools/generate_post_pages.py             # 全量
  python3 tools/generate_post_pages.py --ids id1 id2 id3  # 增量
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')
POSTS_DIR = os.path.join(WEBSITE, 'posts')

TZ_CN = timezone(timedelta(hours=8))

# =========================================================================
# 简易 Markdown → HTML 渲染器（不依赖外部库，覆盖公告常用语法）
# =========================================================================

def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _render_inline(text: str) -> str:
    """渲染行内 Markdown：bold / italic / code / links / images。"""
    # 保护已有的 HTML 标签不被再次转义（我们只在最终输出时转义原始文本）
    # 这里 text 已经是转义过的，所以直接处理
    # image: ![alt](url)
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)',
        lambda m: (
            f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy" '
            f'referrerpolicy="no-referrer"'
            + (f' title="{m.group(3)}"' if m.group(3) else '')
            + '>'
        ),
        text,
    )
    # link: [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)\s]+)\)',
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
        text,
    )
    # inline code: `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # bold + italic ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic *text* or _text_
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', text)
    return text


def md_to_html(md: str) -> str:
    """把 Markdown 渲染成 HTML 片段。"""
    if not md:
        return ''
    md = md.replace('\r\n', '\n')
    lines = md.split('\n')
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # ---- 代码块 ```
        m_code = re.match(r'^```(\w*)\s*$', line)
        if m_code:
            lang = m_code.group(1)
            buf = []
            i += 1
            while i < n and not re.match(r'^```\s*$', lines[i]):
                buf.append(_escape(lines[i]))
                i += 1
            i += 1  # skip closing ```
            cls = f' language-{lang}' if lang else ''
            out.append(f'<pre><code{cls}>' + '\n'.join(buf) + '</code></pre>')
            continue

        # ---- 表格（连续 | 行）
        if line.startswith('|') and '|' in line[1:]:
            # 收集所有 | 行
            rows = []
            while i < n and lines[i].startswith('|') and '|' in lines[i][1:]:
                rows.append(lines[i])
                i += 1
            if len(rows) >= 2:
                # 第一行表头，第二行分隔(---)，之后数据
                header = [c.strip() for c in rows[0].strip('|').split('|')]
                body_rows = rows[2:]  # skip separator
                html_rows = [
                    '<tr>' + ''.join(f'<th>{_render_inline(_escape(c))}</th>' for c in header) + '</tr>'
                ]
                for r in body_rows:
                    cells = [c.strip() for c in r.strip('|').split('|')]
                    html_rows.append(
                        '<tr>' + ''.join(f'<td>{_render_inline(_escape(c))}</td>' for c in cells) + '</tr>'
                    )
                out.append('<table>' + ''.join(html_rows) + '</table>')
                continue

        # ---- 水平线
        if re.match(r'^(\s*[-*_]){3,}\s*$', line):
            out.append('<hr>')
            i += 1
            continue

        # ---- 标题 #
        m_h = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m_h:
            lvl = len(m_h.group(1))
            txt = _render_inline(_escape(m_h.group(2).strip()))
            out.append(f'<h{lvl}>{txt}</h{lvl}>')
            i += 1
            continue

        # ---- 引用块 >
        if line.startswith('>'):
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            inner = md_to_html('\n'.join(buf))
            out.append(f'<blockquote>{inner}</blockquote>')
            continue

        # ---- 无序列表
        if re.match(r'^(\s*)([-*+])\s+', line):
            items = []
            while i < n and re.match(r'^(\s*)([-*+])\s+', lines[i]):
                m_li = re.match(r'^(\s*)([-*+])\s+(.*)$', lines[i])
                items.append(_render_inline(_escape(m_li.group(3))))
                i += 1
            out.append('<ul>' + ''.join(f'<li>{it}</li>' for it in items) + '</ul>')
            continue

        # ---- 有序列表
        if re.match(r'^(\s*)\d+\.\s+', line):
            items = []
            while i < n and re.match(r'^(\s*)\d+\.\s+', lines[i]):
                m_li = re.match(r'^(\s*)\d+\.\s+(.*)$', lines[i])
                items.append(_render_inline(_escape(m_li.group(2))))
                i += 1
            out.append('<ol>' + ''.join(f'<li>{it}</li>' for it in items) + '</ol>')
            continue

        # ---- 空行
        if line.strip() == '':
            i += 1
            continue

        # ---- 段落：累积到空行为止
        para = [line]
        i += 1
        while i < n:
            nl = lines[i]
            if nl.strip() == '' or nl.startswith('#') or nl.startswith('```') or nl.startswith('|') or nl.startswith('>') or re.match(r'^(\s*[-*_]){3,}\s*$', nl) or re.match(r'^(\s*)([-*+])\s+', nl) or re.match(r'^(\s*)\d+\.\s+', nl):
                break
            para.append(nl)
            i += 1
        text = _render_inline(_escape('\n'.join(para)))
        # <br> 处理硬换行
        text = text.replace('\n', '<br>\n')
        out.append(f'<p>{text}</p>')

    return '\n'.join(out)


# =========================================================================
# 工具函数
# =========================================================================

def fmt_date(ts_ms) -> str:
    if not ts_ms:
        return ''
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000, TZ_CN).strftime('%Y-%m-%d')
    except Exception:
        return ''


def fmt_iso(ts_ms) -> str:
    """ISO-8601 UTC+8（schema.org 期望）。"""
    if not ts_ms:
        return ''
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000, TZ_CN).strftime('%Y-%m-%dT%H:%M:%S+08:00')
    except Exception:
        return ''


def fmt_full_date(ts_ms) -> str:
    if not ts_ms:
        return ''
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000, TZ_CN).strftime('%Y年%m月%d日')
    except Exception:
        return ''


def strip_markdown(text: str) -> str:
    """去 Markdown 语法 → 纯文本。"""
    if not text:
        return ''
    # 图片先去掉
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    # 链接保留文字
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 代码块 / 行内代码去掉
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 标题符号 / 粗体斜体 / 引用
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', text)
    text = re.sub(r'^>\s*', '', text, flags=re.M)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.M)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.M)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def need_risk_notice(post: dict) -> bool:
    text = ((post.get('title') or '') + ' ' + (post.get('content') or '') + ' ' + ' '.join(post.get('tags') or [])).lower()
    kws = [
        # 直接术语
        '数字资产', '数字藏品', '数藏', '文创',
        # 交易 & 玩法
        '合成', '寄售', '开放交易', '限价', '求购', '空投', '销毁', '大礼包',
        # 亿数生态资产名 / 产品线
        '瓦当', '通宝', '之钥', '嘉年华', '亿象', '出发吧夏天', '疯狂路亚', '卷卷猫',
        '五路财神', '山海归序', '赤髯龙', '敬仲龙', '飞鱼引擎', '飞鱼', '飞行卡',
        # 活动 / 邀新 / 首发
        '首发', '邀新', '限定',
        # 合规 / 政策相关
        '违规', '数字文化',
    ]
    for kw in kws:
        if kw in text:
            return True
    # 兜底：分类为「合规公告」的一律加提示
    tags = post.get('tags') or []
    for t in tags:
        if '公告' in t and t != '平台公告':
            return True
    return False


def classify_post(post: dict) -> dict:
    tag_map = [
        {'keywords': ['邀新', '邀请', '福利', '拓生态', '嘉年华', '大礼包', '生态', '商城', '飞行卡', '身份'], 'name': '生态进展', 'cls': 'green'},
        {'keywords': ['限价', '异常', '通告', '违规', '规范', '合规', '调整'], 'name': '合规公告', 'cls': 'purple'},
        {'keywords': ['行业', '政策', '解读', '日报', '风口', '文旅', '媒体', '报道'], 'name': '行业洞察', 'cls': 'gold'},
    ]
    text = (post.get('title') or '') + ' ' + ' '.join(post.get('tags') or [])
    for group in tag_map:
        for kw in group['keywords']:
            if kw in text:
                return group
    return {'name': '平台动态', 'cls': 'blue'}


def _force_https(url: str) -> str:
    if url.startswith('http://eopcos.yishuzichan.cn'):
        return 'https://' + url[len('http://'):]
    return url


def pick_cover(post: dict) -> str:
    """挑第一张图作为 OG 封面图。CDN 强制 https。"""
    content = post.get('content') or ''
    m = re.search(r'!\[[^\]]*\]\(([^)\s]+)\)', content)
    if m:
        return _force_https(m.group(1))
    return 'https://yishuzichan.cc/images/es-logo.png'


def fallback_desc(post: dict) -> str:
    """当正文全是图片、无纯文本时的兜底摘要。"""
    tags = ' '.join(post.get('tags') or [])
    return f"亿数官方公告：{post.get('title','')}。{tags}。亿数是AI驱动的数实融合生态平台，官网 https://yishuzichan.cc"


# =========================================================================
# 单页模板
# =========================================================================

NAV_HTML = '''
<nav class="nav" role="navigation" aria-label="主导航">
  <div class="nav-inner">
    <a href="../index.html" class="nav-logo" aria-label="亿数首页">
      <img src="../images/yishu-logo-nav.png" alt="亿数Logo" fetchpriority="high" decoding="async">
      <span>亿数</span>
    </a>
    <div class="nav-links" role="menubar">
      <a href="../about.html">关于我们</a>
      <a href="../products.html">IP矩阵</a>
      <a href="../ecosystem.html">生态版图</a>
      <a href="../news.html" class="active">最新资讯</a>
      <a href="../media.html">相关媒体</a>
      <a href="https://f59962zb6q.coze.site/admin" target="_blank" rel="noopener noreferrer">会议签到</a>
      <a href="../contact.html">联系我们</a>
    </div>
    <a href="https://www.yishuzichan.cn/signup?inviteCode=HBEV2B" target="_blank" rel="noopener noreferrer" class="nav-cta">进入亿数</a>
  </div>
</nav>
'''

FOOTER_HTML = '''
<footer class="footer" aria-label="页脚">
  <div class="container">
    <div class="footer-inner">
      <div class="footer-brand">
        <img src="../images/yishu-logo-nav.png" alt="亿数Logo" loading="lazy" decoding="async">
        <span>亿数</span>
      </div>
      <div class="footer-copy">
        <small>© 2026 亿数 · AI驱动数实融合生态 · 以数兴商，链接未来</small>
      </div>
      <nav class="footer-links" aria-label="底部链接">
        <a href="https://yishuzichan.cn" target="_blank" rel="noopener noreferrer">交易平台</a>
        <a href="../about.html">关于我们</a>
        <a href="../contact.html">联系方式</a>
      </nav>
    </div>
  </div>
</footer>
'''

CSS_HTML = '''
:root {
  --brand: #5B5FC7; --brand-light: #7B7FD9; --brand-dark: #4A4EA8;
  --gold: #D4AF37; --gold-light: #E8C94A;
  --surface-0: #FFFFFF; --surface-1: #FAFBFD; --surface-2: #F3F4F6;
  --surface-3: #E5E7EB; --surface-4: #D1D5DB;
  --text-primary: #1A1A2E; --text-secondary: #6B7280;
  --border-subtle: #E5E7EB;
  --font: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
  --space-12: 48px; --space-16: 64px; --space-20: 80px;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-full: 9999px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-card: 0 2px 12px rgba(0,0,0,0.06);
  --ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);
  --max-width: 1200px; --nav-height: 64px;
  --duration-fast: 0.15s; --duration-normal: 0.3s;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body { font-family: var(--font); background: var(--surface-0); color: var(--text-primary); line-height: 1.6; overflow-x: hidden; }
img { max-width: 100%; height: auto; display: block; }
a { color: inherit; text-decoration: none; }
.container { max-width: 860px; margin: 0 auto; padding: 0 var(--space-6); }

.nav { position: fixed; top: 0; left: 0; right: 0; height: var(--nav-height); background: rgba(255,255,255,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--border-subtle); z-index: 100; }
.nav-inner { max-width: var(--max-width); margin: 0 auto; height: 100%; display: flex; align-items: center; justify-content: space-between; padding: 0 var(--space-6); }
.nav-logo { display: flex; align-items: center; gap: var(--space-2); font-size: 20px; font-weight: 700; color: var(--brand); }
.nav-logo img { height: 32px; width: auto; }
.nav-links { display: flex; align-items: center; gap: var(--space-8); }
.nav-links a { font-size: 14px; font-weight: 500; color: var(--text-secondary); transition: color var(--duration-fast) var(--ease-smooth); position: relative; }
.nav-links a:hover { color: var(--text-primary); }
.nav-links a.active { color: var(--brand); }
.nav-links a.active::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 100%; height: 2px; background: var(--brand); }
.nav-cta { padding: 8px 20px; background: var(--brand); color: white !important; border-radius: var(--radius-full); font-size: 14px; font-weight: 600; }
.nav-cta:hover { background: var(--brand-dark); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(91,95,199,0.3); }
@media (max-width: 768px) {
  .nav-links { display: none; }
}

.breadcrumb { padding-top: calc(var(--nav-height) + var(--space-8)); background: var(--surface-1); border-bottom: 1px solid var(--border-subtle); }
.breadcrumb-inner { padding: var(--space-4) 0; display: flex; align-items: center; gap: var(--space-2); font-size: 13px; color: var(--text-secondary); }
.breadcrumb-inner a { color: var(--text-secondary); }
.breadcrumb-inner a:hover { color: var(--brand); }
.breadcrumb-inner .current { color: var(--text-primary); font-weight: 500; max-width: 560px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.article-wrap { padding: var(--space-12) 0 var(--space-20); }
.article-meta { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-3); margin-bottom: var(--space-5); font-size: 13px; color: var(--text-secondary); }
.article-tag { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; }
.article-tag.blue { background: rgba(91,95,199,0.1); color: var(--brand); }
.article-tag.green { background: rgba(16,185,129,0.1); color: #10B981; }
.article-tag.purple { background: rgba(139,92,246,0.1); color: #8B5CF6; }
.article-tag.gold { background: rgba(212,175,55,0.12); color: #B8971F; }
.article-meta-dot { width: 3px; height: 3px; background: var(--surface-4); border-radius: 50%; }

.article-title { font-size: clamp(24px, 4vw, 40px); font-weight: 700; line-height: 1.3; color: var(--text-primary); margin-bottom: var(--space-4); letter-spacing: -0.01em; }
.article-source { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-10); padding: var(--space-4) var(--space-5); background: var(--surface-1); border-left: 3px solid var(--brand); border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 13px; color: var(--text-secondary); }
.article-source strong { color: var(--brand); font-weight: 600; }

.article-content { font-size: 16px; line-height: 1.85; color: var(--text-primary); }
.article-content h1, .article-content h2, .article-content h3, .article-content h4 { color: var(--text-primary); font-weight: 700; line-height: 1.4; margin: var(--space-10) 0 var(--space-4); }
.article-content h1 { font-size: 28px; }
.article-content h2 { font-size: 24px; padding-bottom: var(--space-3); border-bottom: 1px solid var(--border-subtle); }
.article-content h3 { font-size: 20px; }
.article-content h4 { font-size: 18px; }
.article-content p { margin: var(--space-4) 0; }
.article-content ul, .article-content ol { margin: var(--space-4) 0 var(--space-4) var(--space-6); padding: 0; }
.article-content ul { list-style: disc; }
.article-content ol { list-style: decimal; }
.article-content li { margin: var(--space-2) 0; }
.article-content li::marker { color: var(--brand); }
.article-content strong { color: var(--brand-dark); font-weight: 600; }
.article-content code { background: var(--surface-2); padding: 2px 8px; border-radius: var(--radius-sm); font-family: 'SF Mono', Consolas, monospace; font-size: 0.9em; color: var(--brand-dark); }
.article-content pre { background: #1A1A2E; color: #E5E7EB; padding: var(--space-5); border-radius: var(--radius-md); overflow-x: auto; margin: var(--space-5) 0; }
.article-content pre code { background: transparent; color: inherit; padding: 0; }
.article-content blockquote { margin: var(--space-5) 0; padding: var(--space-4) var(--space-5); border-left: 4px solid var(--brand); background: var(--surface-1); border-radius: 0 var(--radius-md) var(--radius-md) 0; color: var(--text-secondary); }
.article-content a { color: var(--brand); text-decoration: underline; text-underline-offset: 3px; word-break: break-word; }
.article-content img { margin: var(--space-6) auto; border-radius: var(--radius-md); box-shadow: var(--shadow-card); max-width: 100%; }
.article-content hr { border: none; height: 1px; background: var(--border-subtle); margin: var(--space-8) 0; }
.article-content table { width: 100%; border-collapse: collapse; margin: var(--space-5) 0; font-size: 14px; }
.article-content th, .article-content td { padding: var(--space-3) var(--space-4); border: 1px solid var(--border-subtle); text-align: left; }
.article-content th { background: var(--surface-1); font-weight: 600; color: var(--text-primary); }

.risk-notice { margin-top: var(--space-10); padding: var(--space-4) var(--space-5); background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(212,175,55,0.03)); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); font-size: 13px; color: #7A5F00; display: flex; align-items: flex-start; gap: var(--space-3); }
.risk-notice-icon { flex-shrink: 0; font-size: 18px; line-height: 1; }

.article-actions { display: flex; align-items: center; justify-content: space-between; margin-top: var(--space-12); padding-top: var(--space-8); border-top: 1px solid var(--border-subtle); flex-wrap: wrap; gap: var(--space-4); }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: 12px 24px; border-radius: var(--radius-full); font-size: 14px; font-weight: 600; cursor: pointer; border: none; font-family: inherit; }
.btn-primary { background: var(--brand); color: white; }
.btn-primary:hover { background: var(--brand-dark); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(91,95,199,0.3); }
.btn-ghost { background: transparent; color: var(--text-secondary); border: 1px solid var(--border-subtle); }
.btn-ghost:hover { color: var(--brand); border-color: var(--brand); background: rgba(91,95,199,0.05); }

.footer { background: #1A1A2E; color: white; padding: var(--space-12) 0; }
.footer-inner { display: flex; flex-direction: column; align-items: center; gap: var(--space-6); text-align: center; }
.footer-brand { display: flex; align-items: center; gap: var(--space-3); }
.footer-brand img { height: 36px; width: auto; }
.footer-brand span { font-size: 24px; font-weight: 700; color: white; }
.footer-copy small { color: rgba(255,255,255,0.5); }
.footer-links { display: flex; gap: var(--space-6); }
.footer-links a { font-size: 14px; color: rgba(255,255,255,0.6); }
.footer-links a:hover { color: white; }

@media (max-width: 768px) {
  .container { padding: 0 var(--space-5); }
  .article-wrap { padding: var(--space-8) 0 var(--space-12); }
  .article-title { font-size: 24px; }
  .article-content { font-size: 15px; }
  .article-actions { flex-direction: column-reverse; align-items: stretch; }
  .btn { justify-content: center; }
}
'''


def build_head(post: dict, body_html: str, plain_desc: str, cover_url: str, date_iso: str) -> str:
    pid = post['id']
    title_raw = post.get('title') or '亿数公告'
    title_esc = _escape(title_raw)
    # 独立 meta description（≤150 字）
    desc = plain_desc[:150] if plain_desc else '亿数平台公告：' + title_raw
    desc = _escape(desc)
    tags = post.get('tags') or []
    keywords = '亿数,' + '亿数公告,' + ','.join(tags) + ',亿数资产,亿数ES,数实融合'
    tag = classify_post(post)
    canonical = f'https://yishuzichan.cc/posts/{pid}.html'
    date_fmt = fmt_full_date(post.get('publishAt'))
    view_count = post.get('viewCount') or 0

    # JSON-LD
    news_article = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': title_raw,
        'url': canonical,
        'datePublished': date_iso,
        'dateModified': date_iso,
        'image': [cover_url],
        'articleBody': plain_desc[:2000] if plain_desc else title_raw,
        'inLanguage': 'zh-CN',
        'wordCount': len(plain_desc or ''),
        'keywords': ','.join(tags),
        'author': {
            '@type': 'Organization',
            'name': '亿数',
            'url': 'https://yishuzichan.cc',
        },
        'publisher': {
            '@type': 'Organization',
            'name': '亿数',
            'url': 'https://yishuzichan.cc',
            'logo': {
                '@type': 'ImageObject',
                'url': 'https://yishuzichan.cc/images/es-logo.png',
            },
        },
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': canonical,
        },
    }
    breadcrumb = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '首页', 'item': 'https://yishuzichan.cc/'},
            {'@type': 'ListItem', 'position': 2, 'name': '最新资讯', 'item': 'https://yishuzichan.cc/news.html'},
            {'@type': 'ListItem', 'position': 3, 'name': title_raw, 'item': canonical},
        ],
    }

    risk_block = ''
    if need_risk_notice(post):
        risk_block = '''
      <div class="risk-notice">
        <span class="risk-notice-icon">⚠️</span>
        <div class="risk-notice-text">数字藏品为文化娱乐产品，不构成投资建议。请通过合规渠道理性参与，警惕炒作风险。</div>
      </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="no-referrer">
<meta name="format-detection" content="telephone=no">

<title>{title_esc} — 亿数</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{_escape(keywords)}">
<meta name="author" content="亿数">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">

<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/x-icon" href="../images/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="../images/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="../images/apple-touch-icon.png">
<link rel="manifest" href="../site.webmanifest">
<meta name="theme-color" content="#0a1628">

<meta property="og:type" content="article">
<meta property="og:site_name" content="亿数">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{cover_url}">
<meta property="og:locale" content="zh_CN">
<meta property="article:published_time" content="{date_iso}">
<meta property="article:section" content="{_escape(tag['name'])}">
<meta property="article:tag" content="{_escape(','.join(tags))}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_esc}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{cover_url}">

<script type="application/ld+json">
{json.dumps(news_article, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
</script>

<style>{CSS_HTML}</style>
<link rel="stylesheet" href="../assets/theme-dark.css">
</head>
<body>

{NAV_HTML}

<div class="breadcrumb">
  <div class="container">
    <div class="breadcrumb-inner">
      <a href="../index.html">首页</a>
      <span>/</span>
      <a href="../news.html">最新资讯</a>
      <span>/</span>
      <span class="current">{title_esc}</span>
    </div>
  </div>
</div>

<main class="article-wrap">
  <div class="container">
    <article>
      <div class="article-meta">
        <span class="article-tag {tag['cls']}">{_escape(tag['name'])}</span>
        <span class="article-meta-dot"></span>
        <time datetime="{date_iso}">{_escape(date_fmt)}</time>
        <span class="article-meta-dot"></span>
        <span>阅读 {view_count:,}</span>
      </div>
      <h1 class="article-title">{title_esc}</h1>
      <div class="article-source">
        <span class="icon-inline" aria-hidden="true"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 11-5.8-1.6"/></svg></span>
        <div>本文由 <strong>亿数</strong> 官方发布 · 内容源自 <strong>亿数主平台 CMS</strong> · 转载请注明出处</div>
      </div>
      <div class="article-content">
{body_html}
      </div>
{risk_block}
      <div class="article-actions">
        <a href="../news.html" class="btn btn-ghost">
          ← 返回资讯列表
        </a>
        <a href="https://www.yishuzichan.cn/signup?inviteCode=HBEV2B" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
          进入亿数平台 →
        </a>
      </div>
    </article>
  </div>
</main>

{FOOTER_HTML}
</body>
</html>
'''


def sanitize_brand(text: str) -> str:
    """把 CMS 内可能出现的历史品牌名统一替换成「亿数」。"""
    if not text:
        return text
    return (
        text.replace('国文汇通', '亿数')
            .replace('江苏文交所', '亿数')
    )


def render_post_html(post: dict) -> str:
    pid = post['id']
    # 品牌合规：先做替换
    if post.get('title'):
        post['title'] = sanitize_brand(post['title'])
    content_md = sanitize_brand(post.get('content') or '')
    # 图片链接也统一转 https
    content_md_https = re.sub(
        r'(!\[[^\]]*\]\()http://eopcos\.yishuzichan\.cn',
        r'\1https://eopcos.yishuzichan.cn',
        content_md,
    )
    body_html = md_to_html(content_md_https) or '<p><em>（公告暂无正文内容）</em></p>'
    plain = strip_markdown(content_md_https)
    if not plain or len(plain) < 30:
        plain = fallback_desc(post)
    cover = pick_cover(post)
    date_iso = fmt_iso(post.get('publishAt'))
    return build_head(post, body_html, plain, cover, date_iso)


# =========================================================================
# 主流程
# =========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', nargs='*', default=None, help='仅生成指定 id')
    args = ap.parse_args()

    os.makedirs(POSTS_DIR, exist_ok=True)

    with open(POSTS_JSON, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    target = posts
    if args.ids:
        id_set = set(args.ids)
        target = [p for p in posts if p['id'] in id_set]
        print(f'[增量] 只生成 {len(target)} 条')

    success = 0
    errors = []
    for p in target:
        try:
            html_str = render_post_html(p)
            out_path = os.path.join(POSTS_DIR, f"{p['id']}.html")
            tmp = out_path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(html_str)
            os.replace(tmp, out_path)
            success += 1
        except Exception as e:
            errors.append((p.get('id'), str(e)))
            print(f'  ❌ {p.get("id")}: {e}')

    print(f'[done] 生成成功 {success} / {len(target)} 条。')
    if errors:
        print(f'  ⚠️ {len(errors)} 条失败：', [e[0][:8] for e in errors])
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())

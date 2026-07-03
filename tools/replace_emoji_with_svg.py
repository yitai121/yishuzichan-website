#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换 HTML 中的 emoji：
  - 图标性 emoji → inline SVG（Feather Icons 风格）
  - 装饰性 emoji → 直接删除
  - ⚠️ ✓ 保留

用法：
  python3 tools/replace_emoji_with_svg.py             # 全站
  python3 tools/replace_emoji_with_svg.py index.html  # 指定文件
"""
from __future__ import annotations
import os
import re
import sys

WEBSITE = '/app/data/所有对话/主对话/yishu-website'

# ============================================================
# Feather-icons 风格 SVG 图标内容（stroke 由外层 class 控制）
# ============================================================
SVG_PATHS = {
    'building':  '<rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    'gamepad':   '<line x1="6" y1="11" x2="10" y2="11"/><line x1="8" y1="9" x2="8" y2="13"/><line x1="15" y1="12" x2="15.01" y2="12"/><line x1="18" y1="10" x2="18.01" y2="10"/><path d="M17.32 5H6.68a4 4 0 00-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 003 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 019.828 16h4.344a2 2 0 011.414.586L17 18c.5.5 1 1 2 1a3 3 0 003-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.152A4 4 0 0017.32 5z"/>',
    'fish':      '<path d="M6.5 12c.94-3.46 4.94-6 8.5-6 3.56 0 6.06 2.54 7 6-.94 3.47-3.44 6-7 6s-7.56-2.53-8.5-6z"/><path d="M18 12v.5"/><path d="M16 17.93a9.77 9.77 0 010-11.86"/><path d="M7 10.67C7 8 5.58 5.97 2.73 5.5c-1 1.5-1 5 .5 8-1.5 3-1.5 6.5-.5 8 2.85-.47 4.27-2.5 4.27-5.17"/>',
    'store':     '<path d="M3 9l1-5h16l1 5"/><path d="M5 9v11a1 1 0 001 1h12a1 1 0 001-1V9"/><path d="M9 21v-6h6v6"/><line x1="3" y1="9" x2="21" y2="9"/>',
    'factory':   '<path d="M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z"/><path d="M17 18h1M13 18h1M9 18h1"/>',
    'link':      '<path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>',
    'bar-chart': '<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>',
    'trending-up':'<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    'shield':    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'refresh-cw':'<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>',
    'lock':      '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>',
    'globe':     '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>',
    'cpu':       '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    'file-text': '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
    'zap':       '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'palette':   '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 011.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    'search':    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    'users':     '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>',
    'user':      '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'lightbulb': '<path d="M9 21h6"/><path d="M12 17v4"/><path d="M12 3a6 6 0 00-4 10.5c.5.5 1 1 1 2v.5h6v-.5c0-1 .5-1.5 1-2A6 6 0 0012 3z"/>',
    'film':      '<rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/>',
    'smartphone':'<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    'scroll':    '<path d="M8 21h12a2 2 0 002-2v-2H10v2a2 2 0 11-4 0V5a2 2 0 10-4 0v3h4"/><path d="M19 17V5a2 2 0 00-2-2H4"/>',
    'sparkles':  '<path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>',
    'map-pin':   '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>',
    'credit-card':'<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
    'gift':      '<polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z"/>',
    'landmark':  '<line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    'briefcase': '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>',
    'handshake': '<path d="M11 17l2 2a1 1 0 103-3"/><path d="M14 14l2.5 2.5a1 1 0 103-3l-3.88-3.88a3 3 0 00-4.24 0l-.88.88a1 1 0 11-3-3l2.81-2.81a5.79 5.79 0 017.06-.87l.47.28a2 2 0 001.42.25L21 4"/>',
    'inbox':     '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/>',
    'shopping-bag':'<path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>',
    'megaphone': '<path d="M3 11l18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 11-5.8-1.6"/>',
    'clipboard': '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M9 4H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2h-4"/>',
    'check-circle':'<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    'check':     '<polyline points="20 6 9 17 4 12"/>',
}


def svg_icon(name: str, color: str = 'brand', size: int = 24) -> str:
    """生成 inline SVG 图标，包在 icon-inline span 里。"""
    path = SVG_PATHS.get(name)
    if not path:
        # 未知图标 → 用默认的方块
        path = '<rect x="4" y="4" width="16" height="16" rx="2"/>'
    cls = 'icon-inline'
    if color == 'gold':
        cls += ' gold'
    return (
        f'<span class="{cls}" aria-hidden="true">'
        f'<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{path}</svg>'
        f'</span>'
    )


# ============================================================
# 映射：emoji → SVG icon 名 或 特殊标记
# ============================================================
# 特殊值：
#   None  → 删除（装饰性）
#   'KEEP'→ 保留（如 ⚠️ ✓）
EMOJI_MAP: dict[str, str | None] = {
    # 图标性 → 换 SVG
    '🏢': 'building',
    '🎮': 'gamepad',
    '🎣': 'fish',
    '🐟': 'fish',
    '🏪': 'store',
    '🛍': 'shopping-bag', '🛍️': 'shopping-bag',
    '🏭': 'factory',
    '🔗': 'link',
    '⛓': 'link', '⛓️': 'link',
    '📊': 'bar-chart',
    '📈': 'trending-up',
    '🛡': 'shield', '🛡️': 'shield',
    '🔄': 'refresh-cw',
    '🔐': 'lock',
    '🔒': 'lock',
    '🌐': 'globe',
    '🌍': 'globe',
    '🌊': 'globe',
    '🤖': 'cpu',
    '📝': 'file-text',
    '📄': 'file-text',
    '📋': 'clipboard',
    '⚡': 'zap',
    '🎨': 'palette',
    '🔍': 'search',
    '👥': 'users',
    '👤': 'user',
    '💡': 'lightbulb',
    '🎬': 'film',
    '📱': 'smartphone',
    '📜': 'scroll',
    '🦄': 'sparkles',
    '📍': 'map-pin',
    '🎴': 'credit-card',
    '🎁': 'gift',
    '🏛': 'landmark', '🏛️': 'landmark',
    '💼': 'briefcase',
    '🤝': 'handshake',
    '📭': 'inbox',
    '📢': 'megaphone',

    # 装饰性 → 删除
    '🌟': None,
    '✅': None,
    '📮': None,

    # 保留
    '⚠': 'KEEP', '⚠️': 'KEEP',
    '✓': 'KEEP',
}


# 匹配 emoji 的正则（含变体选择符 U+FE0F）
EMOJI_REGEX = re.compile(
    r'(?:'
    r'⚠️|⛓️|🛡️|🛍️|🏛️|'
    r'🏢|🎮|🎣|🐟|🏪|🛍|🏭|🔗|⛓|📊|📈|🛡|🔄|🔐|🔒|🌐|🌍|🌊|'
    r'🤖|📝|📄|📋|⚡|🎨|🔍|👥|👤|💡|🎬|📱|📜|🦄|📍|🎴|🎁|'
    r'🏛|💼|🤝|📭|📢|🌟|✅|📮'
    r')'
)


def replace_in_html(content: str, filename: str = '') -> tuple[str, dict]:
    """返回 (新内容, {emoji: count})。"""
    stats: dict[str, int] = {}

    def repl(m: re.Match) -> str:
        emo = m.group(0)
        action = EMOJI_MAP.get(emo)
        stats[emo] = stats.get(emo, 0) + 1
        if action is None:
            # 装饰性删除，同时清理紧邻的空格
            return ''
        if action == 'KEEP':
            return emo
        # 图标性 → SVG
        return svg_icon(action)

    new = EMOJI_REGEX.sub(repl, content)

    # 清理因为删除留下的多余空白：">   <" or "   ,"
    # 简单处理：将两个及以上空格压缩为一个，但保留在 <pre>/<code> 内的原样
    # 为了保险，只清理"标签间"多余空格
    new = re.sub(r'>\s{2,}<', '> <', new)

    return new, stats


def process_file(fpath: str) -> dict:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    new, stats = replace_in_html(content, fpath)
    if stats:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new)
    return stats


def collect_targets(args: list[str]) -> list[str]:
    if args:
        return [os.path.join(WEBSITE, a) if not os.path.isabs(a) else a for a in args]
    targets = []
    # 8 主页面
    for name in ('index.html', 'news.html', 'post.html', 'about.html',
                 'ecosystem.html', 'products.html', 'contact.html',
                 'media.html', 'subscribe-thanks.html'):
        p = os.path.join(WEBSITE, name)
        if os.path.exists(p):
            targets.append(p)
    # posts/*.html
    posts_dir = os.path.join(WEBSITE, 'posts')
    if os.path.isdir(posts_dir):
        for name in sorted(os.listdir(posts_dir)):
            if name.endswith('.html'):
                targets.append(os.path.join(posts_dir, name))
    return targets


def main():
    args = sys.argv[1:]
    targets = collect_targets(args)
    print(f'[emoji-replace] 处理 {len(targets)} 个文件')

    total_stats: dict[str, int] = {}
    files_touched = 0
    for f in targets:
        stats = process_file(f)
        if stats:
            files_touched += 1
            rel = os.path.relpath(f, WEBSITE)
            summary = ', '.join(f'{e}×{c}' for e, c in stats.items())
            print(f'  ✓ {rel}: {summary}')
            for e, c in stats.items():
                total_stats[e] = total_stats.get(e, 0) + c

    print()
    print(f'[emoji-replace] 共处理 {files_touched} 个文件')
    print(f'[emoji-replace] Emoji 统计：')
    kept = removed = svg_replaced = 0
    for emo, cnt in sorted(total_stats.items(), key=lambda x: -x[1]):
        action = EMOJI_MAP.get(emo)
        act_str = 'DELETE' if action is None else ('KEEP' if action == 'KEEP' else f'SVG:{action}')
        print(f'  {emo} × {cnt:3d} → {act_str}')
        if action is None:
            removed += cnt
        elif action == 'KEEP':
            kept += cnt
        else:
            svg_replaced += cnt
    print()
    print(f'汇总：SVG 替换 {svg_replaced} 次 · 装饰性删除 {removed} 次 · 保留 {kept} 次 · 总计 {svg_replaced+removed+kept}')


if __name__ == '__main__':
    main()

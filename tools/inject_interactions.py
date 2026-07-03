#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_interactions.py — 全站注入 assets/interactions.js 引用（Round 5）
- <head> 前加 <link rel="preload" href="{prefix}assets/interactions.js" as="script">
- </body> 前加 <script src="{prefix}assets/interactions.js" defer></script>
- 主 8 页面：prefix = ./
- posts/*.html：prefix = ../
- 幂等：已存在则跳过
- 排除：v3.html、亿数ES官网.html（老遗留，另议）
"""
import os
import re
import sys

WEBSITE = '/app/data/所有对话/主对话/yishu-website'

# 主 8 页面 + subscribe-thanks
MAIN_PAGES = [
    'index.html', 'about.html', 'ecosystem.html', 'products.html',
    'contact.html', 'media.html', 'news.html', 'post.html',
    'subscribe-thanks.html',
]

EXCLUDES = {'v3.html', '亿数ES官网.html'}

PRELOAD_MARK = 'assets/interactions.js" as="script"'
SCRIPT_MARK = 'assets/interactions.js" defer>'


def inject(file_path, prefix):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    changed = False

    preload_tag = f'<link rel="preload" href="{prefix}assets/interactions.js" as="script">'
    script_tag = f'<script src="{prefix}assets/interactions.js" defer></script>'

    # 1. 注入 preload 到 </head> 前（若尚未存在）
    if PRELOAD_MARK not in html:
        if '</head>' in html:
            html = html.replace('</head>', preload_tag + '\n</head>', 1)
            changed = True

    # 2. 注入 script 到 </body> 前（若尚未存在）
    if SCRIPT_MARK not in html:
        if '</body>' in html:
            html = html.replace('</body>', script_tag + '\n</body>', 1)
            changed = True

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def main():
    injected = 0
    skipped = 0
    total = 0

    # 主 8 页面（prefix = ./）
    for name in MAIN_PAGES:
        path = os.path.join(WEBSITE, name)
        if not os.path.exists(path):
            print(f'  ⚠️  missing: {name}')
            continue
        total += 1
        if inject(path, './'):
            injected += 1
            print(f'  ✅ {name}')
        else:
            skipped += 1
            print(f'  ⏭️  {name} (already injected)')

    # posts/*.html（prefix = ../）
    posts_dir = os.path.join(WEBSITE, 'posts')
    if os.path.isdir(posts_dir):
        for name in sorted(os.listdir(posts_dir)):
            if not name.endswith('.html'):
                continue
            if name in EXCLUDES:
                continue
            path = os.path.join(posts_dir, name)
            total += 1
            if inject(path, '../'):
                injected += 1
            else:
                skipped += 1
    print(f'\n[posts] scanned: {total - len(MAIN_PAGES)}')

    print(f'\n[inject_interactions] total={total}  injected={injected}  skipped={skipped}')


if __name__ == '__main__':
    main()

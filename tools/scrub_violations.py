#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrub_violations.py — 全站清理违规词（Round 5）
1. "亿数ES" → "亿数"   （品牌统一）
2. "江苏文交所" → 已扫描，0 处（无需处理）
3. "国文汇通" → 已扫描，0 处（无需处理）
- 覆盖 meta keywords / description / JSON-LD alternateName / FAQ / og / body
- 幂等：无违规词则跳过
- 排除：v3.html / 亿数ES官网.html（老遗留，另议）
"""
import os
import re
import sys

WEBSITE = '/app/data/所有对话/主对话/yishu-website'

# 违规词映射（顺序敏感）
VIOLATIONS = [
    ('亿数ES', '亿数'),  # 品牌统一
]

# 要处理的目录 / 文件
MAIN_PAGES = [
    'index.html', 'about.html', 'ecosystem.html', 'products.html',
    'contact.html', 'media.html', 'news.html', 'post.html',
    'subscribe-thanks.html',
    'llms.txt',
]
EXCLUDES = {'v3.html', '亿数ES官网.html'}


def scrub(file_path):
    """返回：(是否修改, 替换次数)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    total = 0
    for bad, good in VIOLATIONS:
        count = content.count(bad)
        if count > 0:
            content = content.replace(bad, good)
            total += count

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, total
    return False, 0


def main():
    modified = 0
    total_replacements = 0

    # 主页面 + llms.txt
    for name in MAIN_PAGES:
        p = os.path.join(WEBSITE, name)
        if not os.path.exists(p):
            continue
        changed, n = scrub(p)
        if changed:
            modified += 1
            total_replacements += n
            print(f'  ✅ {name}  (-{n})')

    # posts/*.html
    posts_dir = os.path.join(WEBSITE, 'posts')
    if os.path.isdir(posts_dir):
        posts_modified = 0
        for name in sorted(os.listdir(posts_dir)):
            if not name.endswith('.html') or name in EXCLUDES:
                continue
            p = os.path.join(posts_dir, name)
            changed, n = scrub(p)
            if changed:
                posts_modified += 1
                total_replacements += n
        modified += posts_modified
        print(f'  ✅ posts/  ({posts_modified} files scrubbed)')

    print(f'\n[scrub_violations] files modified: {modified}  total replacements: {total_replacements}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 theme-dark.css 注入到所有 HTML 页面（8 主页面 + posts/*.html）。

在 </style> 之后（或者 </head> 之前）插入 <link rel="stylesheet" href="./assets/theme-dark.css">，
使其加载顺序 **在页面内联 style 之后**，从而 override :root 变量。

同时更新 <meta name="theme-color"> 为深色主题色 #0a1628。
首页 index.html 额外加 preload hero-bg.webp。
"""
from __future__ import annotations
import os
import re
import sys

WEBSITE = '/app/data/所有对话/主对话/yishu-website'

DARK_THEME_META = '<meta name="theme-color" content="#0a1628">'
DARK_MS_TILE = '<meta name="msapplication-TileColor" content="#0a1628">'


def upgrade_html(fpath: str, is_post: bool = False) -> bool:
    """返回是否修改过。"""
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content

    # 计算 theme-dark.css 的相对路径
    css_href = '../assets/theme-dark.css' if is_post else './assets/theme-dark.css'
    link_tag = f'<link rel="stylesheet" href="{css_href}">'

    # 幂等：如果已经注入过，不重复处理
    if 'assets/theme-dark.css' not in content:
        # 优先插入在最后一个 </style> 之后（使 dark theme 覆盖）
        # 找不到 </style> 就退到 </head> 前
        if '</style>' in content:
            # 找到最后一个 </style>
            idx = content.rfind('</style>')
            end = idx + len('</style>')
            content = content[:end] + '\n' + link_tag + '\n' + content[end:]
        elif '</head>' in content:
            content = content.replace('</head>', link_tag + '\n</head>', 1)
        else:
            # 兜底：直接插到 <body> 前
            content = content.replace('<body', link_tag + '\n<body', 1)

    # 更新 theme-color
    content = re.sub(
        r'<meta name="theme-color" content="[^"]*">',
        DARK_THEME_META,
        content,
    )
    content = re.sub(
        r'<meta name="msapplication-TileColor" content="[^"]*">',
        DARK_MS_TILE,
        content,
    )

    # 首页专属：加 preload hero-bg
    if fpath.endswith('/index.html') and not is_post:
        preload_tag = '<link rel="preload" as="image" href="./images/bg/hero-bg.webp" fetchpriority="high">'
        if 'hero-bg.webp' not in content or 'rel="preload"' not in content or preload_tag not in content:
            # 只加一次
            if preload_tag not in content:
                content = content.replace(
                    '<link rel="canonical"',
                    preload_tag + '\n<link rel="canonical"',
                    1,
                )

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    args = sys.argv[1:]
    if args:
        files = [(os.path.join(WEBSITE, a) if not os.path.isabs(a) else a, False) for a in args]
    else:
        files = []
        for name in ('index.html', 'news.html', 'post.html', 'about.html',
                     'ecosystem.html', 'products.html', 'contact.html',
                     'media.html', 'subscribe-thanks.html'):
            p = os.path.join(WEBSITE, name)
            if os.path.exists(p):
                files.append((p, False))
        posts_dir = os.path.join(WEBSITE, 'posts')
        if os.path.isdir(posts_dir):
            for name in sorted(os.listdir(posts_dir)):
                if name.endswith('.html'):
                    files.append((os.path.join(posts_dir, name), True))

    print(f'[inject-theme] 处理 {len(files)} 个 HTML')
    touched = 0
    for fpath, is_post in files:
        if upgrade_html(fpath, is_post=is_post):
            touched += 1
            rel = os.path.relpath(fpath, WEBSITE)
            print(f'  ✓ {rel}')
    print(f'[inject-theme] 已更新 {touched} 个文件')


if __name__ == '__main__':
    main()

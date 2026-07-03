#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 posts.json 生成 sitemap.xml：主页面 + 125 条公告静态页。
"""
import json
import os
from datetime import datetime, timezone, timedelta

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')
SITEMAP = os.path.join(WEBSITE, 'sitemap.xml')
TZ_CN = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ_CN).strftime('%Y-%m-%d')

# 主页面：路径 -> (priority, changefreq, lastmod override)
MAIN_PAGES = [
    ('',            '1.0', 'daily'),
    ('news.html',   '0.9', 'daily'),
    ('about.html',  '0.9', 'monthly'),
    ('products.html','0.9', 'monthly'),
    ('ecosystem.html','0.9', 'monthly'),
    ('media.html',  '0.8', 'monthly'),
    ('contact.html','0.7', 'monthly'),
]


def fmt_date(ts_ms):
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000, TZ_CN).strftime('%Y-%m-%d')
    except Exception:
        return TODAY


def main():
    with open(POSTS_JSON, encoding='utf-8') as f:
        posts = json.load(f)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # 主页面（首页用 lastmod=TODAY 表示每次同步都活跃）
    for path, pri, freq in MAIN_PAGES:
        loc = f'https://yishuzichan.cc/{path}'
        lines += [
            '  <url>',
            f'    <loc>{loc}</loc>',
            f'    <lastmod>{TODAY}</lastmod>',
            f'    <changefreq>{freq}</changefreq>',
            f'    <priority>{pri}</priority>',
            '  </url>',
        ]

    # 公告页
    for p in posts:
        pid = p['id']
        lastmod = fmt_date(p.get('publishAt'))
        lines += [
            '  <url>',
            f'    <loc>https://yishuzichan.cc/posts/{pid}.html</loc>',
            f'    <lastmod>{lastmod}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.7</priority>',
            '  </url>',
        ]

    lines.append('</urlset>')
    xml = '\n'.join(lines) + '\n'

    tmp = SITEMAP + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(xml)
    os.replace(tmp, SITEMAP)
    print(f'[sitemap.xml] 生成完成，URL 数 = {len(MAIN_PAGES) + len(posts)}')


if __name__ == '__main__':
    main()

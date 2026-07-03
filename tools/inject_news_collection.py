#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 news.html 注入 CollectionPage + ItemList JSON-LD（最新 20 条）。"""
import json
import os
import re

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
NEWS_HTML = os.path.join(WEBSITE, 'news.html')
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')

with open(POSTS_JSON, encoding='utf-8') as f:
    posts = json.load(f)

sorted_p = sorted(
    [p for p in posts if p.get('publishAt')],
    key=lambda x: x['publishAt'], reverse=True,
)[:20]

item_list = []
for i, p in enumerate(sorted_p, 1):
    pid = p['id']
    item_list.append({
        '@type': 'ListItem',
        'position': i,
        'url': f'https://yishuzichan.cc/posts/{pid}.html',
        'name': p.get('title') or '亿数公告',
    })

collection = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': '亿数最新资讯',
    'url': 'https://yishuzichan.cc/news.html',
    'description': '亿数官方最新公告、平台动态、生态进展、行业洞察与合规公告汇总。',
    'inLanguage': 'zh-CN',
    'isPartOf': {'@type': 'WebSite', 'name': '亿数', 'url': 'https://yishuzichan.cc'},
    'mainEntity': {
        '@type': 'ItemList',
        'name': '亿数最新公告',
        'numberOfItems': len(item_list),
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'itemListElement': item_list,
    },
}

block = '<script type="application/ld+json" id="newsCollectionLd">\n' + json.dumps(collection, ensure_ascii=False, indent=2) + '\n</script>\n'

with open(NEWS_HTML, encoding='utf-8') as f:
    html = f.read()

# 去掉旧的（如果存在），再插入到 </head> 前
html = re.sub(
    r'<script type="application/ld\+json" id="newsCollectionLd">[\s\S]*?</script>\n?',
    '',
    html,
)
html = html.replace('</head>', block + '</head>', 1)

with open(NEWS_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[news.html] 已注入 CollectionPage/ItemList Schema，{len(item_list)} 条')

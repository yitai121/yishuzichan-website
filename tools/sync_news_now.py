#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步主平台新公告到 news.html / posts.json / posts-cards.json / title2id.json。
同时刷新 banners.json（走独立模块 sync_banners.py）。

用法：
  1) 老式：把 NEW_ITEMS 列表 + tmp_new_posts.json 传入，追加新公告后重刷 SSR 首屏
  2) 无新增：NEW_ITEMS 留空，本脚本仍会：
     - 从 posts-cards.json 重刷 news.html 前 12 张 SSR（幂等）
     - 更新侧边栏分类计数
     - 拉 Banner API 生成 banners.json
"""
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
NEWS_HTML = os.path.join(WEBSITE, 'news.html')
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')
CARDS_JSON = os.path.join(WEBSITE, 'data/posts-cards.json')
T2ID = os.path.join(WEBSITE, 'tools/title2id.json')
TMP_NEW_POSTS = os.path.join(WEBSITE, 'tmp_new_posts.json')

TZ_CN = timezone(timedelta(hours=8))

# ==========================================================================
# 每次运行前，把新增公告写到这里；无新增时留空即可（仍会跑 SSR 重刷 & Banner）
# ==========================================================================
NEW_ITEMS: list = [
    # {
    #     'id': 'xxx-uuid',
    #     'title': '...',
    #     'category': 'blue', 'category_name': '平台动态',
    #     'desc': '...',
    # },
]

CATEGORY_MAP = {
    'blue': '平台动态',
    'green': '生态进展',
    'gold': '行业洞察',
    'purple': '合规公告',
}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data, indent=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        if indent:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        else:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, path)


def fmt_date(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, TZ_CN).strftime('%Y-%m-%d')


def sync_posts_json(raw_new):
    """把 NEW_ITEMS 追加到 posts.json（去重 by id）。"""
    posts = load_json(POSTS_JSON, [])
    existing_ids = {p['id'] for p in posts}
    added = 0
    for item in NEW_ITEMS:
        if item['id'] in existing_ids:
            continue
        raw = raw_new.get(item['id'], {})
        posts.append({
            'id': item['id'],
            'title': item['title'],
            'content': raw.get('content', ''),
            'publishAt': raw.get('publishAt') or raw.get('createdAt'),
            'tags': raw.get('tags', []),
            'viewCount': raw.get('viewCount', 0),
        })
        added += 1
    save_json(POSTS_JSON, posts)
    print(f'[posts.json] 追加 {added} 条，总数 {len(posts)}')
    return posts


def sync_cards_json(raw_new):
    """把 NEW_ITEMS 追加到 posts-cards.json 头部（去重 by id）。"""
    cards = load_json(CARDS_JSON, [])
    existing_ids = {c['id'] for c in cards}
    prepend = []
    for item in NEW_ITEMS:
        if item['id'] in existing_ids:
            continue
        raw = raw_new.get(item['id'], {})
        ts = raw.get('publishAt') or raw.get('createdAt') or 0
        prepend.append({
            'date': fmt_date(ts) if ts else '',
            'category': item['category'],
            'categoryName': item['category_name'],
            'title': item['title'],
            'desc': item['desc'],
            'id': item['id'],
        })
    cards = prepend + cards
    save_json(CARDS_JSON, cards, indent=2)
    print(f'[posts-cards.json] 头部追加 {len(prepend)} 条，总数 {len(cards)}')
    return cards


def render_card_html(c):
    return (
        f'          <article class="news-card">\n'
        f'            <div class="news-card-meta">\n'
        f'              <span class="news-card-date">{c["date"]}</span>\n'
        f'              <span class="news-card-tag {c["category"]}">{c["categoryName"]}</span>\n'
        f'            </div>\n'
        f'            <h3 class="news-card-title">{c["title"]}</h3>\n'
        f'            <p class="news-card-desc">{c["desc"]}</p>\n'
        f'            <a class="news-card-link" href="post.html?id={c["id"]}">阅读全文 →</a>\n'
        f'          </article>'
    )


NEWS_LIST_RE = re.compile(
    r'(<div class="news-list">\n)(.*?)(\n\s*<!-- 剩余卡片由 JS)',
    re.DOTALL,
)


def refresh_news_html(cards):
    """幂等：把 news.html 里 <div class="news-list"> 顶部的前 12 张同步为最新。"""
    with open(NEWS_HTML, encoding='utf-8') as f:
        html = f.read()

    top12 = cards[:12]
    new_block = '\n'.join(render_card_html(c) for c in top12)

    m = NEWS_LIST_RE.search(html)
    if not m:
        # 兜底：如果不匹配，尝试匹配旧结构（<div class="news-list">...</div>）
        old_re = re.compile(
            r'(<div class="news-list">\n)(.*?)(\s*</div>\s*\n\s*</div>\s*\n\s*\n\s*<!-- Sidebar -->)',
            re.DOTALL,
        )
        m = old_re.search(html)
        if not m:
            raise SystemExit('news-list 段未匹配，请检查 news.html 结构')
        new_html = html[:m.start()] + m.group(1) + new_block + m.group(3) + html[m.end():]
    else:
        new_html = html[:m.start()] + m.group(1) + new_block + m.group(3) + html[m.end():]

    # 更新侧边栏计数
    counts = {'blue': 0, 'green': 0, 'gold': 0, 'purple': 0}
    for c in cards:
        cat = c.get('category')
        if cat in counts:
            counts[cat] += 1

    def update_sidebar(html, name, count):
        pattern = re.compile(
            r'(<span class="sidebar-category-name">' + re.escape(name) + r'</span>\s*\n\s*<span class="sidebar-category-count">)(\d+)(</span>)'
        )
        new = pattern.sub(lambda m: m.group(1) + str(count) + m.group(3), html, count=1)
        return new

    new_html = update_sidebar(new_html, '平台动态', counts['blue'])
    new_html = update_sidebar(new_html, '生态进展', counts['green'])
    new_html = update_sidebar(new_html, '行业洞察', counts['gold'])
    new_html = update_sidebar(new_html, '合规公告', counts['purple'])

    # 品牌违禁词
    for bad in ['国文汇通', '江苏文交所']:
        if bad in new_html:
            raise SystemExit(f'品牌违禁词命中: {bad}')

    with open(NEWS_HTML, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'[news.html] SSR 首屏 12 张已刷新；侧边栏 {counts}')


def sync_t2id():
    t2id = load_json(T2ID, {})
    added = 0
    for item in NEW_ITEMS:
        if item['title'] not in t2id:
            t2id[item['title']] = item['id']
            added += 1
    save_json(T2ID, t2id, indent=2)
    print(f'[title2id.json] 追加 {added} 条，总数 {len(t2id)}')


def sync_banners():
    """调用 sync_banners.py 里的逻辑。"""
    try:
        sys.path.insert(0, os.path.join(WEBSITE, 'tools'))
        import sync_banners as sb
        banners = sb.fetch_banners()
        local_ids = sb.load_local_post_ids()
        items, missing = sb.transform(banners, local_ids)
        changed = sb.is_changed(items)
        sb.write_banners(items)
        sb.log_missing(missing)
        print(f'[banners.json] 拉取 {len(banners)} 条，有效 {len(items)} 条，changed={changed}')
        if missing:
            print(f'[banners.json] 待同步 postID {len(missing)} 条: {missing}')
        return changed
    except Exception as e:
        print(f'[banners.json] sync 失败: {e}')
        return False


def main():
    # 载入原始 API 数据（tmp_new_posts.json 由外部调度方准备）
    if NEW_ITEMS:
        if not os.path.exists(TMP_NEW_POSTS):
            raise SystemExit(f'NEW_ITEMS 非空但缺少 {TMP_NEW_POSTS}')
        with open(TMP_NEW_POSTS, encoding='utf-8') as f:
            raw_new = {p['id']: p for p in json.load(f)}
    else:
        raw_new = {}

    # 1. posts.json
    sync_posts_json(raw_new)

    # 2. posts-cards.json（新架构：单一数据源）
    cards = sync_cards_json(raw_new)

    # 3. news.html 前 12 张 SSR + 侧边栏计数（幂等）
    refresh_news_html(cards)

    # 4. title2id.json
    sync_t2id()

    # 5. banners.json
    sync_banners()

    print('\n[done] all sync tasks completed.')


if __name__ == '__main__':
    main()

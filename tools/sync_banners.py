#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步主平台 Banner 到官网 data/banners.json

- API: GET https://yishuzichan.cn/v1/cms/banner
- 只保留 status=1
- 按 createdAt 降序（最新在前）
- 图片 URL: https://eopcos.yishuzichan.cn + urllib.parse.quote(bannerImgUrl, safe='/')
- 跳转策略:
    redirectType 未定义/0: 站内 postID -> post.html?id={redirectUrl}, target=_self
    redirectType=1: 外链 -> redirectUrl, target=_blank
    redirectType=2: 主平台 detail URL -> 提取 id -> post.html?id={id}, target=_self
    redirectType=3: 无跳转 -> link="", target=""
- 检查跳站内的 postID 是否已在本地 posts.json，未同步的记录到日志

支持独立运行, 也支持被 sync_news_now.py 引用。
"""
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

WEBSITE = os.environ.get(
    'YISHU_WEBSITE',
    '/app/data/所有对话/主对话/yishu-website'
)
BANNERS_JSON = os.path.join(WEBSITE, 'data/banners.json')
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')
LOG_DIR = os.path.join(WEBSITE, 'logs')

BANNER_API = 'https://yishuzichan.cn/v1/cms/banner'
IMG_HOST = 'https://eopcos.yishuzichan.cn'
DETAIL_ID_RE = re.compile(r'[?&]id=([0-9a-fA-F-]{36})')


def fetch_banners(timeout: int = 30):
    """拉取远端 Banner 列表 (status=1)。"""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(BANNER_API, headers={'User-Agent': 'yishu-sync-bot/1.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get('data', {}).get('banners') or []


def load_local_post_ids():
    if not os.path.exists(POSTS_JSON):
        return set()
    with open(POSTS_JSON, encoding='utf-8') as f:
        return {p.get('id') for p in json.load(f) if p.get('id')}


def transform(banners, local_ids):
    """转换原始 banner -> 官网可用格式，并返回 (list, missing_ids)。"""
    out = []
    missing = []  # 待同步 postID 列表
    for b in banners:
        if b.get('status') != 1:
            continue
        raw_img = b.get('bannerImgUrl') or ''
        if not raw_img:
            continue
        img_url = IMG_HOST + urllib.parse.quote(raw_img, safe='/')

        rtype = b.get('redirectType')  # 可能为 None
        rurl = b.get('redirectUrl') or ''
        link = ''
        target = ''

        if rtype in (None, 0):
            # 站内 postID
            pid = rurl.strip()
            if pid:
                link = f'post.html?id={pid}'
                target = '_self'
                if pid not in local_ids:
                    missing.append(pid)
        elif rtype == 1:
            # 外链
            link = rurl
            target = '_blank'
        elif rtype == 2:
            m = DETAIL_ID_RE.search(rurl)
            if m:
                pid = m.group(1)
                link = f'post.html?id={pid}'
                target = '_self'
                if pid not in local_ids:
                    missing.append(pid)
            else:
                # 兜底：直接当外链
                link = rurl
                target = '_blank'
        elif rtype == 3:
            link = ''
            target = ''
        else:
            # 未知类型 -> 保守当作展示，不跳转
            link = ''
            target = ''

        out.append({
            'id': b.get('postID'),
            'title': b.get('bannerTitle') or '',
            'img': img_url,
            'link': link,
            'target': target,
            'createdAt': b.get('createdAt') or 0,
        })
    # 排序：createdAt 降序
    out.sort(key=lambda x: x.get('createdAt') or 0, reverse=True)
    return out, missing


def write_banners(items):
    os.makedirs(os.path.dirname(BANNERS_JSON), exist_ok=True)
    tmp = BANNERS_JSON + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, BANNERS_JSON)


def is_changed(new_items):
    """对比 banners.json 是否发生变化。"""
    if not os.path.exists(BANNERS_JSON):
        return True
    try:
        with open(BANNERS_JSON, encoding='utf-8') as f:
            old = json.load(f)
    except Exception:
        return True

    def _key(x):
        return (
            x.get('id'), x.get('title'), x.get('img'),
            x.get('link'), x.get('target'), x.get('createdAt'),
        )

    return [_key(x) for x in old] != [_key(x) for x in new_items]


def log_missing(missing_ids):
    if not missing_ids:
        return
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, 'banner_missing.log')
    tz = timezone(timedelta(hours=8))
    stamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as f:
        for pid in missing_ids:
            f.write(f'{stamp} 待同步的 Banner 关联 postID: {pid}\n')


def main():
    banners = fetch_banners()
    local_ids = load_local_post_ids()
    items, missing = transform(banners, local_ids)

    changed = is_changed(items)
    write_banners(items)

    log_missing(missing)

    print(f'[banners] 拉取 {len(banners)} 条，有效 {len(items)} 条')
    if missing:
        print(f'[banners] 待同步 postID {len(missing)} 条: {missing}')
    print(f'[banners] changed={changed} -> {BANNERS_JSON}')
    # 用退出码 20 表示"有变化"，0 表示无变化，方便 shell 分支
    if '--exit-code' in sys.argv:
        sys.exit(20 if changed else 0)


if __name__ == '__main__':
    main()

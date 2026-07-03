#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向 8 主页 nav 注入"视频会议"入口（幂等）。

规则：
- 检测 <a href="meeting.html" 已存在 → 跳过
- 未存在 → 在"相关媒体"链接和"会议签到"链接之间/之后插入
  优先策略：紧跟"会议签到"外链之后
  兜底策略：紧跟"相关媒体"之后（若无"会议签到"）
- 只做最小 diff，不动其它 nav 结构

用法：
  python3 tools/inject_meeting_nav.py            # 处理默认 8 主页
  python3 tools/inject_meeting_nav.py --dry-run  # 试跑
"""
import os
import re
import sys

WEBSITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAIN_PAGES = [
    'index.html',
    'about.html',
    'products.html',
    'ecosystem.html',
    'news.html',
    'media.html',
    'contact.html',
    'post.html',
]

MEETING_LINK = '<a href="meeting.html">视频会议</a>'
# 页面自身命中 active
MEETING_LINK_ACTIVE = '<a href="meeting.html" class="active">视频会议</a>'

# 匹配"会议签到"整行（含 target/rel 属性），后面追加
# 使用非贪婪 + 属性顺序容错
SIGN_IN_PATTERN = re.compile(
    r'(<a\s+href="https://f59962zb6q\.coze\.site/admin"[^>]*>会议签到</a>)',
    re.IGNORECASE,
)

# 兜底：匹配"相关媒体"链接
MEDIA_PATTERN = re.compile(
    r'(<a\s+href="media\.html"[^>]*>相关媒体</a>)',
    re.IGNORECASE,
)

# 幂等检测
ALREADY_HAS_MEETING = re.compile(
    r'<a\s+href="meeting\.html"[^>]*>视频会议</a>',
    re.IGNORECASE,
)


def process_file(path, dry_run=False):
    if not os.path.exists(path):
        print(f'  ⚠️ skip {path} (missing)')
        return 'skip'

    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    if ALREADY_HAS_MEETING.search(original):
        print(f'  ⏭️  {os.path.basename(path):20s} 已包含视频会议入口，跳过')
        return 'idempotent'

    # 是否是 meeting.html 本页（不应处理，但仍防御一下）
    if os.path.basename(path) == 'meeting.html':
        print(f'  ⏭️  {os.path.basename(path):20s} meeting.html 本页，跳过')
        return 'self'

    # 策略 1：紧跟"会议签到"之后
    if SIGN_IN_PATTERN.search(original):
        new_content = SIGN_IN_PATTERN.sub(r'\1 ' + MEETING_LINK, original, count=1)
        if new_content == original:
            print(f'  ❌ {os.path.basename(path):20s} 命中会议签到但替换失败')
            return 'fail'
        strategy = 'after-sign-in'
    # 策略 2：紧跟"相关媒体"之后
    elif MEDIA_PATTERN.search(original):
        new_content = MEDIA_PATTERN.sub(r'\1 ' + MEETING_LINK, original, count=1)
        strategy = 'after-media'
    else:
        print(f'  ❌ {os.path.basename(path):20s} 未找到锚点（会议签到/相关媒体）')
        return 'no-anchor'

    if dry_run:
        print(f'  🔍 {os.path.basename(path):20s} 将注入 [{strategy}]')
        return 'dry-run'

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  ✅ {os.path.basename(path):20s} 注入成功 [{strategy}]')
    return 'ok'


def main():
    dry_run = '--dry-run' in sys.argv
    print(f'[inject] {"DRY-RUN" if dry_run else "APPLY"} 模式，处理 {len(MAIN_PAGES)} 个主页')
    print(f'[inject] 站点根：{WEBSITE}')
    print()

    stats = {'ok': 0, 'idempotent': 0, 'fail': 0, 'skip': 0, 'dry-run': 0, 'no-anchor': 0, 'self': 0}
    for name in MAIN_PAGES:
        r = process_file(os.path.join(WEBSITE, name), dry_run=dry_run)
        stats[r] = stats.get(r, 0) + 1

    print()
    print(f'[inject] 完成 · 成功:{stats["ok"]} 幂等:{stats["idempotent"]} '
          f'试跑:{stats["dry-run"]} 失败:{stats["fail"]+stats["no-anchor"]} 跳过:{stats["skip"]+stats["self"]}')


if __name__ == '__main__':
    main()

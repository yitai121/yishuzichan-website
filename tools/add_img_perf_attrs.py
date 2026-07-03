#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为全站 HTML 里的 <img> 补上性能属性。

规则：
- nav 内的 logo（每个页面 body 里出现的第一个 <img>）：fetchpriority="high" decoding="async"
- footer 内的 logo（已经带 loading="lazy"）：补 decoding="async"
- 其它非首屏 <img>（业务内容图）：loading="lazy" decoding="async"
"""
import os
import re

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
FILES = [
    'index.html', 'about.html', 'ecosystem.html', 'contact.html',
    'products.html', 'news.html', 'post.html', 'media.html',
]

IMG_RE = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)


def has_attr(attrs, name):
    return re.search(r'\b' + re.escape(name) + r'\s*=', attrs, re.IGNORECASE) is not None


def add_attr(attrs, kv):
    if attrs.endswith('/'):
        attrs = attrs[:-1].rstrip() + ' ' + kv + '/'
    else:
        attrs = attrs.rstrip() + ' ' + kv
    return attrs


def process_file(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    body_start = html.find('<body')
    if body_start == -1:
        return 0

    # 找到 body 内第一个 img（视为首屏 logo）
    first_body_img = IMG_RE.search(html, body_start)
    first_pos = first_body_img.start() if first_body_img else -1

    changes = 0

    def repl(match):
        nonlocal changes
        attrs = match.group(1)
        is_first = (match.start() == first_pos)

        # 跳过 JS 字符串里的 img（news.html Banner 里的 '<img src=' 拼接）
        # 通过前置字符判断：若前面是 "+ '" 或 "' + '"，则跳过
        pre = html[max(0, match.start()-3):match.start()]
        if "'" in pre and '+' in pre:
            return match.group(0)

        original = match.group(0)

        if is_first:
            # 首屏 logo
            if not has_attr(attrs, 'fetchpriority'):
                attrs = add_attr(attrs, 'fetchpriority="high"')
            if not has_attr(attrs, 'decoding'):
                attrs = add_attr(attrs, 'decoding="async"')
        else:
            if not has_attr(attrs, 'loading'):
                attrs = add_attr(attrs, 'loading="lazy"')
            if not has_attr(attrs, 'decoding'):
                attrs = add_attr(attrs, 'decoding="async"')

        new = '<img' + attrs + '>'
        if new != original:
            changes += 1
        return new

    new_html = IMG_RE.sub(repl, html)
    if new_html != html:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
    return changes


def main():
    total = 0
    for name in FILES:
        p = os.path.join(WEBSITE, name)
        if not os.path.exists(p):
            print(f'[skip] {name} not found')
            continue
        n = process_file(p)
        total += n
        print(f'[{name}] {n} img updated')
    print(f'--- total {total} img updated ---')


if __name__ == '__main__':
    main()

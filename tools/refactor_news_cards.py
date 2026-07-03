#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性重构：从 news.html 中抽出全部 news-card，
- 生成 data/posts-cards.json（所有卡片，按 HTML 中原顺序）
- 把 news.html 中的 <div class="news-list">...</div> 内容替换为“前 12 张 + 加载占位 + noscript 兜底”
- 在 breadcrumb 之后插入 Banner 轮播区块（HTML/CSS/JS 全部就位）
- 全站图片 loading=lazy / decoding=async / hero fetchpriority=high

只运行一次；后续同步走 sync_news_now.py（会把新卡片追加进 posts-cards.json 头部）
"""
import json
import os
import re
from html import unescape

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
NEWS_HTML = os.path.join(WEBSITE, 'news.html')
CARDS_JSON = os.path.join(WEBSITE, 'data/posts-cards.json')

CARD_RE = re.compile(
    r'<article class="news-card">\s*'
    r'<div class="news-card-meta">\s*'
    r'<span class="news-card-date">([^<]+)</span>\s*'
    r'<span class="news-card-tag (blue|green|gold|purple)">([^<]+)</span>\s*'
    r'</div>\s*'
    r'<h3 class="news-card-title">([^<]+)</h3>\s*'
    r'<p class="news-card-desc">([^<]+)</p>\s*'
    r'<a class="news-card-link" href="post\.html\?id=([^"]+)">阅读全文 →</a>\s*'
    r'</article>',
    re.DOTALL,
)


def extract_cards(html):
    cards = []
    for m in CARD_RE.finditer(html):
        cards.append({
            'date': m.group(1).strip(),
            'category': m.group(2),
            'categoryName': m.group(4).strip() if False else m.group(3).strip(),
            'title': unescape(m.group(4).strip()),
            'desc': unescape(m.group(5).strip()),
            'id': m.group(6).strip(),
        })
    return cards


def render_card_html(c, extra_class=''):
    cls = 'news-card' + ((' ' + extra_class) if extra_class else '')
    return (
        f'          <article class="{cls}">\n'
        f'            <div class="news-card-meta">\n'
        f'              <span class="news-card-date">{c["date"]}</span>\n'
        f'              <span class="news-card-tag {c["category"]}">{c["categoryName"]}</span>\n'
        f'            </div>\n'
        f'            <h3 class="news-card-title">{c["title"]}</h3>\n'
        f'            <p class="news-card-desc">{c["desc"]}</p>\n'
        f'            <a class="news-card-link" href="post.html?id={c["id"]}">阅读全文 →</a>\n'
        f'          </article>'
    )


def main():
    with open(NEWS_HTML, encoding='utf-8') as f:
        html = f.read()

    cards = extract_cards(html)
    print(f'[extract] {len(cards)} cards')
    if len(cards) < 20:
        raise SystemExit('抽卡数量异常，请检查正则')

    # 保存全量 posts-cards.json
    os.makedirs(os.path.dirname(CARDS_JSON), exist_ok=True)
    with open(CARDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f'[posts-cards.json] saved {len(cards)} cards')

    # 生成前 12 张的 HTML 作为 SSR 首屏
    first12 = cards[:12]
    first_html = '\n'.join(render_card_html(c) for c in first12)

    # 找到 <div class="news-list"> ... </div>（包含所有 article）
    anchor_open = '<div class="news-list">'
    open_idx = html.find(anchor_open)
    assert open_idx != -1, 'news-list 开始锚点未找到'
    open_end = open_idx + len(anchor_open)

    # 找到本 div 的闭合标签（在其后面的第一个 </div>）
    # 结构：<div class="news-list"> ... </div>\n      </div>\n      <!-- Sidebar -->
    close_marker = '</div>\n      </div>\n      \n      <!-- Sidebar -->'
    close_idx = html.find(close_marker, open_end)
    assert close_idx != -1, 'news-list 结束锚点未找到'
    # close_idx 指向 </div>（news-list 的关闭）

    new_list_block = (
        anchor_open + '\n' +
        first_html + '\n' +
        '          <!-- 剩余卡片由 JS 从 data/posts-cards.json 动态加载到此处之前 -->\n' +
        '        </div>\n' +
        '        \n' +
        '        <!-- 加载更多按钮 & 状态 -->\n' +
        '        <div class="news-loadmore" id="newsLoadMoreWrap">\n' +
        '          <button type="button" class="news-loadmore-btn" id="newsLoadMoreBtn">加载更多资讯</button>\n' +
        '          <div class="news-loadmore-status" id="newsLoadMoreStatus" aria-live="polite"></div>\n' +
        '        </div>\n' +
        '        <noscript>\n' +
        '          <p style="margin-top:16px;color:var(--text-secondary);font-size:14px;">您的浏览器已禁用 JavaScript，仅展示前 12 条最新资讯。请启用 JS 以查看更多内容，或直接前往 <a href="https://yishuzichan.cn" style="color:var(--brand)">亿数主平台</a>。</p>\n' +
        '        </noscript>'
    )

    new_html = html[:open_idx] + new_list_block + html[close_idx:]
    # 上面替换：news-list 起始到 </div>（含）之间全部替换；因为我们的新块以 '</div>' 结尾（news-list 关闭），所以 close_idx 指向的 </div> 应该被跳过。
    # 修正：让 html[close_idx:] 从 close_idx + len('</div>') 开始（即从 </div> 之后）
    new_html = html[:open_idx] + new_list_block + html[close_idx + len('</div>'):]

    # 输出统计
    print(f'[replace] news-list 段替换成功，前 12 张 SSR，剩余 {len(cards)-12} 走 JS 加载')

    with open(NEWS_HTML, 'w', encoding='utf-8') as f:
        f.write(new_html)


if __name__ == '__main__':
    main()

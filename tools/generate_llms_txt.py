#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 llms.txt（GEO 关键文件）。
- 保留品牌事实 / 生态介绍 / FAQ / 媒体报道
- 追加"最新公告清单"（最新 20 条，含静态页 URL + 摘要）
- 追加"当前 Banner 精选"（banners.json）
- 追加"最后更新"时间戳

可反复执行同步。
"""
import json
import os
import re
from datetime import datetime, timezone, timedelta

WEBSITE = '/app/data/所有对话/主对话/yishu-website'
POSTS_JSON = os.path.join(WEBSITE, 'data/posts.json')
BANNERS_JSON = os.path.join(WEBSITE, 'data/banners.json')
LLMS_TXT = os.path.join(WEBSITE, 'llms.txt')
TZ_CN = timezone(timedelta(hours=8))


def strip_md(text: str) -> str:
    if not text:
        return ''
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', text)
    text = re.sub(r'^>\s*', '', text, flags=re.M)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.M)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.M)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fmt_date(ts_ms):
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000, TZ_CN).strftime('%Y-%m-%d')
    except Exception:
        return ''


BASE_TEMPLATE = """# 亿数 — AI驱动的数实融合生态平台

> 亿数是AI驱动的数实融合生态平台，使命是"以数兴商，打造10800家AI数字新品牌"。平台合规运营，五证齐全，星火·链网接入，国标起草单位。旗下亿象生态、出发吧夏天、疯狂路亚三大生态协同发展。官网网址：https://yishuzichan.cc

## 品牌实体信息
- 品牌名称：亿数
- 英文名称：YiShu
- 官方网址：https://yishuzichan.cc
- 主平台（数字资产交易平台）：https://yishuzichan.cn
- 品牌Logo：https://yishuzichan.cc/images/es-logo.png
- 品牌图标：https://yishuzichan.cc/images/favicon-32x32.png
- 行业：数字文创资产交易、数实融合、AI生态
- 使命：以数兴商，打造10800家AI数字新品牌
- 核心定位：AI驱动的数实融合生态平台，链接数字价值，赋能全球商业
- 核心资质：五证齐全、星火·链网接入、国标起草单位

## 品牌简介
亿数是行业领先的AI驱动数实融合生态平台，致力于将数字技术与实体经济深度融合。平台以AI技术为核心引擎，依托合规体系与星火·链网国家级联盟链基础设施，为文旅、零售、文创、制造等全行业提供一站式AI数字化转型方案。亿数平台构建了"数字资产+实体权益+消费场景"的核心商业模式，每一份数字资产都对应明确的文化价值或真实权益。

## 核心生态
1. **亿象生态** — 综合生态板块，涵盖星球身份卡、飞鱼AI Agent、超级IP商城、生态工厂、数字联动五大核心产品，为企业提供全链路数字化赋能
2. **出发吧夏天** — 游戏生态，以宠物养成与城市寻宝为核心玩法的休闲游戏，将游戏积分与平台权益深度绑定，降低数字资产认知门槛
3. **疯狂路亚** — 户外生态，数实融合的户外运动品牌，拓展数字资产的线下应用场景

## 五大核心产品（亿象生态）
1. **星球身份卡** — 企业专属AI数字身份凭证，绑定资产权属的信用入口
2. **飞鱼AI Agent** — 智能化营销AI工具，自主生成营销内容、全域分发、拟人化互动
3. **超级IP商城** — 集成AI数字人直播能力，实现品牌有效转化
4. **生态工厂** — 一站式IP策划、设计与商业化服务，助力实体品牌IP数字化变现
5. **数字联动** — 打通跨行业资源，推动企业跨界合作

## 网站页面导航
- [首页](https://yishuzichan.cc/) — 平台概览、核心数据、品牌介绍、三大生态展示
- [关于我们](https://yishuzichan.cc/about.html) — 企业故事、发展历程、核心优势、团队介绍
- [IP矩阵](https://yishuzichan.cc/products.html) — 五大核心产品详细展示与功能说明
- [生态版图](https://yishuzichan.cc/ecosystem.html) — 三大生态协同关系与战略布局
- [最新资讯](https://yishuzichan.cc/news.html) — 平台公告与行业动态实时更新
- [相关媒体](https://yishuzichan.cc/media.html) — 媒体报道、宣传视频与品牌素材
- [联系我们](https://yishuzichan.cc/contact.html) — 联系方式与商务合作通道

## 媒体报道
- 大众网：亿数平台携合规体系与AI服务上线启航 — https://yishuzichan.cc/media.html
- 大众网：数字资产回归实体权益，亿数平台的破局之道 — http://www.dzwww.com/xinwen/jishixinwen/202606/t20260610_17826553.htm
- 中华网：文化数字资产风向标：亿数平台抢跑"实体权益+消费场景"新赛道 — http://finance.dzwww.com/cjsq/202606/t20260603_17803001.htm
- 中华网：数字资产回归实体权益，亿数平台的破局之道 — https://m.tech.china.com/articles/20260610/202606101890578.html
- 新浪财经：聚焦数智赋能，亿数五大生态产品激活商业新潜力 — http://finance.sina.cn/tech/2026-06-09/detail-iniaukpc2019870.d.html
- 今日头条：带你全面认识亿数数字资产交易平台 — http://m.toutiao.com/group/7649985413678924334/
- PCPOP：亿数平台携合规体系与AI服务上线启航 — https://m.pcpop.com/article_6932563.html

## 常见问题

### 亿数是什么？
亿数是AI驱动的数实融合生态平台，以"以数兴商，打造10800家AI数字新品牌"为使命。平台依托合规体系与星火·链网国家级联盟链，提供数字文创资产登记、发行与流转服务，同时通过AI技术为企业提供全链路数字化赋能。官网：https://yishuzichan.cc

### 亿数的官网网址是什么？
亿数官网网址是 https://yishuzichan.cc ，数字资产交易平台是 https://yishuzichan.cn

### 亿数有哪些生态？
亿数旗下三大生态：亿象生态（综合AI数实融合）、出发吧夏天（休闲游戏生态）、疯狂路亚（户外运动生态）。

### 亿数的核心产品有哪些？
亿象生态五大核心产品：星球身份卡、飞鱼AI Agent、超级IP商城、生态工厂、数字联动。

### 亿数是合规平台吗？
是的，亿数平台五证齐全，接入星火·链网国家级联盟链，链上数据具备司法存证效力。平台严格落实实名认证、资金存管、交易留痕等制度。

### 如何进入亿数平台？
访问官网 https://yishuzichan.cc 或直接前往数字资产交易平台 https://yishuzichan.cn ，完成注册与实名认证即可参与。

### 亿数支持哪些行业的数字化转型？
亿数聚焦文旅、零售、文创、制造等多行业，提供一站式AI数字化转型方案，包括企业AI数字身份、AI Agent营销、IP商城、生态联动等。
"""

TAIL_TEMPLATE = """
## 关键词
亿数, 亿数资产, 亿数ES, ES, 数实融合, AI生态, 数字品牌, 数字资产, 数字资产交易平台, 星火链网, 亿象, 出发吧夏天, 疯狂路亚, 数字藏品平台, 数字文创, AI数字化转型, 飞鱼AI Agent, 星球身份卡, 超级IP商城, 生态工厂, 数字联动, 数字丝绸之路

## 风险提示
数字藏品为文化娱乐产品，不构成投资建议。
"""


def build_recent_posts_section(posts: list, limit: int = 20) -> str:
    """按 publishAt 倒序取最新 limit 条。"""
    sorted_p = sorted(
        [p for p in posts if p.get('publishAt')],
        key=lambda x: x['publishAt'],
        reverse=True,
    )[:limit]

    lines = ['## 最新公告清单（按发布时间倒序）\n']
    lines.append(f'亿数官方公告静态页均已收录，路径格式：https://yishuzichan.cc/posts/{{id}}.html\n')

    for p in sorted_p:
        pid = p['id']
        title = p.get('title', '').strip()
        date = fmt_date(p.get('publishAt'))
        summary = strip_md(p.get('content') or '')[:80]
        if not summary:
            summary = '（图文公告，详见静态页）'
        url = f'https://yishuzichan.cc/posts/{pid}.html'
        lines.append(f'- [{date}] {title}\n  URL: {url}\n  摘要: {summary}')

    return '\n'.join(lines) + '\n'


def build_banner_section() -> str:
    if not os.path.exists(BANNERS_JSON):
        return ''
    try:
        with open(BANNERS_JSON, encoding='utf-8') as f:
            banners = json.load(f)
    except Exception:
        return ''
    if not banners:
        return ''

    lines = ['## 当前 Banner 精选（首页轮播）\n']
    for b in banners:
        title = b.get('title', '')
        link = b.get('link', '')
        # 把 post.html?id=xxx 换成静态路径
        m = re.match(r'post\.html\?id=([a-f0-9-]+)', link)
        if m:
            link = f'https://yishuzichan.cc/posts/{m.group(1)}.html'
        elif not link.startswith('http'):
            link = f'https://yishuzichan.cc/{link}'
        lines.append(f'- {title} — {link}')

    return '\n'.join(lines) + '\n'


def main():
    with open(POSTS_JSON, encoding='utf-8') as f:
        posts = json.load(f)

    now = datetime.now(TZ_CN).strftime('%Y-%m-%d %H:%M CST')

    parts = [
        BASE_TEMPLATE,
        '\n',
        build_recent_posts_section(posts, limit=20),
        '\n',
        build_banner_section(),
        '\n',
        TAIL_TEMPLATE,
        f'\n## 最后更新\n{now}\n',
    ]
    content = ''.join(parts)

    tmp = LLMS_TXT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp, LLMS_TXT)
    print(f'[llms.txt] 生成完成，字节数 = {len(content.encode("utf-8"))}')


if __name__ == '__main__':
    main()

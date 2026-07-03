/*!
 * Yishu Round 5 · interactions.js
 * Lightweight vanilla-JS animation driver (no deps)
 * - IntersectionObserver 触发滚动入场（.js-anim / [data-stagger] → .in-view）
 * - Hero 首屏 stagger
 * - Nav shrink on scroll
 * - Image lazy fade-in
 * - Count-up numbers (兼容页面已有 count-up 系统)
 * (c) 2026 亿数
 */
(function () {
  'use strict';

  var doc = document;
  var win = window;
  var reduced = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in win;

  /* ------------------------------------------------------------
   * 1. Page-banner 首屏入场（DOMContentLoaded 立即挂 class）
   *    index.html 的 .hero-inner 有自己的内联 animation，不接管
   *    其他 6 页面（about/products/ecosystem/contact/media/news）的
   *    .page-banner-content 由此系统接管
   * ---------------------------------------------------------- */
  function initBanner() {
    var banner = doc.querySelector('.page-banner-content');
    if (banner) banner.classList.add('js-banner-init');
  }

  /* ------------------------------------------------------------
   * 2. 滚动触发入场（.js-anim + [data-stagger]）
   * ---------------------------------------------------------- */
  function autoTagTargets() {
    // 自动为常见 section / 卡片挂上 .js-anim（若尚未挂）
    // 注意：index.html 里 .overview-card 和 .stat-item 有自己的 IO+".visible" 系统，
    // 我们通过检测页面是否含 [data-target] 或 内联 fade-up keyframe 来避开冲突
    var selector = [
      '.news-card', '.product-card', '.eco-card',
      '.contact-card', '.feature-card', '.value-card', '.team-card',
      '.media-card', '.banner-card', '.ecosystem-card', '.qual-item',
      '.card',
      '.section-pad > .container > *',
      '.cta-inner'
    ].join(',');
    var els = doc.querySelectorAll(selector);
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      // 排除 Hero / Splash / Nav / Footer 内部元素
      if (el.closest('.hero') || el.closest('.splash-screen') ||
          el.closest('.nav') || el.closest('.footer')) continue;
      // 排除已经在 [data-stagger] 内部（stagger 系统自己接管）
      if (el.parentElement && el.parentElement.hasAttribute('data-stagger')) continue;
      // 已被其他系统管理的（.visible、内联 animation）也排除
      if (el.classList.contains('overview-card') || el.classList.contains('stat-item')) continue;
      if (!el.classList.contains('js-anim') && !el.hasAttribute('data-stagger')) {
        el.classList.add('js-anim');
      }
    }
  }

  function initScrollReveal() {
    if (reduced) {
      // 直接显示，跳过动画
      var all = doc.querySelectorAll('.js-anim, [data-stagger]');
      for (var i = 0; i < all.length; i++) all[i].classList.add('in-view');
      return;
    }
    autoTagTargets();

    if (!hasIO) {
      var all2 = doc.querySelectorAll('.js-anim, [data-stagger]');
      for (var j = 0; j < all2.length; j++) all2[j].classList.add('in-view');
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      for (var k = 0; k < entries.length; k++) {
        var entry = entries[k];
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          io.unobserve(entry.target);
        }
      }
    }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });

    var targets = doc.querySelectorAll('.js-anim, [data-stagger]');
    for (var t = 0; t < targets.length; t++) io.observe(targets[t]);
  }

  /* ------------------------------------------------------------
   * 3. Nav shrink on scroll
   * ---------------------------------------------------------- */
  function initNavShrink() {
    var nav = doc.querySelector('.nav');
    if (!nav) return;
    var last = null;
    function onScroll() {
      var s = win.scrollY > 40;
      if (s !== last) {
        last = s;
        nav.classList.toggle('scrolled', s);
      }
    }
    win.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ------------------------------------------------------------
   * 4. Image lazy fade-in
   * ---------------------------------------------------------- */
  function initImageFade() {
    if (reduced) return;
    var imgs = doc.querySelectorAll('img:not([data-no-fade])');
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      // 已加载完的直接跳过（不加 opacity:0，避免闪烁）
      if (img.complete && img.naturalHeight > 0) continue;
      img.classList.add('js-lazy-fade');
      (function (el) {
        function mark() { el.classList.add('loaded'); }
        el.addEventListener('load', mark, { once: true });
        el.addEventListener('error', mark, { once: true });
      })(img);
    }
  }

  /* ------------------------------------------------------------
   * 5. Count-up numbers（兼容页面自己已有的 count-up）
   *    只处理还未标记的 .stat-number（避免与 index.html 的 animateCountUp 冲突）
   * ---------------------------------------------------------- */
  function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }

  function parseTarget(text) {
    var m = /([\d.,]+)/.exec(text);
    if (!m) return null;
    var num = parseFloat(m[1].replace(/,/g, ''));
    if (isNaN(num)) return null;
    return {
      n: num,
      prefix: text.slice(0, m.index),
      suffix: text.slice(m.index + m[1].length)
    };
  }

  function animateCount(el, t, dur) {
    var start = performance.now();
    var n = t.n, pfx = t.prefix, sfx = t.suffix;
    var isInt = n === Math.floor(n) && n < 1e6;
    function step(now) {
      var p = Math.min(1, (now - start) / dur);
      var e = easeOutQuart(p);
      var v = n * e;
      el.textContent = pfx + (isInt ? Math.floor(v).toLocaleString() : v.toFixed(1)) + sfx;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = pfx + (isInt ? n.toLocaleString() : n.toString()) + sfx;
    }
    requestAnimationFrame(step);
  }

  function initCountUp() {
    if (reduced || !hasIO) return;
    var nums = doc.querySelectorAll('.stat-number');
    if (!nums.length) return;
    // 只处理没有 data-target（即不被页面自身 count-up 系统管理的）
    var targets = [];
    for (var i = 0; i < nums.length; i++) {
      var n = nums[i];
      if (n.hasAttribute('data-target')) continue; // 页面已管
      if (n.dataset.counted) continue;
      targets.push(n);
    }
    if (!targets.length) return;

    var io = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (!entry.isIntersecting) continue;
        var el = entry.target;
        if (el.dataset.counted) { io.unobserve(el); continue; }
        var t = parseTarget((el.textContent || '').trim());
        if (!t) { io.unobserve(el); continue; }
        el.dataset.counted = '1';
        animateCount(el, t, 1500);
        io.unobserve(el);
      }
    }, { threshold: 0.4 });

    for (var j = 0; j < targets.length; j++) io.observe(targets[j]);
  }

  /* ------------------------------------------------------------
   * 6. Boot
   * ---------------------------------------------------------- */
  function boot() {
    try { initBanner(); } catch (e) {}
    try { initScrollReveal(); } catch (e) {}
    try { initNavShrink(); } catch (e) {}
    try { initImageFade(); } catch (e) {}
    try { initCountUp(); } catch (e) {}
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

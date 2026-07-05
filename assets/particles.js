/**
 * 亿数官网 · 全站粒子交互系统 v1.0
 * ================================================================
 * 特性：
 *   - 背景飘浮粒子（低密度、紫蓝金三色）
 *   - 鼠标附近连线（距离衰减，最多同时 6 条）
 *   - 鼠标移动带动附近粒子微推力
 *   - 点击触发金色粒子爆发扩散
 *   - 移动端自动降级（粒子数减半、关闭连线）
 *   - 支持 prefers-reduced-motion 关闭
 *   - 与现有页面 z-index 隔离（-1），不遮挡任何交互
 * 引入方式：<script src="assets/particles.js" defer></script>
 * ================================================================
 */
(function () {
  'use strict';

  // ===== 尊重用户偏好 =====
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  // 已注入过（防重复）
  if (document.getElementById('yishu-particles-canvas')) return;

  // ===== 配置 =====
  const CFG = {
    // 颜色（品牌紫蓝金 + 冷白）
    colors: [
      { r: 91,  g: 95,  b: 199 },   // 品牌紫 #5B5FC7
      { r: 212, g: 175, b: 55 },    // 高级金 #D4AF37
      { r: 123, g: 127, b: 217 },   // 浅紫 #7B7FD9
      { r: 176, g: 139, b: 62 },    // 沉稳金 #B08B3E
    ],
    // 密度：桌面 vs 移动
    countDesktop: 72,
    countMobile: 32,
    // 粒子大小范围
    sizeMin: 0.6,
    sizeMax: 2.4,
    // 速度范围（px/frame）
    speedMin: 0.05,
    speedMax: 0.35,
    // 连线阈值
    linkDistance: 130,
    linkAlpha: 0.14,
    // 鼠标交互
    mouseRadius: 160,
    mousePush: 0.35,
    // 点击爆发
    burstCount: 24,
    burstSpeed: 4.5,
    burstLife: 60, // frames
    // 全局透明度基础值（低调不抢镜）
    alphaBase: 0.55,
  };

  const isMobile = window.matchMedia('(max-width: 768px)').matches;
  const enableLinks = !isMobile;
  const targetCount = isMobile ? CFG.countMobile : CFG.countDesktop;

  // ===== Canvas 创建 =====
  const canvas = document.createElement('canvas');
  canvas.id = 'yishu-particles-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  Object.assign(canvas.style, {
    position: 'fixed',
    top: '0',
    left: '0',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: '0',           // 不与内容争层：body 上放，内容 z-index >=1 即在其上
    opacity: '0',
    transition: 'opacity 1.2s cubic-bezier(0.25,0.1,0.25,1)',
  });

  // 挂到 body 最前，让所有内容自然叠在其上（内容元素本身多带 position/z-index，无干扰）
  function mount() {
    if (!document.body) { requestAnimationFrame(mount); return; }
    document.body.prepend(canvas);
    requestAnimationFrame(() => { canvas.style.opacity = '1'; });
    init();
  }

  // ===== 状态 =====
  let ctx, W, H, DPR;
  const particles = [];
  const bursts = [];
  const mouse = { x: -9999, y: -9999, active: false };

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  function rand(a, b) { return a + Math.random() * (b - a); }

  function makeParticle() {
    const c = CFG.colors[(Math.random() * CFG.colors.length) | 0];
    const angle = Math.random() * Math.PI * 2;
    const speed = rand(CFG.speedMin, CFG.speedMax);
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: rand(CFG.sizeMin, CFG.sizeMax),
      color: c,
      alpha: rand(0.3, 0.9),
      // 呼吸相位
      phase: Math.random() * Math.PI * 2,
    };
  }

  function makeBurstParticle(cx, cy) {
    const angle = Math.random() * Math.PI * 2;
    const speed = rand(1.5, CFG.burstSpeed);
    return {
      x: cx,
      y: cy,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: rand(1.2, 2.6),
      life: CFG.burstLife,
      maxLife: CFG.burstLife,
      color: CFG.colors[1], // 金色
    };
  }

  function updateParticle(p) {
    // 鼠标推力
    if (mouse.active) {
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const dist = Math.hypot(dx, dy);
      if (dist < CFG.mouseRadius && dist > 0.5) {
        const force = (CFG.mouseRadius - dist) / CFG.mouseRadius * CFG.mousePush;
        p.vx += (dx / dist) * force * 0.15;
        p.vy += (dy / dist) * force * 0.15;
      }
    }

    // 缓慢摩擦（避免速度累积过大）
    p.vx *= 0.985;
    p.vy *= 0.985;

    p.x += p.vx;
    p.y += p.vy;

    // 边界环绕
    if (p.x < -10) p.x = W + 10;
    if (p.x > W + 10) p.x = -10;
    if (p.y < -10) p.y = H + 10;
    if (p.y > H + 10) p.y = -10;

    // 呼吸
    p.phase += 0.015;
  }

  function drawParticle(p) {
    const breathAlpha = p.alpha * (0.7 + 0.3 * Math.sin(p.phase)) * CFG.alphaBase;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${p.color.r},${p.color.g},${p.color.b},${breathAlpha})`;
    ctx.fill();
  }

  function drawLinks() {
    if (!enableLinks) return;
    const L2 = CFG.linkDistance * CFG.linkDistance;
    for (let i = 0; i < particles.length; i++) {
      const a = particles[i];
      for (let j = i + 1; j < particles.length; j++) {
        const b = particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < L2) {
          const t = 1 - d2 / L2; // 距离越近越强
          const alpha = t * CFG.linkAlpha;
          // 用两端色平均
          const r = ((a.color.r + b.color.r) / 2) | 0;
          const g = ((a.color.g + b.color.g) / 2) | 0;
          const bl = ((a.color.b + b.color.b) / 2) | 0;
          ctx.strokeStyle = `rgba(${r},${g},${bl},${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }

      // 鼠标连线（更亮）
      if (mouse.active) {
        const mdx = a.x - mouse.x;
        const mdy = a.y - mouse.y;
        const md2 = mdx * mdx + mdy * mdy;
        if (md2 < L2 * 1.8) {
          const t = 1 - md2 / (L2 * 1.8);
          ctx.strokeStyle = `rgba(212,175,55,${t * 0.35})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.stroke();
        }
      }
    }
  }

  function updateBursts() {
    for (let i = bursts.length - 1; i >= 0; i--) {
      const p = bursts[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.94;
      p.vy *= 0.94;
      p.life--;
      if (p.life <= 0) bursts.splice(i, 1);
    }
  }

  function drawBursts() {
    for (const p of bursts) {
      const t = p.life / p.maxLife;
      const alpha = t * 0.9;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * (0.5 + t * 0.8), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color.r},${p.color.g},${p.color.b},${alpha})`;
      ctx.fill();
    }
  }

  let rafId = null;
  let running = true;

  function loop() {
    if (!running) return;
    ctx.clearRect(0, 0, W, H);

    // 更新 & 绘制
    for (const p of particles) updateParticle(p);
    drawLinks();
    for (const p of particles) drawParticle(p);

    updateBursts();
    drawBursts();

    rafId = requestAnimationFrame(loop);
  }

  function spawnBurst(x, y) {
    for (let i = 0; i < CFG.burstCount; i++) {
      bursts.push(makeBurstParticle(x, y));
    }
  }

  // ===== 初始化 =====
  function init() {
    ctx = canvas.getContext('2d', { alpha: true });
    resize();
    for (let i = 0; i < targetCount; i++) particles.push(makeParticle());
    window.addEventListener('resize', () => {
      resize();
    });

    // 鼠标
    let mouseTimer;
    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
      clearTimeout(mouseTimer);
      mouseTimer = setTimeout(() => { mouse.active = false; }, 200);
    }, { passive: true });

    // 触摸
    window.addEventListener('touchmove', (e) => {
      if (e.touches[0]) {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
        mouse.active = true;
      }
    }, { passive: true });

    // 点击爆发（避免在按钮/链接上抢焦点，只在没落到可交互元素时触发；实际因为 pointer-events:none，click 不会触发 —— 改用 window 层监听 mousedown）
    window.addEventListener('mousedown', (e) => {
      // 忽略滚动条区域
      if (e.clientX > W - 20) return;
      spawnBurst(e.clientX, e.clientY);
    }, { passive: true });
    window.addEventListener('touchstart', (e) => {
      if (e.touches[0]) spawnBurst(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });

    // 页面隐藏时暂停
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        running = false;
        if (rafId) cancelAnimationFrame(rafId);
      } else if (!running) {
        running = true;
        loop();
      }
    });

    loop();
  }

  // 启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();

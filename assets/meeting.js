/**
 * 亿数视频会议 - Jitsi Meet External API 集成
 * ------------------------------------------------------------
 * 目标：
 *   1) 品牌完全去 Jitsi 化（水印/logo/背景/文案 → 亿数）
 *   2) 生产级功能齐全（toolbar 全开，无阉割）
 *   3) 中文优先，禁止 App 深链拉起
 *   4) 端到端加密（E2EE）能力保留
 *   5) 服务器未部署时给友好的错误提示，不白屏
 *
 * TODO(claude): 后端部署完成后确认此域名。
 *   切换命令示例：
 *     sed -i "s|meet.yishuzichan.cc|真实域名|g" assets/meeting.js room.html
 */
(function () {
  'use strict';

  // ========== 配置常量 ==========
  // TODO(claude): 部署完成后确认此域名（腾讯云香港 + docker-jitsi-meet + meet.yishuzichan.cc）
  var JITSI_DOMAIN = 'meet.yishuzichan.cc';
  var DEFAULT_ROOM = 'yishu-lobby';
  var BRAND_LOGO_URL = 'https://yishuzichan.cc/images/yishu-logo-nav.png';
  var BACK_URL = 'meeting.html';

  // ========== DOM 元素 ==========
  var container = document.getElementById('jitsi-container');
  var loadingOverlay = document.getElementById('loadingOverlay');
  var loadingRoomLabel = document.getElementById('loadingRoom');
  var errorOverlay = document.getElementById('errorOverlay');
  var errorTitle = document.getElementById('errorTitle');
  var errorDesc = document.getElementById('errorDesc');
  var roomBadge = document.getElementById('roomBadge');
  var roomLabel = document.getElementById('roomLabel');
  var leaveBtn = document.getElementById('leaveBtn');
  var orientationTip = document.getElementById('orientationTip');

  // ========== 工具函数 ==========
  function sanitizeRoomId(raw) {
    if (!raw) return '';
    var s = String(raw).trim();
    // 只保留字母数字、下划线、短横线、中文
    s = s.replace(/[^\w\u4e00-\u9fa5\-]/g, '');
    // 长度截断（Jitsi 房间名建议 < 128）
    if (s.length > 96) s = s.substring(0, 96);
    return s;
  }

  function getRoomId() {
    var params = new URLSearchParams(window.location.search);
    var raw = params.get('id') || params.get('room') || '';
    var clean = sanitizeRoomId(raw);
    return clean || DEFAULT_ROOM;
  }

  function showError(title, desc) {
    if (errorTitle && title) errorTitle.textContent = title;
    if (errorDesc && desc) errorDesc.textContent = desc;
    if (loadingOverlay) loadingOverlay.classList.add('hide');
    if (errorOverlay) errorOverlay.classList.add('show');
  }

  function hideLoading() {
    if (loadingOverlay) loadingOverlay.classList.add('hide');
  }

  // 生成随机匿名用户名（从预设池随机 + 4 位随机数）
  function pickDisplayName() {
    var pool = ['亿数用户', '亿数访客', '会议参与者'];
    var pick = pool[Math.floor(Math.random() * pool.length)];
    var suffix = Math.floor(1000 + Math.random() * 9000);
    return pick + suffix;
  }

  // ========== 房间信息初始化 ==========
  var roomId = getRoomId();
  if (roomLabel) roomLabel.textContent = roomId;
  if (loadingRoomLabel) loadingRoomLabel.textContent = '房间号：' + roomId;
  document.title = roomId + ' — 亿数视频会议室';

  // ========== 移动端横屏提示（3 秒后自动出现） ==========
  if (orientationTip) {
    setTimeout(function () {
      orientationTip.classList.add('enabled');
      // 8 秒后自动淡出
      setTimeout(function () {
        orientationTip.style.transition = 'opacity 0.4s ease';
        orientationTip.style.opacity = '0';
      }, 8000);
    }, 3000);
  }

  // ========== 退出按钮 ==========
  function goBack() {
    // 若 api 存在，先优雅挂断
    if (window.__jitsiApi && typeof window.__jitsiApi.executeCommand === 'function') {
      try { window.__jitsiApi.executeCommand('hangup'); } catch (e) { /* noop */ }
    }
    window.location.href = BACK_URL;
  }
  if (leaveBtn) leaveBtn.addEventListener('click', goBack);

  // ========== 主流程：等待 external_api.js 加载 ==========
  var loadStartTime = Date.now();
  var LOAD_TIMEOUT = 15000; // 15 秒超时（含 DNS + TLS + 首屏）
  var pollTimer = null;

  function startJitsi() {
    if (typeof window.JitsiMeetExternalAPI !== 'function') {
      showError(
        '会议服务暂时不可用',
        '无法连接到亿数会议服务器（' + JITSI_DOMAIN + '）。可能原因：\n' +
        '1) 服务器尚未部署完成\n' +
        '2) 您的网络无法访问该域名\n' +
        '3) 浏览器阻止了跨域脚本\n\n' +
        '请稍后重试，或联系亿数团队。'
      );
      return;
    }

    if (!container) {
      showError('页面加载错误', '未找到会议容器（#jitsi-container）。请刷新页面。');
      return;
    }

    // ========== Jitsi options ==========
    var options = {
      roomName: roomId,
      width: '100%',
      height: '100%',
      parentNode: container,
      userInfo: {
        displayName: pickDisplayName()
      },
      configOverwrite: {
        prejoinPageEnabled: true,            // 加入前预览页（选头像/麦克风）
        disableDeepLinking: true,            // 不弹 App 引导
        startWithAudioMuted: true,
        startWithVideoMuted: false,
        enableWelcomePage: false,
        enableClosePage: false,
        defaultLanguage: 'zh',               // 强制中文
        p2p: { enabled: true },              // 2 人时启用 P2P，降低服务器负担
        disableThirdPartyRequests: true,     // 关闭第三方外链（Google Analytics 等）
        analytics: { disabled: true },
        toolbarButtons: [
          'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
          'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
          'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
          'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
          'tileview', 'select-background', 'download', 'help', 'mute-everyone',
          'security'
        ]
      },
      interfaceConfigOverwrite: {
        // 品牌合规注入：完全去 Jitsi 化
        SHOW_JITSI_WATERMARK: false,
        SHOW_WATERMARK_FOR_GUESTS: false,
        SHOW_BRAND_WATERMARK: false,
        BRAND_WATERMARK_LINK: '',
        JITSI_WATERMARK_LINK: 'https://yishuzichan.cc',
        DEFAULT_LOGO_URL: BRAND_LOGO_URL,
        DEFAULT_WELCOME_PAGE_LOGO_URL: BRAND_LOGO_URL,
        DEFAULT_REMOTE_DISPLAY_NAME: '亿数用户',
        DEFAULT_LOCAL_DISPLAY_NAME: '我',
        HIDE_INVITE_MORE_HEADER: false,
        MOBILE_APP_PROMO: false,             // 移动端不弹"下载 Jitsi App"
        LANG_DETECTION: false,               // 不做浏览器语言探测（强制中文）
        DEFAULT_BACKGROUND: '#f7f9fc',       // 亿数浅色主题基调
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
        DISABLE_VIDEO_BACKGROUND: false,
        DISABLE_FOCUS_INDICATOR: false,
        DISABLE_DOMINANT_SPEAKER_INDICATOR: false,
        DISABLE_TRANSCRIPTION_SUBTITLES: false,
        DISABLE_RINGING: false,
        AUDIO_LEVEL_PRIMARY_COLOR: 'rgba(91,95,199,0.4)',
        AUDIO_LEVEL_SECONDARY_COLOR: 'rgba(91,95,199,0.4)',
        POLICY_LOGO: null,
        PROVIDER_NAME: '亿数',
        NATIVE_APP_NAME: '亿数视频会议',
        APP_NAME: '亿数视频会议',
        // Toolbar 按钮全开（覆盖默认精简）
        TOOLBAR_BUTTONS: [
          'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
          'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
          'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
          'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
          'tileview', 'select-background', 'download', 'help', 'mute-everyone',
          'security'
        ]
      }
    };

    // ========== 实例化 ==========
    var api;
    try {
      api = new window.JitsiMeetExternalAPI(JITSI_DOMAIN, options);
    } catch (err) {
      showError(
        '会议初始化失败',
        '无法在当前浏览器创建会议实例：' + (err && err.message ? err.message : '未知错误') +
        '。请尝试使用最新版 Chrome / Edge / Safari。'
      );
      return;
    }
    window.__jitsiApi = api; // 暴露给退出按钮使用

    // ========== 事件监听 ==========
    api.addEventListener('videoConferenceJoined', function (data) {
      hideLoading();
      // 主动设置显示名（覆盖 userInfo，保底）
      try { api.executeCommand('displayName', pickDisplayName()); } catch (e) {}
    });

    api.addEventListener('videoConferenceLeft', function () {
      window.location.href = BACK_URL;
    });

    api.addEventListener('readyToClose', function () {
      window.location.href = BACK_URL;
    });

    // 长连接失败：显示错误
    api.addEventListener('connectionFailed', function (data) {
      showError(
        '连接失败',
        '与亿数会议服务器的连接失败，请检查网络后重试。'
      );
    });

    // 兜底：iframe 首次内容加载完毕就隐藏 loading（避免长时间白屏）
    setTimeout(function () {
      hideLoading();
    }, 6000);
  }

  // 轮询等待 JitsiMeetExternalAPI 全局对象出现
  function poll() {
    // 外部脚本明确加载失败
    if (window.__jitsiScriptFailed) {
      showError(
        '无法加载会议服务',
        '会议服务器脚本加载失败（' + JITSI_DOMAIN + '/external_api.js）。' +
        '可能是服务器尚未部署完成，或您的网络无法访问该域名。请稍后重试。'
      );
      return;
    }

    if (typeof window.JitsiMeetExternalAPI === 'function') {
      startJitsi();
      return;
    }

    if (Date.now() - loadStartTime > LOAD_TIMEOUT) {
      showError(
        '会议服务响应超时',
        '连接亿数会议服务器超时（' + JITSI_DOMAIN + '）。请检查网络连接后刷新重试。' +
        '若持续无法进入，请前往会议入口页面查看提示。'
      );
      return;
    }
    pollTimer = setTimeout(poll, 300);
  }

  // DOM 就绪后启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', poll);
  } else {
    poll();
  }
})();

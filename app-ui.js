/* ==========================================================================
   VendSolution App · 导航行为（与 app-ui.css 配套）
   统一所有页面的「返回 / 回首页 / 退出登录」：
   - 在 demo 外壳（navigation.html 的 iframe）内：优先 history.back()，
     无历史时通知外壳回到上一个内置视图，绝不把整页 App 套进 iframe。
   - 单独打开页面时：有 href 的返回控件沿用原 href 作为兜底。
   ========================================================================== */
(function () {
  var inSub = /\/app_workorder\//.test(location.pathname);

  function homeHref() { return inSub ? '../navigation.html' : 'navigation.html'; }

  function inFrame() {
    try { return window.self !== window.top; } catch (e) { return false; }
  }

  function tellHost(type, extra) {
    if (!inFrame()) return false;
    try {
      var msg = { type: type };
      if (extra) { for (var k in extra) { if (Object.prototype.hasOwnProperty.call(extra, k)) msg[k] = extra[k]; } }
      parent.postMessage(msg, '*');
      return true;
    } catch (e) { return false; }
  }

  /* 上报当前地址：外壳在 file:// 下读不到 iframe 的 location，
     靠这条消息判断页面层级——分区页保留底部导航，详情页收起 */
  if (inFrame()) {
    try { parent.postMessage({ type: 'app:route', href: location.href }, '*'); } catch (e) {}
  }

  /* 返回上一级
     外壳里每个原型页都从空白页重新挂载，历史只有「空白 + 当前页」两条：
     此时直接请求外壳回上一个视图，不再触发 iframe 后退；
     页面内部跳转过（如设备页 → 补货页）才真正 history.back()。 */
  window.appBack = function (event) {
    var el = event && event.currentTarget;
    var hasHref = el && el.getAttribute && el.getAttribute('href');

    if (window.history.length > 2) {
      if (event) event.preventDefault();
      window.history.back();
      return false;
    }
    if (inFrame()) {
      if (event) event.preventDefault();
      tellHost('app:home');
      return false;
    }
    if (hasHref) return true;          /* 单独打开：沿用原 href */
    if (event) event.preventDefault();
    location.href = homeHref();
    return false;
  };

  /* 回到 demo 首页视图 */
  window.appHome = function (event, view) {
    if (event && event.preventDefault) event.preventDefault();
    if (tellHost('app:home', view ? { view: view } : null)) return false;
    location.href = homeHref() + (view ? '#' + view : '');
    return false;
  };

  /* 退出登录 */
  window.appLogout = function (event) {
    if (event) event.preventDefault();
    if (tellHost('app:logout')) return false;
    location.href = inSub ? '../login.html' : 'login.html';
    return false;
  };

  /* 远程开锁：确认弹层 + 「已开锁」态，单门 / 双门 / 咖啡机共用
     opts = {
       buttons:   触发按钮选择器，可带 data-door="left|right"
       sheet:     确认弹层 id
       doorRow:   弹层内显示门名的行（可选，双门用）
       statusRow: 设备状态里「门状态」行的 id（可选）
       toast:     toast 元素 id（可选）
     }
     按钮内用 <span data-unlock-label> 包住文字，弹层用 data-close / data-unlock-confirm 标记按钮。 */
  window.appUnlock = function (opts) {
    var sheet = document.getElementById(opts.sheet);
    if (!sheet) return;
    var buttons = [].slice.call(document.querySelectorAll(opts.buttons || '[data-unlock]'));
    var doorRow = opts.doorRow ? document.getElementById(opts.doorRow) : null;
    var statusRow = opts.statusRow ? document.getElementById(opts.statusRow) : null;
    var toastEl = opts.toast ? document.getElementById(opts.toast) : null;
    var confirmBtn = sheet.querySelector('[data-unlock-confirm]');
    var busy = false, timer, active = null, activeDoor = null, toastTimer;

    function label(btn) { return btn.querySelector('[data-unlock-label]') || btn; }
    function doorName(door) { return door === 'left' ? '左门' : door === 'right' ? '右门' : '柜门'; }

    function close() { sheet.classList.remove('open'); }
    function open(btn) {
      active = btn;
      activeDoor = btn.getAttribute('data-door');
      if (doorRow && activeDoor) doorRow.textContent = doorName(activeDoor);
      sheet.classList.add('open');
    }
    function toast(text) {
      if (!toastEl) return;
      toastEl.textContent = text;
      toastEl.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 2000);
    }

    buttons.forEach(function (btn) {
      var text = label(btn);
      btn.setAttribute('data-label', text.textContent.trim());
      btn.addEventListener('click', function () {
        if (busy || btn.disabled) return;
        open(btn);
      });
    });

    sheet.querySelectorAll('[data-close]').forEach(function (btn) {
      btn.addEventListener('click', close);
    });
    sheet.addEventListener('click', function (event) { if (event.target === sheet) close(); });
    document.addEventListener('keydown', function (event) { if (event.key === 'Escape') close(); });

    if (!confirmBtn) return;
    confirmBtn.addEventListener('click', function () {
      if (!active) return;
      var btn = active, text = label(btn), door = activeDoor;
      close();
      busy = true;
      text.textContent = '已开锁';
      btn.classList.add('is-done');
      btn.disabled = true;
      if (statusRow) statusRow.textContent = door ? doorName(door) + '已开' : '已开锁';
      toast(door ? doorName(door) + ' · 开锁指令已下发' : '开锁指令已下发');
      if (opts.onUnlock) opts.onUnlock(door);
      clearTimeout(timer);
      timer = setTimeout(function () {
        busy = false;
        text.textContent = btn.getAttribute('data-label');
        btn.classList.remove('is-done');
        btn.disabled = false;
        if (statusRow) statusRow.textContent = '已关闭';
        if (opts.onReset) opts.onReset();
      }, 4000);
    });
  };

  /* 设备详情页：列表带 ?id=&name=&status= 打开时，同步页头与在线状态
     页面需在对应元素上加 data-device-name / data-device-id /
     data-conn-badge（徽标容器）/ data-conn-value（在线状态值） */
  (function () {
    var params = new URLSearchParams(location.search);
    var name = params.get('name');
    var id = params.get('id');
    var status = params.get('status');
    if (name) { var nameEl = document.querySelector('[data-device-name]'); if (nameEl) nameEl.textContent = name; }
    if (id) { var idEl = document.querySelector('[data-device-id]'); if (idEl) idEl.textContent = id; }
    var map = { online: ['在线', 'badge ok', 'dot ok'], offline: ['离线', 'badge', 'dot off'], unknown: ['未知', 'badge', 'dot'] };
    if (!status || !map[status]) return;
    var conf = map[status];
    var badge = document.querySelector('[data-conn-badge]');
    if (badge) {
      badge.className = conf[1];
      badge.innerHTML = '<span class="' + conf[2] + '"></span>' + conf[0];
    }
    var value = document.querySelector('[data-conn-value]');
    if (value) {
      value.textContent = conf[0];
      if (status !== 'online') value.classList.add('muted');
    }
  })();

  /* 带 #锚点 打开时（如常用 → 经营分析 → analytics.html#analysis）：
     只滚动页面的 .body 容器，避免把状态栏 / 导航栏一起滚出视口 */
  (function () {
    var hash = location.hash;
    if (!hash || hash.length < 2) return;
    var target = document.querySelector(hash);
    var scroller = document.querySelector('.body');
    if (!target || !scroller) return;
    var top = target.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop - 12;
    scroller.scrollTop = Math.max(0, top);
    window.scrollTo(0, 0);
  })();

  /* 一级模块切换：页面头部标题点击展开菜单（按钮加 data-mod-toggle="#modMenu"） */
  (function () {
    var btn = document.querySelector('[data-mod-toggle]');
    if (!btn) return;
    var menu = document.querySelector(btn.getAttribute('data-mod-toggle'));
    if (!menu) return;
    function set(open) {
      menu.classList.toggle('open', !!open);
      btn.classList.toggle('open', !!open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    btn.addEventListener('click', function (event) {
      event.stopPropagation();
      set(!menu.classList.contains('open'));
    });
    menu.addEventListener('click', function (event) { event.stopPropagation(); });
    document.addEventListener('click', function () { set(false); });
    document.addEventListener('keydown', function (event) { if (event.key === 'Escape') set(false); });
  })();

  /* ==========================================================================
     页面过渡 Loading（方案 A）：页内跳转时盖住白帧
     - 只拦截站内 .html 链接，外链 / 锚点 / 新窗口一律不动
     - 6s 兜底淡出，避免导航被取消时遮罩卡住
     ========================================================================== */
  var ASSET_BASE = (function () {
    var s = document.currentScript;
    if (!s || !s.src) return '';
    return s.src.slice(0, s.src.lastIndexOf('/') + 1);
  })();

  /* 过渡与提示组件样式：独立文件，页面没引用时自动挂上 */
  (function ensureOverlayCss() {
    if (document.querySelector('link[data-app-overlay]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = ASSET_BASE + 'app-overlay.css';
    link.setAttribute('data-app-overlay', '');
    document.head.appendChild(link);
  })();

  function appRoot() { return document.querySelector('.app') || document.body; }

  function ensureLoader() {
    var app = appRoot();
    var el = app.querySelector('.app-loader');
    if (el) return el;
    el = document.createElement('div');
    el.className = 'app-loader';
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML =
      '<div class="al-glow"></div>' +
      '<img class="al-logo" src="' + ASSET_BASE + 'assets/logo.png" alt="">' +
      '<div class="al-dots"><i></i><i></i><i></i></div>' +
      '<div class="al-txt">正在加载</div>';
    app.appendChild(el);
    return el;
  }

  var loaderFailsafe = null;

  window.appLoader = function (show) {
    var el = ensureLoader();
    if (!el) return;
    clearTimeout(loaderFailsafe);
    if (show === false) {
      el.classList.add('out');
      loaderFailsafe = setTimeout(function () { el.hidden = true; el.classList.remove('out'); }, 220);
      return;
    }
    el.hidden = false;
    el.classList.remove('out');
    loaderFailsafe = setTimeout(function () {
      el.classList.add('out');
      loaderFailsafe = setTimeout(function () { el.hidden = true; el.classList.remove('out'); }, 220);
    }, 6000);
  };

  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#') return;
    if (/^(https?:|mailto:|tel:|javascript:|blob:|data:)/i.test(href)) return;
    if (link.target === '_blank' || link.hasAttribute('download')) return;
    window.appLoader(true);
  }, true);

  /* ==========================================================================
     顶部错误横幅（方案 C）
     appAlert({ level:'error|warn|ok', title, desc, action, busyText, onAction, duration })
     - 导航栏下缘 8px，同标题 10s 内不重复弹，最多并存 2 条
     - 默认 3.4s 自动收；带操作 6s；按下暂停倒计时；上滑可关
     ========================================================================== */
  var BANNER_ICONS = {
    error: '<path d="M8 4.4v4.2"/><path d="M8 11.4v.1"/><circle cx="8" cy="8" r="6.4"/>',
    warn: '<path d="M8 3.2 13.6 13H2.4L8 3.2Z"/><path d="M8 6.8v2.4"/><path d="M8 11.2v.1"/>',
    ok: '<path d="M3.2 8.4 6.4 11.6 12.8 4.8"/>'
  };
  var alertRecent = {};
  var alertLive = {};

  function bannerHost() {
    var app = appRoot();
    var host = app.querySelector('.app-banner-host');
    if (!host) {
      host = document.createElement('div');
      host.className = 'app-banner-host';
      app.appendChild(host);
    }
    var nav = app.querySelector('.navbar');
    var top = 8;
    if (nav) {
      var base = app.getBoundingClientRect().top;
      top = Math.round(nav.getBoundingClientRect().bottom - base + 8);
    }
    host.style.top = Math.max(8, top) + 'px';
    return host;
  }

  function buildBanner(opts, duration) {
    var level = opts.level === 'warn' ? 'warn' : opts.level === 'ok' ? 'ok' : 'error';
    var el = document.createElement('div');
    el.className = 'app-banner' + (level === 'error' ? '' : ' lv-' + level);
    el.setAttribute('role', 'alert');
    el.setAttribute('aria-live', 'assertive');

    var ic = document.createElement('div');
    ic.className = 'ab-ic';
    ic.innerHTML = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + BANNER_ICONS[level] + '</svg>';

    var cp = document.createElement('div');
    cp.className = 'ab-cp';
    var title = document.createElement('b');
    title.textContent = opts.title || '操作失败';
    cp.appendChild(title);
    var desc = document.createElement('p');
    desc.textContent = opts.desc || '';
    if (opts.desc) cp.appendChild(desc);

    var act = document.createElement('div');
    act.className = 'ab-act';
    var retry = null;
    if (opts.action) {
      retry = document.createElement('button');
      retry.type = 'button';
      retry.className = 'ab-retry';
      retry.textContent = opts.action;
      act.appendChild(retry);
    }
    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'ab-x';
    closeBtn.setAttribute('aria-label', '关闭');
    closeBtn.textContent = '×';
    act.appendChild(closeBtn);

    var meter = document.createElement('div');
    meter.className = 'ab-meter';
    meter.innerHTML = '<i style="animation-duration:' + (duration / 1000) + 's"></i>';

    el.appendChild(ic); el.appendChild(cp); el.appendChild(act); el.appendChild(meter);

    var remain = duration, startedAt = 0, timer = null, closed = false;

    function arm() {
      startedAt = Date.now();
      timer = setTimeout(dismiss, remain);
    }
    function pause() {
      if (!timer) return;
      clearTimeout(timer);
      timer = null;
      remain -= Date.now() - startedAt;
      el.classList.add('paused');
    }
    function resume() {
      if (timer || remain < 120 || closed) return;
      el.classList.remove('paused');
      arm();
    }
    function dismiss() {
      if (closed) return;
      closed = true;
      clearTimeout(timer);
      el.classList.remove('in');
      el.classList.add('out');
      setTimeout(function () {
        if (el.parentNode) el.parentNode.removeChild(el);
        Object.keys(alertLive).forEach(function (k) { if (alertLive[k] === el) delete alertLive[k]; });
      }, 220);
    }

    if (retry) {
      retry.addEventListener('click', function () {
        retry.disabled = true;
        retry.textContent = opts.busyText || '处理中…';
        clearTimeout(timer);
        if (typeof opts.onAction === 'function') {
          try { opts.onAction(); } catch (e) {}
        }
        setTimeout(dismiss, 520);
      });
    }
    closeBtn.addEventListener('click', dismiss);

    el.addEventListener('pointerdown', function (event) {
      el._downY = event.clientY;
      pause();
    });
    el.addEventListener('pointerup', function (event) {
      var up = el._downY;
      el._downY = null;
      if (up !== null && up - event.clientY > 28) { dismiss(); return; }
      resume();
    });
    el.addEventListener('pointercancel', resume);

    el._reset = function (next, dur) {
      title.textContent = next.title || title.textContent;
      if (next.desc) { desc.textContent = next.desc; if (!desc.parentNode) cp.appendChild(desc); }
      clearTimeout(timer);
      closed = false;
      remain = dur;
      el.classList.remove('out');
      el.classList.add('in');
      arm();
    };

    requestAnimationFrame(function () { el.classList.add('in'); });
    arm();
    return el;
  }

  window.appAlert = function (opts) {
    opts = opts || {};
    var level = opts.level || 'error';
    var duration = opts.duration || (opts.action ? 6000 : 3400);
    var key = level + '|' + (opts.title || '');

    var live = alertLive[key];
    if (live && live.parentNode && alertRecent[key] && Date.now() - alertRecent[key] < 10000) {
      live._reset(opts, duration);
      alertRecent[key] = Date.now();
      return live;
    }

    var host = bannerHost();
    while (host.children.length >= 2) host.removeChild(host.firstElementChild);

    var el = buildBanner(opts, duration);
    host.appendChild(el);
    alertLive[key] = el;
    alertRecent[key] = Date.now();
    return el;
  };

})();

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成两个静态原型页：
  recipe-list.html    -> /products/recipes 现制商品列表
  recipe-detail.html  -> 现制商品详情（右侧抽屉，含基础信息 / 制作流程）

母版：recipe-library.html（线上平台 /products/recipes 的真实静态快照）
     直接复用其已编译的 element-plus + 组件样式，DOM 需带对应 data-v-* 属性才能命中样式。
数据：按 types/recipe.ts 的字段语义构造，RCP-011 香浓巧克力为完整变体样例。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'recipe-library.html'
SRC = BASE.read_text(encoding='utf-8')

# ---------- scope id（取自母版，勿改） ----------
V_SHELL = 'e7291ef4'   # 侧边栏 + 内容壳
V_PAGE = '794ae131'    # RecipeListPage
V_DRAWER = '9ea2e778'  # RecipeDrawer
V_PAGER = '16b8fa4e'   # TablePagination
V_OPS = '5ba75a65'     # AdaptiveOperationMenu

# ---------- 从母版提取 head / aside ----------
head_end = SRC.index('</head>')
HEAD = SRC[:head_end] + '</head>'
HEAD = HEAD.replace(
    '<title>VendSolution — 京品高科运营平台</title>',
    '<title>__TITLE__</title>'
)
aside_start = SRC.index('<aside')
aside_end = SRC.index('</aside>') + len('</aside>')
ASIDE = SRC[aside_start:aside_end]
ASIDE = ASIDE.replace(
    'http://localhost:5173/brand/vendsolution-mark.png',
    'assets/brand/vendsolution-mark.png'
)

# ---------- 列表数据：(编码, 名称, 分类, 适用杯型, 机器, 状态, 更新日期, 生效范围) ----------
RECIPES = [
    ('RCP-011', '香浓巧克力', 'COFFEE', 'Tall / Grande / Venti', 'WSD 1008, TCN S3', 'ACTIVE', '2026/11/24', '全局'),
    ('RCP-004', '拿铁', 'COFFEE', 'Tall / Grande / Venti', 'WSD 1008, TCN S3', 'ACTIVE', '2026/11/20', '全局'),
    ('RCP-006', '美式', 'COFFEE', 'Tall / Grande', 'WSD 1008', 'ACTIVE', '2026/11/19', '全局'),
    ('RCP-008', '卡布奇诺', 'COFFEE', 'Tall / Grande', 'WSD 1008, TCN S3', 'DRAFT', '2026/11/17', '香港运营中心'),
    ('RCP-012', '燕麦拿铁', 'COFFEE', 'Tall / Grande', 'TCN S3', 'ACTIVE', '2026/11/15', '香港运营中心'),
    ('RCP-020', '焦糖玛奇朵', 'COFFEE', 'Grande / Venti', 'TCN S3', 'DRAFT', '2026/11/12', '全局'),
    ('RCP-015', '抹茶拿铁', 'TEA', 'Tall / Grande', 'TCN S3', 'ACTIVE', '2026/11/09', '全局'),
    ('RCP-018', '茉莉绿茶', 'TEA', 'Tall / Grande / Venti', 'WSD 1008', 'ACTIVE', '2026/11/05', '全局'),
]
CAT_LABEL = {'COFFEE': '咖啡', 'TEA': '茶'}
STATUS_LABEL = {'ACTIVE': '启用', 'DRAFT': '草稿'}

# ---------- 配方详情数据 ----------
# 工序：name 原料名称 / code 原料编码 / amount 用量 / unit 单位 /
#       hot 热水量 / cold 冷水量 / rpm 搅拌速度 / gps 出料速度 / gap 出水间隔 / pre 预冲泡
def s(name, code, amount, unit, hot=0, cold=0, rpm=0, gps=0, gap=0, pre=0, water=False):
    return dict(name=name, code=code, amount=amount, unit=unit, hot=hot, cold=cold,
                rpm=rpm, gps=gps, gap=gap, pre=pre, water=water)


DETAILS = {
    'RCP-011': dict(
        name='香浓巧克力', category='COFFEE', price=18.0, currency='CNY',
        machines=['WSD 1008', 'TCN S3'], status='ACTIVE', scope='全局',
        cups=[dict(id='cup-tall', name='Tall', volumeMl=355, isDefault=True, price=18.0),
              dict(id='cup-grande', name='Grande', volumeMl=473, price=21.0),
              dict(id='cup-venti', name='Venti', volumeMl=591, price=24.0)],
        temps=[dict(key='HOT', isDefault=True), dict(key='ICE')],
        steps={
            'cup-tall|HOT': [
                s('巧克力粉', 'CHC-01', 25, 'g', hot=0, gps=12, pre=0),
                s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
                s('热水', 'WTR-01', 0, 'ml', hot=180, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 150, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 8, 'g', gps=10),
            ],
            'cup-tall|ICE': [
                s('巧克力粉', 'CHC-01', 25, 'g', gps=12),
                s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
                s('冷水', 'WTR-01', 0, 'ml', cold=140, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 90, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 8, 'g', gps=10),
            ],
            'cup-grande|HOT': [
                s('巧克力粉', 'CHC-01', 33, 'g', gps=12),
                s('浓缩咖啡', 'ESP-01', 40, 'ml', gps=8),
                s('热水', 'WTR-01', 0, 'ml', hot=230, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 195, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 10, 'g', gps=10),
            ],
            'cup-grande|ICE': [
                s('巧克力粉', 'CHC-01', 33, 'g', gps=12),
                s('浓缩咖啡', 'ESP-01', 40, 'ml', gps=8),
                s('冷水', 'WTR-01', 0, 'ml', cold=180, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 120, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 10, 'g', gps=10),
            ],
            'cup-venti|HOT': [
                s('巧克力粉', 'CHC-01', 40, 'g', gps=12),
                s('浓缩咖啡', 'ESP-01', 48, 'ml', gps=8),
                s('热水', 'WTR-01', 0, 'ml', hot=280, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 240, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 13, 'g', gps=10),
            ],
            'cup-venti|ICE': [
                s('巧克力粉', 'CHC-01', 40, 'g', gps=12),
                s('浓缩咖啡', 'ESP-01', 48, 'ml', gps=8),
                s('冷水', 'WTR-01', 0, 'ml', cold=220, gap=8, water=True),
                s('全脂牛奶', 'MLK-01', 150, 'ml', gps=18),
                s('香草糖浆', 'SYR-02', 13, 'g', gps=10),
            ],
        },
        pers={
            'cup-tall|HOT': [
                dict(id='pers-s1', title='巧克力粉', options=[
                    dict(label='浓郁', delta='+5', unit='g'),
                    dict(label='清爽', delta='-5', unit='g')]),
                dict(id='pers-s4', title='全脂牛奶', options=[
                    dict(label='多加奶', delta='+30', unit='ml'),
                    dict(label='少奶', delta='-30', unit='ml')]),
                dict(id='pers-s5', title='香草糖浆', options=[
                    dict(label='加甜', delta='+5', unit='g'),
                    dict(label='半糖', delta='-4', unit='g')]),
            ],
        },
        addons=[
            dict(id='ad-1', ingredientId='ESP-01', name='浓缩咖啡', amount=30, unit='ml', price=3.0),
            dict(id='ad-2', ingredientId='MLK-04', name='燕麦奶', amount=150, unit='ml', price=4.0),
        ],
    ),
}

# 其余配方：两杯型 + 单温度，工序 3~4 步（未配置个性化 / 加料）
SIMPLE = {
    'RCP-004': ('拿铁', 'COFFEE', 16.0, ['WSD 1008', 'TCN S3'], [
        s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
        s('蒸汽牛奶', 'MLK-01', 180, 'ml', gps=18),
        s('奶泡', 'MLK-01', 40, 'ml', gps=12)]),
    'RCP-006': ('美式', 'COFFEE', 13.0, ['WSD 1008'], [
        s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
        s('热水', 'WTR-01', 0, 'ml', hot=200, gap=8, water=True)]),
    'RCP-008': ('卡布奇诺', 'COFFEE', 17.0, ['WSD 1008', 'TCN S3'], [
        s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
        s('蒸汽牛奶', 'MLK-01', 120, 'ml', gps=18),
        s('奶泡', 'MLK-01', 90, 'ml', gps=10)]),
    'RCP-012': ('燕麦拿铁', 'COFFEE', 19.0, ['TCN S3'], [
        s('浓缩咖啡', 'ESP-01', 30, 'ml', gps=8),
        s('燕麦奶', 'MLK-04', 200, 'ml', gps=18)]),
    'RCP-020': ('焦糖玛奇朵', 'COFFEE', 21.0, ['TCN S3'], [
        s('浓缩咖啡', 'ESP-01', 40, 'ml', gps=8),
        s('焦糖糖浆', 'SYR-05', 12, 'g', gps=10),
        s('蒸汽牛奶', 'MLK-01', 200, 'ml', gps=18)]),
    'RCP-015': ('抹茶拿铁', 'TEA', 18.0, ['TCN S3'], [
        s('抹茶粉', 'TEA-02', 6, 'g', gps=6),
        s('热水', 'WTR-01', 0, 'ml', hot=60, gap=6, water=True),
        s('蒸汽牛奶', 'MLK-01', 200, 'ml', gps=18)]),
    'RCP-018': ('茉莉绿茶', 'TEA', 11.0, ['WSD 1008'], [
        s('茉莉绿茶包', 'TEA-05', 1, '包', pre=0),
        s('热水', 'WTR-01', 0, 'ml', hot=320, gap=10, water=True)]),
}
for code, (nm, cat, price, machines, steps) in SIMPLE.items():
    DETAILS[code] = dict(
        name=nm, category=cat, price=price, currency='CNY', machines=machines,
        status='ACTIVE', scope='全局',
        cups=[dict(id='cup-tall', name='Tall', volumeMl=355, isDefault=True, price=price),
              dict(id='cup-large', name='Large', volumeMl=473, price=round(price + 2.5, 2))],
        temps=[dict(key='HOT', isDefault=True)],
        steps={'cup-tall|HOT': steps, 'cup-large|HOT': steps},
        pers={}, addons=[],
    )

import json
DETAIL_JSON = json.dumps(DETAILS, ensure_ascii=False)

# ---------- 表格主体 ----------
def rows_html():
    out = []
    for (code, name, cat, cups, machines, status, updated, scope) in RECIPES:
        badge = 'status-badge--active' if status == 'ACTIVE' else 'status-badge--draft'
        out.append(f'''        <tr data-v-{V_PAGE}="">
          <td data-v-{V_PAGE}="" class="name-td">
            <div data-v-{V_PAGE}="" class="name-cell">
              <span data-v-{V_PAGE}="" class="recipe-row-image-slot"></span>
              <button data-v-{V_PAGE}="" type="button" class="name-link" data-code="{code}">{name}</button>
              <span data-v-{V_PAGE}="" class="name-code">{code}</span>
            </div>
          </td>
          <td data-v-{V_PAGE}="">{CAT_LABEL[cat]}</td>
          <td data-v-{V_PAGE}=""><span data-v-{V_PAGE}="" class="muted-text">{cups}</span></td>
          <td data-v-{V_PAGE}="" class="col-machine"><span data-v-{V_PAGE}="" class="machine-text" title="{machines}">{machines}</span></td>
          <td data-v-{V_PAGE}=""><span data-v-{V_PAGE}="" class="status-badge {badge}">{STATUS_LABEL[status]}</span></td>
          <td data-v-{V_PAGE}=""><span data-v-{V_PAGE}="" class="muted-text">{updated}</span></td>
          <td data-v-{V_PAGE}="">{scope}</td>
          <td data-v-{V_PAGE}="" class="col-actions col-actions--adaptive">
            <div data-v-{V_OPS}="" class="operation-menu">
              <div data-v-{V_OPS}="" class="operation-visible">
                <button data-v-{V_OPS}="" type="button" class="action-btn" data-edit="{code}">编辑</button>
                <div data-v-{V_OPS}="" class="operation-more">
                  <button data-v-{V_OPS}="" type="button" class="icon-btn" aria-label="更多操作" data-more="{code}">⋯</button>
                </div>
              </div>
            </div>
          </td>
        </tr>''')
    return '\n'.join(out)

TABLE_HEAD = '\n'.join(
    f'                <th data-v-{V_PAGE}="">{h}</th>'
    for h in ['商品名称', '分类', '适用杯型', '机器', '状态', '更新日期', '生效范围', '操作']
)

# ---------- 主内容 ----------
MAIN = f'''      <main data-v-{V_SHELL}="" class="el-main main main--viewport">
        <div data-v-{V_PAGE}="" class="recipe-page">
          <header data-v-{V_PAGE}="" class="page-header">
            <div data-v-{V_PAGE}="" class="page-header__text">
              <p data-v-{V_PAGE}="" class="page-label">RECIPE LIBRARY</p>
              <h1 data-v-{V_PAGE}="" class="page-title">现制商品</h1>
              <p data-v-{V_PAGE}="" class="page-description">管理饮品制作配方，一个配方可绑定多个杯型。</p>
            </div>
            <button data-v-{V_PAGE}="" type="button" class="primary-btn" id="btnCreate">＋ 创建现制商品</button>
          </header>

          <section data-v-{V_PAGE}="" class="panel panel-overflow-safe">
            <div data-v-{V_PAGE}="" class="filter-panel">
              <div data-v-{V_PAGE}="" class="filter-toolbar">
                <label data-v-{V_PAGE}="" class="filter-search">
                  <svg data-v-{V_PAGE}="" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><circle cx="7" cy="7" r="4.25" fill="none" stroke="currentColor" stroke-width="1.4"></circle><path d="M10.2 10.2L13 13" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"></path></svg>
                  <input data-v-{V_PAGE}="" id="kw" type="search" placeholder="输入商品名称搜索" aria-label="输入商品名称搜索">
                </label>
                <button data-v-{V_PAGE}="" type="button" class="filter-funnel is-on" aria-expanded="true" aria-label="显示或隐藏筛选项" id="btnFunnel">
                  <svg data-v-{V_PAGE}="" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M4 5h16l-6.2 7.2V19l-3.6 2v-8.8L4 5z"></path></svg>
                </button>
                <button data-v-{V_PAGE}="" type="button" class="list-refresh-button" aria-label="刷新" title="刷新" id="btnRefresh">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 7v5h-5M20 12a8 8 0 1 0-2.3 5.7M20 12a8 8 0 0 0-2.3-5.7"></path></svg>
                </button>
              </div>
              <div data-v-{V_PAGE}="" class="filter-chip-row" id="chipRow">
                <div data-v-{V_PAGE}="" class="filter-chip-wrap">
                  <button data-v-{V_PAGE}="" type="button" class="filter-chip" aria-expanded="false" data-filter="machine">
                    <span data-v-{V_PAGE}="">机器</span>
                    <svg data-v-{V_PAGE}="" class="filter-chip__arrow" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path fill="currentColor" d="M3 4.5L6 7.5L9 4.5"></path></svg>
                  </button>
                  <div class="rp-popover" data-pop="machine" hidden>
                    <label><input type="checkbox" value="WSD 1008"> WSD 1008</label>
                    <label><input type="checkbox" value="TCN S3"> TCN S3</label>
                    <label><input type="checkbox" value="Smooder 001"> Smooder 001</label>
                  </div>
                </div>
                <div data-v-{V_PAGE}="" class="filter-chip-wrap">
                  <button data-v-{V_PAGE}="" type="button" class="filter-chip" aria-expanded="false" aria-label="租户" data-filter="scope">
                    <span data-v-{V_PAGE}="">租户</span>
                    <svg data-v-{V_PAGE}="" class="filter-chip__arrow" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path fill="currentColor" d="M3 4.5L6 7.5L9 4.5"></path></svg>
                  </button>
                  <div class="rp-popover" data-pop="scope" hidden>
                    <label><input type="checkbox" value="全局"> 全局</label>
                    <label><input type="checkbox" value="香港运营中心"> 香港运营中心</label>
                  </div>
                </div>
                <button data-v-{V_PAGE}="" type="button" class="filter-clear-all" id="btnClear">清除过滤条件</button>
              </div>
            </div>

            <div data-v-{V_PAGE}="" class="table-frame">
              <div data-v-{V_PAGE}="" class="table-wrap table-wrap-overflow-safe">
                <table data-v-{V_PAGE}="" class="recipe-table">
                  <thead data-v-{V_PAGE}="">
                    <tr data-v-{V_PAGE}="">
{TABLE_HEAD}
                    </tr>
                  </thead>
                  <tbody data-v-{V_PAGE}="" id="rows">
{rows_html()}
                  </tbody>
                </table>
              </div>
            </div>

            <div data-v-{V_PAGER}="" class="table-pagination">
              <span data-v-{V_PAGER}="" class="table-pagination__range" id="pagerRange">显示 1-8 / 8 个配方</span>
              <div data-v-{V_PAGER}="" class="table-pagination__controls">
                <button data-v-{V_PAGER}="" type="button" class="page-btn" disabled>‹</button>
                <button data-v-{V_PAGER}="" type="button" class="page-btn page-btn--active">1</button>
                <button data-v-{V_PAGER}="" type="button" class="page-btn" disabled>›</button>
              </div>
            </div>
          </section>
        </div>
      </main>'''

# ---------- 抽屉（详情页） ----------
DRAWER = f'''  <div class="el-overlay is-drawer el-modal-drawer" id="drawerOverlay" style="z-index:2002">
    <div class="recipe-drawer-root el-drawer rtl" role="dialog" aria-modal="true" aria-labelledby="drawerTitle" style="width: min(740px, 100vw);">
      <span class="el-drawer__sr-focus" tabindex="-1"></span>
      <div class="el-drawer__body">
        <div data-v-{V_DRAWER}="" class="recipe-drawer">
          <header data-v-{V_DRAWER}="" class="drawer-header">
            <div data-v-{V_DRAWER}="" class="drawer-header__text">
              <p data-v-{V_DRAWER}="" class="drawer-label">现制商品详情</p>
              <h2 data-v-{V_DRAWER}="" class="drawer-title" id="drawerTitle">香浓巧克力</h2>
              <p data-v-{V_DRAWER}="" class="drawer-subtitle" id="drawerSubtitle">咖啡 · RCP-011</p>
            </div>
            <button data-v-{V_DRAWER}="" type="button" class="close-btn" aria-label="关闭" id="btnCloseDrawer">×</button>
          </header>

          <nav data-v-{V_DRAWER}="" class="drawer-tabs">
            <button data-v-{V_DRAWER}="" type="button" class="drawer-tab drawer-tab--active" data-tab="basic">基本信息</button>
            <button data-v-{V_DRAWER}="" type="button" class="drawer-tab" data-tab="process">制作流程</button>
          </nav>

          <div data-v-{V_DRAWER}="" class="drawer-body" id="drawerBody">
            <section data-v-{V_DRAWER}="" class="section-card" data-pane="basic">
              <div data-v-{V_DRAWER}="" class="section-card__head">
                <h3 data-v-{V_DRAWER}="" class="section-card__title">基本信息</h3>
                <p data-v-{V_DRAWER}="" class="section-card__desc">用于识别配方并关联可执行的设备</p>
              </div>
              <div data-v-{V_DRAWER}="" class="field-grid">
                <div data-v-{V_DRAWER}="" class="field field--full">
                  <span data-v-{V_DRAWER}="" class="field__label">适用机器 <span data-v-{V_DRAWER}="" class="field__optional">（可选）</span></span>
                  <div data-v-{V_DRAWER}="" class="machine-box" id="fMachines"></div>
                </div>
                <label data-v-{V_DRAWER}="" class="field">
                  <span data-v-{V_DRAWER}="" class="field__label">商品名称 <span data-v-{V_DRAWER}="" class="field__required" aria-hidden="true">*</span></span>
                  <input data-v-{V_DRAWER}="" type="text" class="field__input" id="fName" readonly>
                </label>
                <label data-v-{V_DRAWER}="" class="field">
                  <span data-v-{V_DRAWER}="" class="field__label">商品编码</span>
                  <input data-v-{V_DRAWER}="" type="text" class="field__input recipe-code" id="fCode" readonly>
                </label>
              </div>
              <label data-v-{V_DRAWER}="" class="field recipe-base-price">
                <span data-v-{V_DRAWER}="" class="field__label">价格</span>
                <div data-v-{V_DRAWER}="" class="recipe-price-input">
                  <input data-v-{V_DRAWER}="" type="number" class="field__input" id="fPrice" readonly>
                  <span id="fCurrency">CNY</span>
                </div>
              </label>
              <div data-v-{V_DRAWER}="" class="recipe-image-field">
                <span data-v-{V_DRAWER}="" class="field__label">商品图片</span>
                <span data-v-{V_DRAWER}="" class="machine-placeholder">未上传图片</span>
                <small data-v-{V_DRAWER}="" class="machine-placeholder">建议 1:1 正方形，JPG / PNG / WebP，最大 5 MB</small>
              </div>
            </section>

            <div data-v-{V_DRAWER}="" class="process-tab" data-pane="process" hidden>
              <section data-v-{V_DRAWER}="" class="section-card">
                <div data-v-{V_DRAWER}="" class="section-toolbar">
                  <div>
                    <h3 data-v-{V_DRAWER}="" class="section-card__title">杯型</h3>
                    <p data-v-{V_DRAWER}="" class="section-card__desc">选择杯型后，下方制作流程与个性化选项会同步切换。</p>
                  </div>
                </div>
                <div data-v-{V_DRAWER}="" class="cup-grid" id="cupGrid"></div>
                <div data-v-{V_DRAWER}="" class="temp-block">
                  <div data-v-{V_DRAWER}="" class="section-toolbar">
                    <div>
                      <h3 data-v-{V_DRAWER}="" class="section-card__title">温度</h3>
                      <p data-v-{V_DRAWER}="" class="section-card__desc">温度规格仅适用于当前杯型；添加或删除不会影响其他杯型。</p>
                    </div>
                  </div>
                  <div data-v-{V_DRAWER}="" class="temp-chips" id="tempChips"></div>
                </div>
              </section>

              <section data-v-{V_DRAWER}="" class="section-card">
                <div data-v-{V_DRAWER}="" class="section-toolbar">
                  <div>
                    <h3 data-v-{V_DRAWER}="" class="section-card__title" id="processTitle">制作过程</h3>
                    <p data-v-{V_DRAWER}="" class="section-card__desc">当前杯型与温度下的原料及执行顺序。</p>
                  </div>
                  <label data-v-{V_DRAWER}="" class="advanced-toggle">
                    <span>高级</span>
                    <button data-v-{V_DRAWER}="" type="button" class="switch switch--sm" id="switchAdvanced" aria-pressed="false"><span data-v-{V_DRAWER}="" class="switch__thumb"></span></button>
                    <span id="advancedLabel">关</span>
                  </label>
                </div>
                <div data-v-{V_DRAWER}="" class="process-table-wrap" id="processTable"></div>
              </section>

              <section data-v-{V_DRAWER}="" class="section-card">
                <div data-v-{V_DRAWER}="" class="section-toolbar">
                  <div>
                    <h3 data-v-{V_DRAWER}="" class="section-card__title" id="persTitle">个性化选项</h3>
                    <p data-v-{V_DRAWER}="" class="section-card__desc">分组由制作过程原料自动生成，组名不可修改；可配置选项。</p>
                  </div>
                </div>
                <div data-v-{V_DRAWER}="" class="pers-grid" id="persGrid"></div>
              </section>

              <section data-v-{V_DRAWER}="" class="section-card">
                <div data-v-{V_DRAWER}="" class="section-toolbar">
                  <div>
                    <h3 data-v-{V_DRAWER}="" class="section-card__title">加料</h3>
                    <p data-v-{V_DRAWER}="" class="section-card__desc">为当前杯型创建独立可选加料。</p>
                  </div>
                </div>
                <div id="addonWrap"></div>
              </section>
            </div>
          </div>

          <footer data-v-{V_DRAWER}="" class="drawer-footer">
            <div data-v-{V_DRAWER}="" class="recipe-footer-status">
              <span>商品状态</span>
              <button data-v-{V_DRAWER}="" type="button" class="switch switch--sm" id="switchStatus" aria-pressed="true"><span data-v-{V_DRAWER}="" class="switch__thumb"></span></button>
              <span data-v-{V_DRAWER}="" class="recipe-status-badge is-enabled" id="statusBadge">启用</span>
            </div>
            <button data-v-{V_DRAWER}="" type="button" class="footer-btn footer-btn--outline" id="btnCancel">取消</button>
            <button data-v-{V_DRAWER}="" type="button" class="footer-btn footer-btn--primary" id="btnSave">保存</button>
          </footer>
        </div>
      </div>
    </div>
  </div>'''

EXTRA_CSS = '''
<style>
  /* 静态原型补充：筛选浮层 / 行操作菜单 / 抽屉遮罩 */
  [hidden]{display:none !important}
  .recipe-table td.name-td{min-width:240px}
  .recipe-row-image-slot:empty{display:none}
  .recipe-table th.col-machine,.recipe-table td.col-machine{min-width:190px}
  .rp-banner{position:sticky;top:0;z-index:1000;background:#EEF2FF;color:#2f4ab8;
    font:600 12px/32px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    padding:0 16px;border-bottom:1px solid #c9d4ff}
  .rp-popover{position:absolute;top:calc(100% + 6px);left:0;z-index:30;min-width:200px;
    padding:8px;border:1px solid #d9e1ec;border-radius:10px;background:#fff;
    box-shadow:0 12px 28px rgba(15,23,42,.12);display:flex;flex-direction:column;gap:2px}
  .rp-popover[hidden]{display:none}
  .rp-popover label{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:6px;
    color:#314158;font-size:13px;cursor:pointer}
  .rp-popover label:hover{background:#f8fafc}
  .filter-chip-wrap{position:relative}
  .operation-more{position:relative}
  .rp-menu{position:absolute;right:0;top:calc(100% + 4px);z-index:40;min-width:132px;padding:6px;
    border:1px solid #d9e1ec;border-radius:10px;background:#fff;box-shadow:0 12px 28px rgba(15,23,42,.14)}
  .rp-menu[hidden]{display:none}
  .rp-menu button{display:block;width:100%;padding:8px 10px;border:0;border-radius:6px;
    background:transparent;color:#314158;font-size:13px;text-align:left;cursor:pointer}
  .rp-menu button:hover{background:#f8fafc}
  .rp-menu button.is-danger{color:#d64545}
  .el-overlay.is-drawer{display:flex;justify-content:flex-end;background:rgba(15,23,42,.28);
    backdrop-filter:blur(2px);position:fixed;inset:0}
  .el-drawer.rtl{position:relative;height:100%;background:#fff;display:flex;flex-direction:column}
  .el-drawer__body{flex:1 1 auto;min-height:0;overflow:hidden}
  .rp-empty{padding:18px 16px;color:#8b9ab0;font-size:13px;text-align:center}
  .mini-table td .table-input{width:100%}
  .mini-table td.rp-cell-name,.mini-table th.rp-cell-name{min-width:150px}
  .mini-table td,.mini-table th{white-space:nowrap}
  .rp-static-note{color:#8b9ab0;font-size:12px}
</style>'''


def build(title, drawer=False):
    head = HEAD.replace('__TITLE__', title) + EXTRA_CSS
    body = f'''<body>
<div class="rp-banner">静态原型 · 配方库（/products/recipes）· root 视角 · 数据为演示种子</div>
  <div id="app" data-v-app="">
    <section data-v-{V_SHELL}="" class="el-container layout" style="--app-sidebar-width: 280px;">
{ASIDE}
      <section data-v-{V_SHELL}="" class="el-container content-shell">
{MAIN}
      </section>
    </section>
  </div>
{('  ' + DRAWER) if drawer else ''}
  <script>window.RP_DETAILS = {DETAIL_JSON};</script>
  <script>{SCRIPT}</script>
</body>
</html>'''
    return head + '\n' + body


# ---------- 交互脚本 ----------
SCRIPT = r'''
(function () {
  var D = window.RP_DETAILS || {};
  var state = { cupId: null, tempKey: null, advanced: false, status: 'ACTIVE' };

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  var V = 'data-v-9ea2e778';

  function detailOf(code) { return D[code] || null; }

  /* ---------- 列表页交互 ---------- */
  var rowsBox = document.getElementById('rows');
  function applyListFilter() {
    if (!rowsBox) return;
    var q = (document.getElementById('kw').value || '').trim().toLowerCase();
    var picked = {};
    document.querySelectorAll('.rp-popover input:checked').forEach(function (i) {
      picked[i.value] = true;
    });
    var visible = 0, total = 0;
    rowsBox.querySelectorAll('tr').forEach(function (tr) {
      total++;
      var txt = tr.textContent.toLowerCase();
      var okQ = !q || txt.indexOf(q) >= 0;
      var okF = true;
      var keys = Object.keys(picked);
      if (keys.length) {
        var cells = tr.children;
        var machines = cells[3].textContent;
        var scope = cells[6].textContent.trim();
        okF = keys.some(function (k) { return machines.indexOf(k) >= 0 || scope === k; });
      }
      var show = okQ && okF;
      tr.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    var range = document.getElementById('pagerRange');
    if (range) {
      range.textContent = visible
        ? '显示 1-' + visible + ' / ' + visible + ' 个配方'
        : '暂无现制商品';
    }
  }
  var kw = document.getElementById('kw');
  if (kw) kw.addEventListener('input', applyListFilter);

  document.querySelectorAll('[data-filter]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var pop = btn.parentNode.querySelector('.rp-popover');
      var open = pop.hidden;
      document.querySelectorAll('.rp-popover').forEach(function (p) { p.hidden = true; });
      document.querySelectorAll('[data-filter]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
      pop.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.querySelectorAll('.rp-popover').forEach(function (pop) {
    pop.addEventListener('click', function (e) { e.stopPropagation(); });
    pop.addEventListener('change', applyListFilter);
  });
  document.addEventListener('click', function () {
    document.querySelectorAll('.rp-popover').forEach(function (p) { p.hidden = true; });
    document.querySelectorAll('[data-filter]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    document.querySelectorAll('.rp-menu').forEach(function (m) { m.hidden = true; });
  });
  var clearBtn = document.getElementById('btnClear');
  if (clearBtn) clearBtn.addEventListener('click', function () {
    if (kw) kw.value = '';
    document.querySelectorAll('.rp-popover input').forEach(function (i) { i.checked = false; });
    applyListFilter();
  });
  var funnel = document.getElementById('btnFunnel');
  var chipRow = document.getElementById('chipRow');
  if (funnel) funnel.addEventListener('click', function () {
    var hidden = chipRow.style.display === 'none';
    chipRow.style.display = hidden ? '' : 'none';
    funnel.classList.toggle('is-on', hidden);
    funnel.setAttribute('aria-expanded', hidden ? 'true' : 'false');
  });

  // 行操作：编辑 / 更多
  function gotoDetail(code) {
    location.href = 'recipe-detail.html?code=' + encodeURIComponent(code);
  }
  document.querySelectorAll('[data-edit]').forEach(function (b) {
    b.addEventListener('click', function () { gotoDetail(b.dataset.edit); });
  });
  document.querySelectorAll('.name-link').forEach(function (b) {
    b.addEventListener('click', function () { gotoDetail(b.dataset.code); });
  });
  document.querySelectorAll('[data-more]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var code = b.dataset.more;
      var existed = b.parentNode.querySelector('.rp-menu');
      var open = !existed || existed.hidden;
      document.querySelectorAll('.rp-menu').forEach(function (m) { m.hidden = true; });
      if (existed) existed.remove();
      if (!open) return;
      var menu = el('div', 'rp-menu');
      menu.innerHTML = '<button data-act="edit">编辑</button><button data-act="draft">设为草稿</button><button data-act="delete" class="is-danger">删除</button>';
      menu.addEventListener('click', function (ev) {
        var act = ev.target.dataset.act;
        if (!act) return;
        if (act === 'edit') gotoDetail(code);
        else menu.hidden = true;
      });
      b.parentNode.appendChild(menu);
    });
  });

  /* ---------- 抽屉 ---------- */
  var overlay = document.getElementById('drawerOverlay');
  if (!overlay) return;

  var params = new URLSearchParams(location.search);
  var code = params.get('code') || 'RCP-011';
  var d = detailOf(code);

  function renderHeader() {
    document.getElementById('drawerTitle').textContent = d ? d.name : code;
    document.getElementById('drawerSubtitle').textContent =
      (d ? (d.category === 'COFFEE' ? '咖啡' : '茶') : '未知分类') + ' · ' + code;
  }

  function renderBasic() {
    var box = document.getElementById('fMachines');
    box.innerHTML = '';
    (d.machines || []).forEach(function (m) {
      var tag = el('span', 'machine-tag', esc(m));
      tag.setAttribute(V, '');
      box.appendChild(tag);
    });
    if (!(d.machines || []).length) {
      var ph = el('span', 'machine-placeholder', '选择适用机器');
      ph.setAttribute(V, '');
      box.appendChild(ph);
    }
    document.getElementById('fName').value = d.name;
    document.getElementById('fCode').value = code;
    document.getElementById('fPrice').value = d.price != null ? d.price : '';
    document.getElementById('fCurrency').textContent = d.currency || 'CNY';
  }

  function variantKey() { return state.cupId + '|' + state.tempKey; }

  function renderCups() {
    var grid = document.getElementById('cupGrid');
    grid.innerHTML = '';
    d.cups.forEach(function (cup) {
      var card = el('div', 'cup-card' + (cup.id === state.cupId ? ' cup-card--active' : ''));
      card.setAttribute(V, '');
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      var top = el('div', 'cup-card__top', '<strong data-v-9ea2e778="">' + esc(cup.name) + '</strong>');
      var vol = el('p', 'cup-card__volume', esc(cup.volumeMl) + ' ml');
      card.appendChild(top);
      card.appendChild(vol);
      if (cup.isDefault) {
        var def = el('span', 'cup-default', '默认');
        def.setAttribute(V, '');
        card.appendChild(def);
      }
      card.addEventListener('click', function () {
        state.cupId = cup.id;
        state.tempKey = (d.temps[0] || {}).key || null;
        renderAll();
      });
      grid.appendChild(card);
    });
    var count = d.cups.length;
    grid.className = 'cup-grid' + (count === 1 ? ' cup-grid--single' : '') + ' cup-grid--readonly';
    grid.style.gridTemplateColumns = 'repeat(' + count + ', minmax(0, 1fr))';
  }

  var TEMP_LABEL = { HOT: '热', COLD: '冷', ICE: '冰', ROOM_TEMP: '常温' };

  function renderTemps() {
    var wrap = document.getElementById('tempChips');
    wrap.innerHTML = '';
    d.temps.forEach(function (t) {
      var chip = el('button', 'temp-chip' + (t.key === state.tempKey ? ' temp-chip--active' : ''));
      chip.setAttribute(V, '');
      chip.type = 'button';
      chip.innerHTML = '<span data-v-9ea2e778="" class="temp-chip__label">' + esc(TEMP_LABEL[t.key] || t.key) + '</span>'
        + (t.isDefault ? '<span data-v-9ea2e778="" class="temp-chip__default">默认</span>' : '');
      chip.addEventListener('click', function () {
        state.tempKey = t.key;
        renderAll();
      });
      wrap.appendChild(chip);
    });
  }

  var ADV_COLS = ['顺序', '原料名称', '原料编码', '用量', '单位', '冷水 (ml)', '热水 (ml)',
    '搅拌速度 (rpm)', '出料速度 (g/s)', '出水间隔 (s)', '预冲泡水量 (0–200 ml)'];

  function renderProcess() {
    var box = document.getElementById('processTable');
    var steps = (d.steps || {})[variantKey()] || [];
    var cup = d.cups.filter(function (c) { return c.id === state.cupId; })[0] || {};
    var title = document.getElementById('processTitle');
    title.textContent = '制作过程 · ' + (cup.name || '') + ' / ' + (TEMP_LABEL[state.tempKey] || '');

    if (!steps.length) {
      box.innerHTML = '<p class="rp-empty">该杯型与温度组合尚未配置制作过程。</p>';
      renderPers([]);
      renderAddons();
      return;
    }

    var head = state.advanced
      ? '<tr data-v-9ea2e778="">' + ADV_COLS.map(function (c) {
          return '<th data-v-9ea2e778=""' + (c === '原料名称' ? ' class="rp-cell-name"' : '') + '>' + c + '</th>';
        }).join('') + '</tr>'
      : '<tr data-v-9ea2e778="">' + ['顺序', '原料名称', '用量', '单位'].map(function (c) {
          return '<th data-v-9ea2e778=""' + (c === '原料名称' ? ' class="rp-cell-name"' : '') + '>' + c + '</th>';
        }).join('') + '</tr>';

    var rows = steps.map(function (st, i) {
      if (state.advanced) {
        return '<tr data-v-9ea2e778="">'
          + '<td data-v-9ea2e778="" class="process-order-cell">' + (i + 1) + '</td>'
          + '<td data-v-9ea2e778="" class="rp-cell-name">' + esc(st.name) + '</td>'
          + '<td data-v-9ea2e778="" class="process-code-cell">' + esc(st.code) + '</td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact table-input--amount" value="' + (st.water ? 0 : st.amount) + '" readonly></td>'
          + '<td data-v-9ea2e778="" class="process-unit-cell">' + esc(st.unit) + '</td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.cold || 0) + '" readonly></td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.hot || 0) + '" readonly></td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.rpm || 0) + '" readonly></td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.gps || 0) + '" readonly></td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.gap || 0) + '" readonly></td>'
          + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--compact" value="' + (st.pre || 0) + '" readonly></td>'
          + '</tr>';
      }
      return '<tr data-v-9ea2e778="">'
        + '<td data-v-9ea2e778="">' + (i + 1) + '</td>'
        + '<td data-v-9ea2e778="" class="rp-cell-name">' + esc(st.name) + '</td>'
        + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--num" value="' + (st.water ? 0 : st.amount) + '" readonly></td>'
        + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--unit" value="' + esc(st.unit) + '" readonly></td>'
        + '</tr>';
    }).join('');

    box.innerHTML = '<table data-v-9ea2e778="" class="mini-table' + (state.advanced ? ' mini-table--process' : '') + '">'
      + '<thead data-v-9ea2e778="">' + head + '</thead>'
      + '<tbody data-v-9ea2e778="">' + rows + '</tbody></table>';

    renderPers(steps);
    renderAddons();
  }

  function renderPers(steps) {
    var grid = document.getElementById('persGrid');
    var groups = (d.pers || {})[variantKey()] || [];
    document.getElementById('persTitle').textContent = '个性化选项 · '
      + ((d.cups.filter(function (c) { return c.id === state.cupId; })[0] || {}).name || '')
      + ' / ' + (TEMP_LABEL[state.tempKey] || '');
    grid.innerHTML = '';
    if (!groups.length) {
      var empty = el('div', 'pers-card pers-card--empty', '该规格尚未配置个性化选项。');
      empty.setAttribute(V, '');
      grid.appendChild(empty);
      return;
    }
    groups.forEach(function (g) {
      var card = el('div', 'pers-card');
      card.setAttribute(V, '');
      var head = '<div data-v-9ea2e778="" class="pers-card__head"><div data-v-9ea2e778="" class="pers-group-title pers-group-title--readonly">' + esc(g.title) + '</div></div>';
      var hdr = '<div data-v-9ea2e778="" class="pers-row pers-row--header"><span data-v-9ea2e778="">口味偏好</span><span data-v-9ea2e778="">调节值</span><span data-v-9ea2e778="">单位</span><span data-v-9ea2e778="" class="pers-row__actions"></span></div>';
      var rows = g.options.map(function (o) {
        return '<div data-v-9ea2e778="" class="pers-row">'
          + '<input data-v-9ea2e778="" class="pers-input pers-input--label" value="' + esc(o.label) + '" readonly>'
          + '<input data-v-9ea2e778="" class="pers-input pers-input--delta" value="' + esc(o.delta) + '" readonly>'
          + '<input data-v-9ea2e778="" class="pers-input pers-input--unit" value="' + esc(o.unit || '') + '" readonly>'
          + '<span data-v-9ea2e778="" class="pers-row__actions"></span></div>';
      }).join('');
      card.innerHTML = head + hdr + rows;
      grid.appendChild(card);
    });
  }

  function renderAddons() {
    var wrap = document.getElementById('addonWrap');
    var list = d.addons || [];
    if (!list.length) {
      wrap.innerHTML = '<p class="rp-empty">该配方暂未配置加料。</p>';
      return;
    }
    var rows = list.map(function (a) {
      return '<tr data-v-9ea2e778="">'
        + '<td data-v-9ea2e778="">' + esc(a.name) + '（' + esc(a.ingredientId) + '）</td>'
        + '<td data-v-9ea2e778=""><input data-v-9ea2e778="" class="table-input table-input--num" value="' + a.amount + '" readonly> ' + esc(a.unit || '') + '</td>'
        + '<td data-v-9ea2e778=""><div data-v-9ea2e778="" class="price-cell"><input data-v-9ea2e778="" class="table-input table-input--num" value="' + a.price.toFixed(2) + '" readonly><span data-v-9ea2e778="">CNY</span></div></td>'
        + '</tr>';
    }).join('');
    wrap.innerHTML = '<table data-v-9ea2e778="" class="mini-table"><thead data-v-9ea2e778=""><tr data-v-9ea2e778="">'
      + '<th data-v-9ea2e778="">原料名称</th><th data-v-9ea2e778="">用量 (g)</th><th data-v-9ea2e778="">价格</th>'
      + '</tr></thead><tbody data-v-9ea2e778="">' + rows + '</tbody></table>';
  }

  function renderStatus() {
    var badge = document.getElementById('statusBadge');
    var sw = document.getElementById('switchStatus');
    var on = state.status === 'ACTIVE';
    badge.textContent = on ? '启用' : '草稿';
    badge.classList.toggle('is-enabled', on);
    sw.classList.toggle('switch--on', on);
    sw.setAttribute('aria-pressed', on ? 'true' : 'false');
  }

  function renderAll() {
    renderCups();
    renderTemps();
    renderProcess();
    renderStatus();
  }

  // tab 切换
  function setTab(pane) {
    document.querySelectorAll('.drawer-tab').forEach(function (t) {
      t.classList.toggle('drawer-tab--active', t.dataset.tab === pane);
    });
    document.querySelectorAll('[data-pane]').forEach(function (p) {
      p.hidden = p.dataset.pane !== pane;
    });
    document.getElementById('drawerBody').classList.toggle('drawer-body--process', pane === 'process');
    overlay.querySelector('.el-drawer').style.width =
      pane === 'basic' ? 'min(740px, 100vw)' : 'min(1000px, 100vw)';
  }
  document.querySelectorAll('.drawer-tab').forEach(function (tab) {
    tab.addEventListener('click', function () { setTab(tab.dataset.tab); });
  });

  var swAdv = document.getElementById('switchAdvanced');
  swAdv.addEventListener('click', function () {
    state.advanced = !state.advanced;
    swAdv.classList.toggle('switch--on', state.advanced);
    swAdv.setAttribute('aria-pressed', state.advanced ? 'true' : 'false');
    document.getElementById('advancedLabel').textContent = state.advanced ? '开' : '关';
    renderProcess();
  });

  var swStatus = document.getElementById('switchStatus');
  swStatus.addEventListener('click', function () {
    state.status = state.status === 'ACTIVE' ? 'DRAFT' : 'ACTIVE';
    renderStatus();
  });

  function closeDrawer() { location.href = 'recipe-list.html'; }
  document.getElementById('btnCloseDrawer').addEventListener('click', closeDrawer);
  document.getElementById('btnCancel').addEventListener('click', closeDrawer);
  document.getElementById('btnSave').addEventListener('click', function () {
    var btn = this;
    btn.disabled = true;
    btn.textContent = '保存中…';
    setTimeout(function () { btn.disabled = false; btn.textContent = '保存'; }, 700);
  });
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeDrawer();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrawer();
  });

  if (!d) {
    document.getElementById('drawerTitle').textContent = code;
    document.getElementById('drawerSubtitle').textContent = '该编码暂无演示数据';
    document.getElementById('fName').value = '';
    document.getElementById('fCode').value = code;
    return;
  }

  // 初始化：默认杯型 / 默认温度
  var defCup = d.cups.filter(function (c) { return c.isDefault; })[0] || d.cups[0];
  state.cupId = defCup.id;
  var defTemp = d.temps.filter(function (t) { return t.isDefault; })[0] || d.temps[0];
  state.tempKey = defTemp.key;
  state.status = d.status || 'ACTIVE';
  if (params.get('advanced') === '1') {
    state.advanced = true;
    swAdv.classList.add('switch--on');
    swAdv.setAttribute('aria-pressed', 'true');
    document.getElementById('advancedLabel').textContent = '开';
  }

  renderHeader();
  renderBasic();
  renderAll();
  if (params.get('tab') === 'process') setTab('process');
})();
'''


def main():
    (ROOT / 'recipe-list.html').write_text(build('现制商品 · VendSolution', drawer=False), encoding='utf-8')
    (ROOT / 'recipe-detail.html').write_text(build('现制商品详情 · 香浓巧克力 · VendSolution', drawer=True), encoding='utf-8')
    for name in ('recipe-list.html', 'recipe-detail.html'):
        p = ROOT / name
        print(f'{name}\t{p.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()

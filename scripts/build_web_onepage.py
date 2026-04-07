#!/usr/bin/env python3
"""
构建 OnePage 网页版本 —— V2 可视化增强
自动识别内容类型（数据指标、流程步骤、优先级、风险等级），
渲染为 metric 卡片、流程图、badge、进度条等可视化组件。
"""
import argparse
import os
import json
import re
import html as html_lib


# ─────────── Markdown → HTML (增强版) ───────────

def md_to_html(text):
    if not text:
        return ''
    lines = text.split('\n')
    result = []
    i = 0
    in_ol = False
    in_ul = False

    def close_lists():
        nonlocal in_ol, in_ul
        parts = []
        if in_ol:
            parts.append('</ol>')
            in_ol = False
        if in_ul:
            parts.append('</ul>')
            in_ul = False
        return ''.join(parts)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('|') and stripped.endswith('|'):
            result.append(close_lists())
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            result.append(_render_table(rows))
            continue

        # 独立图片行：![alt](src)
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', stripped)
        if img_match:
            result.append(close_lists())
            alt = html_lib.escape(img_match.group(1))
            src = html_lib.escape(img_match.group(2))
            caption = f'<figcaption>{alt}</figcaption>' if alt else ''
            result.append(f'<figure class="op-figure"><img src="{src}" alt="{alt}" loading="lazy" />{caption}</figure>')
            i += 1
            continue

        ol_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ol_match:
            if not in_ol:
                result.append(close_lists())
                result.append('<ol class="op-list">')
                in_ol = True
            result.append(f'<li>{_inline(ol_match.group(2))}</li>')
            i += 1
            continue

        ul_match = re.match(r'^[-*]\s+(.*)', stripped)
        if ul_match:
            if not in_ul:
                result.append(close_lists())
                result.append('<ul class="op-list">')
                in_ul = True
            result.append(f'<li>{_inline(ul_match.group(1))}</li>')
            i += 1
            continue

        if not stripped:
            result.append(close_lists())
            i += 1
            continue

        result.append(close_lists())
        result.append(f'<p>{_inline(stripped)}</p>')
        i += 1

    result.append(close_lists())
    return '\n'.join(result)


def _inline(text):
    text = html_lib.escape(text)
    # 图片语法 ![alt](src) — 内联时渲染为 img 标签
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="inline-img" />', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def _render_table(rows):
    html_rows = []
    is_header = True
    for row in rows:
        if re.match(r'^\s*\|[\s\-:|]+\|\s*$', row):
            is_header = False
            continue
        cells = row.strip().strip('|').split('|')
        tag = 'th' if is_header else 'td'
        cells_html = ''.join(f'<{tag}>{_inline(c.strip())}</{tag}>' for c in cells)
        html_rows.append(f'<tr>{cells_html}</tr>')
        if is_header:
            is_header = False
    return f'<table>{chr(10).join(html_rows)}</table>'


# ─────────── 内容类型自动识别 ───────────

def _extract_metrics(text):
    """从文本中提取数字指标，返回 [(value, label, color)] 列表"""
    metrics = []
    # 匹配 **数字%** 或 **数字** 模式
    for m in re.finditer(r'\*\*(\d+(?:\.\d+)?%?)\*\*', text):
        val = m.group(1)
        # 获取数字前后的上下文作为label
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        ctx = text[start:end]
        # 清理 markdown
        ctx = re.sub(r'\*\*.*?\*\*', '', ctx).strip()
        # 取最近的中文短语
        label_match = re.search(r'[\u4e00-\u9fff]+[^\n|*]*', ctx)
        label = label_match.group(0).strip('，。、：') if label_match else ''
        if len(label) > 15:
            label = label[:15] + '…'
        metrics.append((val, label))
    return metrics


def _detect_has_priority(text):
    """检测文本是否包含优先级标记（仅匹配独立的 P00/P0/P1/P2）"""
    return bool(re.search(r'(?<!\w)P0{1,2}(?!\w)|(?<!\w)P[12](?!\w)|优先级', text))


def _detect_has_risk_level(text):
    """检测文本是否包含风险等级列"""
    # 需要表头包含"风险等级"，或者同时包含"风险"和独立的等级词
    if '风险等级' in text:
        return True
    if '风险' in text and re.search(r'\|\s*(高|中|低)\s*\|', text):
        return True
    return False


def _detect_is_flow(text):
    """检测是否为流程/步骤型内容（有序列表）"""
    lines = text.strip().split('\n')
    numbered = sum(1 for l in lines if re.match(r'^\d+\.', l.strip()))
    return numbered >= 2


def _detect_is_journey(text):
    """检测是否为用户旅程/时间线型内容"""
    keywords = ['购买后', '预约', '行程', '之前', '之后', '期间', '阶段', '第一步', '第二步']
    return sum(1 for k in keywords if k in text) >= 2


# ─────────── 可视化组件渲染 ───────────

def _render_metric_cards(metrics, color):
    """渲染指标大数卡片"""
    if not metrics:
        return ''
    cards = []
    palette = ['#4F6AF6', '#7C5CFC', '#2DB87F', '#F59E42', '#E8546A', '#3AAFDF']
    for idx, (val, label) in enumerate(metrics[:4]):  # 最多4个
        c = palette[idx % len(palette)]
        cards.append(f'''
        <div class="metric-card" style="--mc:{c}">
          <div class="metric-value">{html_lib.escape(val)}</div>
          <div class="metric-label">{html_lib.escape(label)}</div>
        </div>''')
    return f'<div class="metric-grid">{"".join(cards)}</div>'


def _render_flow_steps(text, color):
    """将有序列表渲染为流程步骤可视化"""
    steps = []
    for m in re.finditer(r'(\d+)\.\s+\*\*(.*?)\*\*[：:]\s*(.*?)(?=\n\d+\.|\Z)', text, re.DOTALL):
        num = m.group(1)
        title = m.group(2)
        desc = m.group(3).strip().replace('\n', ' ')
        steps.append((num, title, desc))

    if not steps:
        # fallback: 简单有序列表
        for m in re.finditer(r'(\d+)\.\s+(.*?)(?=\n\d+\.|\Z)', text, re.DOTALL):
            num = m.group(1)
            content = m.group(2).strip()
            bold_match = re.match(r'\*\*(.*?)\*\*(.*)', content)
            if bold_match:
                steps.append((num, bold_match.group(1), bold_match.group(2).strip().lstrip('：:')))
            else:
                steps.append((num, content[:20], content[20:] if len(content) > 20 else ''))

    if not steps:
        return ''

    items = []
    for num, title, desc in steps:
        items.append(f'''
        <div class="flow-step">
          <div class="flow-node" style="--fc:{color}">
            <div class="flow-num">{html_lib.escape(num)}</div>
          </div>
          <div class="flow-content">
            <div class="flow-title">{_inline(title)}</div>
            <div class="flow-desc">{_inline(desc)}</div>
          </div>
        </div>''')
    return f'<div class="flow-timeline">{"".join(items)}</div>'


def _render_journey(text, color):
    """将用户旅程渲染为时间线"""
    stages = []
    for m in re.finditer(r'[-*]\s+\*\*(.*?)\*\*[：:]\s*(.*?)(?=\n[-*]|\Z)', text, re.DOTALL):
        stage_name = m.group(1)
        desc = m.group(2).strip().replace('\n', ' ')
        stages.append((stage_name, desc))

    if not stages:
        return ''

    items = []
    palette = ['#4F6AF6', '#7C5CFC', '#2DB87F', '#F59E42']
    for idx, (name, desc) in enumerate(stages):
        c = palette[idx % len(palette)]
        items.append(f'''
        <div class="journey-stage">
          <div class="journey-dot" style="background:{c}"></div>
          <div class="journey-line"></div>
          <div class="journey-card" style="--jc:{c}">
            <div class="journey-name">{html_lib.escape(name)}</div>
            <div class="journey-desc">{_inline(desc)}</div>
          </div>
        </div>''')
    return f'<div class="journey-timeline">{"".join(items)}</div>'


def _render_priority_table(rows):
    """渲染带有优先级 badge 的表格"""
    html_rows = []
    is_header = True
    for row in rows:
        if re.match(r'^\s*\|[\s\-:|]+\|\s*$', row):
            is_header = False
            continue
        cells = row.strip().strip('|').split('|')
        if is_header:
            cells_html = ''.join(f'<th>{_inline(c.strip())}</th>' for c in cells)
            html_rows.append(f'<tr>{cells_html}</tr>')
            is_header = False
        else:
            parts = []
            for c in cells:
                ct = c.strip()
                # 优先级 badge
                if re.match(r'^P0{1,2}$', ct):
                    badge_class = 'badge-p00' if ct == 'P00' else 'badge-p0'
                    parts.append(f'<td><span class="priority-badge {badge_class}">{html_lib.escape(ct)}</span></td>')
                elif ct == 'P1':
                    parts.append(f'<td><span class="priority-badge badge-p1">{html_lib.escape(ct)}</span></td>')
                elif ct == 'P2':
                    parts.append(f'<td><span class="priority-badge badge-p2">{html_lib.escape(ct)}</span></td>')
                else:
                    parts.append(f'<td>{_inline(ct)}</td>')
            html_rows.append(f'<tr>{"".join(parts)}</tr>')
    return f'<table class="priority-table">{chr(10).join(html_rows)}</table>'


def _render_risk_table(rows):
    """渲染带有风险等级指示器的表格"""
    html_rows = []
    is_header = True
    for row in rows:
        if re.match(r'^\s*\|[\s\-:|]+\|\s*$', row):
            is_header = False
            continue
        cells = row.strip().strip('|').split('|')
        if is_header:
            cells_html = ''.join(f'<th>{_inline(c.strip())}</th>' for c in cells)
            html_rows.append(f'<tr>{cells_html}</tr>')
            is_header = False
        else:
            parts = []
            for c in cells:
                ct = c.strip()
                if ct == '高':
                    parts.append(f'<td><span class="risk-level risk-high">● {html_lib.escape(ct)}</span></td>')
                elif ct == '中':
                    parts.append(f'<td><span class="risk-level risk-mid">● {html_lib.escape(ct)}</span></td>')
                elif ct == '低':
                    parts.append(f'<td><span class="risk-level risk-low">● {html_lib.escape(ct)}</span></td>')
                else:
                    parts.append(f'<td>{_inline(ct)}</td>')
            html_rows.append(f'<tr>{"".join(parts)}</tr>')
    return f'<table class="risk-table">{chr(10).join(html_rows)}</table>'


def _smart_render_table(rows_text):
    """智能识别表格类型并选择渲染方式"""
    rows = []
    for line in rows_text.split('\n'):
        if line.strip().startswith('|'):
            rows.append(line)
    if not rows:
        return ''

    full_text = ' '.join(rows)
    # 风险优先检测（因为风险表格可能也包含 P0/P1 等文字）
    if _detect_has_risk_level(full_text):
        return _render_risk_table(rows)
    elif _detect_has_priority(full_text):
        return _render_priority_table(rows)
    else:
        return _render_table(rows)


def _smart_render_content(text, color):
    """智能识别内容类型并选择最佳渲染方式"""
    if not text:
        return ''

    parts = []

    # 提取并渲染指标卡片
    metrics = _extract_metrics(text)
    if len(metrics) >= 2:
        parts.append(_render_metric_cards(metrics, color))

    # 按表格和非表格内容分段处理
    lines = text.split('\n')
    i = 0
    segment = []

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # 先处理之前积累的文本段
            if segment:
                seg_text = '\n'.join(segment)
                parts.append(_render_text_segment(seg_text, color))
                segment = []
            # 收集整个表格
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            parts.append(_smart_render_table('\n'.join(table_lines)))
        else:
            segment.append(line)
            i += 1

    # 处理最后的文本段
    if segment:
        seg_text = '\n'.join(segment)
        parts.append(_render_text_segment(seg_text, color))

    return '\n'.join(parts)


def _render_text_segment(text, color):
    """渲染文本段（自动选择流程图/旅程/普通格式）"""
    stripped = text.strip()
    if not stripped:
        return ''

    if _detect_is_flow(stripped):
        flow = _render_flow_steps(stripped, color)
        if flow:
            return flow

    if _detect_is_journey(stripped):
        journey = _render_journey(stripped, color)
        if journey:
            return journey

    return md_to_html(stripped)


# ─────────── 章节分析 ───────────

def detect_section_type(title, content_str):
    t = title.lower()
    if '结论' in t:
        return 'conclusion'
    if '风险' in t:
        return 'risk'
    if '决策' in t or ('建议' in t and '背景' not in t):
        return 'cta'
    if '目标' in t or '指标' in t or '数据' in t:
        return 'metrics'
    if '价值' in t or '收益' in t:
        return 'value'
    return 'normal'


def extract_number_prefix(title):
    m = re.match(r'^(\d{1,2})\s+(.+)$', title)
    if m:
        return m.group(1), m.group(2)
    return None, title


# ─────────── 颜色系统 ───────────

ACCENT_COLORS = [
    '#4F6AF6',  # 蓝
    '#7C5CFC',  # 紫
    '#2DB87F',  # 绿
    '#F59E42',  # 橙
    '#E8546A',  # 玫红
    '#3AAFDF',  # 青
]


# ─────────── 页面构建 ───────────

def build_html(data_json, style='dark', animation='stagger'):
    title = data_json.get('title', 'OnePage')
    sections = data_json.get('sections', {})

    sections_html = []
    section_index = 0

    for sec_title, sec_content in sections.items():
        content_str = json.dumps(sec_content, ensure_ascii=False) if isinstance(sec_content, dict) else str(sec_content)
        sec_type = detect_section_type(sec_title, content_str)

        if sec_type == 'conclusion':
            sections_html.append(_build_conclusion(sec_title, sec_content))
            continue

        num, clean_title = extract_number_prefix(sec_title)
        color = ACCENT_COLORS[section_index % len(ACCENT_COLORS)]
        section_index += 1

        inner = _build_section_content(sec_content, sec_type, color)

        num_html = f'<div class="num" style="--c:{color}">{num}</div>' if num else ''
        type_cls = f'sec-{sec_type}' if sec_type != 'normal' else ''

        # 章节标题拆分：如果有冒号，分主副标题
        title_html = _render_section_title(clean_title)

        sections_html.append(f'''
        <section class="card fade-in {type_cls}" style="--accent:{color}">
          <div class="card-head">
            {num_html}
            <div class="card-title-wrap">{title_html}</div>
          </div>
          <div class="card-body">{inner}</div>
        </section>''')

    return _full_html(title, '\n'.join(sections_html), style)


def _render_section_title(title):
    """拆分章节标题为主标题+副标题（如有冒号分隔）"""
    # 匹配中文冒号或英文冒号
    match = re.match(r'^(.+?)[：:]\s*(.+)$', title)
    if match:
        main_title = match.group(1)
        sub_title = match.group(2)
        return f'<h2>{html_lib.escape(main_title)}</h2><p class="card-subtitle">{html_lib.escape(sub_title)}</p>'
    return f'<h2>{html_lib.escape(title)}</h2>'


def _build_conclusion(title, content):
    if isinstance(content, dict):
        parts = [md_to_html(v) for v in content.values()]
        inner = '\n'.join(parts)
    else:
        inner = md_to_html(content)

    # 提取 CTA（加粗的问句）
    cta_html = ''
    cta_match = re.search(r'\*\*(.*?\?.*?)\*\*', str(content) if not isinstance(content, dict) else json.dumps(content, ensure_ascii=False))
    if cta_match:
        cta_text = cta_match.group(1)
        cta_html = f'<div class="conclusion-cta">{html_lib.escape(cta_text)}</div>'
        # 从 inner 中移除已提取的 CTA
        inner = re.sub(r'<strong>.*?\?.*?</strong>', '', inner)

    return f'''
    <section class="conclusion fade-in">
      <div class="conclusion-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div class="conclusion-label">KEY TAKEAWAY</div>
      <div class="conclusion-content">{inner}</div>
      {cta_html}
    </section>'''


def _build_section_content(content, sec_type, color):
    if isinstance(content, dict):
        parts = []
        for sub_title, sub_content in content.items():
            sub_html = _smart_render_content(sub_content, color)
            # 为 sub card 添加 icon hint
            icon = _pick_sub_icon(sub_title, sec_type)
            parts.append(f'''
            <div class="sub">
              <h3>{icon}<span class="dot" style="background:{color}"></span>{html_lib.escape(sub_title)}</h3>
              <div class="sub-content">{sub_html}</div>
            </div>''')
        return '\n'.join(parts)
    return _smart_render_content(content, color)


def _pick_sub_icon(title, sec_type):
    """根据子标题内容选择图标"""
    # 简单的 keyword → SVG icon 映射
    icons = {
        '市场': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zm6-4a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zm6-3a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/></svg>',
        '验证': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>',
        '试点': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>',
        '痛点': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
        '路径': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>',
        '解法': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"/></svg>',
        '优先': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"/></svg>',
        '旅程': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/></svg>',
        '收益': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd"/></svg>',
        '实验': '<svg class="sub-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7 2a1 1 0 00-.707 1.707L7 4.414v3.758a1 1 0 01-.293.707l-4 4C.816 14.769 2.156 18 4.828 18h10.344c2.672 0 4.012-3.231 2.121-5.121l-4-4A1 1 0 0113 8.172V4.414l.707-.707A1 1 0 0013 2H7zm2 6.172V4h2v4.172a3 3 0 00.879 2.12l1.027 1.028a4 4 0 00-2.171.102l-.47.156a4 4 0 01-2.53 0l-.563-.187 1.116-1.116A3 3 0 009 8.172z" clip-rule="evenodd"/></svg>',
    }
    for keyword, svg in icons.items():
        if keyword in title:
            return svg
    return ''


# ─────────── 完整 HTML ───────────

def _full_html(title, body, style='dark'):
    esc_title = html_lib.escape(title)
    style_vars = _style_vars(style)
    return f'''<!DOCTYPE html>
<html lang="zh-CN" data-style="{style}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc_title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+SC:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {{ {style_vars} }}
{_css()}
</style>
</head>
<body>

<!-- 背景装饰 -->
<div class="bg-glow bg-glow-1"></div>
<div class="bg-glow bg-glow-2"></div>
<div class="bg-glow bg-glow-3"></div>
<div class="bg-grid"></div>

<div class="wrap">

  <!-- Header -->
  <header class="header fade-in">
    <div class="header-inner">
      <p class="header-tag">ONEPAGE REPORT</p>
      <h1>{esc_title}</h1>
      <div class="header-line"></div>
    </div>
  </header>

  <!-- Content -->
  <main>{body}</main>

  <footer class="footer">Generated by OnePage Skill</footer>
</div>

<script>
{_js()}
</script>
</body>
</html>'''


# ─────────── 风格系统 ───────────

def _style_vars(style):
    styles = {
        'dark': '''
            --bg:#0a0b10;
            --surface:rgba(255,255,255,0.03);
            --glass:rgba(255,255,255,0.05);
            --glass-border:rgba(255,255,255,0.07);
            --glass-hover:rgba(255,255,255,0.09);
            --text:#e2e8f0; --text-secondary:#94a3b8; --text-muted:#64748b;
            --heading:#f8fafc;
            --radius:20px;
        ''',
        'light': '''
            --bg:#f5f7fa;
            --surface:rgba(255,255,255,0.85);
            --glass:rgba(255,255,255,0.92);
            --glass-border:rgba(0,0,0,0.06);
            --glass-hover:rgba(255,255,255,1);
            --text:#1e293b; --text-secondary:#475569; --text-muted:#94a3b8;
            --heading:#0f172a;
            --radius:20px;
        ''',
        'corporate': '''
            --bg:#eef1f5;
            --surface:rgba(255,255,255,0.95);
            --glass:white;
            --glass-border:rgba(0,0,0,0.08);
            --glass-hover:white;
            --text:#1a202c; --text-secondary:#4a5568; --text-muted:#a0aec0;
            --heading:#1a202c;
            --radius:16px;
        ''',
        'warm': '''
            --bg:#faf6f1;
            --surface:rgba(255,255,255,0.8);
            --glass:rgba(255,252,248,0.9);
            --glass-border:rgba(180,140,100,0.1);
            --glass-hover:rgba(255,252,248,1);
            --text:#3d2e1e; --text-secondary:#6b5744; --text-muted:#a89279;
            --heading:#2d1f0e;
            --radius:20px;
        ''',
        # ── 物理隐喻风格 ──
        'blueprint': '''
            --bg:#f8f9fc;
            --surface:rgba(255,255,255,0.95);
            --glass:white;
            --glass-border:rgba(70,130,180,0.15);
            --glass-hover:white;
            --text:#2c3e50; --text-secondary:#546e7a; --text-muted:#90a4ae;
            --heading:#1a2530;
            --radius:4px;
        ''',
        'retro': '''
            --bg:#fef9ef;
            --surface:#ffffff;
            --glass:#ffffff;
            --glass-border:#222222;
            --glass-hover:#fffdf5;
            --text:#1a1a1a; --text-secondary:#333333; --text-muted:#666666;
            --heading:#000000;
            --radius:6px;
        ''',
        'folder': '''
            --bg:#e8ecf1;
            --surface:#ffffff;
            --glass:#ffffff;
            --glass-border:rgba(0,0,0,0.08);
            --glass-hover:#fafbfc;
            --text:#1e293b; --text-secondary:#475569; --text-muted:#94a3b8;
            --heading:#0f172a;
            --radius:12px;
        ''',
        'receipt': '''
            --bg:#f5f0eb;
            --surface:#fffef9;
            --glass:#fffef9;
            --glass-border:transparent;
            --glass-hover:#fffef9;
            --text:#1a1a1a; --text-secondary:#444444; --text-muted:#888888;
            --heading:#000000;
            --radius:0px;
        ''',
        'scrapbook': '''
            --bg:#d4a574;
            --surface:rgba(255,255,255,0.92);
            --glass:rgba(255,255,255,0.92);
            --glass-border:rgba(0,0,0,0.06);
            --glass-hover:rgba(255,255,255,0.97);
            --text:#2c1810; --text-secondary:#4a3228; --text-muted:#8b6f5e;
            --heading:#1a0e08;
            --radius:4px;
        ''',
        'dossier': '''
            --bg:#b8956a;
            --surface:rgba(255,255,255,0.95);
            --glass:rgba(255,255,255,0.95);
            --glass-border:rgba(0,0,0,0.08);
            --glass-hover:rgba(255,255,255,0.98);
            --text:#1e1e1e; --text-secondary:#3d3d3d; --text-muted:#777777;
            --heading:#111111;
            --radius:4px;
        ''',
    }
    return styles.get(style, styles['dark'])


# ─────────── CSS ───────────

def _css():
    return '''
*{margin:0;padding:0;box-sizing:border-box}

body {
  font-family: 'Inter','Noto Sans SC',-apple-system,BlinkMacSystemFont,sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  position: relative;
}

/* ── 背景装饰 ── */
.bg-glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(140px);
  opacity: 0.3;
  pointer-events: none;
  z-index: 0;
  animation: float 20s ease-in-out infinite;
}
.bg-glow-1 { width:700px;height:700px;top:-15%;left:-12%;background:radial-gradient(circle,#4F6AF6 0%,transparent 70%);}
.bg-glow-2 { width:600px;height:600px;bottom:5%;right:-10%;background:radial-gradient(circle,#7C5CFC 0%,transparent 70%);animation-delay:-7s;}
.bg-glow-3 { width:500px;height:500px;top:35%;left:45%;background:radial-gradient(circle,#2DB87F 0%,transparent 70%);opacity:0.15;animation-delay:-14s;}

@keyframes float {
  0%,100% { transform: translate(0,0); }
  33% { transform: translate(30px,-20px); }
  66% { transform: translate(-20px,15px); }
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
  z-index: 0;
}

[data-style="light"] .bg-glow, [data-style="corporate"] .bg-glow, [data-style="warm"] .bg-glow,
[data-style="blueprint"] .bg-glow, [data-style="retro"] .bg-glow, [data-style="folder"] .bg-glow,
[data-style="receipt"] .bg-glow, [data-style="scrapbook"] .bg-glow, [data-style="dossier"] .bg-glow { display:none; }
[data-style="light"] .bg-grid, [data-style="corporate"] .bg-grid, [data-style="warm"] .bg-grid,
[data-style="retro"] .bg-grid, [data-style="folder"] .bg-grid, [data-style="receipt"] .bg-grid,
[data-style="scrapbook"] .bg-grid, [data-style="dossier"] .bg-grid { display:none; }

.wrap { max-width:860px;margin:0 auto;padding:2.5rem 1.25rem 3rem;position:relative;z-index:1; }

/* ── Header ── */
.header {
  text-align:center;
  margin-bottom:2.5rem;
  padding:3.5rem 2.5rem 3rem;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  position: relative;
  overflow: hidden;
}
.header::before {
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,transparent 5%,#4F6AF6 25%,#7C5CFC 50%,#E8546A 75%,transparent 95%);
}
.header-tag {
  font-size:0.65rem;font-weight:700;letter-spacing:0.25em;
  color:var(--text-muted);margin-bottom:1.2rem;
  text-transform:uppercase;
}
.header h1 {
  font-size:2.2rem;font-weight:900;letter-spacing:-0.01em;line-height:1.2;
  background:linear-gradient(135deg,var(--heading) 0%,var(--text-secondary) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
[data-style="dark"] .header h1 {
  background:linear-gradient(135deg,#fff 0%,#94a3b8 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.header-line {
  width:56px;height:3px;margin:1.2rem auto 0;border-radius:2px;
  background:linear-gradient(90deg,#4F6AF6,#7C5CFC);
}

/* ── Conclusion ── */
.conclusion {
  background: var(--glass);
  border: 1px solid rgba(79,106,246,0.2);
  border-radius: var(--radius);
  padding: 2rem 2.25rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}
.conclusion::before {
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#4F6AF6,#7C5CFC,#4F6AF6);
}
.conclusion::after {
  content:'';position:absolute;top:0;right:0;width:200px;height:200px;
  background:radial-gradient(circle,rgba(79,106,246,0.08) 0%,transparent 70%);
  pointer-events:none;
}
.conclusion-icon {
  width:44px;height:44px;border-radius:12px;
  background:linear-gradient(135deg,rgba(79,106,246,0.15),rgba(124,92,252,0.1));
  border:1px solid rgba(79,106,246,0.15);
  display:flex;align-items:center;justify-content:center;
  margin-bottom:1rem;color:#818cf8;
}
.conclusion-label {
  display:inline-block;font-size:0.6rem;font-weight:700;letter-spacing:0.2em;
  color:#818cf8;background:rgba(79,106,246,0.1);
  padding:0.25rem 0.85rem;border-radius:100px;margin-bottom:1rem;
  border:1px solid rgba(79,106,246,0.12);
}
.conclusion-content {
  font-size:0.95rem;line-height:1.9;color:var(--text-secondary);
}
.conclusion-content p { margin-bottom:0.5rem; }
.conclusion-content strong { color:#fbbf24;font-weight:700; }
[data-style="light"] .conclusion-content strong,
[data-style="corporate"] .conclusion-content strong { color:#b45309; }
.conclusion-cta {
  margin-top:1.25rem;padding:1rem 1.5rem;
  background:linear-gradient(135deg,rgba(79,106,246,0.12),rgba(124,92,252,0.08));
  border:1px solid rgba(79,106,246,0.2);
  border-radius:12px;
  font-size:1rem;font-weight:700;color:var(--heading);
  text-align:center;
  letter-spacing:0.01em;
}
[data-style="dark"] .conclusion-cta { color:#f8fafc; }

/* ── Section Card ── */
.card {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  margin-bottom: 1.5rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: transform 0.4s cubic-bezier(0.22,1,0.36,1), box-shadow 0.4s ease, border-color 0.4s ease;
  overflow: hidden;
  position: relative;
}
.card::before {
  content:'';position:absolute;top:0;left:0;bottom:0;width:4px;
  background:var(--accent,#4F6AF6);border-radius:4px 0 0 4px;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0,0,0,0.2);
  border-color: var(--glass-hover);
}

.card-head {
  display:flex;align-items:flex-start;gap:1rem;
  padding:1.75rem 2rem 0.5rem;
}
.num {
  width:40px;height:40px;border-radius:12px;
  display:inline-flex;align-items:center;justify-content:center;
  font-size:0.85rem;font-weight:800;color:white;flex-shrink:0;
  background:var(--c);
  box-shadow:0 4px 16px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2);
}
.card-title-wrap { flex:1; }
.card-head h2 {
  font-size:1.2rem;font-weight:800;color:var(--heading);letter-spacing:-0.01em;line-height:1.35;
}
[data-style="dark"] .card-head h2 { color:#f1f5f9; }
.card-subtitle {
  font-size:0.82rem;color:var(--text-secondary);margin-top:0.2rem;font-weight:500;line-height:1.5;
}
.card-body { padding:0.75rem 2rem 1.75rem; }

/* ── Sub Card ── */
.sub {
  background: var(--surface);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 0.75rem;
  transition: background 0.3s ease, border-color 0.3s ease, transform 0.3s ease;
}
.sub:hover {
  background:var(--glass-hover);
  border-color:rgba(255,255,255,0.12);
  transform:translateX(4px);
}
[data-style="light"] .sub:hover,
[data-style="corporate"] .sub:hover,
[data-style="warm"] .sub:hover {
  border-color:rgba(0,0,0,0.1);
}
.sub:last-child { margin-bottom:0; }
.sub h3 {
  font-size:0.9rem;font-weight:700;color:var(--heading);
  margin-bottom:0.6rem;padding-bottom:0.5rem;
  border-bottom:1px solid var(--glass-border);
  display:flex;align-items:center;gap:0.5rem;
  letter-spacing:0.01em;
}
[data-style="dark"] .sub h3 { color:#e2e8f0; }
.sub-icon {
  width:16px;height:16px;flex-shrink:0;
  color:var(--text-muted);opacity:0.7;
}
.dot { width:6px;height:6px;border-radius:50%;flex-shrink:0; }
.sub-content { font-size:0.85rem;color:var(--text-secondary);line-height:1.8; }
.sub-content p { margin-bottom:0.4rem; }
.sub-content p:last-child { margin-bottom:0; }
.sub-content strong { color:var(--heading);font-weight:600; }
[data-style="dark"] .sub-content strong { color:#e2e8f0; }

/* ── Metric Cards ── */
.metric-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
  gap:0.75rem;
  margin:0.75rem 0;
}
.metric-card {
  background:var(--surface);
  border:1px solid var(--glass-border);
  border-radius:14px;
  padding:1.25rem 1rem;
  text-align:center;
  position:relative;
  overflow:hidden;
  transition:transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card::before {
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--mc,#4F6AF6);
}
.metric-card:hover {
  transform:translateY(-3px) scale(1.02);
  box-shadow:0 8px 32px rgba(0,0,0,0.12);
}
.metric-value {
  font-size:2rem;font-weight:900;letter-spacing:-0.02em;
  background:linear-gradient(135deg,var(--mc,#4F6AF6),color-mix(in srgb, var(--mc,#4F6AF6), white 30%));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
  line-height:1.2;
  margin-bottom:0.3rem;
}
.metric-label {
  font-size:0.72rem;font-weight:600;color:var(--text-muted);
  letter-spacing:0.03em;
  line-height:1.4;
}

/* ── Flow Timeline ── */
.flow-timeline {
  position:relative;
  padding-left:2rem;
  margin:0.75rem 0;
}
.flow-timeline::before {
  content:'';position:absolute;left:15px;top:8px;bottom:8px;width:2px;
  background:linear-gradient(180deg,var(--glass-border),var(--glass-border));
  border-radius:1px;
}
.flow-step {
  display:flex;gap:1rem;margin-bottom:1rem;position:relative;
  align-items:flex-start;
}
.flow-step:last-child { margin-bottom:0; }
.flow-node {
  width:32px;height:32px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  background:var(--fc,#4F6AF6);
  box-shadow:0 2px 12px rgba(0,0,0,0.15), 0 0 0 4px var(--bg);
  position:relative;z-index:1;
  margin-left:-17px;
}
.flow-num {
  font-size:0.72rem;font-weight:800;color:white;
}
.flow-content {
  flex:1;
  background:var(--surface);
  border:1px solid var(--glass-border);
  border-radius:12px;
  padding:0.85rem 1.1rem;
  transition:transform 0.3s ease, border-color 0.3s ease;
}
.flow-content:hover {
  transform:translateX(4px);
  border-color:var(--glass-hover);
}
.flow-title {
  font-size:0.88rem;font-weight:700;color:var(--heading);margin-bottom:0.25rem;
}
[data-style="dark"] .flow-title { color:#e2e8f0; }
.flow-desc {
  font-size:0.8rem;color:var(--text-secondary);line-height:1.7;
}

/* ── Journey Timeline ── */
.journey-timeline {
  display:flex;flex-direction:column;gap:0;
  margin:0.75rem 0;
  position:relative;
  padding-left:1.5rem;
}
.journey-stage {
  display:flex;align-items:flex-start;gap:1rem;
  position:relative;
  padding-bottom:1rem;
}
.journey-stage:last-child { padding-bottom:0; }
.journey-stage:last-child .journey-line { display:none; }
.journey-dot {
  width:14px;height:14px;border-radius:50%;flex-shrink:0;
  position:relative;z-index:1;
  box-shadow:0 0 0 4px var(--bg);
  margin-left:-7px;margin-top:4px;
}
.journey-line {
  position:absolute;left:calc(-7px + 6px);top:18px;bottom:-4px;width:2px;
  background:var(--glass-border);
}
.journey-card {
  flex:1;
  background:var(--surface);
  border:1px solid var(--glass-border);
  border-left:3px solid var(--jc,#4F6AF6);
  border-radius:12px;
  padding:0.85rem 1.1rem;
  transition:transform 0.3s ease;
}
.journey-card:hover { transform:translateX(4px); }
.journey-name {
  font-size:0.85rem;font-weight:700;color:var(--heading);margin-bottom:0.2rem;
}
[data-style="dark"] .journey-name { color:#e2e8f0; }
.journey-desc {
  font-size:0.8rem;color:var(--text-secondary);line-height:1.7;
}

/* ── Priority Badge ── */
.priority-badge {
  display:inline-block;padding:0.15rem 0.65rem;border-radius:6px;
  font-size:0.7rem;font-weight:800;letter-spacing:0.05em;
}
.badge-p00 { background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.2); }
.badge-p0  { background:rgba(249,115,22,0.15);color:#f97316;border:1px solid rgba(249,115,22,0.2); }
.badge-p1  { background:rgba(234,179,8,0.15);color:#eab308;border:1px solid rgba(234,179,8,0.2); }
.badge-p2  { background:rgba(34,197,94,0.15);color:#22c55e;border:1px solid rgba(34,197,94,0.2); }
[data-style="light"] .badge-p00, [data-style="corporate"] .badge-p00 { background:#fef2f2;color:#dc2626; }
[data-style="light"] .badge-p0, [data-style="corporate"] .badge-p0 { background:#fff7ed;color:#ea580c; }
[data-style="light"] .badge-p1, [data-style="corporate"] .badge-p1 { background:#fefce8;color:#ca8a04; }

/* ── Risk Level ── */
.risk-level {
  font-weight:700;font-size:0.78rem;
}
.risk-high { color:#ef4444; }
.risk-mid  { color:#f59e0b; }
.risk-low  { color:#22c55e; }

/* ── Section Types ── */
.sec-risk::before { background:#E8546A; }
.sec-risk .num { background:#E8546A !important; box-shadow:0 4px 16px rgba(232,84,106,0.25); }
.sec-risk { border-color:rgba(232,84,106,0.12); }

.sec-cta::before { background:linear-gradient(180deg,#4F6AF6,#7C5CFC); }
.sec-cta { border-color:rgba(79,106,246,0.15); }
.sec-cta .sub-content strong { color:#fbbf24; }
[data-style="light"] .sec-cta .sub-content strong,
[data-style="corporate"] .sec-cta .sub-content strong { color:#1e40af; }

.sec-metrics::before { background:#2DB87F; }
.sec-metrics .num { background:#2DB87F !important; }

.sec-value::before { background:#F59E42; }
.sec-value .num { background:#F59E42 !important; }

/* ── Table ── */
table {
  width:100%;border-collapse:separate;border-spacing:0;
  margin:0.75rem 0;border-radius:12px;overflow:hidden;
  border:1px solid var(--glass-border);font-size:0.82rem;
}
th {
  background:var(--surface);font-weight:700;color:var(--heading);
  padding:0.75rem 1rem;text-align:left;
  border-bottom:2px solid var(--glass-border);
  font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
}
[data-style="dark"] th { color:#cbd5e1; }
td {
  padding:0.7rem 1rem;color:var(--text-secondary);
  border-bottom:1px solid var(--glass-border);
  vertical-align:top;
}
td strong { color:var(--heading);font-weight:600; }
[data-style="dark"] td strong { color:#e2e8f0; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:var(--surface); }

/* ── List ── */
.op-list { padding-left:1.4rem;margin:0.5rem 0; }
.op-list li {
  margin-bottom:0.4rem;font-size:0.85rem;color:var(--text-secondary);line-height:1.75;
  padding-left:0.3rem;
}
.op-list li strong { color:var(--heading);font-weight:600; }
[data-style="dark"] .op-list li strong { color:#e2e8f0; }
ol.op-list { list-style-type:decimal; }
ul.op-list { list-style-type:none; }
ul.op-list li::before {
  content:'';display:inline-block;width:6px;height:6px;border-radius:50%;
  background:var(--text-muted);margin-right:0.6rem;vertical-align:middle;
}
.op-list li::marker { color:var(--text-muted);font-weight:700; }

/* ── 图片 ── */
.op-figure {
  margin:1rem 0;
  text-align:center;
}
.op-figure img {
  max-width:100%;
  border-radius:12px;
  box-shadow:0 4px 20px rgba(0,0,0,0.1);
  transition:transform 0.3s ease;
  cursor:zoom-in;
}
.op-figure img:hover {
  transform:scale(1.02);
}
.op-figure figcaption {
  margin-top:0.5rem;
  font-size:0.82rem;
  color:var(--text-muted);
  font-style:italic;
}
.inline-img {
  max-width:100%;
  border-radius:8px;
  margin:0.5rem 0;
  box-shadow:0 2px 12px rgba(0,0,0,0.08);
}
[data-style="dark"] .op-figure img {
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
[data-style="corporate"] .op-figure img {
  border:1px solid rgba(0,0,0,0.08);
  box-shadow:0 2px 12px rgba(0,0,0,0.06);
}

/* ── Inline ── */
code {
  background:rgba(99,102,241,0.1);padding:0.12em 0.45em;border-radius:5px;
  font-size:0.8em;color:#a5b4fc;font-family:'SF Mono','Fira Code',monospace;
}
[data-style="light"] code, [data-style="corporate"] code {
  background:rgba(99,102,241,0.08);color:#6366f1;
}

/* ── Footer ── */
.footer {
  text-align:center;padding:3rem 1rem;color:var(--text-muted);
  font-size:0.7rem;letter-spacing:0.06em;
  opacity:0.6;
}

/* ── Animation ── */
.fade-in {
  opacity:0;transform:translateY(24px);
  transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1),
              transform 0.7s cubic-bezier(0.22,1,0.36,1);
}
.fade-in.visible { opacity:1;transform:translateY(0); }

/* ── Responsive ── */
@media(max-width:640px){
  .wrap{padding:1.5rem 0.75rem}
  .header{padding:2.5rem 1.25rem 2rem;border-radius:16px}
  .header h1{font-size:1.5rem}
  .card-head{padding:1.25rem 1.25rem 0.4rem}
  .card-head h2{font-size:1.05rem}
  .card-body{padding:0.5rem 1.25rem 1.25rem}
  .sub{padding:1rem 1.1rem}
  .conclusion{padding:1.5rem}
  .metric-grid{grid-template-columns:repeat(2,1fr)}
  .metric-value{font-size:1.6rem}
  .flow-timeline{padding-left:1.5rem}
  .bg-glow{display:none}
  .bg-grid{display:none}
}

/* ════════════════════════════════════════════════
   物理隐喻风格
   ════════════════════════════════════════════════ */

/* ── 1. Blueprint 坐标蓝图风 ── */
[data-style="blueprint"] { font-family:'SF Mono','Fira Code','Noto Sans SC',monospace; }
[data-style="blueprint"] .bg-grid {
  display:block !important;
  background-image:
    repeating-linear-gradient(0deg,rgba(70,130,180,0.08) 0px,rgba(70,130,180,0.08) 1px,transparent 1px,transparent 40px),
    repeating-linear-gradient(90deg,rgba(70,130,180,0.08) 0px,rgba(70,130,180,0.08) 1px,transparent 1px,transparent 40px);
  background-size:40px 40px;
}
[data-style="blueprint"] .header {
  background:white;border:2px solid rgba(70,130,180,0.2);border-radius:4px;
  backdrop-filter:none;
}
[data-style="blueprint"] .header::before {
  height:2px;background:linear-gradient(90deg,#4682B4,#00897B,#E91E63);
}
[data-style="blueprint"] .header h1 {
  font-family:'Inter','Noto Sans SC',sans-serif;
  background:linear-gradient(135deg,#1a2530,#4682B4);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
[data-style="blueprint"] .card {
  background:white;border:1px solid rgba(70,130,180,0.2);border-radius:4px;
  backdrop-filter:none;
}
[data-style="blueprint"] .card::before { width:3px;border-radius:0; }
[data-style="blueprint"] .num { border-radius:4px;font-family:'SF Mono','Fira Code',monospace; }
[data-style="blueprint"] .sub { border-radius:4px;border:1px solid rgba(70,130,180,0.1); }
[data-style="blueprint"] .conclusion { border-radius:4px;border:2px solid rgba(70,130,180,0.25);backdrop-filter:none; }
[data-style="blueprint"] .conclusion::before { background:linear-gradient(90deg,#4682B4,#00897B); }
[data-style="blueprint"] .conclusion-label { color:#4682B4;background:rgba(70,130,180,0.08);border-color:rgba(70,130,180,0.15); }
[data-style="blueprint"] .conclusion-content strong { color:#E91E63; }
[data-style="blueprint"] .conclusion-cta { background:rgba(70,130,180,0.06);border-color:rgba(70,130,180,0.2); }
[data-style="blueprint"] .metric-card { border-radius:4px;border:1px solid rgba(70,130,180,0.15); }
[data-style="blueprint"] .flow-content { border-radius:4px; }
[data-style="blueprint"] table { border-radius:4px;border:1px solid rgba(70,130,180,0.15); }
[data-style="blueprint"] th { background:rgba(70,130,180,0.06);letter-spacing:0.12em; }
[data-style="blueprint"] .card-head h2 { font-family:'Inter','Noto Sans SC',sans-serif; }

/* ── 2. Retro 复古风 ── */
[data-style="retro"] .header {
  background:#FFE066;border:3px solid #222;border-radius:6px;
  backdrop-filter:none;
}
[data-style="retro"] .header::before { height:0;display:none; }
[data-style="retro"] .header h1 {
  background:none;-webkit-text-fill-color:#000;font-size:2.4rem;
  text-shadow:3px 3px 0 #FFE066;
}
[data-style="retro"] .header-tag { color:#555; }
[data-style="retro"] .header-line { background:#222;height:4px;width:80px;border-radius:0; }
[data-style="retro"] .card {
  background:#fff;border:3px solid #222;border-radius:6px;
  backdrop-filter:none;box-shadow:5px 5px 0 #222;
}
[data-style="retro"] .card::before { display:none; }
[data-style="retro"] .card:hover { transform:translate(-2px,-2px);box-shadow:7px 7px 0 #222; }
[data-style="retro"] .num {
  border-radius:50%;width:42px;height:42px;font-size:1rem;
  box-shadow:2px 2px 0 #222;border:2px solid #222;
}
[data-style="retro"] .card:nth-child(3n+1) .num { background:#FF6B6B; }
[data-style="retro"] .card:nth-child(3n+2) .num { background:#4ECDC4; }
[data-style="retro"] .card:nth-child(3n) .num { background:#45B7D1; }
[data-style="retro"] .sub {
  border:2px solid #eee;border-radius:6px;
  background:#fafafa;
}
[data-style="retro"] .sub h3 { border-bottom:2px dashed #ddd; }
[data-style="retro"] .sub-content strong { color:#E91E63;font-weight:800; }
[data-style="retro"] .conclusion {
  background:#E3F2FD;border:3px solid #222;border-radius:6px;
  box-shadow:5px 5px 0 #222;backdrop-filter:none;
}
[data-style="retro"] .conclusion::before { display:none; }
[data-style="retro"] .conclusion-label { background:#222;color:#fff;border:none;border-radius:4px;font-size:0.65rem; }
[data-style="retro"] .conclusion-content strong { color:#D32F2F; }
[data-style="retro"] .conclusion-cta {
  background:#FFE066;border:2px solid #222;border-radius:4px;color:#000;
  box-shadow:3px 3px 0 #222;
}
[data-style="retro"] .metric-card {
  border:2px solid #222;border-radius:6px;box-shadow:3px 3px 0 #222;
}
[data-style="retro"] .metric-card::before { display:none; }
[data-style="retro"] .metric-value { font-size:2.2rem; }
[data-style="retro"] .priority-badge { border-radius:4px;border-width:2px;font-weight:900; }
[data-style="retro"] table { border:2px solid #222;border-radius:6px; }
[data-style="retro"] th { background:#f0f0f0;border-bottom:2px solid #222; }
[data-style="retro"] .footer { color:#999; }

/* ── 3. Folder 文件夹风 ── */
[data-style="folder"] body {
  background:#e8ecf1 url("data:image/svg+xml,%3Csvg width='6' height='6' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='1' cy='1' r='0.5' fill='%23ccc' opacity='0.3'/%3E%3C/svg%3E");
}
[data-style="folder"] .wrap { max-width:880px; }
[data-style="folder"] .header {
  background:linear-gradient(180deg,#2563eb 0%,#1d4ed8 100%);
  border:none;border-radius:12px 12px 0 0;color:white;
  padding-bottom:2rem;position:relative;backdrop-filter:none;
}
[data-style="folder"] .header::before { display:none; }
[data-style="folder"] .header::after {
  content:'';position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);
  width:60px;height:40px;
  background:linear-gradient(180deg,#94a3b8,#b0bec5);
  border-radius:0 0 6px 6px;
  box-shadow:inset 0 2px 4px rgba(0,0,0,0.2);
  z-index:2;
}
[data-style="folder"] .header-tag { color:rgba(255,255,255,0.6); }
[data-style="folder"] .header h1 {
  background:none;-webkit-text-fill-color:#fff;
}
[data-style="folder"] .header-line { background:rgba(255,255,255,0.3); }
[data-style="folder"] main { margin-top:1rem; }
[data-style="folder"] .card {
  background:white;border:none;border-radius:12px;
  box-shadow:0 2px 12px rgba(0,0,0,0.06);backdrop-filter:none;
  border-left:4px solid var(--accent,#2563eb);
}
[data-style="folder"] .card::before { display:none; }
[data-style="folder"] .card:hover { box-shadow:0 8px 24px rgba(0,0,0,0.1);transform:translateY(-3px); }
[data-style="folder"] .sub {
  background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
  position:relative;
}
[data-style="folder"] .conclusion {
  background:white;border:none;border-radius:12px;
  box-shadow:0 2px 12px rgba(0,0,0,0.06);backdrop-filter:none;
  border-top:4px solid #2563eb;
}
[data-style="folder"] .conclusion::before { display:none; }
[data-style="folder"] .conclusion-label { color:#2563eb;background:rgba(37,99,235,0.08);border-color:rgba(37,99,235,0.12); }
[data-style="folder"] .conclusion-content strong { color:#b45309; }
[data-style="folder"] .conclusion-cta { background:#eff6ff;border-color:#bfdbfe; }
[data-style="folder"] .num { border-radius:8px; }
[data-style="folder"] .metric-card { border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05); }

/* ── 4. Receipt 打印热敏纸风 ── */
[data-style="receipt"] .wrap { max-width:560px; }
[data-style="receipt"] body { font-family:'SF Mono','Courier New','Noto Sans SC',monospace; }
[data-style="receipt"] .header {
  background:#fffef9;border:none;border-radius:0;
  padding:2rem 1.5rem;backdrop-filter:none;
  border-bottom:2px dashed #ccc;
  position:relative;
}
[data-style="receipt"] .header::before {
  content:'';position:absolute;top:-12px;left:0;right:0;height:12px;
  background:url("data:image/svg+xml,%3Csvg width='24' height='12' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 12 Q6 0 12 12 Q18 0 24 12' fill='%23f5f0eb' stroke='none'/%3E%3C/svg%3E") repeat-x;
  background-size:24px 12px;
}
[data-style="receipt"] .header h1 {
  font-size:1.6rem;background:none;-webkit-text-fill-color:#000;
  font-family:'SF Mono','Courier New',monospace;letter-spacing:0.05em;
  text-transform:uppercase;
}
[data-style="receipt"] .header-tag { letter-spacing:0.3em;font-size:0.6rem; }
[data-style="receipt"] .header-line { display:none; }
[data-style="receipt"] .card {
  background:#fffef9;border:none;border-radius:0;
  border-bottom:2px dashed #ccc;backdrop-filter:none;
  margin-bottom:0;box-shadow:none;
}
[data-style="receipt"] .card::before { display:none; }
[data-style="receipt"] .card:hover { transform:none;box-shadow:none; }
[data-style="receipt"] .card-head { padding:1.5rem 1.5rem 0.3rem; }
[data-style="receipt"] .card-body { padding:0.25rem 1.5rem 1.5rem; }
[data-style="receipt"] .num {
  background:transparent !important;color:#000;border:2px solid #000;
  border-radius:50%;width:32px;height:32px;font-size:0.75rem;
  box-shadow:none;
}
[data-style="receipt"] .card-head h2 { font-size:1rem;text-transform:uppercase;letter-spacing:0.05em; }
[data-style="receipt"] .sub {
  background:transparent;border:none;border-radius:0;
  padding:0.75rem 0;border-bottom:1px dashed #ddd;
}
[data-style="receipt"] .sub:hover { transform:none;background:transparent; }
[data-style="receipt"] .sub h3 { border-bottom:none;font-size:0.82rem; }
[data-style="receipt"] .conclusion {
  background:#fffef9;border:none;border-radius:0;
  border-bottom:2px dashed #ccc;border-top:2px dashed #ccc;
  backdrop-filter:none;
}
[data-style="receipt"] .conclusion::before { display:none; }
[data-style="receipt"] .conclusion::after { display:none; }
[data-style="receipt"] .conclusion-label { background:#000;color:#fff;border:none;border-radius:2px; }
[data-style="receipt"] .conclusion-content strong { color:#000;font-weight:900; }
[data-style="receipt"] .conclusion-cta {
  background:transparent;border:2px solid #000;border-radius:0;color:#000;
  text-transform:uppercase;letter-spacing:0.08em;font-size:0.85rem;
}
[data-style="receipt"] .metric-card {
  border:1px solid #ddd;border-radius:0;
}
[data-style="receipt"] .metric-card::before { display:none; }
[data-style="receipt"] .metric-value { font-size:1.8rem; }
[data-style="receipt"] table { border-radius:0;border:1px solid #ddd; }
[data-style="receipt"] th { background:#f0ebe3;text-transform:uppercase; }
[data-style="receipt"] .flow-content { border-radius:4px; }
[data-style="receipt"] .footer {
  border-top:2px dashed #ccc;padding-top:1.5rem;
  font-family:'SF Mono','Courier New',monospace;
}

/* ── 5. Scrapbook 复古手账风 ── */
[data-style="scrapbook"] body {
  background:#d4a574;
  background-image:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
}
[data-style="scrapbook"] .header {
  background:rgba(255,253,240,0.92);border:none;border-radius:4px;
  box-shadow:2px 3px 12px rgba(0,0,0,0.15);backdrop-filter:none;
  transform:rotate(-0.5deg);position:relative;
}
[data-style="scrapbook"] .header::before {
  content:'';position:absolute;top:-8px;left:50%;transform:translateX(-50%);
  width:16px;height:16px;background:#d32f2f;border-radius:50%;
  box-shadow:inset -2px -2px 3px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2);
  z-index:2;
}
[data-style="scrapbook"] .header h1 {
  background:none;-webkit-text-fill-color:#1a0e08;font-size:2rem;
}
[data-style="scrapbook"] .header-line { background:#d32f2f; }
[data-style="scrapbook"] .card {
  background:rgba(255,253,240,0.92);border:none;border-radius:4px;
  box-shadow:2px 3px 12px rgba(0,0,0,0.12);backdrop-filter:none;
  position:relative;
}
[data-style="scrapbook"] .card::before { display:none; }
[data-style="scrapbook"] .card::after {
  content:'';position:absolute;top:-6px;right:24px;
  width:14px;height:14px;background:#d32f2f;border-radius:50%;
  box-shadow:inset -1px -1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.2);
}
[data-style="scrapbook"] .card:nth-child(even) { transform:rotate(0.3deg); }
[data-style="scrapbook"] .card:nth-child(odd) { transform:rotate(-0.3deg); }
[data-style="scrapbook"] .card:hover { transform:rotate(0deg) translateY(-3px); }
[data-style="scrapbook"] .sub {
  background:rgba(255,255,200,0.5);border:1px solid rgba(0,0,0,0.06);
  border-radius:2px;border-left:3px solid var(--accent,#d32f2f);
}
[data-style="scrapbook"] .num {
  border-radius:50%;box-shadow:1px 2px 4px rgba(0,0,0,0.2);
}
[data-style="scrapbook"] .conclusion {
  background:rgba(255,253,240,0.95);border:none;border-radius:4px;
  box-shadow:2px 3px 12px rgba(0,0,0,0.15);backdrop-filter:none;
  transform:rotate(0.3deg);
  border-left:4px solid #d32f2f;
}
[data-style="scrapbook"] .conclusion::before { display:none; }
[data-style="scrapbook"] .conclusion::after { display:none; }
[data-style="scrapbook"] .conclusion-label { background:#d32f2f;color:#fff;border:none; }
[data-style="scrapbook"] .conclusion-content strong { color:#d32f2f; }
[data-style="scrapbook"] .conclusion-cta {
  background:rgba(211,47,47,0.08);border:2px dashed #d32f2f;border-radius:2px;
}
[data-style="scrapbook"] .metric-card {
  border-radius:2px;box-shadow:1px 2px 6px rgba(0,0,0,0.1);
  transform:rotate(-0.5deg);
}
[data-style="scrapbook"] .metric-card:nth-child(even) { transform:rotate(0.5deg); }
[data-style="scrapbook"] table { border-radius:2px; }
[data-style="scrapbook"] .footer { color:#8b6f5e; }

/* ── 6. Dossier 档案风 ── */
[data-style="dossier"] body {
  background:#b8956a;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(160,110,60,0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(140,100,50,0.3) 0%, transparent 50%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E");
}
[data-style="dossier"] .header {
  background:white;border:none;border-radius:4px;
  box-shadow:0 4px 16px rgba(0,0,0,0.2);backdrop-filter:none;
  position:relative;padding-top:4rem;
}
[data-style="dossier"] .header::before {
  content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:70px;height:50px;
  background:linear-gradient(180deg,#9e9e9e,#bdbdbd,#9e9e9e);
  border-radius:0 0 8px 8px;
  box-shadow:0 3px 8px rgba(0,0,0,0.2), inset 0 -2px 4px rgba(0,0,0,0.1);
  z-index:2;
}
[data-style="dossier"] .header h1 {
  background:none;-webkit-text-fill-color:#111;font-size:1.8rem;
  letter-spacing:0.02em;
}
[data-style="dossier"] .header-line { background:#d32f2f;width:40px; }
[data-style="dossier"] .card {
  background:white;border:none;border-radius:4px;
  box-shadow:0 3px 12px rgba(0,0,0,0.15);backdrop-filter:none;
  position:relative;
}
[data-style="dossier"] .card::before { display:none; }
[data-style="dossier"] .card::after {
  content:'';position:absolute;top:-7px;left:20px;
  width:12px;height:12px;background:#d32f2f;border-radius:50%;
  box-shadow:inset -1px -1px 2px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2);
}
[data-style="dossier"] .card:hover { transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.2); }
[data-style="dossier"] .sub {
  background:#f9f9f7;border:1px solid #e5e5e0;border-radius:4px;
}
[data-style="dossier"] .sub h3 { font-family:'SF Mono','Courier New','Noto Sans SC',monospace;font-size:0.82rem; }
[data-style="dossier"] .num { border-radius:4px; }
[data-style="dossier"] .conclusion {
  background:white;border:none;border-radius:4px;
  box-shadow:0 4px 16px rgba(0,0,0,0.2);backdrop-filter:none;
  position:relative;
}
[data-style="dossier"] .conclusion::before {
  content:'URGENT';position:absolute;top:12px;right:-8px;
  background:#d32f2f;color:white;font-size:0.6rem;font-weight:800;
  padding:0.2rem 0.8rem;letter-spacing:0.15em;
  transform:rotate(3deg);
  box-shadow:2px 2px 6px rgba(0,0,0,0.2);
  border-radius:2px;
  height:auto;width:auto;
}
[data-style="dossier"] .conclusion::after { display:none; }
[data-style="dossier"] .conclusion-label { background:#333;color:white;border:none;border-radius:2px; }
[data-style="dossier"] .conclusion-content strong { color:#d32f2f; }
[data-style="dossier"] .conclusion-cta {
  background:#fff3e0;border:1px solid #ffe0b2;border-radius:2px;
}
[data-style="dossier"] .metric-card { border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.1); }
[data-style="dossier"] table { border-radius:4px; }
[data-style="dossier"] .footer { color:rgba(255,255,255,0.5); }

/* ── Print ── */
@media print {
  body{background:#fff;color:#1a1a2e}
  .bg-glow,.bg-grid{display:none}
  .card,.conclusion,.header{
    background:#fff;border:1px solid #e5e7eb;
    backdrop-filter:none;-webkit-backdrop-filter:none;
    box-shadow:none;color:#1a1a2e;
  }
  .card-head h2,.sub h3{color:#1a1a2e}
  .sub-content,.conclusion-content{color:#374151}
  .sub-content strong,.conclusion-content strong{color:#111827}
  td,th{color:#374151}
  .header h1{-webkit-text-fill-color:#0f172a;background:none}
  .header-tag,.footer{color:#6b7280}
  .metric-value{-webkit-text-fill-color:#1a1a2e;background:none}
  .fade-in{opacity:1;transform:none}
}
'''


def _js():
    return '''
document.addEventListener('DOMContentLoaded',function(){
  var els=document.querySelectorAll('.fade-in');
  var observer=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        var idx=Array.from(els).indexOf(e.target);
        e.target.style.transitionDelay=(idx*0.08)+'s';
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  },{threshold:0.05,rootMargin:'0px 0px -60px 0px'});
  els.forEach(function(el){observer.observe(el)});

  // 为 metric 卡片添加数字动画
  document.querySelectorAll('.metric-value').forEach(function(el){
    var text=el.textContent;
    var match=text.match(/([\\d.]+)(%?)/);
    if(!match) return;
    var target=parseFloat(match[1]);
    var suffix=match[2];
    var duration=800;
    var start=performance.now();
    el.textContent='0'+suffix;

    var obs=new IntersectionObserver(function(entries){
      if(entries[0].isIntersecting){
        obs.unobserve(el);
        requestAnimationFrame(function animate(now){
          var progress=Math.min((now-start)/duration,1);
          var eased=1-Math.pow(1-progress,3);
          var current=target*eased;
          el.textContent=(target%1===0?Math.round(current):current.toFixed(1))+suffix;
          if(progress<1) requestAnimationFrame(animate);
        });
        start=performance.now();
      }
    },{threshold:0.5});
    obs.observe(el);
  });
});
'''


# ─────────── 图片 base64 内嵌 ───────────

def _embed_images_as_base64(html_content, base_dir):
    """将 HTML 中的本地图片路径替换为 base64 data URI，使 HTML 完全自包含"""
    import base64
    import mimetypes

    def replace_src(m):
        src = m.group(1)
        # 跳过已经是 data URI 或远程 URL 的图片
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            return m.group(0)
        img_path = os.path.join(base_dir, src)
        if not os.path.exists(img_path):
            return m.group(0)
        mime, _ = mimetypes.guess_type(img_path)
        if not mime:
            mime = 'image/png'
        with open(img_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        return f'src="data:{mime};base64,{b64}"'

    return re.sub(r'src="([^"]+)"', replace_src, html_content)


# ─────────── 主入口 ───────────

def main(data, outdir, theme='light', style='dark', animation='default', embed_images=True):
    if not os.path.exists(data):
        raise FileNotFoundError(f"Data file {data} not found")

    with open(data, 'r', encoding='utf-8') as f:
        data_json = json.load(f)

    os.makedirs(outdir, exist_ok=True)

    import shutil
    dest_data = os.path.join(outdir, 'data.json')
    if os.path.abspath(data) != os.path.abspath(dest_data):
        shutil.copy(data, dest_data)

    html_content = build_html(data_json, style, animation)

    # 将本地图片内嵌为 base64，使 HTML 成为单文件可分享
    if embed_images:
        # 图片相对路径以 data.json 所在目录为基准，但渲染时从 outdir 引用
        # 优先在 outdir 下查找，其次在 data 文件所在目录下查找
        html_content = _embed_images_as_base64(html_content, outdir)
        # 如果 outdir 里没有，再从 data 文件旁边找
        data_dir = os.path.dirname(os.path.abspath(data))
        if data_dir != os.path.abspath(outdir):
            html_content = _embed_images_as_base64(html_content, data_dir)

    with open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Web onepage built successfully in: {outdir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build web version of Onepage")
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--outdir', type=str, default="./output")
    parser.add_argument('--theme', type=str, default="light", choices=['light', 'poster'])
    parser.add_argument('--style', type=str, default="dark",
                        choices=['dark', 'light', 'corporate', 'warm',
                                 'blueprint', 'retro', 'folder', 'receipt', 'scrapbook', 'dossier'])
    parser.add_argument('--animation', type=str, default="default",
                        choices=['minimal', 'stagger', 'poster', 'default'])
    parser.add_argument('--no-embed-images', action='store_true',
                        help='不内嵌图片为 base64（保留相对路径引用，HTML 需与 images/ 目录一起分发）')
    args = parser.parse_args()
    main(data=args.data, outdir=args.outdir, theme=args.theme, style=args.style,
         animation=args.animation, embed_images=not args.no_embed_images)

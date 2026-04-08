#!/usr/bin/env python3
"""
分析网页截图，提取视觉风格特征，生成可直接用于 build_web_onepage.py 的自定义风格文件。

用法：
  python3 scripts/analyze_style_from_image.py \\
    --image screenshot.png \\
    --output custom_style.json

  # 然后在 build_web_onepage.py 中使用：
  python3 scripts/build_web_onepage.py \\
    --data data.json \\
    --custom-style custom_style.json \\
    --outdir output/web

依赖：
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
"""
import argparse
import base64
import json
import os
import re
import sys


ANALYSIS_PROMPT = """请仔细分析这张网页截图的视觉设计风格，提取关键设计特征，以 JSON 格式返回。

返回格式（严格按此结构，只返回 JSON，不要其他文字）：

{
  "style_name": "为这个风格起一个英文名称（小写字母+下划线，如 midnight_glass / warm_paper / tech_grid）",
  "description": "一句话描述这个风格（中文，10-20字，如：深色毛玻璃+彩色光晕，科技感强）",
  "mood": "风格情绪关键词（如：professional / playful / minimal / bold / elegant / technical / warm）",

  "colors": {
    "bg": "页面主背景色，十六进制（如 #0a0b10）",
    "surface": "卡片/容器背景色，支持 rgba（如 rgba(255,255,255,0.06)）",
    "glass_border": "卡片边框颜色（如 rgba(255,255,255,0.09)）",
    "glass_hover": "卡片悬停背景色（如 rgba(255,255,255,0.11)）",
    "text": "主要文字颜色（如 #e8ecf4）",
    "text_secondary": "次要文字颜色（如 #94a3b8）",
    "text_muted": "弱化文字颜色（如 #64748b）",
    "heading": "标题颜色（如 #f8fafc）",
    "accent_1": "第1强调色（如 #4F6AF6）",
    "accent_2": "第2强调色（如 #7C5CFC）",
    "accent_3": "第3强调色（如 #2DB87F）"
  },

  "typography": {
    "font_family": "主字体栈（如 'Georgia, serif' 或 'Inter, sans-serif' 或 'Courier New, monospace'）",
    "base_size_px": "基础字号（整数，如 14/15/16）",
    "heading_weight": "标题字重（整数，如 700/800/900）",
    "body_weight": "正文字重（整数，如 400/500）",
    "letter_spacing": "标题字间距（如 '-0.02em' 或 '0.05em' 或 'normal'）"
  },

  "effects": {
    "border_radius_px": "卡片圆角大小（整数px，如 0/4/8/16/24）",
    "shadow": "卡片阴影 CSS 值（如 '0 8px 32px rgba(0,0,0,0.3)' 或 'none'）",
    "use_blur": "是否使用毛玻璃模糊背景效果（true/false）",
    "blur_px": "模糊量（整数，无则为 0）",
    "use_gradient_bg": "是否有彩色光晕/渐变背景装饰（true/false）",
    "gradient_accent_1": "渐变装饰颜色1（如 '#4F6AF6' 或 null）",
    "gradient_accent_2": "渐变装饰颜色2（如 '#7C5CFC' 或 null）"
  },

  "layout": {
    "max_width_px": "内容区最大宽度（整数，如 860/900/1200）",
    "card_padding": "卡片内边距 CSS 值（如 '2rem' 或'1.5rem 2rem'）",
    "section_gap": "章节间距 CSS 值（如 '1.5rem' 或 '2rem'）"
  },

  "special_features": {
    "has_decorative_bg": "是否有背景装饰元素（点阵/网格/光晕等）（true/false）",
    "card_style_type": "卡片风格类型（glass/flat/elevated/outlined/paper 之一）",
    "header_has_gradient_line": "顶部标题区是否有彩色渐变线（true/false）",
    "use_dark_theme": "是否是深色主题（true/false）"
  },

  "css_overrides": "需要额外添加的 CSS 规则字符串（实现截图中特色视觉效果，如特殊边框、装饰元素等；如无特殊要求则返回空字符串 ''）"
}
"""


def _read_image_as_base64(image_path: str):
    ext = os.path.splitext(image_path)[1].lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
    }
    media_type = media_type_map.get(ext, 'image/png')
    with open(image_path, 'rb') as f:
        data = base64.standard_b64encode(f.read()).decode('utf-8')
    return data, media_type


def _call_claude_vision(image_path: str) -> dict:
    try:
        import anthropic
    except ImportError:
        print("错误：请先安装 anthropic SDK：pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("错误：请设置环境变量 ANTHROPIC_API_KEY")
        sys.exit(1)

    print(f"正在分析图片：{image_path}")
    client = anthropic.Anthropic(api_key=api_key)
    image_data, media_type = _read_image_as_base64(image_path)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": ANALYSIS_PROMPT
                }
            ],
        }]
    )

    response_text = message.content[0].text.strip()
    # 提取 JSON（Claude 可能在 JSON 前后加了说明文字）
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if not json_match:
        print(f"错误：无法从响应中提取 JSON\n响应内容：{response_text[:500]}")
        sys.exit(1)

    return json.loads(json_match.group())


def _analysis_to_custom_style(analysis: dict) -> dict:
    """将 Claude 返回的风格分析转换为 build_web_onepage.py 可用的 custom_style.json 格式"""
    c = analysis.get('colors', {})
    t = analysis.get('typography', {})
    e = analysis.get('effects', {})
    l = analysis.get('layout', {})
    sf = analysis.get('special_features', {})

    # 构建 CSS 变量字符串
    radius = e.get('border_radius_px', 16)
    vars_parts = [
        f"--bg:{c.get('bg', '#0a0b10')};",
        f"--surface:{c.get('surface', 'rgba(255,255,255,0.06)')};",
        f"--glass:{c.get('surface', 'rgba(255,255,255,0.06)')};",
        f"--glass-border:{c.get('glass_border', 'rgba(255,255,255,0.09)')};",
        f"--glass-hover:{c.get('glass_hover', 'rgba(255,255,255,0.11)')};",
        f"--text:{c.get('text', '#e8ecf4')};",
        f"--text-secondary:{c.get('text_secondary', '#94a3b8')};",
        f"--text-muted:{c.get('text_muted', '#64748b')};",
        f"--heading:{c.get('heading', '#f8fafc')};",
        f"--radius:{radius}px;",
    ]
    css_vars = '\n            '.join(vars_parts)

    # 构建 accent 颜色列表（供 ACCENT_COLORS 使用）
    accent_colors = [
        c.get('accent_1', '#4F6AF6'),
        c.get('accent_2', '#7C5CFC'),
        c.get('accent_3', '#2DB87F'),
    ]
    # 补足到6个（循环填充）
    while len(accent_colors) < 6:
        accent_colors.append(accent_colors[len(accent_colors) % 3])

    # 构建额外的 CSS overrides
    style_key = 'custom'
    override_parts = []

    # 字体覆盖
    font = t.get('font_family', '')
    base_size = t.get('base_size_px', 15)
    if font and font not in ('Inter, sans-serif', "'Inter','Noto Sans SC'"):
        override_parts.append(f"body {{ font-family: {font}, 'Noto Sans SC', sans-serif; font-size:{base_size}px; }}")

    # 毛玻璃 / 无模糊
    blur_px = e.get('blur_px', 0)
    use_blur = e.get('use_blur', False)
    if not use_blur or blur_px == 0:
        override_parts.append(f"[data-style=\"{style_key}\"] .card, [data-style=\"{style_key}\"] .header, [data-style=\"{style_key}\"] .conclusion {{ backdrop-filter:none; -webkit-backdrop-filter:none; }}")

    # 阴影覆盖
    shadow = e.get('shadow', '')
    if shadow and shadow != 'none':
        override_parts.append(f"[data-style=\"{style_key}\"] .card {{ box-shadow:{shadow}; }}")

    # 背景装饰控制
    has_decorative_bg = sf.get('has_decorative_bg', True)
    is_dark = sf.get('use_dark_theme', True)
    if not has_decorative_bg or not is_dark:
        override_parts.append(f"[data-style=\"{style_key}\"] .bg-glow, [data-style=\"{style_key}\"] .bg-grid {{ display:none; }}")
    elif has_decorative_bg and is_dark:
        g1 = e.get('gradient_accent_1') or c.get('accent_1', '#4F6AF6')
        g2 = e.get('gradient_accent_2') or c.get('accent_2', '#7C5CFC')
        override_parts.append(f".bg-glow-1 {{ background:radial-gradient(circle,{g1} 0%,transparent 70%); }}")
        override_parts.append(f".bg-glow-2 {{ background:radial-gradient(circle,{g2} 0%,transparent 70%); }}")

    # 标题区顶部渐变线
    has_gradient_line = sf.get('header_has_gradient_line', True)
    if not has_gradient_line:
        override_parts.append(f"[data-style=\"{style_key}\"] .header::before {{ display:none; }}")

    # 用户指定的额外 CSS
    user_overrides = analysis.get('css_overrides', '')
    if user_overrides and user_overrides.strip():
        override_parts.append(f"/* 自定义风格特殊规则 */\n{user_overrides}")

    # 卡片边框半径
    if radius == 0:
        override_parts.append(f"[data-style=\"{style_key}\"] .card, [data-style=\"{style_key}\"] .header, [data-style=\"{style_key}\"] .conclusion {{ border-radius:0; }}")

    return {
        "name": analysis.get('style_name', 'custom'),
        "description": analysis.get('description', '自定义风格'),
        "mood": analysis.get('mood', 'custom'),
        "vars": css_vars,
        "accent_colors": accent_colors,
        "css_overrides": '\n'.join(override_parts),
        "source_analysis": analysis,
    }


def main():
    parser = argparse.ArgumentParser(
        description="分析网页截图风格，生成 OnePage 自定义风格文件"
    )
    parser.add_argument('--image', type=str, required=True,
                        help='网页截图路径（PNG/JPG/WebP）')
    parser.add_argument('--output', type=str, default='custom_style.json',
                        help='输出的自定义风格 JSON 文件路径（默认：custom_style.json）')
    parser.add_argument('--show-analysis', action='store_true',
                        help='同时打印 Claude 的原始分析结果')
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"错误：图片文件不存在：{args.image}")
        sys.exit(1)

    # Step 1: Claude Vision 分析
    analysis = _call_claude_vision(args.image)

    if args.show_analysis:
        print("\n── Claude 风格分析结果 ──")
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        print()

    # Step 2: 转换为 custom_style.json 格式
    custom_style = _analysis_to_custom_style(analysis)

    # Step 3: 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(custom_style, f, ensure_ascii=False, indent=2)

    style_name = custom_style['name']
    desc = custom_style['description']
    print(f"✓ 风格分析完成：{style_name} — {desc}")
    print(f"✓ 已保存至：{args.output}")
    print()
    print("下一步：使用此风格生成网页")
    print(f"  python3 scripts/build_web_onepage.py \\")
    print(f"    --data data.json \\")
    print(f"    --custom-style {args.output} \\")
    print(f"    --outdir output/web")


if __name__ == '__main__':
    main()

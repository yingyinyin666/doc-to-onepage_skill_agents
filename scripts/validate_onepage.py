#!/usr/bin/env python3
"""
OnePage 自检与自修复系统
在生成网页后，自动进行"结构 + 视觉"的质量检查，并进行自我优化。
适配 V2 可视化增强模板。

模式说明：
- 默认模式（OnePage重构）：强制要求结论区/CTA/风险模块
- Lenient 模式（--lenient）：用户要求保留原文结构时使用，跳过结构性强制检查
"""
import argparse
import os
import re


# 所有模式共用的基础规则
BASE_RULES = {
    'module_count': {
        'name': '模块数量',
        'check': lambda html: len(re.findall(r'<section\s+class="card\s', html)) <= 8,
        'weight': 20
    },
    'has_visual_hierarchy': {
        'name': '视觉层级',
        'check': lambda html: bool(
            re.search(r'font-weight:\s*[789]00|font-weight:\s*bold', html)
            or re.search(r'\.metric-value|\.flow-title|\.num\b', html)
        ),
        'weight': 20
    },
    'appropriate_length': {
        'name': '内容长度',
        # 排除 base64 图片数据再计算长度，避免因内嵌图片误判内容过长
        'check': lambda html: len(re.sub(r'src="data:image[^"]{100,}"', 'src="__img__"', html)) < 80000,
        'weight': 20
    }
}

# 仅在 OnePage 重构模式（非 lenient）下生效的结构规则
ONEPAGE_RULES = {
    'has_conclusion': {
        'name': '结论优先',
        'check': lambda html: bool(re.search(r'class="conclusion[\s"]', html)),
        'weight': 20
    },
    'has_cta': {
        'name': 'CTA行动号召',
        'check': lambda html: bool(
            re.search(r'conclusion-cta|是否批准|是否推进|是否分配|是否启动', html)
        ),
        'weight': 20
    },
    'has_risk': {
        'name': '风险说明',
        'check': lambda html: bool(re.search(r'sec-risk|risk-level|风险', html)),
        'weight': 15
    },
}

# 兼容旧代码：默认规则集 = 基础 + OnePage 结构规则
QUALITY_RULES = {**ONEPAGE_RULES, **BASE_RULES}


def validate_html_structure(html_content, lenient=False):
    """检查HTML是否符合OnePage设计规范

    Args:
        lenient: True 时使用宽松模式（用户保留原文结构），跳过结构性强制检查（结论/CTA/风险）
    """
    results = []
    total_score = 0
    max_score = 0

    rules = BASE_RULES if lenient else QUALITY_RULES

    for rule_key, rule in rules.items():
        max_score += rule['weight']
        try:
            passed = rule['check'](html_content)
            results.append({
                'rule': rule['name'],
                'passed': passed,
                'weight': rule['weight']
            })
            if passed:
                total_score += rule['weight']
        except Exception as e:
            results.append({
                'rule': rule['name'],
                'passed': False,
                'weight': rule['weight'],
                'error': str(e)
            })

    score_percent = int((total_score / max_score) * 100) if max_score > 0 else 0

    return {
        'score': score_percent,
        'total_score': total_score,
        'max_score': max_score,
        'results': results,
        'passed': score_percent >= 70
    }


def generate_fix_suggestions(validation_result):
    """根据验证结果生成修复建议"""
    suggestions = []

    for result in validation_result['results']:
        if not result['passed']:
            rule = result['rule']
            if rule == '结论优先':
                suggestions.append({
                    'issue': '缺少结论区域',
                    'fix': '在页面顶部添加 .conclusion 区域，包含 KEY TAKEAWAY 标签和核心结论',
                    'auto_fixable': True
                })
            elif rule == 'CTA行动号召':
                suggestions.append({
                    'issue': '缺少明确的行动号召',
                    'fix': '添加 .conclusion-cta 决策框，如"是否批准？"',
                    'auto_fixable': True
                })
            elif rule == '风险说明':
                suggestions.append({
                    'issue': '缺少风险模块',
                    'fix': '添加 .sec-risk 风险章节',
                    'auto_fixable': True
                })
            elif rule == '模块数量':
                suggestions.append({
                    'issue': '模块过多',
                    'fix': '精简章节，核心模块控制在 4-6 个',
                    'auto_fixable': False
                })
            elif rule == '视觉层级':
                suggestions.append({
                    'issue': '视觉层级不清晰',
                    'fix': '确保使用 metric-card、flow-timeline 等可视化组件',
                    'auto_fixable': False
                })
            elif rule == '内容长度':
                suggestions.append({
                    'issue': '内容过长',
                    'fix': '删除冗余内容，保持信息密度',
                    'auto_fixable': False
                })

    return suggestions


def apply_fixes(html_content, suggestions):
    """应用自动修复"""
    fixes_applied = []

    for suggestion in suggestions:
        if not suggestion.get('auto_fixable'):
            continue

        issue = suggestion['issue']

        if issue == '缺少结论区域' and 'class="conclusion' not in html_content:
            conclusion_html = '''
    <section class="conclusion fade-in visible">
      <div class="conclusion-label">KEY TAKEAWAY</div>
      <div class="conclusion-content">
        <p>请补充核心结论。</p>
      </div>
      <div class="conclusion-cta">请补充决策问题</div>
    </section>'''
            # 插入到 <main> 标签之后
            html_content = html_content.replace('<main>', f'<main>{conclusion_html}', 1)
            fixes_applied.append('添加结论区域')

        elif issue == '缺少明确的行动号召' and 'conclusion-cta' not in html_content:
            cta_html = '\n      <div class="conclusion-cta">是否批准推进？</div>'
            # 在 conclusion 结束前插入
            html_content = html_content.replace(
                '</section>\n\n        <section class="card',
                f'{cta_html}\n    </section>\n\n        <section class="card',
                1
            )
            fixes_applied.append('添加CTA决策框')

        elif issue == '缺少风险模块' and 'sec-risk' not in html_content:
            risk_html = '''
        <section class="card fade-in sec-risk" style="--accent:#E8546A">
          <div class="card-head">
            <div class="num" style="--c:#E8546A">!</div>
            <div class="card-title-wrap"><h2>风险与应对</h2></div>
          </div>
          <div class="card-body">
            <div class="sub">
              <h3><span class="dot" style="background:#E8546A"></span>待补充</h3>
              <div class="sub-content"><p>请根据实际情况补充风险项及应对措施。</p></div>
            </div>
          </div>
        </section>'''
            html_content = html_content.replace('</main>', f'{risk_html}\n</main>')
            fixes_applied.append('添加风险模块')

    return html_content, fixes_applied


def main(html_path, output_path=None, auto_fix=False, lenient=False):
    if not os.path.exists(html_path):
        print(f"Error: File not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("=" * 50)
    mode_label = "宽松模式（原文结构）" if lenient else "标准模式（OnePage重构）"
    print(f"OnePage V2 自检系统 [{mode_label}]")
    print("=" * 50)

    validation = validate_html_structure(html_content, lenient=lenient)

    print(f"\n质量得分: {validation['score']}/100")
    print(f"通过状态: {'通过' if validation['passed'] else '未通过'}")

    print("\n检查详情:")
    for result in validation['results']:
        status = 'PASS' if result['passed'] else 'FAIL'
        print(f"  [{status}] {result['rule']} ({result['weight']}分)")

    suggestions = generate_fix_suggestions(validation)

    if suggestions:
        print(f"\n修复建议 ({len(suggestions)}项):")
        for i, suggestion in enumerate(suggestions, 1):
            fixable = '[可自动修复]' if suggestion.get('auto_fixable') else '[需手动修复]'
            print(f"  {i}. {suggestion['issue']} {fixable}")
            print(f"     -> {suggestion['fix']}")

    if lenient and auto_fix:
        print("\n[宽松模式] 跳过结构性自动修复（结论/CTA/风险），仅报告视觉问题")
        auto_fix = False  # 宽松模式下不强制插入 OnePage 专属结构

    if auto_fix and suggestions:
        print("\n自动修复中...")
        html_content, fixes = apply_fixes(html_content, suggestions)

        if fixes:
            print(f"  已应用: {', '.join(fixes)}")
            target = output_path or html_path
            with open(target, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  输出: {target}")

            # 修复后重新验证
            revalidation = validate_html_structure(html_content)
            print(f"  修复后得分: {revalidation['score']}/100")
        else:
            print("  无可自动修复的项目")

    print("\n" + "=" * 50)
    return validation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OnePage V2 自检与自修复系统")
    parser.add_argument('--html', type=str, required=True, help='HTML文件路径')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--auto-fix', action='store_true', help='自动修复问题')
    parser.add_argument('--lenient', action='store_true',
                        help='宽松模式：用户保留原文档结构时使用，跳过结论/CTA/风险的强制检查')

    args = parser.parse_args()
    main(
        html_path=args.html,
        output_path=args.output,
        auto_fix=args.auto_fix,
        lenient=args.lenient
    )

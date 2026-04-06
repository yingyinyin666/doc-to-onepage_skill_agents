#!/usr/bin/env python3
"""
OnePage 自检与自修复系统
在生成网页后，自动进行"结构 + 视觉"的质量检查，并进行自我优化
"""
import argparse
import os
import json
import re

QUALITY_RULES = {
    'has_conclusion': {
        'name': '结论优先',
        'check': lambda html: bool(re.search(r'结论 CTA|结论区|Conclusion', html, re.IGNORECASE)),
        'weight': 20
    },
    'has_cta': {
        'name': 'CTA行动号召',
        'check': lambda html: bool(re.search(r'是否批准|是否推进|是否分配|批准|推进|决策', html)),
        'weight': 20
    },
    'has_risk': {
        'name': '风险说明',
        'check': lambda html: bool(re.search(r'风险|Risk|依赖', html)),
        'weight': 15
    },
    'module_count': {
        'name': '模块数量',
        'check': lambda html: True,
        'weight': 15,
        'subcheck': lambda html: len(re.findall(r'<h2|<h3', html)) <= 10
    },
    'has_visual_hierarchy': {
        'name': '视觉层级',
        'check': lambda html: bool(re.search(r'font-bold|text-\w+-\d+|font-semibold', html)),
        'weight': 15
    },
    'appropriate_length': {
        'name': '内容长度',
        'check': lambda html: len(html) < 50000,
        'weight': 15
    }
}

def validate_html_structure(html_content):
    """检查HTML是否符合OnePage设计规范"""
    results = []
    total_score = 0
    max_score = 0

    for rule_key, rule in QUALITY_RULES.items():
        max_score += rule['weight']
        try:
            passed = rule['check'](html_content)
            if passed and 'subcheck' in rule:
                passed = rule['subcheck'](html_content)

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
                    'fix': '在页面顶部添加结论区，包含标题、一句话结论和CTA'
                })
            elif rule == 'CTA行动号召':
                suggestions.append({
                    'issue': '缺少明确的行动号召',
                    'fix': '添加CTA按钮，如"是否批准？"、"是否推进？"'
                })
            elif rule == '风险说明':
                suggestions.append({
                    'issue': '缺少风险模块',
                    'fix': '添加风险与依赖说明部分'
                })
            elif rule == '模块数量':
                suggestions.append({
                    'issue': '模块过多或层级过深',
                    'fix': '精简模块，确保核心模块≤3个'
                })
            elif rule == '视觉层级':
                suggestions.append({
                    'issue': '视觉层级不清晰',
                    'fix': '使用加粗、不同字号、颜色区分内容层级'
                })
            elif rule == '内容长度':
                suggestions.append({
                    'issue': '内容过长',
                    'fix': '删除冗余内容，保持信息密度'
                })

    return suggestions

def apply_fixes(html_content, suggestions):
    """应用基本修复"""
    fixes_applied = []

    for suggestion in suggestions:
        issue = suggestion['issue']
        fix = suggestion['fix']

        if issue == '缺少结论区域' and '结论区' not in html_content:
            conclusion_html = '''
            <div class="conclusion-banner" style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
                <h2 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;">结论</h2>
                <p style="margin: 0;">建议立即推进本方案</p>
                <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.2); border-radius: 4px;">
                    <strong>CTA:</strong> 是否批准资源投入？
                </div>
            </div>
            '''
            html_content = html_content.replace('<div id="content"></div>', f'<div id="content">{conclusion_html}</div>')
            fixes_applied.append('添加结论区域')

        elif issue == '缺少风险模块' and '风险' not in html_content:
            risk_html = '''
            <div class="section" style="border-top: 2px solid #ef4444; margin-top: 2rem; padding-top: 1rem;">
                <h2 style="color: #ef4444;">风险与依赖</h2>
                <div style="background: #fef2f2; padding: 1rem; border-radius: 4px; border-left: 4px solid #ef4444;">
                    <p><strong>主要风险：</strong>请根据实际情况补充</p>
                    <p><strong>应对策略：</strong>请根据实际情况补充</p>
                </div>
            </div>
            '''
            html_content = html_content.replace('</body>', f'{risk_html}</body>')
            fixes_applied.append('添加风险模块')

    return html_content, fixes_applied

def main(html_path, output_path=None, auto_fix=False):
    """主函数"""
    if not os.path.exists(html_path):
        print(f"Error: File not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("=" * 50)
    print("🔍 OnePage 自检系统")
    print("=" * 50)

    validation = validate_html_structure(html_content)

    print(f"\n📊 质量得分: {validation['score']}/100")
    print(f"✅ 通过状态: {'通过' if validation['passed'] else '未通过'}")

    print("\n📋 检查详情:")
    for result in validation['results']:
        status = '✅' if result['passed'] else '❌'
        print(f"  {status} {result['rule']} ({result['weight']}分)")

    suggestions = generate_fix_suggestions(validation)

    if suggestions:
        print(f"\n💡 修复建议 ({len(suggestions)}项):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['issue']}")
            print(f"     → {suggestion['fix']}")

    if auto_fix and suggestions:
        print("\n🔧 自动修复中...")
        html_content, fixes = apply_fixes(html_content, suggestions[:2])

        if fixes:
            print(f"  ✅ 已应用修复: {', '.join(fixes)}")

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"  📁 输出文件: {output_path}")
        else:
            print("  ⚠️ 未能自动修复，需要手动调整")

    print("\n" + "=" * 50)

    return validation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OnePage 自检与自修复系统")
    parser.add_argument('--html', type=str, required=True, help='HTML文件路径')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--auto-fix', action='store_true', help='自动修复问题')

    args = parser.parse_args()
    main(
        html_path=args.html,
        output_path=args.output,
        auto_fix=args.auto_fix
    )

#!/usr/bin/env python3
"""
OnePage 截图校验脚本
使用 Playwright 进行视觉质量检查
"""
import argparse
import os
import sys
import base64
import re
from pathlib import Path

def check_playwright_installed():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False

def take_screenshot(html_path, output_path=None):
    from playwright.sync_api import sync_playwright

    if not os.path.exists(html_path):
        print(f"Error: HTML file not found: {html_path}")
        return None

    if output_path is None:
        output_path = html_path.replace('.html', '_screenshot.png')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto(f'file://{os.path.abspath(html_path)}')
        page.wait_for_timeout(1000)
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    return output_path

def analyze_visual_quality(html_path):
    from playwright.sync_api import sync_playwright

    issues = []
    checks = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto(f'file://{os.path.abspath(html_path)}')
        page.wait_for_timeout(1000)

        has_conclusion = page.query_selector('.conclusion-banner, [class*="conclusion"], #conclusion')
        checks.append({
            'item': '结论区域',
            'passed': has_conclusion is not None,
            'selector': '.conclusion-banner, [class*="conclusion"]'
        })

        cta_elements = page.query_selector_all('button, a[href], [class*="cta"], [class*="btn"]')
        checks.append({
            'item': 'CTA按钮',
            'passed': len(cta_elements) > 0,
            'count': len(cta_elements)
        })

        h1_count = len(page.query_selector_all('h1'))
        h2_count = len(page.query_selector_all('h2'))
        checks.append({
            'item': '标题层级',
            'passed': h1_count >= 1 and h2_count <= 5,
            'h1': h1_count,
            'h2': h2_count
        })

        sections = page.query_selector_all('h2, [class*="section"]')
        checks.append({
            'item': '模块数量',
            'passed': len(sections) <= 8,
            'count': len(sections)
        })

        visible_text = page.evaluate('''() => {
            const el = document.body;
            const style = window.getComputedStyle(el);
            return {
                visible: style.visibility !== 'hidden' && style.display !== 'none',
                hasContent: el.innerText.length > 100
            };
        }''')
        checks.append({
            'item': '内容可见性',
            'passed': visible_text['visible'] and visible_text['hasContent'],
            'char_count': len(visible_text.get('text', '')) if isinstance(visible_text, dict) else 0
        })

        browser.close()

    for check in checks:
        if not check['passed']:
            if check['item'] == '结论区域':
                issues.append('视觉检查：缺少结论横幅区域')
            elif check['item'] == 'CTA按钮':
                issues.append('视觉检查：页面缺少CTA按钮')
            elif check['item'] == '标题层级':
                issues.append(f"视觉检查：标题层级异常 (H1:{check['h1']}, H2:{check['h2']})")
            elif check['item'] == '模块数量':
                issues.append(f"视觉检查：模块过多 ({check['count']}个)")

    return {
        'checks': checks,
        'issues': issues,
        'score': max(0, 100 - len(issues) * 15)
    }

def main():
    parser = argparse.ArgumentParser(description="OnePage 截图校验")
    parser.add_argument('--html', type=str, required=True, help='HTML文件路径')
    parser.add_argument('--screenshot', type=str, help='截图保存路径')
    parser.add_argument('--analyze', action='store_true', help='进行视觉分析')

    args = parser.parse_args()

    if not check_playwright_installed():
        print("⚠️ Playwright 未安装")
        print("请运行: pip install playwright && playwright install chromium")
        return

    print("=" * 50)
    print("📸 OnePage 截图校验")
    print("=" * 50)

    screenshot_path = take_screenshot(args.html, args.screenshot)
    if screenshot_path:
        print(f"\n✅ 截图已保存: {screenshot_path}")

    if args.analyze:
        print("\n🔍 视觉质量分析...")
        analysis = analyze_visual_quality(args.html)

        print(f"\n📊 视觉得分: {analysis['score']}/100")
        print("\n📋 检查结果:")
        for check in analysis['checks']:
            status = '✅' if check['passed'] else '❌'
            extra = ''
            if 'count' in check:
                extra = f" ({check['count']}个)"
            if 'h1' in check:
                extra = f" (H1:{check['h1']}, H2:{check['h2']})"
            print(f"  {status} {check['item']}{extra}")

        if analysis['issues']:
            print(f"\n⚠️ 发现问题 ({len(analysis['issues'])}项):")
            for issue in analysis['issues']:
                print(f"  • {issue}")
        else:
            print("\n✅ 视觉质量检查通过")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()

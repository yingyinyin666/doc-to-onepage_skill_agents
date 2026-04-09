#!/usr/bin/env python3
import argparse
import os
import re
import json

TEMPLATE_KEYWORDS = {
    'decision-report': {
        'keywords': ['决策', '方案', '评审', '申请', '对比', '资源', '预算', '投资', '回报', '决策', '高层', '批准'],
        'weight': 1.0
    },
    'product-solution': {
        'keywords': ['产品', '方案', 'BRD', 'PRD', '需求', '功能', '设计', '用户体验', '竞品', '市场规模'],
        'weight': 1.0
    },
    'project-progress': {
        'keywords': ['进展', '周报', '月报', '里程碑', '进度', '完成度', '项目', '阶段', '计划', '延期'],
        'weight': 1.0
    },
    'governance-improvement': {
        'keywords': ['治理', '优化', '体验', '痛点', '风险', '协同', '跨团队', '长期', '根因', '问题定义'],
        'weight': 1.0
    },
    'holiday-support': {
        'keywords': ['大促', '春节', '国庆', '节假日', '保障', '预案', '应急', '峰值', '流量', '稳定性'],
        'weight': 1.0
    },
    'product-tool': {
        'keywords': ['工具', '系统', '开发', '迭代', '功能', '技术方案', '架构', 'API', '数据埋点', 'A/B'],
        'weight': 1.0
    },
    'project-management': {
        'keywords': ['年度', '规划', ' roadmap', '能力建设', '长期', '多年', '平台', '战略', '北极星', '指标'],
        'weight': 1.0
    },
    'team-intro': {
        'keywords': ['团队', '介绍', '职能', '分工', '接口人', '联系人', '协作', '流程', 'FAQ', '地图'],
        'weight': 1.0
    },
    'personal-review': {
        'keywords': ['述职', '个人', '成长', '反思', '自评', '绩效', '复盘', '能力', '季度总结', '半年', '年终', '贡献', 'OKR'],
        'weight': 1.0
    },
    'cartoon-brochure': {
        'keywords': ['宣传', '宣传册', '服务介绍', '服务流程', '扫码', '二维码', '预约', '报名', '旅游', '教育', '活动', '推广', '用户手册', '使用说明', '客服', '群服务', '保障承诺', '联系我们'],
        'weight': 1.0
    },
    'blackboard-notice': {
        'keywords': ['公告', '通知', '公示', '声明', '紧急通知', '重要通知', '停课', '停工', '放假', '安排', '须知', '注意事项', '规定', '制度', '公示', '告知', '温馨提示', '特此通知', '望周知'],
        'weight': 1.0
    }
}

TEMPLATE_SCENARIOS = {
    'decision-report': '高层汇报 / 决策申请',
    'product-solution': '产品方案 / BRD',
    'project-progress': '项目进展 / 周报',
    'governance-improvement': '专项治理 / 体验优化',
    'holiday-support': '大促 / 节假日保障',
    'product-tool': '工具 / 系统建设',
    'project-management': '长周期项目 / 能力建设',
    'team-intro': '团队介绍 / 协作地图',
    'personal-review': '个人述职 / 阶段性总结',
    'cartoon-brochure': '服务/活动宣传册（卡通风）',
    'blackboard-notice': '公告 / 通知 / 公示（黑板报风）'
}

def analyze_text(text):
    """分析文本内容"""
    text_lower = text.lower()
    text_chinese = text

    scores = {}

    for template, config in TEMPLATE_KEYWORDS.items():
        score = 0
        matched_keywords = []

        for keyword in config['keywords']:
            if keyword.lower() in text_lower:
                score += config['weight']
                matched_keywords.append(keyword)

        if matched_keywords:
            scores[template] = {
                'score': score,
                'matched': matched_keywords
            }

    return scores

def recommend_template(scores):
    """基于得分推荐模板"""
    if not scores:
        return 'project-progress', 50, [], []

    sorted_templates = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)

    top_template = sorted_templates[0][0]
    top_score = sorted_templates[0][1]['score']
    top_matched = sorted_templates[0][1]['matched']

    max_possible = len(TEMPLATE_KEYWORDS[top_template]['keywords'])
    confidence = min(int((top_score / max_possible) * 100), 100) if max_possible > 0 else 50
    confidence = max(confidence, 30)  # 至少30%，避免显示过低误导用户

    alternatives = []
    for template, data in sorted_templates[1:4]:
        alternatives.append({
            'template': template,
            'scenario': TEMPLATE_SCENARIOS[template],
            'matched': data['matched'][:3]
        })

    return top_template, confidence, top_matched, alternatives

def generate_recommendation_output(text):
    """生成推荐输出"""
    scores = analyze_text(text)
    top_template, confidence, matched, alternatives = recommend_template(scores)

    output = []
    output.append("我分析了你的文档，推荐：")
    output.append("")
    output.append(f"🥇 **{TEMPLATE_SCENARIOS[top_template]}**（匹配度 {confidence}%）")

    if matched:
        output.append(f"   → 命中关键词：{', '.join(matched[:5])}")

    if alternatives:
        output.append("")
        for alt in alternatives:
            output.append(f"🥈 {alt['scenario']}（命中：{', '.join(alt['matched'])})")

    output.append("")
    output.append("你可以直接使用推荐，或手动选择其他模板")

    return {
        'top_template': top_template,
        'confidence': confidence,
        'matched_keywords': matched,
        'alternatives': alternatives,
        'output_text': '\n'.join(output)
    }

def main(file_path, output):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    result = generate_recommendation_output(text)

    print(result['output_text'])

    if output:
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump({
                'top_template': result['top_template'],
                'confidence': result['confidence'],
                'matched_keywords': result['matched_keywords'],
                'alternatives': result['alternatives']
            }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Template Recommendation")
    parser.add_argument('--file', type=str, help='Path to document file')
    parser.add_argument('--text', type=str, help='Direct text input')
    parser.add_argument('--output', type=str, help='Output JSON file path')

    args = parser.parse_args()

    if args.file:
        main(args.file, args.output)
    elif args.text:
        result = generate_recommendation_output(args.text)
        print(result['output_text'])
    else:
        print("Please provide --file or --text argument")

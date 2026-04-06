#!/usr/bin/env python3
import argparse
import os
import re
import json

def parse_wechat_chat(text):
    """解析微信聊天记录"""
    messages = []
    lines = text.strip().split('\n')
    
    # 微信聊天记录格式：时间 | 发送者 | 内容
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*[|]\s*([^:]+):\s*(.+)')
    
    for line in lines:
        match = pattern.match(line)
        if match:
            time, sender, content = match.groups()
            messages.append({
                'time': time,
                'sender': sender.strip(),
                'content': content.strip()
            })
    
    return messages

def parse_dingtalk_chat(text):
    """解析钉钉聊天记录"""
    messages = []
    lines = text.strip().split('\n')
    
    # 钉钉格式：[时间] 发送者: 内容
    pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)')
    
    for line in lines:
        match = pattern.match(line)
        if match:
            time, sender, content = match.groups()
            messages.append({
                'time': time,
                'sender': sender.strip(),
                'content': content.strip()
            })
    
    return messages

def parse_generic_chat(text):
    """通用聊天记录解析"""
    messages = []
    lines = text.strip().split('\n')
    
    for line in lines:
        # 尝试多种格式
        # 格式1: 时间 - 发送者: 内容
        pattern1 = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*[-–]\s*([^:]+):\s*(.+)')
        match = pattern1.match(line)
        if match:
            time, sender, content = match.groups()
            messages.append({
                'time': time,
                'sender': sender.strip(),
                'content': content.strip()
            })
            continue
        
        # 格式2: [时间] 发送者: 内容
        pattern2 = re.compile(r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s*([^:]+):\s*(.+)')
        match = pattern2.match(line)
        if match:
            time, sender, content = match.groups()
            messages.append({
                'time': time,
                'sender': sender.strip(),
                'content': content.strip()
            })
    
    return messages

def analyze_chat(messages):
    """分析聊天记录，提取关键信息"""
    if not messages:
        return {
            'total_messages': 0,
            'participants': [],
            'summary': '',
            'key_topics': [],
            'decisions': [],
            'action_items': []
        }
    
    # 统计参与者
    senders = set()
    for msg in messages:
        senders.add(msg['sender'])
    
    # 提取关键话题（出现频率高的词）
    all_text = ' '.join([msg['content'] for msg in messages])
    words = re.findall(r'[\u4e00-\u9fa5]+', all_text)
    word_freq = {}
    for word in words:
        if len(word) >= 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 获取最常见的词（排除停用词）
    stopwords = ['这个', '那个', '什么', '怎么', '为什么', '可以', '不是', '是的', '没有', '有的']
    key_topics = [w for w, c in sorted(word_freq.items(), key=lambda x: x[1], reverse=True) if w not in stopwords][:10]
    
    # 提取决策（包含"决定"、"同意"、"通过"等的句子）
    decisions = []
    decision_keywords = ['决定', '同意', '通过', '批准', '确认', '达成', '共识']
    for msg in messages:
        for keyword in decision_keywords:
            if keyword in msg['content']:
                decisions.append({
                    'time': msg['time'],
                    'sender': msg['sender'],
                    'content': msg['content']
                })
                break
    
    # 提取行动项（包含"要"、"会"、"需要"、"应该"等的句子）
    action_items = []
    action_keywords = ['要', '会', '需要', '应该', '会做', '来做', '负责', '安排']
    for msg in messages:
        for keyword in action_keywords:
            if keyword in msg['content'] and ('点' in msg['content'] or '事' in msg['content'] or '任务' in msg['content']):
                action_items.append({
                    'time': msg['time'],
                    'sender': msg['sender'],
                    'content': msg['content']
                })
                break
    
    # 生成摘要
    summary = f"本次聊天共{len(messages)}条消息，参与者{len(senders)}人：{', '.join(senders)}。"
    
    return {
        'total_messages': len(messages),
        'participants': list(senders),
        'summary': summary,
        'key_topics': key_topics,
        'decisions': decisions,
        'action_items': action_items,
        'time_range': f"{messages[0]['time']} - {messages[-1]['time']}" if messages else ""
    }

def convert_to_markdown(messages, analysis):
    """将聊天记录转换为Markdown格式"""
    md = f"""# 聊天记录摘要

## 基本信息

- **总消息数**: {analysis['total_messages']}
- **参与人数**: {len(analysis['participants'])}
- **参与者**: {', '.join(analysis['participants'])}
- **时间范围**: {analysis['time_range']}

## 摘要

{analysis['summary']}

## 关键话题

{', '.join(analysis['key_topics'])}

## 重要决策

"""
    
    if analysis['decisions']:
        for i, decision in enumerate(analysis['decisions'][:5], 1):
            md += f"{i}. **{decision['content']}** ({decision['sender']} @ {decision['time']})\n"
    else:
        md += "_暂无明显决策记录_\n"
    
    md += "\n## 行动项\n\n"
    
    if analysis['action_items']:
        for i, item in enumerate(analysis['action_items'][:5], 1):
            md += f"{i}. **{item['content']}** ({item['sender']} @ {item['time']})\n"
    else:
        md += "_暂无明显行动项记录_\n"
    
    md += "\n## 聊天内容详情\n\n"
    
    for msg in messages[:50]:
        md += f"**{msg['time']}** [{msg['sender']}]: {msg['content']}\n\n"
    
    if len(messages) > 50:
        md += f"\n_... 共{len(messages)}条消息，显示前50条 _\n"
    
    return md

def main(file_path, output, chat_type):
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析聊天记录
    if chat_type == 'wechat':
        messages = parse_wechat_chat(text)
    elif chat_type == 'dingtalk':
        messages = parse_dingtalk_chat(text)
    else:
        messages = parse_generic_chat(text)
    
    # 分析聊天记录
    analysis = analyze_chat(messages)
    
    # 转换为Markdown
    markdown = convert_to_markdown(messages, analysis)
    
    # 保存结果
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # 保存Markdown
    md_path = output.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # 保存分析结果
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'messages': messages,
            'analysis': analysis,
            'markdown': markdown
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Chat processed successfully!")
    print(f"Markdown saved to: {md_path}")
    print(f"Analysis saved to: {output}")
    print(f"\nSummary:")
    print(f"- Total messages: {analysis['total_messages']}")
    print(f"- Participants: {', '.join(analysis['participants'])}")
    print(f"- Key topics: {', '.join(analysis['key_topics'][:5])}")
    print(f"- Decisions found: {len(analysis['decisions'])}")
    print(f"- Action items found: {len(analysis['action_items'])}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process chat records")
    parser.add_argument('--file', type=str, required=True, help='Path to chat file')
    parser.add_argument('--output', type=str, default="./output/chat_analysis.json", help='Output JSON file path')
    parser.add_argument('--type', type=str, default="generic", choices=['wechat', 'dingtalk', 'generic'], help='Chat type')
    
    args = parser.parse_args()
    main(
        file_path=args.file,
        output=args.output,
        chat_type=args.type
    )

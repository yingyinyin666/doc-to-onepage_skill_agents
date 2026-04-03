#!/usr/bin/env python3
import argparse
import os
import re
import json

def parse_lark_markdown(text):
    """解析飞书Markdown格式"""
    lines = text.strip().split('\n')
    result = {
        'title': '',
        'sections': [],
        'blocks': []
    }
    
    current_section = None
    current_block = []
    
    for line in lines:
        # 提取标题
        if line.startswith('# '):
            result['title'] = line[2:].strip()
            continue
        
        # 一级标题作为section
        if line.startswith('## '):
            if current_section:
                result['sections'].append({
                    'title': current_section,
                    'content': '\n'.join(current_block)
                })
            current_section = line[3:].strip()
            current_block = []
            continue
        
        # 其他内容作为block
        if line.strip():
            current_block.append(line)
    
    # 最后一个section
    if current_section:
        result['sections'].append({
            'title': current_section,
            'content': '\n'.join(current_block)
        })
    
    return result

def parse_lark_blocks(text):
    """解析飞书块格式"""
    blocks = []
    lines = text.strip().split('\n')
    
    current_block = {
        'type': 'paragraph',
        'content': []
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_block['content']:
                blocks.append(current_block)
                current_block = {'type': 'paragraph', 'content': []}
            continue
        
        # 标题块
        if line.startswith('# '):
            if current_block['content']:
                blocks.append(current_block)
            current_block = {'type': 'heading1', 'content': [line[2:]]}
            blocks.append(current_block)
            current_block = {'type': 'paragraph', 'content': []}
        elif line.startswith('## '):
            if current_block['content']:
                blocks.append(current_block)
            current_block = {'type': 'heading2', 'content': [line[3:]]}
            blocks.append(current_block)
            current_block = {'type': 'paragraph', 'content': []}
        elif line.startswith('### '):
            if current_block['content']:
                blocks.append(current_block)
            current_block = {'type': 'heading3', 'content': [line[4:]]}
            blocks.append(current_block)
            current_block = {'type': 'paragraph', 'content': []}
        # 列表块
        elif re.match(r'^[\-\*]\s+', line):
            if current_block['type'] != 'list':
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'list', 'content': []}
            current_block['content'].append(re.sub(r'^[\-\*]\s+', '', line))
        # 数字列表
        elif re.match(r'^\d+\.\s+', line):
            if current_block['type'] != 'ordered_list':
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'ordered_list', 'content': []}
            current_block['content'].append(re.sub(r'^\d+\.\s+', '', line))
        # 引用块
        elif line.startswith('>'):
            if current_block['type'] != 'quote':
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'quote', 'content': []}
            current_block['content'].append(line[1:].strip())
        # 代码块
        elif line.startswith('```'):
            if current_block['type'] == 'code':
                blocks.append(current_block)
                current_block = {'type': 'paragraph', 'content': []}
            else:
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'code', 'content': []}
        # 表格
        elif line.startswith('|'):
            if current_block['type'] != 'table':
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'table', 'content': []}
            current_block['content'].append(line)
        # 普通段落
        else:
            if current_block['type'] not in ['paragraph', 'list', 'ordered_list', 'quote', 'code', 'table']:
                if current_block['content']:
                    blocks.append(current_block)
                current_block = {'type': 'paragraph', 'content': []}
            current_block['content'].append(line)
    
    if current_block['content']:
        blocks.append(current_block)
    
    return blocks

def convert_to_standard_markdown(lark_content):
    """将飞书内容转换为标准Markdown"""
    blocks = parse_lark_blocks(lark_content)
    
    md_lines = []
    for block in blocks:
        if block['type'] == 'heading1':
            md_lines.append(f"# {block['content'][0]}")
        elif block['type'] == 'heading2':
            md_lines.append(f"## {block['content'][0]}")
        elif block['type'] == 'heading3':
            md_lines.append(f"### {block['content'][0]}")
        elif block['type'] == 'paragraph':
            md_lines.extend(block['content'])
        elif block['type'] == 'list':
            for item in block['content']:
                md_lines.append(f"- {item}")
        elif block['type'] == 'ordered_list':
            for i, item in enumerate(block['content'], 1):
                md_lines.append(f"{i}. {item}")
        elif block['type'] == 'quote':
            for item in block['content']:
                md_lines.append(f"> {item}")
        elif block['type'] == 'code':
            md_lines.append('```')
            md_lines.extend(block['content'])
            md_lines.append('```')
        elif block['type'] == 'table':
            for row in block['content']:
                md_lines.append(row)
        md_lines.append('')
    
    return '\n'.join(md_lines)

def analyze_lark_document(text):
    """分析飞书文档内容"""
    parsed = parse_lark_markdown(text)
    
    # 统计信息
    total_chars = len(text)
    total_lines = len(text.split('\n'))
    
    # 提取关键信息
    key_info = {
        'title': parsed['title'],
        'sections': len(parsed['sections']),
        'blocks_count': len(parsed['blocks'])
    }
    
    return {
        'title': parsed['title'],
        'sections': parsed['sections'],
        'blocks': parsed['blocks'],
        'statistics': {
            'characters': total_chars,
            'lines': total_lines,
            'sections': len(parsed['sections'])
        }
    }

def main(file_path, output):
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 分析文档
    analysis = analyze_lark_document(text)
    
    # 转换为标准Markdown
    standard_md = convert_to_standard_markdown(text)
    
    # 保存结果
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # 保存标准Markdown
    md_path = output.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(standard_md)
    
    # 保存分析结果
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"Lark document processed successfully!")
    print(f"Standard Markdown saved to: {md_path}")
    print(f"Analysis saved to: {output}")
    print(f"\nDocument info:")
    print(f"- Title: {analysis['title']}")
    print(f"- Sections: {analysis['statistics']['sections']}")
    print(f"- Blocks: {analysis['statistics']['blocks_count']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Lark/Feishu documents")
    parser.add_argument('--file', type=str, required=True, help='Path to Lark document')
    parser.add_argument('--output', type=str, default="./output/lark_analysis.json", help='Output JSON file path')
    
    args = parser.parse_args()
    main(
        file_path=args.file,
        output=args.output
    )

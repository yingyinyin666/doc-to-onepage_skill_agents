#!/usr/bin/env python3
import argparse
import os
import subprocess
import json
import re

def check_lark_cli():
    """检查lark-cli是否已安装"""
    try:
        result = subprocess.run(['lark-cli', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Lark CLI已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("✗ Lark CLI未安装")
    print("\n请先安装Lark CLI:")
    print("1. npm install -g @larksuite/cli")
    print("2. lark-cli config init --new")
    print("3. lark-cli auth login")
    return False

def get_doc_content_by_cli(doc_id):
    """使用lark-cli获取飞书文档内容"""
    try:
        cmd = ['lark-cli', 'doc', 'get', doc_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("Error: 命令执行超时")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_doc_info_by_cli(doc_id):
    """使用lark-cli获取飞书文档信息"""
    try:
        cmd = ['lark-cli', 'doc', 'info', doc_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            return info
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def list_docs_by_cli(folder_id=None):
    """使用lark-cli列出文件夹中的文档"""
    try:
        if folder_id:
            cmd = ['lark-cli', 'doc', 'list', '--folder', folder_id]
        else:
            cmd = ['lark-cli', 'doc', 'list']

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            docs = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        docs.append({
                            'id': parts[0],
                            'title': ' '.join(parts[1:])
                        })
            return docs
        else:
            print(f"Error: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def parse_doc_id(url_or_id):
    """从飞书文档链接或直接ID中提取文档ID"""
    patterns = [
        r'feishu\.cn/docs/([a-zA-Z0-9]+)',
        r'larksuite\.com/docs/([a-zA-Z0-9]+)',
        r'^(https?://[^\s]+)$',
        r'^([a-zA-Z0-9]+)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return url_or_id

def main(doc_url, output, format_type):
    # 检查CLI
    if not check_lark_cli():
        print("\n请先安装并配置Lark CLI，然后重新运行此脚本")
        return

    # 提取文档ID
    doc_id = parse_doc_id(doc_url)
    print(f"\n文档ID: {doc_id}")

    # 获取文档内容
    print("正在获取文档内容...")
    content = get_doc_content_by_cli(doc_id)

    if content:
        # 保存内容
        os.makedirs(os.path.dirname(output), exist_ok=True)

        if format_type == 'markdown':
            md_path = output
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Markdown内容已保存到: {md_path}")
        else:
            json_path = output
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'doc_id': doc_id,
                    'content': content,
                    'source': 'feishu'
                }, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON内容已保存到: {json_path}")

        print("\n✓ 文档读取成功!")
    else:
        print("\n✗ 文档读取失败，请检查:")
        print("1. 文档ID是否正确")
        print("2. 是否有权限访问该文档")
        print("3. Lark CLI是否已授权")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用Lark CLI读取飞书文档")
    parser.add_argument('--doc', type=str, required=True, help='飞书文档URL或文档ID')
    parser.add_argument('--output', type=str, default="./output/lark_content.md", help='输出文件路径')
    parser.add_argument('--format', type=str, default='markdown', choices=['markdown', 'json'], help='输出格式')

    args = parser.parse_args()
    main(
        doc_url=args.doc,
        output=args.output,
        format_type=args.format
    )

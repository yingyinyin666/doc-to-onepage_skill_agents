#!/usr/bin/env python3
import argparse
import os
import subprocess
import json

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

def create_doc_by_cli(title, content, folder_id=None):
    """使用lark-cli创建飞书文档"""
    try:
        # 先创建临时文件
        temp_file = '/tmp/lark_doc_content.md'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 构建命令
        cmd = ['lark-cli', 'doc', 'create', '--title', title, '--file', temp_file]
        if folder_id:
            cmd.extend(['--folder', folder_id])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # 解析返回的文档URL/ID
            output = result.stdout.strip()
            # 尝试提取文档ID
            doc_id = None
            for line in output.split('\n'):
                if 'docx' in line or 'feishu' in line or 'larksuite' in line:
                    # 提取URL中的ID
                    import re
                    match = re.search(r'([a-zA-Z0-9]{20,})', line)
                    if match:
                        doc_id = match.group(1)
                        break

            if not doc_id:
                # 如果没找到，假设输出就是ID
                doc_id = output.split('\n')[-1].strip()

            return {
                'success': True,
                'doc_id': doc_id,
                'url': f"https://feishu.cn/docx/{doc_id}",
                'output': output
            }
        else:
            return {
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def update_doc_by_cli(doc_id, content):
    """使用lark-cli更新飞书文档"""
    try:
        temp_file = '/tmp/lark_doc_update.md'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)

        cmd = ['lark-cli', 'doc', 'update', doc_id, '--file', temp_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def list_folders_by_cli():
    """列出根目录的文件夹"""
    try:
        cmd = ['lark-cli', 'folder', 'list']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            folders = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split(maxsplit=1)
                    if len(parts) >= 1:
                        folders.append(parts[0])
            return folders
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main(action, title, content, doc_id, folder_id, output):
    if not check_lark_cli():
        print("\n请先安装并配置Lark CLI")
        return

    if action == 'create':
        print(f"\n正在创建文档: {title}")
        result = create_doc_by_cli(title, content, folder_id)

        if result['success']:
            print("\n✓ 文档创建成功!")
            print(f"文档ID: {result['doc_id']}")
            print(f"文档URL: {result['url']}")

            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"结果已保存到: {output}")
        else:
            print(f"\n✗ 文档创建失败: {result.get('error')}")

    elif action == 'update':
        print(f"\n正在更新文档: {doc_id}")
        result = update_doc_by_cli(doc_id, content)

        if result['success']:
            print("\n✓ 文档更新成功!")
        else:
            print(f"\n✗ 文档更新失败: {result.get('error')}")

    elif action == 'list-folders':
        print("\n文件夹列表:")
        folders = list_folders_by_cli()
        for folder in folders:
            print(f"  - {folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用Lark CLI操作飞书文档")
    subparsers = parser.add_subparsers(dest='action', help='操作类型')

    # create命令
    create_parser = subparsers.add_parser('create', help='创建新文档')
    create_parser.add_argument('--title', type=str, required=True, help='文档标题')
    create_parser.add_argument('--content', type=str, required=True, help='文档内容(Markdown格式)')
    create_parser.add_argument('--folder', type=str, help='目标文件夹ID')
    create_parser.add_argument('--output', type=str, help='输出JSON文件路径')

    # update命令
    update_parser = subparsers.add_parser('update', help='更新文档')
    update_parser.add_argument('--doc', type=str, required=True, help='文档ID')
    update_parser.add_argument('--content', type=str, required=True, help='新的文档内容')
    update_parser.add_argument('--output', type=str, help='输出JSON文件路径')

    # list-folders命令
    list_parser = subparsers.add_parser('list-folders', help='列出文件夹')

    args = parser.parse_args()

    if args.action == 'create':
        main('create', args.title, args.content, None, args.folder, args.output)
    elif args.action == 'update':
        main('update', None, args.content, args.doc, None, args.output)
    elif args.action == 'list-folders':
        main('list-folders', None, None, None, None, None)
    else:
        parser.print_help()

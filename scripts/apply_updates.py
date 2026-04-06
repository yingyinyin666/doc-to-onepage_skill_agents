#!/usr/bin/env python3
import argparse
import os
import json

def load_onepage(onepage_path):
    if not os.path.exists(onepage_path):
        raise FileNotFoundError(f"Onepage file {onepage_path} not found")
    
    with open(onepage_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_updates(updates_path):
    if not os.path.exists(updates_path):
        raise FileNotFoundError(f"Updates file {updates_path} not found")
    
    with open(updates_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_updates(onepage_content, updates, anchors):
    updated_content = onepage_content
    
    # 解析锚点
    anchor_list = anchors.split(',') if anchors else []
    
    for anchor, update in updates.items():
        # 检查锚点是否在允许列表中
        if anchor_list and anchor not in anchor_list:
            continue
        
        # 处理更新模式
        if isinstance(update, dict) and 'mode' in update:
            mode = update['mode']
            content = update['content']
        else:
            mode = 'replace'
            content = update

        pattern = f"## {anchor}"
        start_idx = updated_content.find(pattern)

        if mode == 'replace':
            if start_idx != -1:
                next_idx = updated_content.find("## ", start_idx + len(pattern))
                if next_idx == -1:
                    updated_content = updated_content[:start_idx] + f"## {anchor}\n\n{content}"
                else:
                    updated_content = updated_content[:start_idx] + f"## {anchor}\n\n{content}\n\n" + updated_content[next_idx:]

        elif mode == 'append':
            if start_idx != -1:
                # 找到章节结尾，在原内容后追加
                next_idx = updated_content.find("## ", start_idx + len(pattern))
                if next_idx == -1:
                    updated_content = updated_content.rstrip() + f"\n\n{content}"
                else:
                    section_end = updated_content[:next_idx].rstrip()
                    updated_content = section_end + f"\n\n{content}\n\n" + updated_content[next_idx:]
            else:
                # 章节不存在则追加到文档末尾
                updated_content = updated_content.rstrip() + f"\n\n## {anchor}\n\n{content}"
    
    return updated_content

def main(onepage, updates, anchors):
    # 加载文件
    onepage_content = load_onepage(onepage)
    updates_data = load_updates(updates)
    
    # 应用更新
    updated_content = apply_updates(onepage_content, updates_data, anchors)
    
    # 写回文件
    with open(onepage, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updates applied successfully to: {onepage}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply updates to Onepage document")
    parser.add_argument('--onepage', type=str, required=True, help='Path to onepage file')
    parser.add_argument('--updates', type=str, required=True, help='Path to updates JSON file')
    parser.add_argument('--anchors', type=str, default="", help='Comma-separated list of anchors to update')
    
    args = parser.parse_args()
    main(
        onepage=args.onepage,
        updates=args.updates,
        anchors=args.anchors
    )

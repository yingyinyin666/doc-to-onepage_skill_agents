#!/usr/bin/env python3
import argparse
import os
import json
import zipfile
import shutil

def create_zip(source_dir, output_path):
    """创建ZIP压缩包"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    print(f"ZIP created: {output_path}")

def generate_share_link(local_path):
    """生成分享链接（这里只是一个示例，实际需要根据部署平台实现）"""
    # 实际部署时，这里应该调用实际的部署API
    # 例如：Netlify、Vercel、Surge 等服务的API
    return f"https://example.com/{os.path.basename(local_path)}"

def deploy_to_netlify(dir_path, api_token):
    """部署到Netlify（示例）"""
    print(f"Deploying to Netlify from: {dir_path}")
    print(f"Note: This is a placeholder. Implement actual Netlify API call here.")
    # 实际实现需要：
    # 1. 创建ZIP包
    # 2. 调用Netlify API上传
    # 3. 返回部署URL
    return None

def deploy_to_vercel(dir_path, token):
    """部署到Vercel（示例）"""
    print(f"Deploying to Vercel from: {dir_path}")
    print(f"Note: This is a placeholder. Implement actual Vercel API call here.")
    # 实际实现需要：
    # 1. 调用Vercel API
    # 2. 等待部署完成
    # 3. 返回部署URL
    return None

def deploy_to_surge(dir_path, email, token):
    """部署到Surge（示例）"""
    print(f"Deploying to Surge from: {dir_path}")
    print(f"Note: This is a placeholder. Implement actual Surge CLI call here.")
    # 实际实现需要：
    # 1. 使用subprocess调用surge CLI
    # 2. 指定域名
    # 3. 返回部署URL
    return None

def local_preview_server(dir_path, port=8000):
    """启动本地预览服务器"""
    import http.server
    import socketserver
    
    os.chdir(dir_path)
    
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print(f"Serving directory: {dir_path}")
        httpd.serve_forever()

def main(dir_path, output, platform, port):
    # 检查目录
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    # 创建ZIP包
    if output:
        create_zip(dir_path, output)
        print(f"\nDownload your deployment package: {output}")
    
    # 部署到平台
    if platform == 'netlify':
        url = deploy_to_netlify(dir_path, os.getenv('NETLIFY_TOKEN'))
    elif platform == 'vercel':
        url = deploy_to_vercel(dir_path, os.getenv('VERCEL_TOKEN'))
    elif platform == 'surge':
        url = deploy_to_surge(dir_path, os.getenv('SURGE_EMAIL'), os.getenv('SURGE_TOKEN'))
    elif platform == 'local':
        print("\n" + "="*50)
        print("Starting local preview server...")
        print("Press Ctrl+C to stop")
        print("="*50 + "\n")
        local_preview_server(dir_path, port)
        return
    else:
        print("No platform specified. Use --platform to choose deployment target.")
        print("\nStarting local preview server...")
        print("="*50)
        local_preview_server(dir_path, port)
        return
    
    if url:
        print(f"\n🎉 Deployed successfully!")
        print(f"URL: {url}")
    
    print("\n" + "="*50)
    print("Alternative: Download the ZIP and deploy manually")
    print(f"ZIP location: {output}")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy web onepage")
    parser.add_argument('--dir', type=str, required=True, help='Directory to deploy')
    parser.add_argument('--output', type=str, default="./output/deploy.zip", help='Output ZIP file path')
    parser.add_argument('--platform', type=str, choices=['netlify', 'vercel', 'surge', 'local'], help='Deployment platform')
    parser.add_argument('--port', type=int, default=8000, help='Local server port')
    
    args = parser.parse_args()
    main(
        dir_path=args.dir,
        output=args.output,
        platform=args.platform,
        port=args.port
    )

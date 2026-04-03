#!/usr/bin/env python3
import argparse
import os
import json

def create_html_template(theme, style='default', animation='default'):
    """根据主题、风格和动效创建HTML模板"""
    base_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {
            font-family: 'Noto Sans SC', sans-serif;
            background-color: #f5f5f5;
        }
        {{style_css}}
        {{animation_css}}
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <div class="{{container_class}} p-6 md:p-8">
            <h1 class="{{title_class}}">{{title}}</h1>
            <div id="content"></div>
        </div>
    </div>
    <script src="render.js"></script>
</body>
</html>
'''

    styles = {
        'report': {
            'style_css': '''
        .card { background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; }
        .section { border-bottom: 1px solid #e5e7eb; }
        .section:last-child { border-bottom: none; }
        .step { background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; }
        .cta { background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 500; }
        .card-title { color: #1e40af; }
        ''',
            'container_class': 'card',
            'title_class': 'text-3xl md:text-4xl font-bold mb-8 text-center text-blue-600'
        },
        'tutorial': {
            'style_css': '''
        .card { background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 4px solid #10b981; }
        .section { border-bottom: 1px solid #e5e7eb; }
        .section:last-child { border-bottom: none; }
        .step { background-color: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; margin: 1rem 0; }
        .cta { background: #10b981; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 500; }
        pre { background-color: #f3f4f6; padding: 1rem; border-radius: 4px; overflow-x: auto; }
        code { font-family: 'Courier New', monospace; }
        ''',
            'container_class': 'card',
            'title_class': 'text-3xl md:text-4xl font-bold mb-8 text-center text-green-600'
        },
        'promotion': {
            'style_css': '''
        .poster { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); color: white; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .section { border-bottom: 1px solid rgba(255,255,255,0.2); }
        .section:last-child { border-bottom: none; }
        .highlight { background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 4px; font-weight: bold; }
        .cta { background: white; color: #ef4444; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 500; }
        ''',
            'container_class': 'poster',
            'title_class': 'text-3xl md:text-4xl font-bold mb-8 text-center text-white'
        },
        'project': {
            'style_css': '''
        .card { background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #8b5cf6; }
        .section { border-bottom: 1px solid #e5e7eb; }
        .section:last-child { border-bottom: none; }
        .timeline-item { border-left: 2px solid #8b5cf6; padding-left: 1.5rem; position: relative; }
        .timeline-item::before { content: ''; position: absolute; left: -5px; top: 0; width: 8px; height: 8px; background: #8b5cf6; border-radius: 50%; }
        .cta { background: #8b5cf6; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 500; }
        ''',
            'container_class': 'card',
            'title_class': 'text-3xl md:text-4xl font-bold mb-8 text-center text-purple-600'
        },
        'default': {
            'style_css': '''
        .card { background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .section { border-bottom: 1px solid #e5e7eb; }
        .section:last-child { border-bottom: none; }
        .cta { background: #6b7280; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 500; }
        ''',
            'container_class': 'card',
            'title_class': 'text-3xl md:text-4xl font-bold mb-8 text-center text-gray-800'
        }
    }

    animations = {
        'minimal': '''
        .fade-in { opacity: 0; transform: translateY(20px); transition: opacity 0.3s ease-out, transform 0.3s ease-out; }
        .fade-in.visible { opacity: 1; transform: translateY(0); }
        .card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        ''',
        'stagger': '''
        .fade-in { opacity: 0; transform: translateY(20px); transition: opacity 0.4s ease-out, transform 0.4s ease-out; }
        .fade-in.visible { opacity: 1; transform: translateY(0); }
        .stagger-item { opacity: 0; transform: translateX(-10px); transition: opacity 0.3s ease-out, transform 0.3s ease-out; }
        .stagger-item.visible { opacity: 1; transform: translateX(0); }
        .card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        ''',
        'poster': '''
        .fade-in { opacity: 0; transform: scale(0.95); transition: opacity 0.5s ease-out, transform 0.5s ease-out; }
        .fade-in.visible { opacity: 1; transform: scale(1); }
        .card-hover { transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .card-hover:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
        .pulse-once { animation: pulse 0.6s ease-out 1; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
        ''',
        'default': '''
        .fade-in { opacity: 0; transform: translateY(20px); transition: opacity 0.3s ease-out, transform 0.3s ease-out; }
        .fade-in.visible { opacity: 1; transform: translateY(0); }
        .card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        '''
    }

    if theme == 'poster':
        style_config = styles['promotion']
        animation_config = animations['poster']
    elif style == 'report':
        style_config = styles['report']
        animation_config = animations['minimal']
    elif style == 'tutorial':
        style_config = styles['tutorial']
        animation_config = animations['stagger']
    elif style == 'project':
        style_config = styles['project']
        animation_config = animations['stagger']
    else:
        style_config = styles.get(style, styles['default'])
        animation_config = animations.get(animation, animations['default'])

    html = base_template.replace('{{style_css}}', style_config['style_css'])
    html = html.replace('{{animation_css}}', animation_config)
    html = html.replace('{{container_class}}', style_config['container_class'])
    html = html.replace('{{title_class}}', style_config['title_class'])

    return html

def create_render_js(animation='default'):
    """创建渲染脚本，包含动效"""
    if animation == 'stagger':
        render_js = '''
// 加载数据
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        renderContent(data);
        initAnimation();
    })
    .catch(error => console.error('Error loading data:', error));

function renderContent(data) {
    const contentDiv = document.getElementById('content');

    // 按顺序渲染章节（结论优先）
    const entries = Object.entries(data.sections);
    entries.forEach(([sectionTitle, sectionContent], index) => {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section mb-8 pb-6 fade-in';

        const sectionHeader = document.createElement('h2');
        sectionHeader.className = 'text-xl md:text-2xl font-semibold mb-4';
        sectionHeader.textContent = sectionTitle;
        sectionDiv.appendChild(sectionHeader);

        if (typeof sectionContent === 'object') {
            const cardsContainer = document.createElement('div');
            cardsContainer.className = 'grid gap-4';

            Object.entries(sectionContent).forEach(([subTitle, subContent], cardIndex) => {
                const card = document.createElement('div');
                card.className = 'stagger-item card-hover p-4 rounded-lg bg-gray-50';

                const cardTitle = document.createElement('h3');
                cardTitle.className = 'text-lg font-medium mb-2';
                cardTitle.textContent = subTitle;
                card.appendChild(cardTitle);

                const cardText = document.createElement('div');
                cardText.className = 'text-sm leading-relaxed text-gray-600';
                cardText.innerHTML = markdownToHtml(subContent);
                card.appendChild(cardText);

                cardsContainer.appendChild(card);

                // 卡片错位出现
                setTimeout(() => {
                    card.classList.add('visible');
                }, 100 + cardIndex * 80);
            });

            sectionDiv.appendChild(cardsContainer);
        } else {
            const sectionText = document.createElement('div');
            sectionText.className = 'text-sm leading-relaxed';
            sectionText.innerHTML = markdownToHtml(sectionContent);
            sectionDiv.appendChild(sectionText);
        }

        contentDiv.appendChild(sectionDiv);
    });
}

function initAnimation() {
    // 滚动渐入动画
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}
'''
    elif animation == 'poster':
        render_js = '''
// 加载数据
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        renderContent(data);
        initAnimation();
    })
    .catch(error => console.error('Error loading data:', error));

function renderContent(data) {
    const contentDiv = document.getElementById('content');

    const entries = Object.entries(data.sections);
    entries.forEach(([sectionTitle, sectionContent], index) => {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section mb-8 pb-6 fade-in';

        const sectionHeader = document.createElement('h2');
        sectionHeader.className = 'text-xl md:text-2xl font-semibold mb-4';
        sectionHeader.textContent = sectionTitle;
        sectionDiv.appendChild(sectionHeader);

        if (typeof sectionContent === 'object') {
            Object.entries(sectionContent).forEach(([subTitle, subContent]) => {
                const subDiv = document.createElement('div');
                subDiv.className = 'mb-4 p-4 rounded-lg bg-white/10';

                const subHeader = document.createElement('h3');
                subHeader.className = 'text-lg font-medium mb-2';
                subHeader.textContent = subTitle;
                subDiv.appendChild(subHeader);

                const subText = document.createElement('div');
                subText.className = 'text-sm leading-relaxed';
                subText.innerHTML = markdownToHtml(subContent);
                subDiv.appendChild(subText);

                sectionDiv.appendChild(subDiv);
            });
        } else {
            const sectionText = document.createElement('div');
            sectionText.className = 'text-sm leading-relaxed';
            sectionText.innerHTML = markdownToHtml(sectionContent);
            sectionDiv.appendChild(sectionText);
        }

        contentDiv.appendChild(sectionDiv);
    });

    // 标题动画
    const title = document.querySelector('h1');
    if (title) {
        title.classList.add('pulse-once');
    }
}

function initAnimation() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}
'''
    else:  # minimal or default
        render_js = '''
// 加载数据
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        renderContent(data);
        initAnimation();
    })
    .catch(error => console.error('Error loading data:', error));

function renderContent(data) {
    const contentDiv = document.getElementById('content');

    const entries = Object.entries(data.sections);
    entries.forEach(([sectionTitle, sectionContent]) => {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section mb-8 pb-6 fade-in';

        const sectionHeader = document.createElement('h2');
        sectionHeader.className = 'text-xl md:text-2xl font-semibold mb-4';
        sectionHeader.textContent = sectionTitle;
        sectionDiv.appendChild(sectionHeader);

        if (typeof sectionContent === 'object') {
            Object.entries(sectionContent).forEach(([subTitle, subContent]) => {
                const subDiv = document.createElement('div');
                subDiv.className = 'card-hover mb-4 p-4 rounded-lg';

                const subHeader = document.createElement('h3');
                subHeader.className = 'text-lg font-medium mb-2';
                subHeader.textContent = subTitle;
                subDiv.appendChild(subHeader);

                const subText = document.createElement('div');
                subText.className = 'text-sm leading-relaxed text-gray-600';
                subText.innerHTML = markdownToHtml(subContent);
                subDiv.appendChild(subText);

                sectionDiv.appendChild(subDiv);
            });
        } else {
            const sectionText = document.createElement('div');
            sectionText.className = 'text-sm leading-relaxed';
            sectionText.innerHTML = markdownToHtml(sectionContent);
            sectionDiv.appendChild(sectionText);
        }

        contentDiv.appendChild(sectionDiv);
    });
}

function initAnimation() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}
'''

    render_js += '''
function markdownToHtml(markdown) {
    return markdown
        .replace(/\\n/g, '<br>')
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/\\[(.*?)\\]\\((.*?)\\)/g, '<a href="$2" target="_blank">$1</a>');
}
'''

    return render_js

def main(data, outdir, theme='light', style='default', animation='default'):
    if not os.path.exists(data):
        raise FileNotFoundError(f"Data file {data} not found")

    with open(data, 'r', encoding='utf-8') as f:
        data_json = json.load(f)

    os.makedirs(outdir, exist_ok=True)

    import shutil
    dest_data = os.path.join(outdir, 'data.json')
    if data != dest_data:
        shutil.copy(data, dest_data)

    html_template = create_html_template(theme, style, animation)
    html_content = html_template.replace("{{title}}", data_json.get('title', ''))

    with open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

    render_js = create_render_js(animation)

    with open(os.path.join(outdir, 'render.js'), 'w', encoding='utf-8') as f:
        f.write(render_js)

    print(f"Web onepage built successfully in: {outdir}")
    print(f"Style: {style}, Animation: {animation}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build web version of Onepage")
    parser.add_argument('--data', type=str, required=True, help='Path to data JSON file')
    parser.add_argument('--outdir', type=str, default="./output", help='Output directory')
    parser.add_argument('--theme', type=str, default="light", choices=['light', 'poster'], help='Theme')
    parser.add_argument('--style', type=str, default="default", choices=['report', 'tutorial', 'promotion', 'project', 'default'], help='Visual style')
    parser.add_argument('--animation', type=str, default="default", choices=['minimal', 'stagger', 'poster', 'default'], help='Animation style')

    args = parser.parse_args()
    main(
        data=args.data,
        outdir=args.outdir,
        theme=args.theme,
        style=args.style,
        animation=args.animation
    )

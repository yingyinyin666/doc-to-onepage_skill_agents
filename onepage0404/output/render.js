
// 加载数据
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        renderContent(data);
    })
    .catch(error => console.error('Error loading data:', error));

function renderContent(data) {
    const contentDiv = document.getElementById('content');
    
    // 渲染章节
    for (const [sectionTitle, sectionContent] of Object.entries(data.sections)) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section mb-8 pb-6';
        
        // 章节标题
        const sectionHeader = document.createElement('h2');
        sectionHeader.className = 'text-xl md:text-2xl font-semibold mb-4';
        sectionHeader.textContent = sectionTitle;
        sectionDiv.appendChild(sectionHeader);
        
        // 渲染子章节或内容
        if (typeof sectionContent === 'object') {
            for (const [subsectionTitle, subsectionContent] of Object.entries(sectionContent)) {
                const subsectionDiv = document.createElement('div');
                subsectionDiv.className = 'ml-4 mb-4';
                
                const subsectionHeader = document.createElement('h3');
                subsectionHeader.className = 'text-lg font-medium mb-2';
                subsectionHeader.textContent = subsectionTitle;
                subsectionDiv.appendChild(subsectionHeader);
                
                const subsectionText = document.createElement('div');
                subsectionText.className = 'text-sm leading-relaxed';
                subsectionText.innerHTML = markdownToHtml(subsectionContent);
                subsectionDiv.appendChild(subsectionText);
                
                sectionDiv.appendChild(subsectionDiv);
            }
        } else {
            const sectionText = document.createElement('div');
            sectionText.className = 'text-sm leading-relaxed';
            sectionText.innerHTML = markdownToHtml(sectionContent);
            sectionDiv.appendChild(sectionText);
        }
        
        contentDiv.appendChild(sectionDiv);
    }
}

function markdownToHtml(markdown) {
    // 简单的Markdown转换
    return markdown
        .replace(/
/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
}


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

function markdownToHtml(markdown) {
    if (!markdown) return '';
    return markdown
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
}

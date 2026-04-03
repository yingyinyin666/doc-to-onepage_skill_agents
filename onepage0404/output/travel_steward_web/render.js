
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

function markdownToHtml(markdown) {
    return markdown
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
}

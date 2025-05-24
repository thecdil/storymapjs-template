// Thêm vào cuối file JavaScript có sẵn
(function() {
    'use strict';
    
    function addAgentCAttribution() {
        // Đợi StoryMapJS load xong
        setTimeout(function() {
            const attribution = document.querySelector('.leaflet-control-attribution');
            
            if (attribution && !document.querySelector('.agentc-link')) {
                // Tạo link AgentC
                const agentcLink = document.createElement('a');
                agentcLink.href = 'https://agentc.asia/';
                agentcLink.target = '_blank';
                agentcLink.className = 'agentc-link';
                agentcLink.style.textDecoration = 'none';
                agentcLink.style.color = 'inherit';
                
                // Tạo logo
                const logo = document.createElement('img');
                logo.src = 'https://agentc.asia/wp-content/uploads/2020/12/logo-agentc-asia-color-1024x179.png';
                logo.alt = 'AgentC Asia';
                logo.style.height = '14px';
                logo.style.verticalAlign = 'middle';
                logo.style.marginRight = '4px';
                
                // Tạo text
                const text = document.createTextNode('AgentC Asia');
                
                // Ghép lại
                agentcLink.appendChild(logo);
                agentcLink.appendChild(text);
                
                // Thêm separator
                const separator = document.createTextNode(' | ');
                
                // Insert vào attribution
                attribution.insertBefore(agentcLink, attribution.firstChild);
                attribution.insertBefore(separator, agentcLink.nextSibling);
                
                console.log('AgentC Asia link added');
            }
        }, 1000); // Đợi 1 giây để StoryMapJS load xong
    }
    
    // Chạy khi DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addAgentCAttribution);
    } else {
        addAgentCAttribution();
    }
})();

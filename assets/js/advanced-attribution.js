// File: assets/js/advanced-attribution.js
(function() {
    'use strict';
    
    function addAgentCAttribution() {
        const attribution = document.querySelector('.leaflet-control-attribution');
        
        if (attribution && !attribution.querySelector('.agentc-brand')) {
            // Ẩn StoryMapJS brand
            const storyMapBrand = attribution.querySelector('a[href*="storymap.knightlab.com"]');
            if (storyMapBrand) {
                storyMapBrand.style.display = 'none';
            }
            
            // Tạo AgentC brand
            const agentcBrand = document.createElement('a');
            agentcBrand.href = 'https://agentc.asia/';
            agentcBrand.target = '_blank';
            agentcBrand.className = 'agentc-brand';
            agentcBrand.style.cssText = `
                text-decoration: none;
                color: #0078A8;
                font-weight: normal;
                display: inline-flex;
                align-items: center;
                margin-right: 4px;
            `;
            
            agentcBrand.innerHTML = `
                <img src="https://agentc.asia/wp-content/uploads/2020/12/logo-agentc-asia-color-1024x179.png" 
                     alt="AgentC Asia" 
                     style="height: 14px; margin-right: 4px;">
                AgentC Asia
            `;
            
            // Thêm hover effect
            agentcBrand.addEventListener('mouseenter', function() {
                this.style.opacity = '0.8';
            });
            
            agentcBrand.addEventListener('mouseleave', function() {
                this.style.opacity = '1';
            });
            
            // Insert vào attribution
            attribution.insertBefore(agentcBrand, attribution.firstChild);
            attribution.insertBefore(document.createTextNode(' | '), agentcBrand.nextSibling);
            
            return true;
        }
        return false;
    }
    
    // Sử dụng MutationObserver để theo dõi thay đổi DOM
    function observeAttributionChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    const attribution = document.querySelector('.leaflet-control-attribution');
                    if (attribution && !attribution.querySelector('.agentc-brand')) {
                        if (addAgentCAttribution()) {
                            observer.disconnect(); // Dừng observe khi đã thêm thành công
                        }
                    }
                }
            });
        });
        
        // Bắt đầu observe
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Timeout sau 15 giây
        setTimeout(function() {
            observer.disconnect();
        }, 15000);
    }
    
    // Khởi chạy
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(observeAttributionChanges, 100);
        });
    } else {
        setTimeout(observeAttributionChanges, 100);
    }
})();

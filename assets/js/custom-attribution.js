// Chờ DOM load xong
document.addEventListener('DOMContentLoaded', function() {
    // Tìm element attribution
    const attribution = document.querySelector('.leaflet-control-attribution');
    
    if (attribution) {
        // Tạo wrapper cho AgentC Asia
        const agentcWrapper = document.createElement('span');
        agentcWrapper.className = 'agentc-attribution-wrapper';
        agentcWrapper.style.cursor = 'pointer';
        agentcWrapper.style.display = 'inline-block';
        
        // Thêm event listener cho click
        agentcWrapper.addEventListener('click', function(e) {
            e.preventDefault();
            window.open('https://agentc.asia/', '_blank');
        });
        
        // Insert vào đầu attribution
        attribution.insertBefore(agentcWrapper, attribution.firstChild);
        
        console.log('AgentC Asia attribution added successfully');
    }
});

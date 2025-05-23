// Thêm vào file JS custom để tạo link clickable
document.addEventListener('DOMContentLoaded', function() {
    const attribution = document.querySelector('.leaflet-control-attribution');
    if (attribution) {
        // Thêm event listener cho click
        attribution.addEventListener('click', function(e) {
            // Kiểm tra nếu click vào vùng logo/text AgentC Asia
            const rect = attribution.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            
            // Nếu click vào 120px đầu tiên (vùng logo + text)
            if (clickX <= 120) {
                window.open('https://agentc.asia/', '_blank');
                e.preventDefault();
            }
        });
        
        // Thêm style cursor cho toàn bộ vùng clickable
        attribution.style.cursor = 'pointer';
    }
});

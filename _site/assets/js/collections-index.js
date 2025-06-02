document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const sortSelect = document.getElementById('sortSelect');
    const collectionsGrid = document.getElementById('collectionsGrid');
    const collectionItems = document.querySelectorAll('.collection-card-wrapper');
    const visibleCount = document.getElementById('visibleCount');
    const noResults = document.getElementById('noResults');

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterAndSort();
        }, 300));
    }

    // Category filter
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterAndSort();
        });
    }

    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            filterAndSort();
        });
    }

    function filterAndSort() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const selectedCategory = categoryFilter ? categoryFilter.value.toLowerCase() : '';
        const sortBy = sortSelect ? sortSelect.value : 'date';

        // Filter items
        const filteredItems = Array.from(collectionItems).filter(item => {
            const title = item.getAttribute('data-title');
            const category = item.getAttribute('data-category');

            const matchesSearch = !searchTerm || title.includes(searchTerm);
            const matchesCategory = !selectedCategory || category.replace(/"/g, '') === selectedCategory;

            return matchesSearch && matchesCategory;
        });

        // Sort items
        filteredItems.sort((a, b) => {
            switch (sortBy) {
                case 'title':
                    return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
                case 'category':
                    return a.getAttribute('data-category').localeCompare(b.getAttribute('data-category'));
                case 'stories':
                    return parseInt(b.getAttribute('data-stories')) - parseInt(a.getAttribute('data-stories'));
                case 'date':
                default:
                    return parseInt(b.getAttribute('data-date')) - parseInt(a.getAttribute('data-date'));
            }
        });

        // Hide all items first
        collectionItems.forEach(item => {
            item.style.display = 'none';
        });

        // Show filtered and sorted items
        filteredItems.forEach(item => {
            item.style.display = 'block';
            collectionsGrid.appendChild(item); // Re-append to maintain order
        });

       // Update counter
        if (visibleCount) {
            if (filteredItems) {
                visibleCount.textContent = filteredItems.length;
            }
        }

        // Show/hide no results message
        if (noResults) {
            noResults.style.display = filteredItems.length === 0 ? 'block' : 'none';
        }
        if (collectionsGrid) {
            collectionsGrid.style.display = filteredItems.length === 0 ? 'none' : 'grid';
        }
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Card hover effects
    const cards = document.querySelectorAll('.collection-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Initial sort
    filterAndSort();
});

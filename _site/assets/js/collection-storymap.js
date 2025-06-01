document.addEventListener('DOMContentLoaded', function() {
  const storiesGrid = document.getElementById('storiesGrid');
  const storyItems = document.querySelectorAll('.story-extended-item');

  const searchInput = document.getElementById('searchInput');
  const categoryFilter = document.getElementById('categoryFilter');
  const sortSelect = document.getElementById('sortSelect');
  const visibleCountSpan = document.getElementById('visibleCount');

  function updateVisibleCount() {
    let visibleCount = 0;
    storyItems.forEach(item => {
      if (item.style.display !== 'none') {
        visibleCount++;
      }
    });
    visibleCountSpan.textContent = visibleCount;
  }

  function filterStories() {
    const searchTerm = searchInput.value.toLowerCase();
    const category = categoryFilter.value;

    storyItems.forEach(item => {
      const title = item.dataset.title.toLowerCase();
      const itemCategory = item.dataset.category;

      const matchesSearch = title.includes(searchTerm);
      const matchesCategory = category === '' || itemCategory === category;

      if (matchesSearch && matchesCategory) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
    updateVisibleCount();
  }

  searchInput.addEventListener('input', filterStories);
  categoryFilter.addEventListener('change', filterStories);

  sortSelect.addEventListener('change', function() {
    const sortBy = this.value;

    let sortedStories = Array.from(storyItems);

    switch (sortBy) {
      case 'title':
        sortedStories.sort((a, b) => {
          const titleA = a.querySelector('.story-title').textContent.toUpperCase();
          const titleB = b.querySelector('.story-title').textContent.toUpperCase();
          return titleA.localeCompare(titleB);
        });
        break;
      case 'category':
        sortedStories.sort((a, b) => {
          const categoryA = a.dataset.category.toUpperCase();
          const categoryB = b.dataset.category.toUpperCase();
          return categoryA.localeCompare(categoryB);
        });
        break;
      case 'featured':
        sortedStories.sort((a, b) => {
          const featuredA = a.dataset.featured === 'true' ? -1 : 1;
          const featuredB = b.dataset.featured === 'true' ? -1 : 1;
          return featuredA - featuredB;
        });
        break;
      case 'date':
        sortedStories.sort((a, b) => {
          const dateA = a.dataset.date;
          const dateB = b.dataset.date;
          return dateB.localeCompare(dateA);
        });
        break;
      default:
        // Default order - no sorting needed
        break;
    }

    // Remove existing stories from the grid
    storiesGrid.innerHTML = '';

    // Append sorted stories to the grid
    sortedStories.forEach(story => storiesGrid.appendChild(story));
    updateVisibleCount();
  });

  updateVisibleCount();
});

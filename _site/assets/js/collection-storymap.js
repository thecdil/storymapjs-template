document.addEventListener('DOMContentLoaded', function() {
  const storiesGrid = document.getElementById('storiesGrid');
  const storyItems = document.querySelectorAll('.story-extended-item');

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

  categoryFilter.addEventListener('change', function() {
    const filter = this.value;

    storyItems.forEach(item => {
      if (filter === '' || item.dataset.category === filter) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
    updateVisibleCount();
  });

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

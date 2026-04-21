const productsGrid = document.querySelector('.products-grid');
const paginationBlock = document.querySelector('.pagination');
const searchInput = document.querySelector('.products-controls input[type="text"]');

// 👇 ԱՅՍ ՄԱՍԸ ՆՈՐ
const productsPageState = {
  selectedCategoryId: null,
};

window.productsPageState = productsPageState;
// 👆 ԱՅՍ ՄԱՍԸ ՆՈՐ


function escapeHtml(text) {
  if (typeof text !== 'string') return String(text || '');

  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderProducts(products) {
  if (!productsGrid) return;

  if (!Array.isArray(products) || !products.length) {
    productsGrid.innerHTML = `
      <p class="products-empty">Ապրանքներ չեն գտնվել։</p>
    `;
    return;
  }

  productsGrid.innerHTML = products.map(product => `
    <a href="${product.detail_url}" class="product-card-link">
      <div class="product-card">
        <div class="product-image">
          <img src="${product.image_url}" alt="${escapeHtml(product.name)}">
        </div>

        <div class="product-info">
          <h4>${escapeHtml(product.name)}</h4>
          <span class="more-btn">Ավելին</span>
        </div>
      </div>
    </a>
  `).join('');
}

function setPaginationVisible(isVisible) {
  if (!paginationBlock) return;
  paginationBlock.style.display = isVisible ? '' : 'none';
}

function applyFilteredProducts(response) {
  if (!response || !response.success) return;

  renderProducts(response.products || []);
  setPaginationVisible(false);

  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

function searchProducts() {
  const query = (searchInput?.value || '').trim().toLowerCase();
  const cards = document.querySelectorAll('.product-card-link');

  let visibleCount = 0;

  cards.forEach(card => {
    const title = card.querySelector('.product-info h4')?.textContent?.trim().toLowerCase() || '';
    const isMatch = !query || title.includes(query);

    card.style.display = isMatch ? '' : 'none';

    if (isMatch) {
      visibleCount += 1;
    }
  });

  let emptyBox = document.querySelector('.products-search-empty');

  if (visibleCount === 0) {
    if (!emptyBox) {
      emptyBox = document.createElement('p');
      emptyBox.className = 'products-search-empty';
      emptyBox.textContent = 'Ապրանքներ չեն գտնվել։';
      productsGrid?.appendChild(emptyBox);
    }
  } else if (emptyBox) {
    emptyBox.remove();
  }
}

document.addEventListener('DOMContentLoaded', function () {
  if (searchInput) {
    searchInput.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        searchProducts();
      }
    });
  }

  window.addEventListener('products:category-filtered', function (event) {
    const response = event.detail?.response;

    // 👇 ԱՅՍ ՄԱՍԸ ՆՈՐ (ամենակարևորը)
    const categoryId = event.detail?.categoryId;
    if (categoryId) {
      productsPageState.selectedCategoryId = categoryId;
    }
    // 👆

    applyFilteredProducts(response);

    if (typeof closeFilter === 'function') {
      closeFilter();
    }
  });
});
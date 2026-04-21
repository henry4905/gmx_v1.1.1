const filterRootCategories = document.getElementById('filterRootCategories');
const filterLevelsWizard = document.getElementById('filterLevelsWizard');
const filterLevelsTrack = document.getElementById('filterLevelsTrack');

const filterState = {
  stack: [],
  selectedCategoryId: null,
  selectedCategoryName: '',
  selectedPath: [],
  mode: 'tree',

  draftFilters: {
    brand: '',
    country_of_manufacture: '',
    importer: '',
    status: '',
    price_min: '',
    price_max: '',
    attributes: {},
    custom_attributes: {},
    importer_attributes: {},
  },

  appliedFilters: {
    brand: '',
    country_of_manufacture: '',
    importer: '',
    status: '',
    price_min: '',
    price_max: '',
    attributes: {},
    custom_attributes: {},
    importer_attributes: {},
  },

  lastResponse: null,
};

let isFilterBusy = false;

function createEmptyFilterPayload() {
  return {
    brand: '',
    country_of_manufacture: '',
    importer: '',
    status: '',
    price_min: '',
    price_max: '',
    attributes: {},
    custom_attributes: {},
    importer_attributes: {},
  };
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeDraftState() {
  if (!filterState.draftFilters || typeof filterState.draftFilters !== 'object') {
    filterState.draftFilters = createEmptyFilterPayload();
  }

  filterState.draftFilters.attributes = filterState.draftFilters.attributes || {};
  filterState.draftFilters.custom_attributes = filterState.draftFilters.custom_attributes || {};
  filterState.draftFilters.importer_attributes = filterState.draftFilters.importer_attributes || {};
}

function buildDraftPayload() {
  normalizeDraftState();

  return {
    category: filterState.selectedCategoryId || null,
    brand: filterState.draftFilters.brand || '',
    country_of_manufacture: filterState.draftFilters.country_of_manufacture || '',
    importer: filterState.draftFilters.importer || '',
    status: filterState.draftFilters.status || '',
    price_min: filterState.draftFilters.price_min ?? '',
    price_max: filterState.draftFilters.price_max ?? '',
    attributes: deepClone(filterState.draftFilters.attributes || {}),
    custom_attributes: deepClone(filterState.draftFilters.custom_attributes || {}),
    importer_attributes: deepClone(filterState.draftFilters.importer_attributes || {}),
  };
}

function saveAppliedStateFromDraft() {
  filterState.appliedFilters = deepClone(filterState.draftFilters || createEmptyFilterPayload());

  window.productsPageState = window.productsPageState || {};
  window.productsPageState.selectedCategoryId = filterState.selectedCategoryId;
  window.productsPageState.selectedCategoryName = filterState.selectedCategoryName;
  window.productsPageState.selectedCategoryPath = deepClone(filterState.selectedPath || []);
  window.productsPageState.categoryStack = deepClone(filterState.stack || []);
  window.productsPageState.appliedFilters = deepClone(filterState.appliedFilters);
}

function loadDraftFromAppliedState() {
  window.productsPageState = window.productsPageState || {};

  const applied = window.productsPageState.appliedFilters || createEmptyFilterPayload();
  filterState.appliedFilters = deepClone(applied);
  filterState.draftFilters = deepClone(applied);
  filterState.stack = deepClone(window.productsPageState.categoryStack || []);
}

function clearSingleValue(obj, key) {
  if (!obj || typeof obj !== 'object') return;
  obj[key] = '';
}

function isEmptyRange(value) {
  if (!value || typeof value !== 'object') return true;
  return (value.min === '' || value.min === null || value.min === undefined) &&
         (value.max === '' || value.max === null || value.max === undefined);
}

function formatFilterValue(value) {
  if (value === true) return 'Այո';
  if (value === false) return 'Ոչ';
  if (value === null || value === undefined) return '';
  return String(value);
}

function getOptionNumericRange(values = []) {
  const nums = values
    .map(item => Number(item.value))
    .filter(val => !Number.isNaN(val));

  if (!nums.length) {
    return { min: '', max: '' };
  }

  return {
    min: Math.min(...nums),
    max: Math.max(...nums),
  };
}

function debounce(fn, delay = 350) {
  let timeoutId = null;

  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

function setFilterBusyState(isBusy) {
  isFilterBusy = isBusy;

  const buttons = document.querySelectorAll(
    '.root-category-card, .filter-step-item, .filter-back-btn, .filter-close, .filters-apply-btn, .filters-reset-btn'
  );

  buttons.forEach(button => {
    button.disabled = isBusy;
    button.classList.toggle('is-disabled', isBusy);
  });
}

function openFilter() {
  const overlay = document.getElementById('filterOverlay');
  if (!overlay) return;

  overlay.style.display = 'block';
  document.body.style.overflow = 'hidden';

  const savedCategoryId = window.productsPageState?.selectedCategoryId;
  const savedCategoryName = window.productsPageState?.selectedCategoryName || '';
  const savedCategoryPath = window.productsPageState?.selectedCategoryPath || [];
  const savedStack = window.productsPageState?.categoryStack || [];

  if (savedCategoryId) {
    filterState.selectedCategoryId = savedCategoryId;
    filterState.selectedCategoryName = savedCategoryName;
    filterState.selectedPath = Array.isArray(savedCategoryPath) ? deepClone(savedCategoryPath) : [];
    filterState.stack = Array.isArray(savedStack) ? deepClone(savedStack) : [];
    filterState.mode = 'filters';

    loadDraftFromAppliedState();
    showFiltersMode(filterState.lastResponse);
    refreshFilterPanelPreview();
    return;
  }

  if (filterState.mode === 'filters' && filterState.selectedCategoryId) {
    showFiltersMode(filterState.lastResponse);
    refreshFilterPanelPreview();
    return;
  }

  resetFilterNavigator();
}

function closeFilter() {
  const overlay = document.getElementById('filterOverlay');
  if (!overlay) return;

  overlay.style.display = 'none';
  document.body.style.overflow = '';
}

function resetFilterNavigator() {
  filterState.stack = [];
  filterState.selectedCategoryId = null;
  filterState.selectedCategoryName = '';
  filterState.selectedPath = [];
  filterState.mode = 'tree';
  filterState.lastResponse = null;
  filterState.draftFilters = createEmptyFilterPayload();

  if (filterLevelsTrack) {
    filterLevelsTrack.innerHTML = '';
    filterLevelsTrack.style.transform = 'translateX(0)';
  }

  if (filterRootCategories) {
    filterRootCategories.classList.remove('is-hidden');
    filterRootCategories.style.display = 'block';
  }

  if (filterLevelsWizard) {
    filterLevelsWizard.classList.remove('is-visible');
    filterLevelsWizard.style.display = 'none';
    filterLevelsWizard.setAttribute('aria-hidden', 'true');
  }

  setFilterBusyState(false);
}

async function fetchChildCategories(parentId) {
  const response = await fetch('/products/api/filter/categories/children/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      parent_id: parentId
    })
  });

  let data = {};
  try {
    data = await response.json();
  } catch (error) {
    data = {};
  }

  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch child categories');
  }

  return {
    success: Boolean(data.success),
    categories: Array.isArray(data.categories) ? data.categories : []
  };
}

async function fetchFullFilter(payload) {
  const response = await fetch('/products/api/filter/full/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(payload || {})
  });

  let data = {};
  try {
    data = await response.json();
  } catch (error) {
    data = {};
  }

  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch full filter data');
  }

  return data;
}

async function handleCategorySelection(categoryId, categoryName, categoryPath = []) {
  try {
    setFilterBusyState(true);

    filterState.selectedCategoryId = categoryId;
    filterState.selectedCategoryName = categoryName;
    filterState.selectedPath = Array.isArray(categoryPath) ? categoryPath : [categoryName];
    filterState.mode = 'filters';

    filterState.draftFilters = createEmptyFilterPayload();

    const payload = buildDraftPayload();
    const data = await fetchFullFilter(payload);

    if (!data.success) {
      console.error('Full filter response error:', data.message);
      return;
    }

    filterState.lastResponse = data;
    showFiltersMode(data);
  } catch (error) {
    console.error('Full filter fetch error:', error);
  } finally {
    setFilterBusyState(false);
  }
}

function showWizard() {
  if (!filterRootCategories || !filterLevelsWizard) return;

  filterRootCategories.classList.add('is-hidden');
  filterRootCategories.style.display = 'none';

  filterLevelsWizard.style.display = 'block';
  filterLevelsWizard.setAttribute('aria-hidden', 'false');

  requestAnimationFrame(() => {
    filterLevelsWizard.classList.add('is-visible');
  });
}

function showRootLevel() {
  if (!filterRootCategories || !filterLevelsWizard) return;

  filterLevelsWizard.classList.remove('is-visible');
  filterLevelsWizard.setAttribute('aria-hidden', 'true');

  setTimeout(() => {
    filterLevelsWizard.style.display = 'none';
    filterRootCategories.classList.remove('is-hidden');
    filterRootCategories.style.display = 'block';
  }, 180);
}

function renderSteps() {
  if (!filterLevelsTrack) return;

  filterLevelsTrack.innerHTML = filterState.stack.map((step, index) => {
    const pathText = step.path.join(' / ');

    return `
      <div class="filter-step" data-step-index="${index}">
        <div class="filter-step-card">
          <div class="filter-step-top">
            <div class="filter-step-top-left">
              <button
                type="button"
                class="filter-back-btn"
                data-back-index="${index}"
              >
                <i class="fa-solid fa-arrow-left"></i> Հետ
              </button>

              <h4 class="filter-step-title">${step.level}-րդ մակարդակ</h4>
            </div>

            <div class="filter-step-path">${escapeHtml(pathText)}</div>
          </div>

          <div class="filter-step-grid">
            <button
              type="button"
              class="filter-step-item is-all"
              data-action="all"
              data-step-index="${index}"
              data-category-id="${step.parentId}"
              data-category-name="${escapeHtml(step.parentName)}"
            >
              Բոլորը
            </button>

            ${step.categories.map(category => `
              <button
                type="button"
                class="filter-step-item"
                data-action="child"
                data-step-index="${index}"
                data-category-id="${category.id}"
                data-category-name="${escapeHtml(category.name)}"
              >
                ${escapeHtml(category.name)}
              </button>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }).join('');

  bindStepEvents();
  goToStep(filterState.stack.length - 1);
}

function bindRootEvents() {
  const rootButtons = document.querySelectorAll('.root-category-card');

  rootButtons.forEach(button => {
    button.addEventListener('click', async function () {
      if (isFilterBusy) return;

      const categoryId = this.dataset.categoryId;
      const categoryName = this.dataset.categoryName;

      if (!categoryId || !categoryName) return;

      try {
        setFilterBusyState(true);

        const data = await fetchChildCategories(categoryId);

        showWizard();
        filterState.stack = [];

        if (!data.success || !data.categories.length) {
          filterLevelsTrack.innerHTML = `
            <div class="filter-step">
              <div class="filter-step-card">
                <div class="filter-step-top">
                  <div class="filter-step-top-left">
                    <button type="button" class="filter-back-btn" data-back-root="true">
                      <i class="fa-solid fa-arrow-left"></i> Հետ
                    </button>
                    <h4 class="filter-step-title">1-ին մակարդակ</h4>
                  </div>
                  <div class="filter-step-path">${escapeHtml(categoryName)}</div>
                </div>

                <div class="filter-step-grid">
                  <button
                    type="button"
                    class="filter-step-item is-all"
                    data-action="all-root-only"
                    data-category-id="${categoryId}"
                    data-category-name="${escapeHtml(categoryName)}"
                  >
                    Բոլորը
                  </button>
                </div>
              </div>
            </div>
          `;

          bindFallbackEvents();
          return;
        }

        filterState.stack.push({
          parentId: categoryId,
          parentName: categoryName,
          level: 1,
          path: [categoryName],
          categories: data.categories
        });

        renderSteps();
      } catch (error) {
        console.error('Category fetch error:', error);
      } finally {
        setFilterBusyState(false);
      }
    });
  });
}

function bindFallbackEvents() {
  const backRootBtn = filterLevelsTrack?.querySelector('[data-back-root="true"]');
  if (backRootBtn) {
    backRootBtn.addEventListener('click', function () {
      if (isFilterBusy) return;

      filterState.stack = [];
      filterLevelsTrack.innerHTML = '';
      showRootLevel();
    });
  }

  const allRootOnlyBtn = filterLevelsTrack?.querySelector('[data-action="all-root-only"]');
  if (allRootOnlyBtn) {
    allRootOnlyBtn.addEventListener('click', async function () {
      if (isFilterBusy) return;

      const categoryId = this.dataset.categoryId;
      const categoryName = this.dataset.categoryName;

      await handleCategorySelection(categoryId, categoryName, [categoryName]);
    });
  }
}

function bindStepEvents() {
  const childButtons = filterLevelsTrack.querySelectorAll('[data-action="child"]');
  const allButtons = filterLevelsTrack.querySelectorAll('[data-action="all"]');
  const backButtons = filterLevelsTrack.querySelectorAll('[data-back-index]');

  childButtons.forEach(button => {
    button.addEventListener('click', async function () {
      if (isFilterBusy) return;

      const stepIndex = parseInt(this.dataset.stepIndex, 10);
      const categoryId = this.dataset.categoryId;
      const categoryName = this.dataset.categoryName;

      if (Number.isNaN(stepIndex)) return;

      const currentStep = filterState.stack[stepIndex];
      if (!currentStep) return;

      const nextPath = [...currentStep.path, categoryName];
      const nextLevel = currentStep.level + 1;

      try {
        setFilterBusyState(true);

        const data = await fetchChildCategories(categoryId);

        filterState.stack = filterState.stack.slice(0, stepIndex + 1);

        if (!data.success || !data.categories.length) {
          await handleCategorySelection(categoryId, categoryName, nextPath);
          return;
        }

        filterState.stack.push({
          parentId: categoryId,
          parentName: categoryName,
          level: nextLevel,
          path: nextPath,
          categories: data.categories
        });

        renderSteps();
      } catch (error) {
        console.error('Category fetch error:', error);
      } finally {
        setFilterBusyState(false);
      }
    });
  });

  allButtons.forEach(button => {
    button.addEventListener('click', async function () {
      if (isFilterBusy) return;

      const stepIndex = parseInt(this.dataset.stepIndex, 10);
      const categoryId = this.dataset.categoryId;
      const categoryName = this.dataset.categoryName;

      if (Number.isNaN(stepIndex)) return;

      const currentStep = filterState.stack[stepIndex];
      if (!currentStep) return;

      await handleCategorySelection(categoryId, categoryName, currentStep.path);
    });
  });

  backButtons.forEach(button => {
    button.addEventListener('click', function () {
      if (isFilterBusy) return;

      const backIndex = parseInt(this.dataset.backIndex, 10);
      if (Number.isNaN(backIndex)) return;

      if (backIndex === 0) {
        filterState.stack = [];
        filterLevelsTrack.innerHTML = '';
        showRootLevel();
        return;
      }

      filterState.stack = filterState.stack.slice(0, backIndex);
      renderSteps();
    });
  });
}

function goToStep(stepIndex) {
  if (!filterLevelsTrack) return;

  if (stepIndex < 0) {
    filterLevelsTrack.style.transform = 'translateX(0)';
    return;
  }

  filterLevelsTrack.style.transform = `translateX(-${stepIndex * 100}%)`;
}

function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='));

  return cookieValue ? cookieValue.split('=')[1] : '';
}

function escapeHtml(text) {
  if (typeof text !== 'string') return String(text || '');

  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

document.addEventListener('DOMContentLoaded', function () {
  bindRootEvents();

  const filterCloseBtn = document.getElementById('filterCloseBtn');
  if (filterCloseBtn) {
    filterCloseBtn.addEventListener('click', closeFilter);
  }
});

const debouncedPreviewRefresh = debounce(() => {
  refreshFilterPanelPreview();
}, 350);

async function refreshFilterPanelPreview() {
  try {
    normalizeDraftState();
    setFilterBusyState(true);

    const payload = buildDraftPayload();
    const data = await fetchFullFilter(payload);

    if (!data.success) {
      console.error('Preview filter response error:', data.message);
      return;
    }

    filterState.lastResponse = data;
    renderSelectedFiltersBar(data);
    renderCategoryFilterChain();
    renderStaticFilters(data);
    renderImporterFilters(data);
    renderDynamicFilters(data);
    renderCustomFilters(data);
  } catch (error) {
    console.error('Preview refresh error:', error);
  } finally {
    setFilterBusyState(false);
  }
}

async function applyFiltersToProducts() {
  try {
    normalizeDraftState();
    setFilterBusyState(true);

    const payload = buildDraftPayload();
    const data = await fetchFullFilter(payload);

    if (!data.success) {
      console.error('Apply filter response error:', data.message);
      return;
    }

    filterState.lastResponse = data;
    saveAppliedStateFromDraft();

    window.dispatchEvent(new CustomEvent('products:category-filtered', {
      detail: {
        categoryId: filterState.selectedCategoryId,
        categoryName: filterState.selectedCategoryName,
        categoryPath: deepClone(filterState.selectedPath || []),
        mode: 'filters',
        payload,
        response: data,
      }
    }));

    closeFilter();
  } catch (error) {
    console.error('Apply filters error:', error);
  } finally {
    setFilterBusyState(false);
  }
}

function showFiltersMode(responseData = null) {
  if (!filterRootCategories || !filterLevelsWizard || !filterLevelsTrack) return;

  filterRootCategories.classList.add('is-hidden');
  filterRootCategories.style.display = 'none';

  filterLevelsWizard.style.display = 'block';
  filterLevelsWizard.setAttribute('aria-hidden', 'false');

  requestAnimationFrame(() => {
    filterLevelsWizard.classList.add('is-visible');
  });

  filterLevelsTrack.style.transform = 'translateX(0)';
  filterLevelsTrack.innerHTML = `
    <div class="filters-container" id="filtersContainer">

      <div id="selectedFiltersBar" class="filters-selected-bar"></div>

      <div class="filters-section filters-category-section">
        <button
          type="button"
          class="filters-section-toggle"
          id="categoryFilterToggle"
          aria-expanded="true"
        >
          <span>Կատեգորիա</span>
          <i class="fa-solid fa-chevron-down"></i>
        </button>

        <div class="filters-section-summary" id="categoryFilterSummary"></div>

        <div class="filters-section-body is-open" id="categoryFilterBody">
          <div class="category-filter-chain" id="categoryFilterChain"></div>
        </div>
      </div>

      <div id="filtersStatic" class="filters-block"></div>
      <div id="filtersImporter" class="filters-block"></div>
      <div id="filtersDynamic" class="filters-block"></div>
      <div id="filtersCustom" class="filters-block"></div>

      <div class="filters-actions">
        <button type="button" class="filters-reset-btn" id="filtersResetBtn">
          Մաքրել
        </button>

        <button type="button" class="filters-apply-btn" id="filtersApplyBtn">
          Ֆիլտրել
        </button>
      </div>
    </div>
  `;

  bindCategoryFilterCollapse();
  bindFiltersModeEvents();

  const data = responseData || filterState.lastResponse;
  if (data) {
    filterState.lastResponse = data;
    renderSelectedFiltersBar(data);
    renderCategoryFilterChain();
    renderStaticFilters(data);
    renderImporterFilters(data);
    renderDynamicFilters(data);
    renderCustomFilters(data);
  }
}

function bindFiltersModeEvents() {
  const applyBtn = document.getElementById('filtersApplyBtn');
  const resetBtn = document.getElementById('filtersResetBtn');
  const container = document.getElementById('filtersContainer');

  if (applyBtn) {
    applyBtn.addEventListener('click', async function () {
      if (isFilterBusy) return;
      await applyFiltersToProducts();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', async function () {
      if (isFilterBusy) return;

      filterState.draftFilters = createEmptyFilterPayload();
      await refreshFilterPanelPreview();
    });
  }

  if (!container) return;

  container.addEventListener('click', async function (event) {
    const removeChipBtn = event.target.closest('[data-remove-chip]');
    if (removeChipBtn) {
      if (isFilterBusy) return;

      const chipType = removeChipBtn.dataset.chipType;
      const chipKey = removeChipBtn.dataset.chipKey;
      const chipValue = removeChipBtn.dataset.chipValue;

      await removeSelectedChip(chipType, chipKey, chipValue);
      return;
    }

    const staticBtn = event.target.closest('[data-static-filter-key]');
    if (staticBtn) {
      if (isFilterBusy) return;

      const key = staticBtn.dataset.staticFilterKey;
      const value = staticBtn.dataset.staticFilterValue;
      const isDisabled = staticBtn.hasAttribute('disabled');

      if (isDisabled) return;

      if (filterState.draftFilters[key] === value) {
        filterState.draftFilters[key] = '';
      } else {
        filterState.draftFilters[key] = value;
      }

      await refreshFilterPanelPreview();
      return;
    }

    const boolBtn = event.target.closest('[data-bool-filter-type]');
    if (boolBtn) {
      if (isFilterBusy) return;

      const filterType = boolBtn.dataset.boolFilterType;
      const filterId = boolBtn.dataset.boolFilterId;
      const rawValue = boolBtn.dataset.boolValue;
      const isDisabled = boolBtn.hasAttribute('disabled');

      if (isDisabled) return;

      const value = rawValue === 'true';

      toggleMultiValueFilter(filterType, filterId, value);
      await refreshFilterPanelPreview();
      return;
    }
  });

  container.addEventListener('change', async function (event) {
    const checkbox = event.target.closest('[data-filter-group-type][data-filter-group-id]');
    if (checkbox && checkbox.type === 'checkbox') {
      if (isFilterBusy) return;

      const filterType = checkbox.dataset.filterGroupType;
      const filterId = checkbox.dataset.filterGroupId;
      const value = checkbox.value;

      toggleMultiValueFilter(filterType, filterId, value);
      await refreshFilterPanelPreview();
      return;
    }
  });

  container.addEventListener('input', function (event) {
    const input = event.target;

    if (input.matches('[data-price-input]')) {
      const key = input.dataset.priceInput;
      filterState.draftFilters[key] = input.value;
      debouncedPreviewRefresh();
      return;
    }

    if (input.matches('[data-range-filter-type][data-range-filter-id]')) {
      const filterType = input.dataset.rangeFilterType;
      const filterId = input.dataset.rangeFilterId;
      const rangeKey = input.dataset.rangeKey;

      ensureRangeObject(filterType, filterId);
      getRangeContainer(filterType)[filterId][rangeKey] = input.value;
      cleanupRangeObject(filterType, filterId);
      debouncedPreviewRefresh();
    }
  });
}

async function removeSelectedChip(chipType, chipKey, chipValue) {
  if (chipType === 'category') {
    filterState.stack = [];
    filterState.selectedCategoryId = null;
    filterState.selectedCategoryName = '';
    filterState.selectedPath = [];
    filterState.mode = 'tree';
    filterState.draftFilters = createEmptyFilterPayload();

    window.productsPageState = window.productsPageState || {};
    window.productsPageState.selectedCategoryId = null;
    window.productsPageState.selectedCategoryName = '';
    window.productsPageState.selectedCategoryPath = [];
    window.productsPageState.categoryStack = [];
    window.productsPageState.appliedFilters = createEmptyFilterPayload();

    closeFilter();
    resetFilterNavigator();
    return;
  }

  if (chipType === 'static' || chipType === 'price') {
    clearSingleValue(filterState.draftFilters, chipKey);
    await refreshFilterPanelPreview();
    return;
  }

  if (chipType === 'attributes' || chipType === 'custom_attributes' || chipType === 'importer_attributes') {
    const container = filterState.draftFilters[chipType];

    if (Array.isArray(container?.[chipKey])) {
      container[chipKey] = container[chipKey].filter(item => String(item) !== String(chipValue));
      if (!container[chipKey].length) {
        delete container[chipKey];
      }
    } else {
      delete container[chipKey];
    }

    await refreshFilterPanelPreview();
  }
}

function toggleMultiValueFilter(filterType, filterId, value) {
  const container = getTypeContainer(filterType);
  if (!container) return;

  let current = container[filterId];

  if (!Array.isArray(current)) {
    current = [];
  }

  const exists = current.some(item => String(item) === String(value));

  if (exists) {
    current = current.filter(item => String(item) !== String(value));
  } else {
    current.push(value);
  }

  if (!current.length) {
    delete container[filterId];
  } else {
    container[filterId] = current;
  }
}

function getTypeContainer(filterType) {
  if (filterType === 'attributes') return filterState.draftFilters.attributes;
  if (filterType === 'custom_attributes') return filterState.draftFilters.custom_attributes;
  if (filterType === 'importer_attributes') return filterState.draftFilters.importer_attributes;
  return null;
}

function getRangeContainer(filterType) {
  if (filterType === 'attributes') return filterState.draftFilters.attributes;
  if (filterType === 'custom_attributes') return filterState.draftFilters.custom_attributes;
  if (filterType === 'importer_attributes') return filterState.draftFilters.importer_attributes;
  return {};
}

function ensureRangeObject(filterType, filterId) {
  const container = getRangeContainer(filterType);
  if (!container[filterId] || Array.isArray(container[filterId]) || typeof container[filterId] !== 'object') {
    container[filterId] = { min: '', max: '' };
  }
}

function cleanupRangeObject(filterType, filterId) {
  const container = getRangeContainer(filterType);
  if (isEmptyRange(container[filterId])) {
    delete container[filterId];
  }
}

function renderSelectedFiltersBar(responseData = null) {
  const bar = document.getElementById('selectedFiltersBar');
  if (!bar) return;

  const chips = [];

  if (filterState.selectedCategoryId && filterState.selectedPath?.length) {
    chips.push(`
      <button
        type="button"
        class="selected-filter-chip selected-filter-chip--category"
        data-remove-chip="true"
        data-chip-type="category"
        data-chip-key="category"
      >
        <span>${escapeHtml(filterState.selectedPath.join(' / '))}</span>
        <i class="fa-solid fa-xmark"></i>
      </button>
    `);
  }

  if (filterState.draftFilters.price_min !== '' && filterState.draftFilters.price_min !== null && filterState.draftFilters.price_min !== undefined) {
    chips.push(`
      <button
        type="button"
        class="selected-filter-chip"
        data-remove-chip="true"
        data-chip-type="price"
        data-chip-key="price_min"
      >
        <span>Գին սկսած՝ ${escapeHtml(String(filterState.draftFilters.price_min))}</span>
        <i class="fa-solid fa-xmark"></i>
      </button>
    `);
  }

  if (filterState.draftFilters.price_max !== '' && filterState.draftFilters.price_max !== null && filterState.draftFilters.price_max !== undefined) {
    chips.push(`
      <button
        type="button"
        class="selected-filter-chip"
        data-remove-chip="true"
        data-chip-type="price"
        data-chip-key="price_max"
      >
        <span>Գին մինչև՝ ${escapeHtml(String(filterState.draftFilters.price_max))}</span>
        <i class="fa-solid fa-xmark"></i>
      </button>
    `);
  }

  collectStaticChips(chips, responseData);
  collectNestedChips(chips, responseData, 'attributes', 'attributes');
  collectNestedChips(chips, responseData, 'custom_attributes', 'custom_attributes');
  collectNestedChips(chips, responseData, 'importer_attributes', 'importer_attributes');

  bar.innerHTML = chips.length
    ? chips.join('')
    : `<div class="filters-selected-empty">Ընտրված ֆիլտրեր դեռ չկան</div>`;
}

function collectStaticChips(chips, responseData) {
  const options = responseData?.filter_options || {};

  const staticMaps = [
    ['brand', options.brands || []],
    ['country_of_manufacture', options.countries || []],
    ['importer', options.importers || []],
    ['status', options.statuses || []],
  ];

  staticMaps.forEach(([key, list]) => {
    const currentValue = filterState.draftFilters[key];
    if (!currentValue) return;

    const found = list.find(item =>
      String(item.id || item.value) === String(currentValue)
    );

    const label = found?.name || found?.label || currentValue;

    chips.push(`
      <button
        type="button"
        class="selected-filter-chip"
        data-remove-chip="true"
        data-chip-type="static"
        data-chip-key="${key}"
      >
        <span>${escapeHtml(String(label))}</span>
        <i class="fa-solid fa-xmark"></i>
      </button>
    `);
  });
}

function collectNestedChips(chips, responseData, stateKey, responseKey) {
  const selectedMap = filterState.draftFilters[stateKey] || {};
  const options = responseData?.filter_options?.[responseKey] || [];

  Object.entries(selectedMap).forEach(([filterId, rawValue]) => {
    const optionMeta = options.find(item => String(item.id) === String(filterId));
    const optionName = optionMeta?.name || filterId;

    if (Array.isArray(rawValue)) {
      rawValue.forEach(value => {
        chips.push(`
          <button
            type="button"
            class="selected-filter-chip"
            data-remove-chip="true"
            data-chip-type="${stateKey}"
            data-chip-key="${filterId}"
            data-chip-value="${escapeHtml(String(value))}"
          >
            <span>${escapeHtml(optionName)}: ${escapeHtml(formatFilterValue(value))}</span>
            <i class="fa-solid fa-xmark"></i>
          </button>
        `);
      });
      return;
    }

    if (rawValue && typeof rawValue === 'object') {
      const hasMin = rawValue.min !== '' && rawValue.min !== null && rawValue.min !== undefined;
      const hasMax = rawValue.max !== '' && rawValue.max !== null && rawValue.max !== undefined;
      const minText = hasMin ? ` ${rawValue.min}` : '';
      const maxText = hasMax ? ` ${rawValue.max}` : '';

      chips.push(`
        <button
          type="button"
          class="selected-filter-chip"
          data-remove-chip="true"
          data-chip-type="${stateKey}"
          data-chip-key="${filterId}"
        >
          <span>${escapeHtml(optionName)}: ${escapeHtml(`սկսած${minText} մինչև${maxText}`)}</span>
          <i class="fa-solid fa-xmark"></i>
        </button>
      `);
    }
  });
}

function renderStaticFilters(responseData) {
  const container = document.getElementById('filtersStatic');
  if (!container) return;

  const options = responseData?.filter_options || {};
  const price = options.price || {};

  container.innerHTML = `
    <div class="filters-section">
      <div class="filters-section-head">
        <h3>Հիմնական ֆիլտրեր</h3>
      </div>

      <div class="filters-section-body static-filters-body is-open">

        <div class="filter-field-block filter-field-block--price">
          <label class="filter-label">Գնի միջակայք</label>

          <div class="price-range-inputs">
            <input
              type="number"
              class="filter-range-input"
              data-price-input="price_min"
              value="${escapeHtml(String(filterState.draftFilters.price_min || ''))}"
              placeholder="${price.min ?? ''}"
            />

            <input
              type="number"
              class="filter-range-input"
              data-price-input="price_max"
              value="${escapeHtml(String(filterState.draftFilters.price_max || ''))}"
              placeholder="${price.max ?? ''}"
            />
          </div>

          <div class="filter-help-text">
            Տվյալ միջակայք՝ ${price.min ?? '—'} - ${price.max ?? '—'}
          </div>
        </div>

        ${renderStaticChoiceGroup('Բրենդ', 'brand', options.brands || [])}
        ${renderStaticChoiceGroup('Արտադրման երկիր', 'country_of_manufacture', options.countries || [])}
        ${renderStaticChoiceGroup('Առկայություն', 'status', options.statuses || [])}
      </div>
    </div>
  `;
}

function renderStaticChoiceGroup(title, key, items) {
  if (!items.length) return '';

  return `
    <div class="filter-field-block">
      <label class="filter-label">${escapeHtml(title)}</label>

      <div class="filter-values-scroll">
        <div class="filter-chip-grid">
          ${items.map(item => {
            const value = item.id ?? item.value;
            const label = item.name ?? item.label ?? value;
            const activeClass = item.active ? '' : ' is-inactive';
            const selectedClass = item.selected ? ' is-selected' : '';

            return `
              <button
                type="button"
                class="filter-chip-btn${activeClass}${selectedClass}"
                data-static-filter-key="${key}"
                data-static-filter-value="${escapeHtml(String(value))}"
                ${item.active ? '' : 'disabled'}
              >
                ${escapeHtml(String(label))}
              </button>
            `;
          }).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderImporterFilters(responseData) {
  const container = document.getElementById('filtersImporter');
  if (!container) return;

  const options = responseData?.filter_options || {};
  const importers = options.importers || [];
  const importerAttributes = options.importer_attributes || [];

  container.innerHTML = `
    <div class="filters-section">
      <div class="filters-section-head">
        <h3>Մատակարար</h3>
      </div>

      <div class="filters-section-body is-open">
        ${renderStaticChoiceGroup('Ընկերություն', 'importer', importers)}
        ${renderDynamicOptionGroups(importerAttributes, 'importer_attributes')}
      </div>
    </div>
  `;
}

function renderDynamicFilters(responseData) {
  const container = document.getElementById('filtersDynamic');
  if (!container) return;

  const attributes = responseData?.filter_options?.attributes || [];

  container.innerHTML = `
    <div class="filters-section">
      <div class="filters-section-head">
        <h3>Դինամիկ պարամետրեր</h3>
      </div>

      <div class="filters-section-body is-open">
        ${renderDynamicOptionGroups(attributes, 'attributes')}
      </div>
    </div>
  `;
}

function renderCustomFilters(responseData) {
  const container = document.getElementById('filtersCustom');
  if (!container) return;

  const attributes = responseData?.filter_options?.custom_attributes || [];

  container.innerHTML = `
    <div class="filters-section">
      <div class="filters-section-head">
        <h3>Լրացուցիչ պարամետրեր</h3>
      </div>

      <div class="filters-section-body is-open">
        ${renderDynamicOptionGroups(attributes, 'custom_attributes')}
      </div>
    </div>
  `;
}

function renderDynamicOptionGroups(groups, filterType) {
  if (!Array.isArray(groups) || !groups.length) {
    return `<div class="filters-empty-state">Տվյալ բաժնում ֆիլտրեր չկան</div>`;
  }

  return groups.map(group => {
    const title = group.name || '';
    const subtitle = group.attribute_type || group.parameter_type || '';
    const values = Array.isArray(group.values) ? group.values : [];
    const dataType = group.data_type || group.value_type || 'string';

    if (dataType === 'number') {
      return renderNumberRangeGroup(group, filterType, title, subtitle, values);
    }

    if (dataType === 'boolean') {
      return renderBooleanGroup(group, filterType, title, subtitle, values);
    }

    return renderCheckboxGroup(group, filterType, title, subtitle, values);
  }).join('');
}

function renderCheckboxGroup(group, filterType, title, subtitle, values) {
  return `
    <div class="filter-field-block">
      <label class="filter-label">${escapeHtml(title)}</label>
      ${subtitle ? `<div class="filter-subtitle">${escapeHtml(subtitle)}</div>` : ''}

      <div class="filter-values-scroll">
        <div class="filter-checkbox-list">
          ${values.map(item => `
            <label class="filter-checkbox-item ${item.active ? '' : 'is-inactive'}">
              <input
                type="checkbox"
                value="${escapeHtml(String(item.value))}"
                data-filter-group-type="${filterType}"
                data-filter-group-id="${group.id}"
                ${item.selected ? 'checked' : ''}
                ${item.active ? '' : 'disabled'}
              />
              <span>${escapeHtml(String(item.label || item.value))}</span>
            </label>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderBooleanGroup(group, filterType, title, subtitle, values) {
  return `
    <div class="filter-field-block">
      <label class="filter-label">${escapeHtml(title)}</label>
      ${subtitle ? `<div class="filter-subtitle">${escapeHtml(subtitle)}</div>` : ''}

      <div class="filter-chip-grid">
        ${values.map(item => `
          <button
            type="button"
            class="filter-chip-btn ${item.selected ? 'is-selected' : ''} ${item.active ? '' : 'is-inactive'}"
            data-bool-filter-type="${filterType}"
            data-bool-filter-id="${group.id}"
            data-bool-value="${String(item.value)}"
            ${item.active ? '' : 'disabled'}
          >
            ${escapeHtml(String(item.label || item.value))}
          </button>
        `).join('')}
      </div>
    </div>
  `;
}

function renderNumberRangeGroup(group, filterType, title, subtitle, values) {
  const optionRange = getOptionNumericRange(values);
  const selectedRange = getTypeContainer(filterType)?.[group.id] || {};

  return `
    <div class="filter-field-block">
      <label class="filter-label">${escapeHtml(title)}</label>
      ${subtitle ? `<div class="filter-subtitle">${escapeHtml(subtitle)}</div>` : ''}

      <div class="price-range-inputs">
        <input
          type="number"
          class="filter-range-input"
          data-range-filter-type="${filterType}"
          data-range-filter-id="${group.id}"
          data-range-key="min"
          value="${escapeHtml(String(selectedRange.min || ''))}"
          placeholder="${optionRange.min}"
        />

        <input
          type="number"
          class="filter-range-input"
          data-range-filter-type="${filterType}"
          data-range-filter-id="${group.id}"
          data-range-key="max"
          value="${escapeHtml(String(selectedRange.max || ''))}"
          placeholder="${optionRange.max}"
        />
      </div>
    </div>
  `;
}

function bindCategoryFilterCollapse() {
  const toggle = document.getElementById('categoryFilterToggle');
  const body = document.getElementById('categoryFilterBody');

  if (!toggle || !body) return;

  toggle.addEventListener('click', function () {
    const isOpen = body.classList.contains('is-open');

    body.classList.toggle('is-open', !isOpen);
    toggle.setAttribute('aria-expanded', String(!isOpen));
    toggle.classList.toggle('is-collapsed', isOpen);
  });
}

function renderCategoryFilterChain() {
  const chain = document.getElementById('categoryFilterChain');
  const summary = document.getElementById('categoryFilterSummary');

  if (!chain || !summary) return;

  const selectedPath = Array.isArray(filterState.selectedPath) ? filterState.selectedPath : [];
  summary.textContent = selectedPath.length ? selectedPath.join(' / ') : 'Կատեգորիա ընտրված չէ';

  const levels = filterState.stack || [];

  if (!levels.length) {
    chain.innerHTML = `<div class="filters-empty-state">Կատեգորիայի մակարդակները դեռ հասանելի չեն</div>`;
    return;
  }

  chain.innerHTML = levels.map((step, index) => {
    const currentSelectedId = getSelectedIdForLevel(index);
    const hasAllOption = shouldShowAllOption(step, index);

    return `
      <div class="category-filter-level">
        <label class="category-filter-label">${index + 1}-րդ մակարդակ</label>

        <select
          class="category-filter-select"
          data-category-level-index="${index}"
        >
          ${
            hasAllOption
              ? `<option value="__all__" ${currentSelectedId === '__all__' ? 'selected' : ''}>Բոլորը</option>`
              : ''
          }

          ${step.categories.map(category => `
            <option
              value="${category.id}"
              ${String(currentSelectedId) === String(category.id) ? 'selected' : ''}
            >
              ${escapeHtml(category.name)}
            </option>
          `).join('')}
        </select>
      </div>
    `;
  }).join('');

  bindCategoryChainEvents();
}

function getSelectedIdForLevel(levelIndex) {
  if (!Array.isArray(filterState.stack)) return null;

  const currentStep = filterState.stack[levelIndex];
  if (!currentStep) return null;

  const nextStep = filterState.stack[levelIndex + 1];
  if (nextStep) {
    return String(nextStep.parentId);
  }

  const selectedId = String(filterState.selectedCategoryId || '');
  const parentId = String(currentStep.parentId || '');

  if (selectedId && selectedId === parentId) {
    return '__all__';
  }

  return selectedId || null;
}

function shouldShowAllOption(step, levelIndex) {
  if (!step) return false;

  if (levelIndex === 0 && (!step.categories || step.categories.length <= 1)) {
    return false;
  }

  return true;
}

function bindCategoryChainEvents() {
  const selects = document.querySelectorAll('[data-category-level-index]');

  selects.forEach(select => {
    select.addEventListener('change', async function () {
      if (isFilterBusy) return;

      const levelIndex = parseInt(this.dataset.categoryLevelIndex, 10);
      const value = this.value;

      if (Number.isNaN(levelIndex)) return;

      const currentStep = filterState.stack[levelIndex];
      if (!currentStep) return;

      try {
        setFilterBusyState(true);

        filterState.stack = filterState.stack.slice(0, levelIndex + 1);
        filterState.draftFilters = createEmptyFilterPayload();

        if (value === '__all__') {
          filterState.selectedCategoryId = currentStep.parentId;
          filterState.selectedCategoryName = currentStep.parentName;
          filterState.selectedPath = currentStep.path;
          filterState.mode = 'filters';

          await refreshFilterPanelPreview();
          return;
        }

        const selectedCategory = (currentStep.categories || []).find(
          item => String(item.id) === String(value)
        );

        if (!selectedCategory) return;

        const nextPath = [...currentStep.path, selectedCategory.name];
        const data = await fetchChildCategories(selectedCategory.id);

        filterState.selectedCategoryId = selectedCategory.id;
        filterState.selectedCategoryName = selectedCategory.name;
        filterState.selectedPath = nextPath;
        filterState.mode = 'filters';

        if (data.success && Array.isArray(data.categories) && data.categories.length) {
          filterState.stack.push({
            parentId: selectedCategory.id,
            parentName: selectedCategory.name,
            level: currentStep.level + 1,
            path: nextPath,
            categories: data.categories
          });
        }

        renderCategoryFilterChain();
        await refreshFilterPanelPreview();
      } catch (error) {
        console.error('Category dropdown change error:', error);
      } finally {
        setFilterBusyState(false);
      }
    });
  });
}
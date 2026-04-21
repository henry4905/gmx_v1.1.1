document.addEventListener('DOMContentLoaded', () => {
  const scrollPositionStore = {
    value: 0,
  };

  initSectionTabs();
  initProductMedia(scrollPositionStore);
  initImporterModal(scrollPositionStore);
  initExchangeModal(scrollPositionStore);
});

/* =========================
   BODY SCROLL LOCK
========================= */
function lockBodyScroll(store) {
  if (document.body.classList.contains('modal-open')) return;

  store.value = window.scrollY || window.pageYOffset || 0;
  document.body.classList.add('modal-open');
  document.body.style.position = 'fixed';
  document.body.style.top = `-${store.value}px`;
  document.body.style.left = '0';
  document.body.style.right = '0';
  document.body.style.width = '100%';
}

function unlockBodyScroll(store) {
  if (!document.body.classList.contains('modal-open')) return;

  document.body.classList.remove('modal-open');
  document.body.style.position = '';
  document.body.style.top = '';
  document.body.style.left = '';
  document.body.style.right = '';
  document.body.style.width = '';

  window.scrollTo(0, store.value || 0);
}

/* =========================
   TABS
========================= */
function initSectionTabs() {
  const tabs = Array.from(document.querySelectorAll('.section-tab'));
  const panels = Array.from(document.querySelectorAll('.tab-panel'));

  if (!tabs.length || !panels.length) return;

  function activateTab(tab) {
    const targetId = tab.dataset.tabTarget;
    if (!targetId) return;

    tabs.forEach((item) => {
      item.classList.remove('active');
      item.setAttribute('aria-selected', 'false');
    });

    panels.forEach((panel) => {
      panel.classList.remove('active');
      panel.hidden = true;
    });

    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');

    const targetPanel = document.getElementById(targetId);
    if (targetPanel) {
      targetPanel.classList.add('active');
      targetPanel.hidden = false;
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => activateTab(tab));
  });

  const initiallyActive = document.querySelector('.section-tab.active') || tabs[0];
  activateTab(initiallyActive);
}

/* =========================
   PRODUCT MEDIA + PREVIEW
========================= */
function initProductMedia(scrollPositionStore) {
  const slides = Array.from(document.querySelectorAll('.slide[data-slide-index]'));
  const thumbs = Array.from(document.querySelectorAll('.media-thumb[data-thumb-index]'));
  const prevBtn = document.querySelector('.prev-slide');
  const nextBtn = document.querySelector('.next-slide');
  const currentIndexEl = document.getElementById('mediaCurrentIndex');
  const totalCountEl = document.getElementById('mediaTotalCount');
  const openPreviewBtn = document.getElementById('openMediaPreview');
  const previewTriggers = Array.from(document.querySelectorAll('.media-preview-trigger'));

  const previewModal = document.getElementById('mediaPreviewModal');
  const previewCloseBtn = document.getElementById('closeMediaPreview');
  const previewPrevBtn = document.getElementById('previewPrevBtn');
  const previewNextBtn = document.getElementById('previewNextBtn');
  const previewItems = Array.from(document.querySelectorAll('.media-preview-item[data-preview-index]'));
  const previewCurrentIndexEl = document.getElementById('previewCurrentIndex');
  const previewTotalCountEl = document.getElementById('previewTotalCount');

  if (!slides.length) return;

  let currentIndex = slides.findIndex((slide) => slide.classList.contains('active'));
  if (currentIndex < 0) currentIndex = 0;

  let previewIndex = currentIndex;

  if (totalCountEl) {
    totalCountEl.textContent = String(slides.length);
  }

  if (previewTotalCountEl) {
    previewTotalCountEl.textContent = String(previewItems.length || slides.length);
  }

  function pauseAllInlineVideos() {
    slides.forEach((slide) => {
      const video = slide.querySelector('video');
      if (video && !video.paused) {
        video.pause();
      }
    });
  }

  function pauseAllPreviewVideos() {
    previewItems.forEach((item) => {
      const video = item.querySelector('video');
      if (video) {
        video.pause();
      }
    });
  }

  function updateMainCounter(index) {
    if (currentIndexEl) {
      currentIndexEl.textContent = String(index + 1);
    }
  }

  function updatePreviewCounter(index) {
    if (previewCurrentIndexEl) {
      previewCurrentIndexEl.textContent = String(index + 1);
    }
  }

  function updateThumbs(index) {
    thumbs.forEach((thumb, i) => {
      thumb.classList.toggle('active', i === index);
    });
  }

  function showMainSlide(index) {
    currentIndex = index;

    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });

    pauseAllInlineVideos();
    updateThumbs(index);
    updateMainCounter(index);
  }

  function goToPrevSlide() {
    const nextIndex = (currentIndex - 1 + slides.length) % slides.length;
    showMainSlide(nextIndex);
  }

  function goToNextSlide() {
    const nextIndex = (currentIndex + 1) % slides.length;
    showMainSlide(nextIndex);
  }

  function showPreviewItem(index, syncMain = true) {
    if (!previewItems.length) return;

    previewIndex = index;

    previewItems.forEach((item, i) => {
      item.classList.toggle('active', i === index);
    });

    pauseAllPreviewVideos();

    const activeItem = previewItems[index];
    const activeVideo = activeItem ? activeItem.querySelector('video') : null;

    if (activeVideo) {
      activeVideo.currentTime = 0;
    }

    updatePreviewCounter(index);

    if (syncMain) {
      showMainSlide(index);
    }
  }

  function openPreview(startIndex = currentIndex) {
    if (!previewModal || !previewItems.length) return;

    previewModal.classList.add('active');
    lockBodyScroll(scrollPositionStore);
    showPreviewItem(startIndex, true);
  }

  function closePreview() {
    if (!previewModal) return;

    pauseAllPreviewVideos();
    previewModal.classList.remove('active');
    unlockBodyScroll(scrollPositionStore);
  }

  thumbs.forEach((thumb, index) => {
    thumb.addEventListener('click', () => {
      showMainSlide(index);
    });
  });

  previewTriggers.forEach((trigger, index) => {
    trigger.addEventListener('click', () => {
      openPreview(index);
    });
  });

  if (prevBtn) {
    prevBtn.addEventListener('click', goToPrevSlide);
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', goToNextSlide);
  }

  if (openPreviewBtn) {
    openPreviewBtn.addEventListener('click', () => openPreview(currentIndex));
  }

  if (previewPrevBtn) {
    previewPrevBtn.addEventListener('click', () => {
      const nextIndex = (previewIndex - 1 + previewItems.length) % previewItems.length;
      showPreviewItem(nextIndex, true);
    });
  }

  if (previewNextBtn) {
    previewNextBtn.addEventListener('click', () => {
      const nextIndex = (previewIndex + 1) % previewItems.length;
      showPreviewItem(nextIndex, true);
    });
  }

  if (previewCloseBtn) {
    previewCloseBtn.addEventListener('click', closePreview);
  }

  if (previewModal) {
    previewModal.addEventListener('click', (event) => {
      if (event.target === previewModal) {
        closePreview();
      }
    });
  }

  document.addEventListener('keydown', (event) => {
    const previewOpen = previewModal && previewModal.classList.contains('active');

    if (previewOpen) {
      if (event.key === 'Escape') {
        closePreview();
        return;
      }

      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        const nextIndex = (previewIndex - 1 + previewItems.length) % previewItems.length;
        showPreviewItem(nextIndex, true);
        return;
      }

      if (event.key === 'ArrowRight') {
        event.preventDefault();
        const nextIndex = (previewIndex + 1) % previewItems.length;
        showPreviewItem(nextIndex, true);
        return;
      }
    }

    if (!previewOpen) {
      if (event.key === 'ArrowLeft') {
        goToPrevSlide();
      }

      if (event.key === 'ArrowRight') {
        goToNextSlide();
      }
    }
  });

  let touchStartX = 0;
  let touchEndX = 0;

  const sliderArea = document.querySelector('.product-images-slider');
  if (sliderArea) {
    sliderArea.addEventListener(
      'touchstart',
      (event) => {
        touchStartX = event.changedTouches[0].clientX;
      },
      { passive: true }
    );

    sliderArea.addEventListener(
      'touchend',
      (event) => {
        touchEndX = event.changedTouches[0].clientX;
        handleSwipe();
      },
      { passive: true }
    );
  }

  const previewStage = document.getElementById('mediaPreviewStage');
  if (previewStage) {
    previewStage.addEventListener(
      'touchstart',
      (event) => {
        touchStartX = event.changedTouches[0].clientX;
      },
      { passive: true }
    );

    previewStage.addEventListener(
      'touchend',
      (event) => {
        touchEndX = event.changedTouches[0].clientX;
        handlePreviewSwipe();
      },
      { passive: true }
    );
  }

  function handleSwipe() {
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) < 45) return;

    if (diff > 0) {
      goToNextSlide();
    } else {
      goToPrevSlide();
    }
  }

  function handlePreviewSwipe() {
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) < 45) return;

    if (diff > 0) {
      const nextIndex = (previewIndex + 1) % previewItems.length;
      showPreviewItem(nextIndex, true);
    } else {
      const nextIndex = (previewIndex - 1 + previewItems.length) % previewItems.length;
      showPreviewItem(nextIndex, true);
    }
  }

  showMainSlide(currentIndex);
}

/* =========================
   IMPORTER MODAL
========================= */
function initImporterModal(scrollPositionStore) {
  const modal = document.getElementById('importerModal');
  const openBtn = document.getElementById('openImporterModal');
  const closeBtn = document.getElementById('closeImporterModal');

  if (!modal || !openBtn || !closeBtn) return;

  function openModal() {
    modal.classList.add('active');
    lockBodyScroll(scrollPositionStore);
  }

  function closeModal() {
    modal.classList.remove('active');
    unlockBodyScroll(scrollPositionStore);
  }

  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
}

/* =========================
   EXCHANGE MODAL
========================= */
function initExchangeModal(scrollPositionStore) {
  const modal = document.getElementById('exchangeModal');
  const openBtn = document.getElementById('openExchangeModal');
  const closeBtn = document.getElementById('closeExchangeModal');

  const exchangeData = document.getElementById('exchangeRateData');
  const usdValueEl = document.getElementById('exchangeUsdValue');
  const eurValueEl = document.getElementById('exchangeEurValue');
  const rubValueEl = document.getElementById('exchangeRubValue');
  const cbaRatesLink = document.getElementById('cbaRatesLink');

  if (!modal || !openBtn || !closeBtn || !exchangeData) return;

  const priceMin = parseFloat(exchangeData.dataset.priceMin);
  const priceMax = parseFloat(exchangeData.dataset.priceMax);

  const usdRate = parseFloat(exchangeData.dataset.usdRate);
  const eurRate = parseFloat(exchangeData.dataset.eurRate);
  const rubRate = parseFloat(exchangeData.dataset.rubRate);



  function formatNumber(value) {
    if (Number.isNaN(value) || value === null || value === undefined) {
      return '—';
    }

    return new Intl.NumberFormat('hy-AM', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value);
  }

  function buildConvertedRange(rate) {
    if (!rate || Number.isNaN(rate)) {
      return 'Տվյալը հասանելի չէ';
    }

    const hasMin = !Number.isNaN(priceMin);
    const hasMax = !Number.isNaN(priceMax);

    if (hasMin && hasMax) {
      return `${formatNumber(priceMin / rate)} – ${formatNumber(priceMax / rate)}`;
    }

    if (hasMin) {
      return `սկսած ${formatNumber(priceMin / rate)}`;
    }

    if (hasMax) {
      return `մինչև ${formatNumber(priceMax / rate)}`;
    }

    return 'Տվյալը հասանելի չէ';
  }

  function fillExchangeValues() {
    if (usdValueEl) {
      usdValueEl.textContent = buildConvertedRange(usdRate);
    }

    if (eurValueEl) {
      eurValueEl.textContent = buildConvertedRange(eurRate);
    }

    if (rubValueEl) {
      rubValueEl.textContent = buildConvertedRange(rubRate);
    }
  }

  function openModal() {
    fillExchangeValues();
    modal.classList.add('active');
    lockBodyScroll(scrollPositionStore);
  }

  function closeModal() {
    modal.classList.remove('active');
    unlockBodyScroll(scrollPositionStore);
  }

  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
}
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput");
  const clearFilters = document.getElementById("clearFilters");
  const cards = Array.from(document.querySelectorAll(".importer-card"));
  const noResults = document.getElementById("noResults");

  function normalize(value) {
    return String(value || "").trim().toLowerCase();
  }

  function applyFilters() {
    const query = normalize(searchInput ? searchInput.value : "");
    let visibleCount = 0;

    cards.forEach((card) => {
      const company = normalize(card.dataset.company);
      const phone = normalize(card.dataset.phone);
      const brands = normalize(card.dataset.brands);

      const matches =
        !query ||
        company.includes(query) ||
        phone.includes(query) ||
        brands.includes(query);

      card.style.display = matches ? "flex" : "none";

      if (matches) {
        visibleCount += 1;
      }
    });

    if (noResults) {
      noResults.style.display = visibleCount === 0 ? "block" : "none";
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  if (clearFilters) {
    clearFilters.addEventListener("click", () => {
      if (searchInput) {
        searchInput.value = "";
      }
      applyFilters();
    });
  }

  applyFilters();

  const carousel = document.getElementById("brandsCarousel");
  const stage = document.getElementById("brandsStage");
  const prevBtn = document.getElementById("brandPrev");
  const nextBtn = document.getElementById("brandNext");

  if (carousel && stage) {
    const brandCards = Array.from(carousel.querySelectorAll(".brand-card"));
    let currentIndex = 0;

    function getVisibleCount() {
      if (window.innerWidth <= 780) return 1;
      if (window.innerWidth <= 1100) return 2;
      return 3;
    }

    function getGap() {
      if (window.innerWidth <= 780) return 12;
      return 18;
    }

    function updateActiveStates() {
      brandCards.forEach((card, index) => {
        card.classList.remove("is-active", "is-near");

        if (index === currentIndex) {
          card.classList.add("is-active");
        } else if (Math.abs(index - currentIndex) === 1) {
          card.classList.add("is-near");
        }
      });
    }

    function updateCarousel() {
      if (!brandCards.length) return;

      const visibleCount = getVisibleCount();
      const gap = getGap();
      const stageWidth = stage.clientWidth;
      const cardWidth = stageWidth / visibleCount - (gap * (visibleCount - 1) / visibleCount);

      const maxIndex = Math.max(0, brandCards.length - visibleCount);
      if (currentIndex > maxIndex) {
        currentIndex = maxIndex;
      }

      const offset = (cardWidth + gap) * currentIndex;
      carousel.style.transform = `translateX(-${offset}px)`;

      updateActiveStates();
    }

    function goNext() {
      if (!brandCards.length) return;

      const visibleCount = getVisibleCount();
      const maxIndex = Math.max(0, brandCards.length - visibleCount);

      if (currentIndex >= maxIndex) {
        currentIndex = 0;
      } else {
        currentIndex += 1;
      }

      updateCarousel();
    }

    function goPrev() {
      if (!brandCards.length) return;

      const visibleCount = getVisibleCount();
      const maxIndex = Math.max(0, brandCards.length - visibleCount);

      if (currentIndex <= 0) {
        currentIndex = maxIndex;
      } else {
        currentIndex -= 1;
      }

      updateCarousel();
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", goNext);
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", goPrev);
    }

    let autoSlide = null;

    function startAutoSlide() {
      stopAutoSlide();
      autoSlide = setInterval(goNext, 3500);
    }

    function stopAutoSlide() {
      if (autoSlide) {
        clearInterval(autoSlide);
        autoSlide = null;
      }
    }

    if (stage) {
      stage.addEventListener("mouseenter", stopAutoSlide);
      stage.addEventListener("mouseleave", startAutoSlide);
      stage.addEventListener("touchstart", stopAutoSlide, { passive: true });
      stage.addEventListener("touchend", startAutoSlide);
    }

    window.addEventListener("resize", updateCarousel);

    updateCarousel();
    startAutoSlide();
  }
});
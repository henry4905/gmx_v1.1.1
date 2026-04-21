document.addEventListener("DOMContentLoaded", () => {
  initSmoothAnchorScroll();
  initImporterSlider(".importer-certificates-grid", {
    mobile: 1,
    tablet: 1,
    desktop: 2,
    gap: 20,
  });

  initImporterSlider(".importer-team-grid", {
    mobile: 1,
    tablet: 2,
    desktop: 3,
    gap: 20,
  });
});


/* =========================================
   SMOOTH SCROLL
========================================= */
function initSmoothAnchorScroll() {
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (!targetId || targetId === "#") return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      const headerOffset = 90;
      const targetTop =
        target.getBoundingClientRect().top + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: targetTop,
        behavior: "smooth",
      });
    });
  });
}


/* =========================================
   UNIVERSAL IMPORTER SLIDER
========================================= */
function initImporterSlider(selector, options = {}) {
  const grid = document.querySelector(selector);
  if (!grid) return;

  const items = Array.from(grid.children).filter((item) => item.nodeType === 1);
  if (!items.length) return;

  const config = {
    mobile: options.mobile || 1,
    tablet: options.tablet || 2,
    desktop: options.desktop || 3,
    gap: options.gap || 20,
  };

  const section = grid.closest(".importer-section");
  if (!section) return;

  const head = section.querySelector(".section-head");
  if (!head) return;

  grid.classList.add("gm-slider-grid");

  const slider = document.createElement("div");
  slider.className = "gm-slider";

  const viewport = document.createElement("div");
  viewport.className = "gm-slider-viewport";

  const track = document.createElement("div");
  track.className = "gm-slider-track";

  const controls = document.createElement("div");
  controls.className = "gm-slider-controls";

  const prevBtn = document.createElement("button");
  prevBtn.type = "button";
  prevBtn.className = "gm-slider-btn gm-slider-btn--prev";
  prevBtn.setAttribute("aria-label", "Նախորդը");
  prevBtn.innerHTML = `<span>‹</span>`;

  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "gm-slider-btn gm-slider-btn--next";
  nextBtn.setAttribute("aria-label", "Հաջորդը");
  nextBtn.innerHTML = `<span>›</span>`;

  const dots = document.createElement("div");
  dots.className = "gm-slider-dots";

  controls.appendChild(prevBtn);
  controls.appendChild(nextBtn);

  items.forEach((item) => {
    const slide = document.createElement("div");
    slide.className = "gm-slide";
    slide.appendChild(item);
    track.appendChild(slide);
  });

  viewport.appendChild(track);
  slider.appendChild(viewport);
  slider.appendChild(dots);

  grid.replaceWith(slider);

  if (!head.querySelector(".gm-slider-controls")) {
    head.appendChild(controls);
  }

  let currentIndex = 0;
  let slidesPerView = getSlidesPerView();
  let maxIndex = 0;
  let startX = 0;
  let currentTranslate = 0;
  let isDragging = false;
  let hasMoved = false;

  function getSlidesPerView() {
    const width = window.innerWidth;
    if (width <= 640) return config.mobile;
    if (width <= 992) return config.tablet;
    return config.desktop;
  }

  function clampIndex(index) {
    if (index < 0) return 0;
    if (index > maxIndex) return maxIndex;
    return index;
  }

  function updateLayout() {
    slidesPerView = getSlidesPerView();
    maxIndex = Math.max(0, items.length - slidesPerView);

    const gap = config.gap;
    track.style.gap = `${gap}px`;

    const slideWidth = `calc((100% - ${(slidesPerView - 1) * gap}px) / ${slidesPerView})`;

    Array.from(track.children).forEach((slide) => {
      slide.style.flex = `0 0 ${slideWidth}`;
      slide.style.maxWidth = slideWidth;
    });

    currentIndex = clampIndex(currentIndex);
    updateSlider(false);
    buildDots();
    updateButtons();
    toggleControls();
  }

  function updateSlider(animate = true) {
    const firstSlide = track.querySelector(".gm-slide");
    if (!firstSlide) return;

    const gap = config.gap;
    const slideWidth = firstSlide.getBoundingClientRect().width;
    const offset = currentIndex * (slideWidth + gap);

    track.style.transition = animate ? "transform .42s cubic-bezier(.2,.8,.2,1)" : "none";
    track.style.transform = `translate3d(-${offset}px, 0, 0)`;
    currentTranslate = -offset;

    updateButtons();
    updateDots();
  }

  function updateButtons() {
    prevBtn.disabled = currentIndex <= 0;
    nextBtn.disabled = currentIndex >= maxIndex;
  }

  function toggleControls() {
    const needSlider = items.length > slidesPerView;

    controls.style.display = needSlider ? "flex" : "none";
    dots.style.display = needSlider ? "flex" : "none";
    track.style.justifyContent = needSlider ? "flex-start" : "flex-start";
  }

  function buildDots() {
    dots.innerHTML = "";

    if (maxIndex <= 0) return;

    for (let i = 0; i <= maxIndex; i++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "gm-slider-dot";
      dot.setAttribute("aria-label", `Գնալ դիրք ${i + 1}`);

      dot.addEventListener("click", () => {
        currentIndex = i;
        updateSlider();
      });

      dots.appendChild(dot);
    }

    updateDots();
  }

  function updateDots() {
    const dotItems = dots.querySelectorAll(".gm-slider-dot");
    dotItems.forEach((dot, index) => {
      dot.classList.toggle("is-active", index === currentIndex);
    });
  }

  prevBtn.addEventListener("click", () => {
    currentIndex = clampIndex(currentIndex - 1);
    updateSlider();
  });

  nextBtn.addEventListener("click", () => {
    currentIndex = clampIndex(currentIndex + 1);
    updateSlider();
  });

  viewport.addEventListener("pointerdown", (e) => {
    if (items.length <= slidesPerView) return;

    isDragging = true;
    hasMoved = false;
    startX = e.clientX;
    track.style.transition = "none";
    viewport.setPointerCapture(e.pointerId);
    viewport.classList.add("is-dragging");
  });

  viewport.addEventListener("pointermove", (e) => {
    if (!isDragging) return;

    const deltaX = e.clientX - startX;
    if (Math.abs(deltaX) > 6) hasMoved = true;

    track.style.transform = `translate3d(${currentTranslate + deltaX}px, 0, 0)`;
  });

  function endDrag(e) {
    if (!isDragging) return;

    const deltaX = e.clientX - startX;
    isDragging = false;
    viewport.classList.remove("is-dragging");

    const threshold = 60;

    if (deltaX < -threshold) {
      currentIndex = clampIndex(currentIndex + 1);
    } else if (deltaX > threshold) {
      currentIndex = clampIndex(currentIndex - 1);
    }

    updateSlider();
  }

  viewport.addEventListener("pointerup", endDrag);
  viewport.addEventListener("pointercancel", endDrag);
  viewport.addEventListener("pointerleave", (e) => {
    if (isDragging) endDrag(e);
  });

  track.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", (e) => {
      if (hasMoved) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  let resizeTimer = null;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateLayout, 120);
  });

  injectSliderStyles();
  updateLayout();
}


/* =========================================
   INJECT SLIDER STYLES
========================================= */
let sliderStylesInjected = false;

function injectSliderStyles() {
  if (sliderStylesInjected) return;
  sliderStylesInjected = true;

  const style = document.createElement("style");
  style.textContent = `
    .gm-slider{
      position:relative;
    }

    .gm-slider-viewport{
      overflow:hidden;
      width:100%;
      touch-action:pan-y;
      cursor:grab;
    }

    .gm-slider-viewport.is-dragging{
      cursor:grabbing;
    }

    .gm-slider-track{
      display:flex;
      will-change:transform;
    }

    .gm-slide{
      min-width:0;
    }

    .gm-slide > *{
      height:100%;
    }

    .gm-slider-controls{
      display:flex;
      align-items:center;
      gap:10px;
      margin-top:2px;
    }

    .gm-slider-btn{
      width:46px;
      height:46px;
      border:none;
      border-radius:14px;
      cursor:pointer;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      background:linear-gradient(180deg, #ffffff 0%, #eef5ff 100%);
      border:1px solid rgba(12,99,231,0.10);
      box-shadow:0 10px 24px rgba(15,23,42,0.06);
      transition:transform .22s ease, box-shadow .22s ease, opacity .22s ease, border-color .22s ease;
      color:#0a3fa3;
      flex-shrink:0;
    }

    .gm-slider-btn span{
      font-size:24px;
      font-weight:800;
      line-height:1;
      transform:translateY(-1px);
    }

    .gm-slider-btn:hover:not(:disabled){
      transform:translateY(-2px);
      box-shadow:0 16px 30px rgba(15,23,42,0.10);
      border-color:rgba(12,99,231,0.18);
    }

    .gm-slider-btn:disabled{
      opacity:.45;
      cursor:not-allowed;
      transform:none;
      box-shadow:none;
    }

    .gm-slider-dots{
      display:flex;
      flex-wrap:wrap;
      align-items:center;
      justify-content:center;
      gap:8px;
      margin-top:16px;
    }

    .gm-slider-dot{
      width:10px;
      height:10px;
      border:none;
      border-radius:999px;
      background:rgba(12,99,231,0.18);
      cursor:pointer;
      transition:transform .22s ease, background .22s ease, width .22s ease;
      padding:0;
    }

    .gm-slider-dot.is-active{
      width:28px;
      background:#0c63e7;
    }

    .section-head{
      position:relative;
    }

    .section-head .gm-slider-controls{
      position:absolute;
      right:0;
      top:8px;
    }

    @media (max-width: 860px){
      .section-head .gm-slider-controls{
        position:static;
        margin-top:8px;
      }
    }

    @media (max-width: 640px){
      .gm-slider-btn{
        width:42px;
        height:42px;
        border-radius:12px;
      }

      .gm-slider-btn span{
        font-size:22px;
      }
    }
  `;
  document.head.appendChild(style);
}
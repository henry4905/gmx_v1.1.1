document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const mediaCards = Array.from(document.querySelectorAll(".media-card"));
  const anchorLinks = Array.from(document.querySelectorAll('a[href^="#"]'));

  const revealTargets = Array.from(
    document.querySelectorAll(
      ".brand-section, .media-card, .importer-card, .sidebar-card"
    )
  );

  /* =========================================
     REVEAL ON SCROLL
  ========================================= */
  if (revealTargets.length && "IntersectionObserver" in window) {
    revealTargets.forEach((item) => item.classList.add("reveal-on-scroll"));

    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      {
        threshold: 0.12,
        rootMargin: "0px 0px -30px 0px",
      }
    );

    revealTargets.forEach((item) => revealObserver.observe(item));
  }

  /* =========================================
     SMOOTH ANCHOR SCROLL
  ========================================= */
  anchorLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const href = link.getAttribute("href");

      if (!href || href === "#" || !href.startsWith("#")) return;

      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();

      const headerOffset = window.innerWidth <= 640 ? 74 : 92;
      const targetTop =
        target.getBoundingClientRect().top + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: targetTop,
        behavior: "smooth",
      });
    });
  });

  /* =========================================
     STOP IF NO MEDIA
  ========================================= */
  if (!mediaCards.length) return;

  /* =========================================
     MEDIA DATA
  ========================================= */
  const mediaItems = mediaCards.map((card, index) => {
    const link = card.querySelector(".media-card-link");
    const title =
      card.querySelector(".media-body h3")?.textContent?.trim() ||
      `Media ${index + 1}`;
    const type = card.dataset.mediaType || "image";
    const src = link?.getAttribute("href") || "#";
    const preview =
      card.querySelector(".media-preview img")?.getAttribute("src") || "";

    return {
      index,
      card,
      link,
      title,
      type,
      src,
      preview,
    };
  });

  /* =========================================
     CREATE MODAL
  ========================================= */
  const modal = document.createElement("div");
  modal.className = "brand-media-modal";
  modal.setAttribute("aria-hidden", "true");

  modal.innerHTML = `
    <div class="brand-media-modal-backdrop"></div>

    <div class="brand-media-modal-dialog" role="dialog" aria-modal="true" aria-label="Brand media viewer">
      <div class="brand-media-modal-top">
        <div class="brand-media-modal-title"></div>

        <div class="brand-media-modal-actions">
          <button class="brand-media-modal-btn modal-open-file" type="button" aria-label="Open media in new tab" title="Open">
            ↗
          </button>
          <button class="brand-media-modal-btn modal-close" type="button" aria-label="Close media viewer" title="Close">
            ✕
          </button>
        </div>
      </div>

      <div class="brand-media-modal-body">
        <button class="brand-media-modal-side prev" type="button" aria-label="Previous media">‹</button>
        <div class="brand-media-modal-content"></div>
        <button class="brand-media-modal-side next" type="button" aria-label="Next media">›</button>
      </div>
    </div>
  `;

  body.appendChild(modal);

  const modalBackdrop = modal.querySelector(".brand-media-modal-backdrop");
  const modalTitle = modal.querySelector(".brand-media-modal-title");
  const modalContent = modal.querySelector(".brand-media-modal-content");
  const modalClose = modal.querySelector(".modal-close");
  const modalOpenFile = modal.querySelector(".modal-open-file");
  const modalPrev = modal.querySelector(".prev");
  const modalNext = modal.querySelector(".next");

  let currentIndex = 0;
  let touchStartX = 0;
  let touchEndX = 0;

  /* =========================================
     HELPERS
  ========================================= */
  function isVideoFile(url = "") {
    return /\.(mp4|webm|ogg|mov|m4v)$/i.test(url.split("?")[0]);
  }

  function stopCurrentVideo() {
    const video = modalContent.querySelector("video");
    if (video) {
      video.pause();
      video.currentTime = 0;
    }
  }

  function buildFallbackMessage() {
    const fallback = document.createElement("div");
    fallback.style.color = "#fff";
    fallback.style.textAlign = "center";
    fallback.style.padding = "28px";
    fallback.innerHTML = `
      <strong style="display:block; font-size:20px; margin-bottom:10px;">Նյութը հասանելի չէ</strong>
      <span style="opacity:.82;">Այս ֆայլի հղումը դեռ չկա։</span>
    `;
    return fallback;
  }

  function buildMediaContent(item) {
    modalContent.innerHTML = "";

    if (!item || !item.src || item.src === "#") {
      modalContent.appendChild(buildFallbackMessage());
      return;
    }

    if (item.type === "video" || isVideoFile(item.src)) {
      const video = document.createElement("video");
      video.src = item.src;
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      video.preload = "metadata";
      modalContent.appendChild(video);
      return;
    }

    const img = document.createElement("img");
    img.src = item.src;
    img.alt = item.title || "Brand media";
    img.loading = "eager";
    modalContent.appendChild(img);
  }

  function updateNavButtons() {
    const multiple = mediaItems.length > 1;
    modalPrev.style.display = multiple ? "flex" : "none";
    modalNext.style.display = multiple ? "flex" : "none";
    modalPrev.disabled = !multiple;
    modalNext.disabled = !multiple;
  }

  function renderMedia(index) {
    stopCurrentVideo();

    currentIndex = index;
    const item = mediaItems[currentIndex];

    modalTitle.textContent = item.title || "Media";

    modalOpenFile.onclick = () => {
      if (item.src && item.src !== "#") {
        window.open(item.src, "_blank", "noopener,noreferrer");
      }
    };

    buildMediaContent(item);
    updateNavButtons();
  }

  function openModal(index) {
    renderMedia(index);
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    body.classList.add("media-modal-open");
  }

  function closeModal() {
    stopCurrentVideo();
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    body.classList.remove("media-modal-open");
  }

  function goPrev() {
    if (mediaItems.length <= 1) return;
    currentIndex = (currentIndex - 1 + mediaItems.length) % mediaItems.length;
    renderMedia(currentIndex);
  }

  function goNext() {
    if (mediaItems.length <= 1) return;
    currentIndex = (currentIndex + 1) % mediaItems.length;
    renderMedia(currentIndex);
  }

  /* =========================================
     CARD CLICK
  ========================================= */
  mediaItems.forEach((item, index) => {
    if (!item.link) return;

    item.link.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(index);
    });
  });

  /* =========================================
     MODAL EVENTS
  ========================================= */
  modalClose.addEventListener("click", closeModal);
  modalBackdrop.addEventListener("click", closeModal);
  modalPrev.addEventListener("click", goPrev);
  modalNext.addEventListener("click", goNext);

  document.addEventListener("keydown", (e) => {
    if (!modal.classList.contains("is-open")) return;

    if (e.key === "Escape") {
      closeModal();
    } else if (e.key === "ArrowLeft") {
      goPrev();
    } else if (e.key === "ArrowRight") {
      goNext();
    }
  });

  /* =========================================
     TOUCH SWIPE
  ========================================= */
  modal.addEventListener(
    "touchstart",
    (e) => {
      touchStartX = e.changedTouches[0].clientX;
    },
    { passive: true }
  );

  modal.addEventListener(
    "touchend",
    (e) => {
      touchEndX = e.changedTouches[0].clientX;
      const diff = touchEndX - touchStartX;

      if (Math.abs(diff) < 50) return;

      if (diff > 0) {
        goPrev();
      } else {
        goNext();
      }
    },
    { passive: true }
  );
});
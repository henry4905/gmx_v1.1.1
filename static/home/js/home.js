document.addEventListener("DOMContentLoaded", () => {
  const isMobile = window.innerWidth <= 992;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion) {
    document.documentElement.classList.add("reduced-motion");
  }

  /* ===============================
     1) SYSTEM PANEL 3D EFFECT
  =============================== */
  const stage = document.querySelector(".gmx-device-stage");
  const panel = document.querySelector(".gmx-system-panel");

  if (stage && panel && !isMobile && !prefersReducedMotion) {
    let rafId = null;

    const resetPanel = () => {
      panel.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg)";
    };

    const handleMove = (e) => {
      const rect = stage.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const rotateY = ((x / rect.width) - 0.5) * 8;
      const rotateX = ((y / rect.height) - 0.5) * -8;

      if (rafId) cancelAnimationFrame(rafId);

      rafId = requestAnimationFrame(() => {
        panel.style.transform =
          `perspective(1200px) rotateX(${rotateX * 0.18}deg) rotateY(${rotateY * 0.18}deg)`;
      });
    };

    stage.addEventListener("mousemove", handleMove);
    stage.addEventListener("mouseleave", resetPanel);
  }

  /* ===============================
     2) SCROLL REVEAL
  =============================== */
  const revealItems = document.querySelectorAll(
    ".gmx-system-copy, .gmx-system-panel, .gmx-showcase-main, .gmx-small-showcase-card, .gmx-brand-tile, .gmx-product-featured, .gmx-product-mini-card, .gmx-update-main, .gmx-update-mini, .gmx-compare-shell"
  );

  const applyInitialRevealState = () => {
    if (prefersReducedMotion) return;

    revealItems.forEach((item) => {
      item.style.opacity = "0";
      item.style.transform = "translateY(28px)";
      item.style.transition =
        "opacity 0.7s ease, transform 0.7s cubic-bezier(0.22, 1, 0.36, 1)";
    });
  };

  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.12,
      rootMargin: "0px 0px -40px 0px",
    }
  );

  if (!prefersReducedMotion) {
    applyInitialRevealState();
    revealItems.forEach((item) => revealObserver.observe(item));
  }

  /* ===============================
     3) BRAND TILES STAGGER
  =============================== */
  const brandTiles = document.querySelectorAll(".gmx-brand-tile");

  if (!prefersReducedMotion) {
    brandTiles.forEach((tile, index) => {
      tile.style.transitionDelay = `${Math.min(index * 60, 500)}ms`;
    });
  }

  /* ===============================
     4) PRODUCT IMAGE SUBTLE HOVER
  =============================== */
  const hoverCards = document.querySelectorAll(
    ".gmx-product-featured, .gmx-product-mini-card, .gmx-showcase-main, .gmx-small-showcase-card"
  );

  hoverCards.forEach((card) => {
    const img = card.querySelector("img");
    if (!img) return;

    card.addEventListener("mouseenter", () => {
      if (prefersReducedMotion) return;
      img.style.transition = "transform 0.6s ease";
      img.style.transform = "scale(1.04)";
    });

    card.addEventListener("mouseleave", () => {
      img.style.transform = "scale(1)";
    });
  });

  /* ===============================
     5) PARALLAX GLOW
  =============================== */
  const glow = document.querySelector(".gmx-device-glow");

  if (glow && !isMobile && !prefersReducedMotion) {
    let glowRAF = null;

    window.addEventListener("mousemove", (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 20;
      const y = (e.clientY / window.innerHeight - 0.5) * 20;

      if (glowRAF) cancelAnimationFrame(glowRAF);

      glowRAF = requestAnimationFrame(() => {
        glow.style.transform = `translate(${x}px, ${y}px)`;
      });
    });
  }

  /* ===============================
     6) TOUCH / MOBILE SAFE
  =============================== */
  if (isMobile) {
    document.body.classList.add("is-mobile");
  }

  /* ===============================
     7) RESIZE RESET
  =============================== */
  window.addEventListener("resize", () => {
    if (window.innerWidth <= 992 && panel) {
      panel.style.transform = "none";
    }
  });
});
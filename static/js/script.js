/* ==========================================================================
   Atlas AI — front-end controller
   ========================================================================== */
const Atlas = (() => {

  const CATEGORY_COLORS = ["#E3A23C", "#1E9C87", "#E8604C", "#2A4A6B", "#F0B75C", "#167E6D", "#8A5A16", "#5B6B7C", "#C97B3D"];

  // ---------------------------------------------------------------------
  // Toast helper
  // ---------------------------------------------------------------------
  function showToast(message, icon = "fa-circle-check") {
    const toast = document.getElementById("appToast");
    if (!toast) return;
    toast.querySelector("i").className = `fa-solid ${icon}`;
    document.getElementById("appToastMsg").textContent = message;
    toast.classList.add("show");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove("show"), 2600);
  }

  // ---------------------------------------------------------------------
  // Form validation (client-side, mirrors server-side rules)
  // ---------------------------------------------------------------------
  function attachFormValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", (e) => {
      let valid = true;
      const requiredFields = ["category", "budget", "travel_days", "travelers"];

      requiredFields.forEach((name) => {
        const field = form.querySelector(`[name="${name}"]`);
        if (!field) return;
        field.classList.remove("is-invalid");
        const val = field.value.trim();
        const isNumberField = field.type === "number";

        if (!val || (isNumberField && Number(val) <= 0)) {
          field.classList.add("is-invalid");
          valid = false;
        }
      });

      if (!valid) {
        e.preventDefault();
        showToast("Please fill in all required fields correctly.", "fa-triangle-exclamation");
        const firstInvalid = form.querySelector(".is-invalid");
        if (firstInvalid) firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
      } else {
        const btn = document.getElementById("submitBtn");
        if (btn) {
          btn.disabled = true;
          btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Finding your matches...';
        }
      }
    });

    // Live-clear invalid state as user types
    form.querySelectorAll(".form-control, .form-select").forEach((el) => {
      el.addEventListener("input", () => el.classList.remove("is-invalid"));
      el.addEventListener("change", () => el.classList.remove("is-invalid"));
    });
  }

  // ---------------------------------------------------------------------
  // Wishlist
  // ---------------------------------------------------------------------
  async function fetchWishlist() {
    const res = await fetch("/api/wishlist");
    return res.json();
  }

  async function toggleWishlist(destId, btnEl) {
    try {
      const res = await fetch("/api/wishlist/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination_id: destId }),
      });
      const data = await res.json();
      if (data.success) {
        const added = data.action === "added";
        if (btnEl) btnEl.classList.toggle("active", added);
        showToast(added ? "Added to wishlist" : "Removed from wishlist", added ? "fa-heart" : "fa-heart-crack");
        refreshWishlistCount();
      }
    } catch (err) {
      showToast("Could not update wishlist. Please try again.", "fa-triangle-exclamation");
    }
  }

  async function refreshWishlistCount() {
    const data = await fetchWishlist();
    const countEl = document.getElementById("wishlistCountNav");
    if (countEl) countEl.textContent = data.count || 0;

    // Sync heart icons on the page with current wishlist state
    if (data.success) {
      const ids = new Set(data.results.map((r) => r.id));
      document.querySelectorAll(".wishlist-btn").forEach((btn) => {
        const id = parseInt(btn.dataset.destId, 10);
        btn.classList.toggle("active", ids.has(id));
      });
    }
  }

  function renderWishlistPanel(items) {
    const body = document.getElementById("wishlistPanelBody");
    if (!body) return;
    if (!items.length) {
      body.innerHTML = `<div class="empty-state py-4"><i class="fa-solid fa-heart-crack fa-2x mb-3"></i><p>Your wishlist is empty. Tap the heart on any destination to save it.</p></div>`;
      return;
    }
    body.innerHTML = items.map((d) => `
      <div class="d-flex gap-3 align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--paper-200);">
        <img src="${d.image_url}" style="width:70px;height:70px;object-fit:cover;border-radius:10px;" alt="${d.name}"
             onerror="this.onerror=null;this.src='https://picsum.photos/seed/${encodeURIComponent(d.name.toLowerCase().replace(/\s+/g,'-'))}-fallback/120/120';">
        <div class="flex-grow-1">
          <div class="fw-semibold" style="font-family:var(--font-display);">${d.name}</div>
          <div class="text-secondary" style="font-size:0.8rem;">${d.state} · ₹${Number(d.budget_per_day).toLocaleString("en-IN")}/day</div>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="Atlas.toggleWishlist(${d.id}); Atlas.reopenWishlistPanel();">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `).join("");
  }

  async function reopenWishlistPanel() {
    const data = await fetchWishlist();
    renderWishlistPanel(data.results || []);
    refreshWishlistCount();
  }

  function initWishlistNav() {
    refreshWishlistCount();
    const openBtn = document.getElementById("openWishlistNav");
    if (openBtn) {
      openBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        const panelEl = document.getElementById("wishlistPanel");
        const panel = bootstrap.Offcanvas.getOrCreateInstance(panelEl);
        panel.show();
        const data = await fetchWishlist();
        renderWishlistPanel(data.results || []);
      });
    }

    document.body.addEventListener("click", (e) => {
      const btn = e.target.closest(".wishlist-btn");
      if (btn) {
        const id = parseInt(btn.dataset.destId, 10);
        toggleWishlist(id, btn);
      }
    });
  }

  // ---------------------------------------------------------------------
  // Results page: cards rendering, search/filter/sort, details modal
  // ---------------------------------------------------------------------
  function destCardHTML(d, opts = {}) {
    const showScore = d.match_score !== undefined && d.match_score !== null;
    return `
    <div class="col-lg-4 col-md-6 dest-col">
      <div class="dest-card fade-in-up">
        <div class="dest-img-wrap">
          <img src="${d.image_url}" alt="${d.name}" loading="lazy"
               onerror="this.onerror=null;this.src='https://picsum.photos/seed/${encodeURIComponent(d.name.toLowerCase().replace(/\s+/g,'-'))}-fallback/800/500';">
          ${showScore ? `
          <div class="stamp-badge">
            <span class="stamp-pct">${d.match_score}%</span>
            <span class="stamp-label">AI Match</span>
          </div>` : ""}
          <button class="wishlist-btn" data-dest-id="${d.id}" title="Save to wishlist">
            <i class="fa-solid fa-heart"></i>
          </button>
        </div>
        <div class="dest-body">
          <div class="dest-loc"><i class="fa-solid fa-location-dot"></i> ${d.state}, ${d.region}</div>
          <h5>${d.name}</h5>
          <p class="dest-desc">${d.description}</p>
          <div class="mb-2"><span class="badge-category">${d.category}</span></div>
          <div class="dest-meta">
            <div class="dest-price">₹${Number(d.budget_per_day).toLocaleString("en-IN")} <small>/ day</small></div>
            <div class="text-warning"><i class="fa-solid fa-star"></i> <span class="text-dark fw-semibold" style="font-size:0.88rem;">${d.rating}</span></div>
          </div>
          <button class="btn-details" data-dest-id="${d.id}" data-match="${d.match_score || ''}">
            View Details ${showScore ? "& Score Breakdown" : ""}
          </button>
        </div>
      </div>
    </div>`;
  }

  function renderGrid(items) {
    const grid = document.getElementById("resultsGrid");
    if (!grid) return;
    if (!items.length) {
      grid.innerHTML = `<div class="col-12"><div class="empty-state"><i class="fa-solid fa-compass fa-3x mb-3"></i><h4>No matches found</h4><p>Try adjusting your filters.</p></div></div>`;
      return;
    }
    grid.innerHTML = items.map((d) => destCardHTML(d)).join("");
    refreshWishlistCount();
  }

  let originalRecommendations = [];

  async function runFilterSearch() {
    const search = document.getElementById("searchInput").value.trim();
    const category = document.getElementById("filterCategory").value;
    const region = document.getElementById("filterRegion").value;
    const budgetMax = document.getElementById("filterBudgetMax").value;
    const sort = document.getElementById("sortSelect").value;

    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    if (region) params.set("region", region);
    if (budgetMax) params.set("budget_max", budgetMax);
    if (sort) params.set("sort", sort);

    document.getElementById("filterHint").textContent = "Browsing full catalog with your filters applied.";

    const res = await fetch(`/api/destinations?${params.toString()}`);
    const data = await res.json();
    renderGrid(data.results || []);
  }

  function debounce(fn, delay) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), delay);
    };
  }

  async function populateFilterOptions() {
    const res = await fetch("/api/form-options");
    const data = await res.json();
    if (!data.success) return;

    const catSel = document.getElementById("filterCategory");
    const regSel = document.getElementById("filterRegion");
    if (catSel) data.categories.forEach((c) => catSel.insertAdjacentHTML("beforeend", `<option value="${c}">${c}</option>`));
    if (regSel) data.regions.forEach((r) => regSel.insertAdjacentHTML("beforeend", `<option value="${r}">${r}</option>`));
  }

  function openDetailsModal(destId, matchScore) {
    const modalEl = document.getElementById("detailsModal");
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    const body = document.getElementById("modalBody");
    body.innerHTML = '<div class="spinner-atlas"></div>';
    modal.show();

    fetch(`/api/destination/${destId}`)
      .then((r) => r.json())
      .then((data) => {
        if (!data.success) {
          body.innerHTML = `<div class="p-4 text-center text-secondary">Could not load details.</div>`;
          return;
        }
        const d = data.result;
        const activities = d.activities.split(",").map((a) => `<span class="badge-category me-1 mb-1 d-inline-block">${a.trim()}</span>`).join("");

        let scoreHTML = "";
        const cardEl = document.querySelector(`.btn-details[data-dest-id="${destId}"]`);
        const breakdown = window.__lastBreakdowns ? window.__lastBreakdowns[destId] : null;

        if (breakdown) {
          const labels = {
            budget: "Budget Match", category: "Category Match", activities: "Activities Match",
            location: "Location Match", travel_style: "Travel Style", season: "Season Match",
            food_accommodation: "Food & Accommodation",
          };
          scoreHTML = `<div class="mt-3"><h6 class="text-mono text-uppercase" style="font-size:0.75rem; color:var(--text-600);">AI Match Breakdown — ${matchScore}% Overall</h6>` +
            Object.entries(breakdown).map(([key, val]) => `
              <div class="score-row">
                <div class="score-label"><span>${labels[key] || key}</span><span>${val}%</span></div>
                <div class="score-track"><div class="score-fill" style="width:${val}%;"></div></div>
              </div>
            `).join("") + `</div>`;
        }

        body.innerHTML = `
          <img src="${d.image_url}" class="modal-hero-img" alt="${d.name}"
               onerror="this.onerror=null;this.src='https://picsum.photos/seed/${encodeURIComponent(d.name.toLowerCase().replace(/\s+/g,'-'))}-fallback/900/500';">
          <div class="modal-header">
            <div>
              <h4 class="mb-0">${d.name}</h4>
              <div class="text-secondary" style="font-size:0.85rem;"><i class="fa-solid fa-location-dot"></i> ${d.state}, ${d.region}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>${d.description}</p>
            <div class="row g-3 mb-3">
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">CATEGORY</div><div class="fw-semibold">${d.category}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">BUDGET/DAY</div><div class="fw-semibold">₹${Number(d.budget_per_day).toLocaleString("en-IN")}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">IDEAL DAYS</div><div class="fw-semibold">${d.min_days}-${d.max_days} days</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">BEST SEASON</div><div class="fw-semibold">${d.best_season}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">TRAVEL STYLE</div><div class="fw-semibold">${d.travel_style}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">FOOD</div><div class="fw-semibold">${d.food_type}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">STAY</div><div class="fw-semibold">${d.accommodation}</div></div>
              <div class="col-6 col-md-3"><div class="text-secondary" style="font-size:0.75rem;">RATING</div><div class="fw-semibold"><i class="fa-solid fa-star text-warning"></i> ${d.rating}</div></div>
            </div>
            <div class="mb-2 text-secondary" style="font-size:0.75rem;">ACTIVITIES</div>
            <div class="mb-3">${activities}</div>
            ${scoreHTML}
          </div>
          <div class="modal-footer">
            <button class="btn-outline-atlas" data-bs-dismiss="modal">Close</button>
            <button class="btn-atlas wishlist-modal-btn" data-dest-id="${d.id}"><i class="fa-solid fa-heart me-2"></i>Save to Wishlist</button>
          </div>
        `;

        const wBtn = body.querySelector(".wishlist-modal-btn");
        if (wBtn) wBtn.addEventListener("click", () => toggleWishlist(d.id, null));
      });
  }

  function initResultsPage() {
    // Cache score breakdowns embedded via data attributes / global set by inline script if present
    window.__lastBreakdowns = window.__lastBreakdowns || {};
    document.querySelectorAll(".btn-details").forEach((btn) => {
      const id = btn.dataset.destId;
      // breakdown is fetched lazily from a hidden JSON blob if present
    });

    populateFilterOptions();

    const debouncedSearch = debounce(runFilterSearch, 350);
    const searchInput = document.getElementById("searchInput");
    if (searchInput) searchInput.addEventListener("input", debouncedSearch);

    ["filterCategory", "filterRegion", "filterBudgetMax", "sortSelect"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", runFilterSearch);
    });

    const clearBtn = document.getElementById("clearFiltersBtn");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        document.getElementById("searchInput").value = "";
        document.getElementById("filterCategory").value = "";
        document.getElementById("filterRegion").value = "";
        document.getElementById("filterBudgetMax").value = "";
        document.getElementById("sortSelect").value = "popularity";
        document.getElementById("filterHint").textContent = "Showing your AI-recommended matches, ranked by score.";
        renderGrid(originalRecommendations);
      });
    }

    document.body.addEventListener("click", (e) => {
      const btn = e.target.closest(".btn-details");
      if (btn) openDetailsModal(btn.dataset.destId, btn.dataset.match);
    });

    // Store original server-rendered recommendations (with scores) for "reset" action
    const cards = document.querySelectorAll("#resultsGrid .btn-details");
    originalRecommendations = Array.from(cards).map((btn) => {
      const card = btn.closest(".dest-card");
      return {
        id: parseInt(btn.dataset.destId, 10),
        match_score: btn.dataset.match,
        name: card.querySelector("h5").textContent,
        image_url: card.querySelector("img").src.split("?")[0],
        state: card.querySelector(".dest-loc").textContent.trim(),
        region: "",
        description: card.querySelector(".dest-desc").textContent,
        category: card.querySelector(".badge-category").textContent,
        budget_per_day: card.querySelector(".dest-price").textContent.replace(/[^\d]/g, ""),
        rating: card.querySelector(".text-warning span").textContent,
      };
    });

    refreshWishlistCount();
  }

  // ---------------------------------------------------------------------
  // Analytics (Chart.js)
  // ---------------------------------------------------------------------
  async function initAnalytics() {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    if (!data.success) return;

    // Category bar chart
    const catCtx = document.getElementById("chartCategory");
    if (catCtx) {
      new Chart(catCtx, {
        type: "bar",
        data: {
          labels: data.by_category.map((c) => c.category),
          datasets: [{
            label: "Destinations",
            data: data.by_category.map((c) => c.count),
            backgroundColor: "#1E9C87",
            borderRadius: 6,
          }],
        },
        options: {
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
      });
    }

    // Region doughnut
    const regCtx = document.getElementById("chartRegion");
    if (regCtx) {
      new Chart(regCtx, {
        type: "doughnut",
        data: {
          labels: data.by_region.map((r) => r.region),
          datasets: [{
            data: data.by_region.map((r) => r.count),
            backgroundColor: CATEGORY_COLORS,
          }],
        },
        options: { plugins: { legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 10 } } } } },
      });
    }

    // Budget by category
    const budgetCtx = document.getElementById("chartBudget");
    if (budgetCtx) {
      new Chart(budgetCtx, {
        type: "bar",
        data: {
          labels: data.by_category.map((c) => c.category),
          datasets: [{
            label: "Avg Budget/Day (₹)",
            data: data.by_category.map((c) => c.avg_budget),
            backgroundColor: "#E3A23C",
            borderRadius: 6,
          }],
        },
        options: {
          indexAxis: "y",
          plugins: { legend: { display: false } },
          scales: { x: { beginAtZero: true } },
        },
      });
    }

    // Top rated
    const topCtx = document.getElementById("chartTopRated");
    if (topCtx) {
      new Chart(topCtx, {
        type: "bar",
        data: {
          labels: data.top_rated.map((t) => t.name),
          datasets: [{
            label: "Rating",
            data: data.top_rated.map((t) => t.rating),
            backgroundColor: "#2A4A6B",
            borderRadius: 6,
          }],
        },
        options: {
          indexAxis: "y",
          plugins: { legend: { display: false } },
          scales: { x: { beginAtZero: true, max: 5 } },
        },
      });
    }
  }

  return {
    attachFormValidation,
    initWishlistNav,
    initResultsPage,
    initAnalytics,
    toggleWishlist,
    reopenWishlistPanel,
    showToast,
  };
})();

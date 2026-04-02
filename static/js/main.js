// DjibReco — JS Principal v2

document.addEventListener('DOMContentLoaded', () => {

  // ── Scroll to top ──────────────────────────────────────────────
  const scrollBtn = document.getElementById('scrollTopBtn');
  if (scrollBtn) {
    window.addEventListener('scroll', () => {
      scrollBtn.classList.toggle('visible', window.scrollY > 400);
    });
    scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ── Auto-hide alerts ───────────────────────────────────────────
  document.querySelectorAll('.alert.alert-dismissible').forEach(el => {
    setTimeout(() => {
      const a = bootstrap.Alert.getOrCreateInstance(el);
      if (a) a.close();
    }, 4500);
  });

  // ── Hero search form ───────────────────────────────────────────
  const heroForm = document.getElementById('heroSearchForm');
  if (heroForm) {
    heroForm.addEventListener('submit', e => {
      e.preventDefault();
      const q = document.getElementById('heroSearchInput').value.trim();
      if (q) window.location.href = `/restaurants/recherche/?q=${encodeURIComponent(q)}`;
    });
  }

  // ── Menu Tabs (detail page) ────────────────────────────────────
  const tabBtns = document.querySelectorAll('.menu-tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.menu-tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const content = document.getElementById('tab-' + btn.dataset.tab);
      if (content) content.classList.add('active');
    });
  });

  // ── Star rating (custom) ───────────────────────────────────────
  const noteInput = document.getElementById('id_note');
  const starLabels = document.querySelectorAll('.star-rating-wrap label');
  if (noteInput && starLabels.length) {
    starLabels.forEach(lbl => {
      lbl.addEventListener('click', () => {
        const val = lbl.previousElementSibling?.value || lbl.getAttribute('for')?.replace('star', '');
        if (val) noteInput.value = val;
      });
    });
  }

  // ── Favori AJAX ────────────────────────────────────────────────
  document.querySelectorAll('.btn-favori-ajax').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault();
      const url = btn.dataset.url;
      if (!url) return;
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken'),
          }
        });
        const data = await res.json();
        if (data.est_favori) {
          btn.classList.add('actif');
          btn.innerHTML = '<i class="bi bi-heart-fill"></i>';
          btn.title = 'Retirer des favoris';
        } else {
          btn.classList.remove('actif');
          btn.innerHTML = '<i class="bi bi-heart"></i>';
          btn.title = 'Ajouter aux favoris';
        }
        showToast(data.message, data.est_favori ? 'success' : 'info');
      } catch (err) {
        console.error(err);
      }
    });
  });

  // ── Image preview for file inputs ─────────────────────────────
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function () {
      const preview = document.getElementById(this.id + '_preview');
      if (preview && this.files?.[0]) {
        const reader = new FileReader();
        reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
        reader.readAsDataURL(this.files[0]);
      }
    });
  });

  // ── Animate on scroll ─────────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animationDelay = (Array.from(e.target.parentElement?.children || []).indexOf(e.target) * 0.07) + 's';
          e.target.classList.add('animate-up');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('.rest-card, .stat-card, .cat-chip').forEach(el => obs.observe(el));
  }

  // ── Budget filter buttons ──────────────────────────────────────
  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = new URL(window.location);
      const current = url.searchParams.get('budget');
      if (current === btn.dataset.budget) {
        url.searchParams.delete('budget');
      } else {
        url.searchParams.set('budget', btn.dataset.budget);
      }
      window.location = url.toString();
    });
  });

});

// ── Helpers ────────────────────────────────────────────────────────────────

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function showToast(msg, type = 'info') {
  const wrap = document.getElementById('toastContainer');
  if (!wrap) return;
  const colors = { success: '#06d6a0', info: '#118ab2', error: '#ff3c5f' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    background:white;border-radius:12px;padding:1rem 1.2rem;
    box-shadow:0 8px 30px rgba(0,0,0,0.12);display:flex;align-items:center;gap:.7rem;
    font-size:.88rem;font-weight:600;color:#1a1a2e;margin-bottom:.5rem;
    border-left:4px solid ${colors[type] || colors.info};
    animation:slideUp .3s ease;max-width:320px;
  `;
  toast.innerHTML = `<span>${msg}</span>`;
  wrap.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 300); }, 3000);
}

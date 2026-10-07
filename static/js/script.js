/* SmartBank AI – JavaScript */

// ─── Mobile Nav Toggle ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('mobileToggle');
  const menu   = document.getElementById('navMenu');

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      menu.classList.toggle('open');
      toggle.querySelector('i').className = menu.classList.contains('open')
        ? 'fas fa-times'
        : 'fas fa-bars';
    });
  }

  // Close menu on outside click
  document.addEventListener('click', (e) => {
    if (menu && toggle && !menu.contains(e.target) && !toggle.contains(e.target)) {
      menu.classList.remove('open');
      if (toggle.querySelector('i')) toggle.querySelector('i').className = 'fas fa-bars';
    }
  });

  // ─── Sticky Navbar Shadow ───────────────────────
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.style.boxShadow = window.scrollY > 10
        ? '0 4px 24px rgba(0,0,0,0.12)'
        : '0 2px 20px rgba(0,0,0,0.06)';
    });
  }

  // ─── Auto-dismiss Flash Alerts ──────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // ─── Animate Numbers on Scroll ──────────────────
  const animateNumbers = () => {
    document.querySelectorAll('.kpi-val, .mbval, .mmval').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && !el.dataset.animated) {
        el.dataset.animated = 'true';
        const target = parseFloat(el.textContent.replace(/[^0-9.]/g, ''));
        if (isNaN(target)) return;
        const suffix = el.textContent.replace(/[0-9.]/g, '');
        let start = 0;
        const duration = 1000;
        const step = () => {
          const now = Date.now();
          if (!el.dataset.startTime) el.dataset.startTime = now;
          const elapsed = now - parseInt(el.dataset.startTime);
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = start + (target - start) * eased;
          el.textContent = (Number.isInteger(target)
            ? Math.round(current)
            : current.toFixed(1)) + suffix;
          if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }
    });
  };
  window.addEventListener('scroll', animateNumbers);
  animateNumbers();

  // ─── Smooth Scroll for Anchor Links ─────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── Animate Progress Bars ───────────────────────
  setTimeout(() => {
    document.querySelectorAll('.acc-bar, .prob-bar-fill').forEach(bar => {
      const w = bar.style.width;
      bar.style.width = '0';
      requestAnimationFrame(() => {
        bar.style.transition = 'width 1s ease';
        bar.style.width = w;
      });
    });
  }, 100);

  // ─── Table Search ────────────────────────────────
  const searchInput = document.getElementById('tableSearch');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase();
      document.querySelectorAll('.data-table tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ─── Form Validation Feedback ────────────────────
  document.querySelectorAll('.predict-form input, .predict-form select').forEach(input => {
    input.addEventListener('blur', () => {
      if (input.required && !input.value) {
        input.style.borderColor = 'var(--danger)';
      } else {
        input.style.borderColor = '';
      }
    });
  });
});

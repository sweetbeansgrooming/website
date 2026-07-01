// Fade-up reveal on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add('in');
  });
}, { threshold: 0.12 });

document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));

// Close mobile panel on link click
document.querySelectorAll('.mobile-panel a').forEach((a) => {
  a.addEventListener('click', () => {
    document.getElementById('mobilePanel')?.classList.remove('open');
  });
});

// Toggle border-on-scroll state for the sticky nav
const navWrap = document.getElementById('navWrap');
window.addEventListener('scroll', () => {
  if (navWrap) {
    navWrap.classList.toggle('scrolled', window.scrollY > 8);
  }
});

// GA4 event tracking
function gtagEvent(name, params) {
  if (typeof gtag === 'function') gtag('event', name, params);
}

// Book button / CTA clicks
document.querySelectorAll('a[href*="booking.html"], a[href*="cal.com"]').forEach((el) => {
  el.addEventListener('click', () => {
    gtagEvent('book_click', { button_text: el.textContent.trim().slice(0, 50) });
  });
});

// Phone number clicks
document.querySelectorAll('a[href^="tel:"]').forEach((el) => {
  el.addEventListener('click', () => gtagEvent('phone_click', {}));
});

// Email clicks
document.querySelectorAll('a[href^="mailto:"]').forEach((el) => {
  el.addEventListener('click', () => gtagEvent('email_click', {}));
});

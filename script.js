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

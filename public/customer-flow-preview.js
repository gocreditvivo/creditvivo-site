const menuButton = document.querySelector('.menu');
const nav = document.querySelector('header nav');

menuButton?.addEventListener('click', () => {
  const open = nav?.classList.toggle('open') ?? false;
  menuButton.setAttribute('aria-expanded', String(open));
});

nav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    nav.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const bureauData = {
  Equifax: { score: '602', band: 'Fair' },
  Experian: { score: '611', band: 'Fair' },
  TransUnion: { score: '608', band: 'Fair' },
};

document.querySelectorAll('.tabs button').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tabs button').forEach((item) => {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-selected', String(item === button));
    });
    const bureau = button.textContent.trim();
    const data = bureauData[bureau];
    document.querySelector('.bureau-score span').textContent = bureau;
    document.querySelector('.bureau-score strong').textContent = data.score;
    document.querySelector('.bureau-score em').textContent = data.band;
  });
});

document.querySelectorAll('.comparison-tabs button').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.comparison-tabs button').forEach((item) => {
      item.classList.toggle('active', item === button);
    });
  });
});

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });
  document.querySelectorAll('.reveal').forEach((section) => observer.observe(section));
} else {
  document.querySelectorAll('.reveal').forEach((section) => section.classList.add('revealed'));
}

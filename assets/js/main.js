(function () {
  'use strict';
  var d = document;

  // قائمة الجوال
  var toggle = d.querySelector('.nav-toggle');
  var nav = d.getElementById('primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.querySelector('i').className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
    });
  }
  d.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.closest('.has-sub');
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  d.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && nav && nav.classList.contains('open')) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.querySelector('i').className = 'fa-solid fa-bars';
    }
  });

  // ظل الهيدر عند التمرير
  var header = d.querySelector('.site-header');
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 10);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ظهور العناصر تدريجيًا
  var items = d.querySelectorAll('.reveal');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // نموذج الطلب -> رسالة واتساب جاهزة
  d.querySelectorAll('.wa-form').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var f = form.elements;
      var msg = 'السلام عليكم، أرغب في طلب خدمة صيانة.\n' +
        'الاسم: ' + f.name.value + '\n' +
        'رقم الهاتف: ' + f.phone.value + '\n' +
        'الجهاز: ' + f.device.value + '\n' +
        (f.area.value ? 'المنطقة: ' + f.area.value + '\n' : '') +
        'وصف العطل: ' + f.problem.value;
      var url = 'https://wa.me/' + form.getAttribute('data-wa') + '?text=' + encodeURIComponent(msg);
      window.open(url, '_blank', 'noopener');
    });
  });
})();

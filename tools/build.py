# -*- coding: utf-8 -*-
"""يولّد صفحات الموقع الثابتة (HTML) من tools/content.py.

التشغيل:  python tools/build.py
الناتج ملفات HTML عادية؛ الموقع نفسه static بالكامل ولا يحتاج هذا السكربت للعمل.
"""
import html
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from content import AREAS, BRANDS, BRANDS_NOTE, CARE, CATEGORIES, HOME_FAQ, SITE, STEPS, WHY_US  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YEAR = datetime.now().year
FULL_NAME = f"{SITE['name']} {SITE['tagline']}"
TEL = f"tel:{SITE['phone_intl']}"
WA = f"https://wa.me/{SITE['wa_number']}"
e = html.escape

GTAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18548697970"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'AW-18548697970');
</script>"""



# ───────────────────────── رسومات SVG ─────────────────────────

# صور حقيقية لكل قسم (الأولى هي صورة بطاقة القسم)
PHOTOS = {
    "freezer": [
        ("freezer-1.jpg", "ديب فريزر رأسي مفتوح بأدراج"),
        ("freezer-2.jpg", "فني يصلح كمبروسر الفريزر"),
        ("freezer-3.jpg", "فني يفحص مراوح التبريد"),
    ],
    "wash": [("wash-1.jpg", "غسالة أوتوماتيك حديثة")],
    "dish": [("dish-1.jpg", "غسالة أطباق مدمجة مفتوحة"), ("dish-2.jpg", "غسالة أطباق بداخلها أطباق نظيفة")],
    "fridge": [
        ("fridge-2.jpg", "فني يصلح ثلاجة في مطبخ منزلي"),
        ("fridge-1.jpg", "فني يفحص ثلاجة مفتوحة"),
        ("fridge-3.jpg", "فني يفحص مروحة وأجزاء الثلاجة"),
    ],
    # من غير المفتاح ده كان photo() بيقع على الرسمة SVG وخانة الصور في
    # صفحة الديب فريزر تفضل فاضية
    "freezer": [
        ("freezer-1.jpg", "فني يصلح ديب فريزر بعدّة الصيانة"),
        ("freezer-2.jpg", "ديب فريزر رأسي بأدراج مفتوح"),
        ("freezer-3.jpg", "فني يفحص ملف التبريد خلف الديب فريزر"),
    ],
}


def photo(theme, i, pre, cls="photo"):
    f, alt = PHOTOS[theme][i % len(PHOTOS[theme])]
    return f'<img class="{cls}" src="{pre}assets/img/photos/{f}" alt="{alt}" loading="lazy" width="640" height="480">'

LOGO = '''<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="12" fill="currentColor"/><g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6"><path d="M10 25 24 12l14 13v13H10z"/><path d="m17 27 5 5 9-10" stroke-width="3"/></g></svg>'''


# ───────────────────────── مساعدات ─────────────────────────
def ph():
    return f'<span class="num" dir="ltr">{SITE["phone"]}</span>'


def icon(name, extra=""):
    kind = "fa-brands" if name.startswith("fa-whatsapp") else "fa-solid"
    return f'<i class="{kind} {name} {extra}" aria-hidden="true"></i>'


def cat_url(c, pre):
    return f"{pre}{c['folder']}/index.html"


def svc_url(c, s, pre):
    return f"{pre}{c['folder']}/{s['slug']}.html"


def btn_call(label=None, cls="btn-accent"):
    return f'<a class="btn {cls}" href="{TEL}">{icon("fa-phone")} {label or "اتصل الآن"}</a>'


def btn_wa(label="راسلنا على واتساب", cls="btn-wa"):
    return f'<a class="btn {cls}" href="{WA}" target="_blank" rel="noopener">{icon("fa-whatsapp")} {label}</a>'


def faq_html(items):
    out = []
    for q, a in items:
        out.append(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>")
    return '<div class="faq">' + "".join(out) + "</div>"


def faq_ld(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }


def breadcrumb(trail, pre):
    """trail: [(label, href|None)]"""
    items = [("الرئيسية", f"{pre}index.html")] + trail
    lis = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{href}">{e(label)}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{e(label)}</li>')
    return '<nav class="breadcrumb" aria-label="مسار التنقل"><ol>' + "".join(lis) + "</ol></nav>"


def breadcrumb_ld(trail, pre):
    items = [("الرئيسية", "index.html")] + [(l, h) for l, h in trail]
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": l} for i, (l, _h) in enumerate(items)
        ],
    }


# ───────────────────────── الهيكل المشترك ─────────────────────────
def header(pre, active):
    items = [f'<li><a href="{pre}index.html"{" aria-current=\"page\"" if active == "home" else ""}>الرئيسية</a></li>']
    for c in CATEGORIES:
        subs = "".join(
            f'<li><a href="{svc_url(c, s, pre)}">{e(s["nav"])}</a></li>' for s in c["services"]
        )
        cur = ' aria-current="page"' if active == c["key"] else ""
        items.append(
            f'''<li class="has-sub theme-{c["theme"]}">
<a class="sub-link" href="{cat_url(c, pre)}"{cur}>{e(c["name"])}</a>
<button class="sub-toggle" type="button" aria-expanded="false" aria-label="عرض خدمات {e(c["name"])}">{icon("fa-chevron-down")}</button>
<div class="sub-menu"><ul>{subs}</ul><a class="sub-all" href="{cat_url(c, pre)}">كل خدمات {e(c["name"])} {icon("fa-arrow-left")}</a></div>
</li>'''
        )
    area_links = "".join(f'<li><a href="{pre}areas/{a["slug"]}.html">{e(a["name"])}</a></li>' for a in AREAS)
    items.append(
        f'''<li class="has-sub theme-area">
<a class="sub-link" href="{pre}areas/index.html"{" aria-current=\"page\"" if active == "areas" else ""}>مناطق الخدمة</a>
<button class="sub-toggle" type="button" aria-expanded="false" aria-label="عرض محافظات الدلتا">{icon("fa-chevron-down")}</button>
<div class="sub-menu"><ul>{area_links}</ul><a class="sub-all" href="{pre}areas/index.html">كل محافظات الدلتا {icon("fa-arrow-left")}</a></div>
</li>'''
    )
    items.append(f'<li><a href="{pre}about.html"{" aria-current=\"page\"" if active == "about" else ""}>عن الشركة</a></li>')
    items.append(f'<li><a href="{pre}contact.html"{" aria-current=\"page\"" if active == "contact" else ""}>اتصل بنا</a></li>')
    return f'''<a class="skip" href="#main">تخطَّ إلى المحتوى</a>
<div class="topbar"><div class="container">
<span>{icon("fa-clock")} {SITE["hours"]}</span>
<a href="{TEL}">{icon("fa-phone")} {ph()}</a>
</div></div>
<header class="site-header"><div class="container nav-wrap">
<a class="brand" href="{pre}index.html" aria-label="{e(FULL_NAME)}"><img class="brand-logo" src="{pre}assets/img/logo.png" alt="{FULL_NAME}" width="160" height="90"></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="القائمة">{icon("fa-bars")}</button>
<nav id="primary-nav" class="primary-nav" aria-label="القائمة الرئيسية"><ul>{"".join(items)}</ul>
<a class="btn btn-accent nav-cta" href="{TEL}">{icon("fa-phone")} اتصل الآن</a></nav>
</div></header>'''


def footer(pre):
    cols = []
    for c in CATEGORIES:
        links = "".join(f'<li><a href="{svc_url(c, s, pre)}">{e(s["nav"])}</a></li>' for s in c["services"][:5])
        cols.append(f'<div><h3><a href="{cat_url(c, pre)}">{e(c["name"])}</a></h3><ul>{links}</ul></div>')
    return f'''<footer class="site-footer"><div class="container">
<div class="foot-grid">
<div class="foot-brand"><a class="brand" href="{pre}index.html"><img class="brand-logo on-dark" src="{pre}assets/img/logo.png" alt="{FULL_NAME}" width="160" height="90"></a>
<p>صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر بخبرة تزيد على {SITE["experience"]} سنة، مع تشخيص واضح وتكلفة معلنة قبل البدء.</p>
<ul class="contact-list">
<li>{icon("fa-phone")} <a href="{TEL}">{ph()}</a></li>
<li>{icon("fa-envelope")} <a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
<li>{icon("fa-location-dot")} {SITE["location"]}</li></ul></div>
{"".join(cols)}
<div><h3><a href="{pre}areas/index.html">مناطق الخدمة</a></h3><ul>{"".join(f'<li><a href="{pre}areas/{a["slug"]}.html">{e(a["name"])}</a></li>' for a in AREAS)}</ul></div>
<div><h3>روابط سريعة</h3><ul><li><a href="{pre}index.html">الرئيسية</a></li><li><a href="{pre}services.html">كل الخدمات</a></li><li><a href="{pre}brands.html">الماركات</a></li><li><a href="{pre}about.html">عن الشركة</a></li><li><a href="{pre}contact.html">اتصل بنا</a></li></ul></div>
</div>
<p class="copy">© {YEAR} {e(FULL_NAME)}. جميع الحقوق محفوظة.</p>
</div></footer>
<a class="fab fab-wa" href="{WA}" target="_blank" rel="noopener" aria-label="راسلنا على واتساب">{icon("fa-whatsapp")}</a>
<a class="fab fab-call" href="{TEL}" aria-label="اتصل بنا">{icon("fa-phone")}</a>'''


def page(path, title, desc, body, active="", theme="", ld=None):
    depth = path.count("/")
    pre = "../" * depth
    full_title = title if title.startswith(SITE["name"]) else f"{title} | {FULL_NAME}"
    ld_tag = ""
    if ld:
        ld_tag = '<script type="application/ld+json">' + json.dumps(
            {"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False
        ) + "</script>"
    doc = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0b2a5b">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_EG">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<link rel="icon" href="{pre}assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{pre}assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="{pre}assets/css/style.css">
<script>document.documentElement.classList.add('js')</script>
{GTAG}
{ld_tag}
</head>
<body class="{("theme-" + theme) if theme else ""}">
{header(pre, active)}
<main id="main">
{body.replace("{{PRE}}", pre)}
</main>
{footer(pre)}
<script src="{pre}assets/js/main.js" defer></script>
</body>
</html>
'''
    out = os.path.join(ROOT, *path.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)


# ───────────────────────── مكوّنات الأقسام ─────────────────────────
def cta_band(heading="عندك عطل في جهازك؟ كلّمنا الآن"):
    return f'''<section class="cta-band"><div class="container cta-inner">
<div><h2>{heading}</h2><p>فنيونا جاهزون لتحديد موعد زيارة يناسبك. {SITE["hours"]}.</p></div>
<div class="cta-actions">{btn_call(cls="btn-light")}{btn_wa(cls="btn-wa")}</div></div></section>'''


def svc_card(c, s, pre, local=False):
    href = f"{s['slug']}.html" if local else svc_url(c, s, pre)
    return f'''<a class="svc-card theme-{c["theme"]} reveal" href="{href}">
<span class="svc-ico">{icon(s["icon"])}</span>
<h3>{e(s["nav"])}</h3><p>{e(s["summary"])}</p>
<span class="more">التفاصيل {icon("fa-arrow-left")}</span></a>'''


def alert_box(a, cls="alert-danger"):
    return f'<div class="alert {cls}" role="note">{icon("fa-triangle-exclamation")}<div><strong>{e(a["title"])}</strong><p>{e(a["text"])}</p></div></div>'


def wa_form(prefix=""):
    opts = "".join(f'<option>{e(c["name"])}</option>' for c in CATEGORIES)
    return f'''<form class="wa-form" data-wa="{SITE["wa_number"]}" novalidate>
<div class="form-grid">
<label>الاسم<input name="name" type="text" required autocomplete="name"></label>
<label>رقم الهاتف<input name="phone" type="tel" required dir="ltr" autocomplete="tel"></label>
<label>نوع الجهاز<select name="device" required><option value="">اختر…</option>{opts}</select></label>
<label>المنطقة<input name="area" type="text" autocomplete="address-level2"></label>
<label class="full">وصف العطل<textarea name="problem" rows="4" required></textarea></label>
</div>
<button class="btn btn-wa" type="submit">{icon("fa-whatsapp")} أرسل الطلب عبر واتساب</button>
<p class="form-note">عند الضغط سيفتح واتساب برسالة جاهزة تراجعها وترسلها لنا بنفسك.</p>
</form>'''


def brand_chips(theme):
    return '<ul class="brand-chips">' + "".join(f"<li>{e(b)}</li>" for b in BRANDS[theme]) + "</ul>"


def brand_block(c, heading=None):
    return f'''<section class="section"><div class="container narrow">
<div class="section-head"><span class="eyebrow">الماركات</span><h2>{heading or "ماركات " + c["name"] + " التي نتعامل معها"}</h2></div>
<div class="theme-{c["theme"]}">{brand_chips(c["theme"])}</div><p class="brand-note">{e(BRANDS_NOTE)}</p></div></section>'''


def care_block(c):
    d = CARE[c["key"]]
    tips = "".join(f'<div class="care reveal">{icon("fa-circle-check")}<h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in d["tips"])
    call = "".join(f'<li>{icon("fa-phone-volume")} {e(x)}</li>' for x in d["call_when"])
    return f'''<section class="section alt"><div class="container">
<div class="section-head"><span class="eyebrow">نصائح العناية</span><h2>كيف تحافظ على {e(c["name"])}</h2><p>عادات بسيطة تطيل عمر جهازك وتقلل الأعطال.</p></div>
<div class="care-grid">{tips}</div>
<div class="call-when"><h3>{icon("fa-triangle-exclamation")} اتصل بالفني فورًا إذا لاحظت:</h3><ul>{call}</ul></div></div></section>'''


def area_chips(pre):
    return '<div class="chips">' + "".join(f'<a href="{pre}areas/{a["slug"]}.html">{e(a["name"])}</a>' for a in AREAS) + "</div>"


# ───────────────────────── الصفحات ─────────────────────────
def build_home():
    cards = []
    for c in CATEGORIES:
        lis = "".join(f'<li>{icon("fa-check")} {e(s["nav"])}</li>' for s in c["services"][:4])
        cards.append(
            f'''<article class="cat-card theme-{c["theme"]} reveal">
<div class="art">{photo(c["theme"], 0, "")}</div>
<div class="cat-body"><h3>{e(c["title"])}</h3><p>{e(c["headline"])}</p><ul class="check-list">{lis}</ul>
<a class="btn btn-cat" href="{cat_url(c, "")}">كل خدمات {e(c["name"])} {icon("fa-arrow-left")}</a></div></article>'''
        )
    why = "".join(
        f'<div class="why reveal"><span class="why-ico">{icon(i)}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in WHY_US
    )
    steps = "".join(
        f'<li class="reveal"><span class="step-n">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>'
        for n, (t, d) in enumerate(STEPS, 1)
    )
    pop = []
    for c in CATEGORIES:
        pop.append(
            f'<div class="pop theme-{c["theme"]}"><h3>{icon(c["icon"])} {e(c["name"])}</h3><ul>'
            + "".join(f'<li><a href="{svc_url(c, s, "")}">{e(s["nav"])}</a></li>' for s in c["services"])
            + "</ul></div>"
        )
    body = f'''<section class="hero"><div class="container hero-grid">
<div class="hero-text">
<span class="pill">{icon("fa-award")} أكثر من {SITE["experience"]} سنة خبرة</span>
<h1>صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر</h1>
<p class="lead">فنيون متخصصون يشخّصون العطل بدقة ويصلحونه بسرعة واحترافية. اتصل الآن واحجز موعد زيارة يناسبك.</p>
<div class="hero-actions">{btn_call(f"اتصل: {ph()}")}{btn_wa(cls="btn-ghost")}</div>
<ul class="trust"><li>{icon("fa-circle-check")} تكلفة معلنة قبل البدء</li><li>{icon("fa-circle-check")} {SITE["hours"]}</li><li>{icon("fa-circle-check")} ضمان جودة الخدمة</li></ul>
</div></div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">أقسام الخدمات</span><h2>اختر الجهاز الذي تحتاج صيانته</h2><p>أربعة أقسام متخصصة، لكل قسم صفحات تفصيلية للأعطال والحلول.</p></div>
<div class="cat-grid">{"".join(cards)}</div></div></section>

<section class="section alt"><div class="container">
<div class="section-head"><span class="eyebrow">لماذا خدماتي</span><h2>خدمة تعتمد عليها</h2></div>
<div class="why-grid">{why}</div></div></section>

<section class="section alt"><div class="container">
<div class="section-head"><span class="eyebrow">الماركات</span><h2>نتعامل مع أشهر الماركات</h2><p>اختر جهازك لتعرف الماركات التي نصلحها.</p></div>
<div class="brand-groups">{"".join(f'<div class="brand-group theme-{c["theme"]}"><h3>{icon(c["icon"])} {e(c["name"])}</h3>{brand_chips(c["theme"])}</div>' for c in CATEGORIES)}</div>
<p class="brand-note"><a href="brands.html">عرض صفحة الماركات</a> · {e(BRANDS_NOTE)}</p></div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">كيف نعمل</span><h2>من الاتصال إلى الإصلاح في أربع خطوات</h2></div>
<ol class="steps-row">{steps}</ol></div></section>

<section class="section alt"><div class="container">
<div class="section-head"><span class="eyebrow">دليل الخدمات</span><h2>كل ما نصلحه في مكان واحد</h2></div>
<div class="pop-grid">{"".join(pop)}</div></div></section>

<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">مناطق الخدمة</span><h2>نخدم محافظات الدلتا</h2><p>نصلك أينما كنت في الدلتا، اختر محافظتك لمعرفة المدن التي نغطيها.</p></div>
<div class="area-grid">{"".join(f'<a class="area-card reveal" href="areas/{a["slug"]}.html">{icon("fa-location-dot")}<strong>{e(a["name"])}</strong><small>{e("، ".join(a["cities"][:3]))}…</small></a>' for a in AREAS)}</div></div></section>

<section class="section alt"><div class="container narrow">
<div class="section-head"><span class="eyebrow">اطلب فنيًا</span><h2>أرسل لنا بيانات العطل</h2><p>املأ النموذج وسيتم تجهيز رسالة واتساب جاهزة.</p></div>
{wa_form()}</div></section>

<section class="section alt"><div class="container narrow">
<div class="section-head"><span class="eyebrow">أسئلة شائعة</span><h2>إجابات سريعة</h2></div>
{faq_html(HOME_FAQ)}</div></section>
{cta_band()}'''
    ld = [
        {
            "@type": "LocalBusiness",
            "name": FULL_NAME,
            "telephone": SITE["phone_intl"],
            "email": SITE["email"],
            "areaServed": [{"@type": "AdministrativeArea", "name": a["name"]} for a in AREAS],
            "address": {"@type": "PostalAddress", "addressCountry": "EG"},
            "description": "صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر",
        },
        faq_ld(HOME_FAQ),
    ]
    page("index.html", f"{SITE['name']} | صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر",
         "صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر بخبرة تزيد على 25 سنة. تشخيص دقيق وتكلفة معلنة قبل البدء. اتصل بخدماتي الآن.",
         body, active="home", ld=ld)


def page_hero(trail, h1, lead, pre, art="", ctas=True):
    cta = f'<div class="hero-actions">{btn_call()}{btn_wa(cls="btn-ghost")}</div>' if ctas else ""
    return f'''<section class="page-hero"><div class="container ph-grid">
<div>{breadcrumb(trail, pre)}<h1>{e(h1)}</h1><p class="lead">{e(lead)}</p>{cta}</div>{art}</div></section>'''


def build_services():
    blocks = []
    for c in CATEGORIES:
        blocks.append(
            f'''<section class="section theme-{c["theme"]}"><div class="container">
<div class="section-head left"><span class="eyebrow">{icon(c["icon"])} {e(c["name"])}</span><h2>{e(c["title"])}</h2><p>{e(c["intro"])}</p></div>
<div class="svc-grid">{"".join(svc_card(c, s, "") for s in c["services"])}</div></div></section>'''
        )
    body = page_hero([("خدماتنا", None)], "خدماتنا", "أقسام متخصصة لصيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر، لكل منها صفحات تفصيلية.", "") + "".join(blocks) + cta_band()
    page("services.html", "خدماتنا", "كل خدمات صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر من خدماتي في مكان واحد.", body, active="services")


def build_about():
    vals = [
        ("fa-handshake", "الأمانة والوضوح", "نشرح العطل والتكلفة قبل البدء، ولا نغيّر قطعة لا يحتاجها جهازك."),
        ("fa-stopwatch", "الالتزام بالمواعيد", "نحترم وقتك ونحدد موعدًا واضحًا للزيارة."),
        ("fa-screwdriver-wrench", "إتقان العمل", "نختبر الجهاز بعد الإصلاح للتأكد من عمله بكفاءة."),
    ]
    v = "".join(f'<div class="why reveal"><span class="why-ico">{icon(i)}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in vals)
    body = page_hero([("عن الشركة", None)], "عن خدماتي", f"شركة متخصصة في صيانة الأجهزة المنزلية بخبرة تزيد على {SITE['experience']} سنة.", "") + f'''
<section class="section"><div class="container narrow prose">
<figure class="hero-photo">{photo("fridge", 0, "")}</figure>
<h2>من نحن</h2>
<p>{e(FULL_NAME)} شركة تقدّم خدمات صيانة وإصلاح متخصصة لأربعة من أهم الأجهزة المنزلية: الغسالات وغسالات الأطباق والثلاجات والديب فريزر. نعمل بخبرة تزيد على {SITE["experience"]} سنة، وهدفنا أن يعود جهازك للعمل بكفاءة وأمان بأقل وقت وبتكلفة واضحة منذ البداية.</p>
<p>يقوم فنيونا بفحص الجهاز وتحديد سبب العطل، ثم يشرحون لك الحل المناسب والتكلفة، ولا يبدأ الإصلاح إلا بعد موافقتك.</p>
</div></section>
<section class="section alt"><div class="container"><div class="section-head"><span class="eyebrow">مبادئنا</span><h2>كيف نعمل</h2></div><div class="why-grid three">{v}</div></div></section>
<section class="section"><div class="container"><div class="section-head"><span class="eyebrow">تخصصاتنا</span><h2>أربعة أقسام نتقنها</h2></div>
<div class="svc-grid">{"".join(f'<a class="svc-card theme-{c["theme"]} reveal" href="{cat_url(c, "")}"><span class="svc-ico">{icon(c["icon"])}</span><h3>{e(c["title"])}</h3><p>{e(c["headline"])}</p><span class="more">استعرض القسم {icon("fa-arrow-left")}</span></a>' for c in CATEGORIES)}</div></div></section>
{cta_band()}'''
    page("about.html", "عن الشركة", "تعرّف على خدماتي: شركة صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر بخبرة تزيد على 25 سنة.", body, active="about")


def build_contact():
    cards = f'''<div class="info-grid">
<div class="info reveal">{icon("fa-phone")}<h3>اتصل بنا</h3><p>{ph()}</p><a class="btn btn-accent" href="{TEL}">اتصل الآن</a></div>
<div class="info reveal">{icon("fa-whatsapp")}<h3>واتساب</h3><p>{ph()}</p><a class="btn btn-wa" href="{WA}" target="_blank" rel="noopener">راسلنا</a></div>
<div class="info reveal">{icon("fa-envelope")}<h3>البريد الإلكتروني</h3><p>{SITE["email"]}</p><a class="btn btn-cat" href="mailto:{SITE["email"]}">أرسل بريدًا</a></div>
<div class="info reveal">{icon("fa-location-dot")}<h3>الموقع</h3><p>{SITE["location"]}</p><span class="muted">{SITE["hours"]}</span></div></div>'''
    body = page_hero([("اتصل بنا", None)], "اتصل بنا", "يسعدنا استقبال استفساراتك وطلبات الصيانة في أي وقت.", "", ctas=False) + f'''
<section class="section"><div class="container">{cards}</div></section>
<section class="section alt"><div class="container narrow"><div class="section-head"><span class="eyebrow">اطلب فنيًا</span><h2>أرسل طلب صيانة</h2></div>{wa_form()}</div></section>
<section class="section"><div class="container"><div class="section-head"><span class="eyebrow">موقعنا</span><h2>على الخريطة</h2></div>
<iframe class="map" title="موقع {e(SITE["name"])} على الخريطة" src="{SITE["map_src"]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div></section>'''
    page("contact.html", "اتصل بنا", "تواصل مع خدماتي لصيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر: اتصال أو واتساب أو بريد إلكتروني.", body, active="contact")


def build_category(c):
    art = f'<div class="ph-art">{photo(c["theme"], 0, "../")}</div>'
    trail = [(c["name"], None)]
    sym = "".join(f'<li>{icon("fa-circle-exclamation")} {e(x)}</li>' for x in c["symptoms"])
    alert = alert_box(c["alert"]) if c.get("alert") else ""
    body = page_hero(trail, c["title"], c["headline"], "../", art) + f'''
<section class="section"><div class="container intro-grid">
<div>{alert}<div class="prose"><p>{e(c["intro"])}</p></div></div>
<div class="photo-stack">{"".join(photo(c["theme"], i, "../") for i in range(min(2, len(PHOTOS.get(c["theme"], [])))))}</div></div></section>
<section class="section alt"><div class="container"><div class="section-head"><span class="eyebrow">الخدمات</span><h2>خدمات {e(c["name"])}</h2><p>اختر المشكلة التي تواجهها لتقرأ التفاصيل.</p></div>
<div class="svc-grid">{"".join(svc_card(c, s, "", local=True) for s in c["services"])}</div></div></section>
<section class="section"><div class="container narrow"><div class="section-head"><span class="eyebrow">أعراض شائعة</span><h2>هل تلاحظ شيئًا من هذا؟</h2></div>
<ul class="symptom-list">{sym}</ul></div></section>
{care_block(c)}
{brand_block(c)}
<section class="section alt"><div class="container narrow"><div class="section-head"><span class="eyebrow">أسئلة شائعة</span><h2>أسئلة حول {e(c["name"])}</h2></div>{faq_html(c["faq"])}</div></section>
{cta_band()}'''
    ld = [breadcrumb_ld(trail, "../"), faq_ld(c["faq"])]
    page(f"{c['folder']}/index.html", c["title"], c["meta"], body, active=c["key"], theme=c["theme"], ld=ld)


def build_service(c, s):
    pre = "../"
    trail = [(c["name"], f"index.html"), (s["nav"], None)]
    # روابط breadcrumb داخل المجلد نفسه نسبية للمجلد
    bc_items = [("الرئيسية", f"{pre}index.html"), (c["name"], "index.html"), (s["nav"], None)]
    bc = '<nav class="breadcrumb" aria-label="مسار التنقل"><ol>' + "".join(
        f'<li><a href="{h}">{e(l)}</a></li>' if h else f'<li aria-current="page">{e(l)}</li>' for l, h in bc_items
    ) + "</ol></nav>"
    hero = f'''<section class="page-hero"><div class="container ph-grid"><div>{bc}<h1>{e(s["title"])}</h1><p class="lead">{e(s["summary"])}</p>
<div class="hero-actions">{btn_call()}{btn_wa(cls="btn-ghost")}</div></div>
<div class="ph-art">{photo(c["theme"], c["services"].index(s) + 1, "../")}</div></div></section>'''
    sym_t = s.get("symptoms_title", "الأعراض")
    cau_t = s.get("causes_title", "الأسباب الشائعة")
    sym = "".join(f'<li>{icon("fa-circle-check")} {e(x)}</li>' for x in s["symptoms"])
    cau = "".join(f'<li>{icon("fa-wrench")} {e(x)}</li>' for x in s["causes"])
    steps = "".join(f"<li><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>" for t, d in s["steps"])
    tips = "".join(f'<li>{icon("fa-lightbulb")} {e(x)}</li>' for x in s["tips"])
    alert = alert_box(s["alert"]) if s.get("alert") else (alert_box(c["alert"]) if c.get("alert") else "")
    others = "".join(
        f'<li><a href="{o["slug"]}.html">{icon("fa-chevron-left")} {e(o["nav"])}</a></li>'
        for o in c["services"] if o["slug"] != s["slug"]
    )
    idx = c["services"].index(s)
    article = f'''<article class="article">
{alert}
{('<figure class="hero-photo">' + photo(c["theme"], idx, "../") + "</figure>") if c["theme"] in PHOTOS else ""}
<p class="lead-p">{e(s["intro"])}</p>
<section class="block"><h2><span>{icon("fa-eye")}</span>{e(sym_t)}</h2><ul class="check-list">{sym}</ul></section>
<section class="block"><h2><span>{icon("fa-magnifying-glass")}</span>{e(cau_t)}</h2><ul class="check-list alt-ico">{cau}</ul></section>
<section class="block"><h2><span>{icon("fa-list-check")}</span>كيف نعالج المشكلة</h2><ol class="steps">{steps}</ol></section>
<section class="block"><h2><span>{icon("fa-lightbulb")}</span>نصائح قبل وصول الفني</h2><ul class="check-list tips">{tips}</ul></section>
<section class="block"><h2><span>{icon("fa-circle-question")}</span>أسئلة شائعة</h2>{faq_html(s["faq"])}</section>
<section class="block"><h2><span>{icon("fa-tags")}</span>الماركات التي نتعامل معها</h2><div class="theme-{c["theme"]}">{brand_chips(c["theme"])}</div></section>
<section class="block"><h2><span>{icon("fa-location-dot")}</span>نخدمك في محافظات الدلتا</h2>{area_chips(pre)}</section>
</article>'''
    side = f'''<aside class="sidebar"><div class="side-card contact"><h3>احجز فنيًا الآن</h3><p>{SITE["hours"]}.</p>{btn_call(f"اتصل: {ph()}")}{btn_wa()}</div>
<div class="side-card"><h3>خدمات أخرى في {e(c["name"])}</h3><ul class="side-list">{others}</ul><a class="sub-all" href="index.html">كل خدمات {e(c["name"])} {icon("fa-arrow-left")}</a></div></aside>'''
    body = hero + f'<section class="section"><div class="container article-grid">{article}{side}</div></section>' + cta_band()
    ld = [
        {"@type": "Service", "name": s["title"], "description": s["meta"], "serviceType": c["title"],
         "provider": {"@type": "LocalBusiness", "name": FULL_NAME, "telephone": SITE["phone_intl"]}},
        breadcrumb_ld([(c["name"], ""), (s["nav"], "")], pre),
        faq_ld(s["faq"]),
    ]
    page(f"{c['folder']}/{s['slug']}.html", s["title"], s["meta"], body, active=c["key"], theme=c["theme"], ld=ld)


def build_areas():
    gov = "، ".join(a["name"] for a in AREAS)
    cards = "".join(
        f'<a class="area-card reveal" href="{a["slug"]}.html">{icon("fa-location-dot")}<strong>{e(a["name"])}</strong><small>{e("، ".join(a["cities"][:4]))}</small></a>'
        for a in AREAS
    )
    body = page_hero([("مناطق الخدمة", None)], "مناطق الخدمة في محافظات الدلتا", f"نغطي محافظات الدلتا: {gov}.", "../") + f'''
<section class="section"><div class="container"><div class="area-grid">{cards}</div></div></section>
<section class="section alt"><div class="container"><div class="section-head"><span class="eyebrow">موقعنا</span><h2>في قلب الدلتا</h2></div>
<iframe class="map" title="خريطة محافظات الدلتا" src="{SITE["map_src"]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div></section>
{cta_band()}'''
    page("areas/index.html", "مناطق الخدمة في محافظات الدلتا", f"خدماتي لصيانة الأجهزة المنزلية تخدم محافظات الدلتا: {gov}.", body, active="areas")
    for a in AREAS:
        cities = "".join(f'<li>{icon("fa-location-dot")} {e(x)}</li>' for x in a["cities"])
        svcs = "".join(
            f'<div class="pop theme-{c["theme"]}"><h3>{icon(c["icon"])} <a href="../{c["folder"]}/index.html">{e(c["title"])}</a></h3><ul>'
            + "".join(f'<li><a href="../{c["folder"]}/{s["slug"]}.html">{e(s["nav"])}</a></li>' for s in c["services"][:4])
            + "</ul></div>"
            for c in CATEGORIES
        )
        others = "".join(f'<a href="{o["slug"]}.html">{e(o["name"])}</a>' for o in AREAS if o["slug"] != a["slug"])
        body = page_hero([("مناطق الخدمة", "index.html"), (a["name"], None)], f"صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر في {a['name']}",
                         f"فنيو خدماتي يصلون إليك في مدن ومراكز محافظة {a['name']}.", "../")
        body = body.replace('<a href="index.html">مناطق الخدمة</a>', '<a href="index.html">مناطق الخدمة</a>')
        body += f'''
<section class="section"><div class="container narrow prose"><h2>خدمة صيانة في محافظة {e(a["name"])}</h2>
<p>نقدّم في محافظة {e(a["name"])} خدمات صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر بتشخيص واضح وتكلفة معلنة قبل البدء. تواصل معنا وحدد مدينتك أو قريتك لنؤكد لك أقرب موعد زيارة.</p>
<h3>المدن والمراكز التي نخدمها</h3><ul class="symptom-list cities">{cities}</ul>
<p class="muted">لا ترى منطقتك؟ اتصل بنا، فقد نغطيها أيضًا.</p></div></section>
<section class="section alt"><div class="container"><div class="section-head"><span class="eyebrow">خدماتنا في {e(a["name"])}</span><h2>ماذا نصلح لك</h2></div><div class="pop-grid">{svcs}</div></div></section>
<section class="section"><div class="container narrow"><div class="section-head"><span class="eyebrow">محافظات أخرى</span></div><div class="chips">{others}</div></div></section>
{cta_band()}'''
        page(f"areas/{a['slug']}.html", f"صيانة غسالات وغسالات أطباق وثلاجات وديب فريزر في {a['name']}",
             f"صيانة الغسالات وغسالات الأطباق والثلاجات والديب فريزر في {a['name']}: {'، '.join(a['cities'][:5])} وباقي المدن. اتصل بخدماتي.",
             body, active="areas")


def build_brands():
    groups = "".join(
        f'''<section class="section{" alt" if i % 2 == 0 else ""}"><div class="container narrow theme-{c["theme"]}">
<div class="section-head"><span class="eyebrow">{icon(c["icon"])} {e(c["name"])}</span><h2>ماركات {e(c["name"])}</h2></div>
{brand_chips(c["theme"])}
<p class="center"><a class="btn btn-cat" href="{cat_url(c, "")}">خدمات {e(c["name"])} {icon("fa-arrow-left")}</a></p></div></section>'''
        for i, c in enumerate(CATEGORIES)
    )
    body = page_hero([("الماركات", None)], "الماركات التي نتعامل معها", "نصلح أجهزة المطبخ والغسيل من أشهر الماركات المحلية والعالمية.", "") + groups + f'<section class="section"><div class="container narrow"><p class="brand-note">{e(BRANDS_NOTE)}</p><p class="brand-note">جهازك غير مذكور؟ اتصل بنا واذكر الماركة والموديل لنؤكد لك.</p></div></section>' + cta_band()
    page("brands.html", "الماركات التي نتعامل معها", "ماركات غسالات الأطباق والثلاجات والديب فريزر والغسالات التي نصلحها: بوش، سيمنز، إل جي، سامسونج، توشيبا، فريش وغيرها.", body, active="brands")


def main():
    build_home()
    build_areas()
    build_brands()
    build_services()
    build_about()
    build_contact()
    n = 6 + len(AREAS)
    for c in CATEGORIES:
        build_category(c)
        n += 1
        for s in c["services"]:
            build_service(c, s)
            n += 1
    print(f"تم توليد {n} صفحة")


if __name__ == "__main__":
    main()

# Pastki 5 bo'limli panel: Asosiy, Mahsulotlar, Savat, Savollar, Buyurtmalarim.
# build_site.py oxirida chaqiriladi (s = sayt matni).
def apply_tabs(s):
    def rep(old, new):
        nonlocal s
        assert old in s, "NOT FOUND: " + old[:90]
        s = s.replace(old, new, 1)

    # --- bo'limlarni belgilash (data-v) ---
    rep('<div class="promo" id="promo" hidden>', '<div class="promo" id="promo" data-v="home" hidden>')
    rep('<div class="wrap">\n  <div class="top">', '<div class="wrap" data-v="home">\n  <div class="top">')
    rep('<section class="sec" id="hits-sec"', '<section class="sec" data-v="home" id="hits-sec"')
    rep('<div class="wrap sec" id="combo-wrap"></div>', '<div class="wrap sec" data-v="home" id="combo-wrap"></div>')
    rep('<nav class="cats" id="cats-nav">', '<nav class="cats" data-v="menu" id="cats-nav">')
    rep('<main class="wrap">\n  <div id="menu"></div>', '''<main class="wrap">
  <div class="tab-head" data-v="menu"><h2 data-i18n="tab_menu"></h2></div>
  <div id="menu" data-v="menu"></div>

  <section class="sec tab-page" data-v="faq" aria-labelledby="faq-h">
    <div class="sec-head"><div><p class="eyebrow" data-i18n="faqEyebrow"></p><h2 id="faq-h" data-i18n="faqH"></h2></div></div>
    <div class="faq" id="faq"></div>
    <div class="faq-more"><p data-i18n="faqMore"></p><a class="btn primary" id="faq-call"></a></div>
  </section>

  <section class="sec tab-page" data-v="orders" aria-labelledby="ord-h">
    <div class="sec-head"><div><p class="eyebrow" data-i18n="ordEyebrow"></p><h2 id="ord-h" data-i18n="tab_orders"></h2></div></div>
    <div class="orders" id="orders"></div>
  </section>''')
    rep('<section class="sec" aria-labelledby="how-h">', '<section class="sec" data-v="home" aria-labelledby="how-h">')
    rep('<section class="sec" aria-labelledby="rev-h">', '<section class="sec" data-v="home" aria-labelledby="rev-h">')
    rep('<section class="sec" aria-labelledby="where-h">', '<section class="sec" data-v="home" aria-labelledby="where-h">')
    rep('<footer class="site">', '<footer class="site" data-v="home">')

    # --- pastki panel ---
    ic = {
      "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
      "menu": '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
      "cart": '<path d="M5 8h14l-1.3 11.2a2 2 0 0 1-2 1.8H8.3a2 2 0 0 1-2-1.8z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
      "faq": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2.2-2.4 3.8"/><circle cx="12" cy="17.2" r=".6" fill="currentColor"/>',
      "orders": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
    }
    btns = "".join(
      '<button type="button" data-tab="%s" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>%s<span data-i18n="tab_%s"></span></button>'
      % (k, ic[k], '<b class="badge" id="tab-badge" hidden></b>' if k == "cart" else "", k)
      for k in ["home", "menu", "cart", "faq", "orders"])
    rep('<div class="bar" id="bar-box">', '<nav class="tabbar" id="tabbar" aria-label="Bo\'limlar">' + btns + '</nav>\n<div class="bar" id="bar-box">')

    # --- uslublar ---
    rep('</style>\n<div id="page">', '''body{padding-bottom:calc(150px + env(safe-area-inset-bottom,0px))}
[data-v]{display:none!important}
body[data-tab="home"] [data-v~="home"],body[data-tab="menu"] [data-v~="menu"],body[data-tab="faq"] [data-v~="faq"],body[data-tab="orders"] [data-v~="orders"]{display:revert!important}
body[data-tab="menu"] nav.cats{display:block!important;margin-top:0}
body[data-tab="menu"] #menu,body[data-tab="home"] .wrap[data-v]{display:block!important}
body[data-tab="home"] .promo[data-v]:not([hidden]){display:block!important}
body[data-tab="home"] .promo[hidden]{display:none!important}
.tab-head{padding-top:18px}.tab-head h2{margin:0}
.tab-page{padding-top:18px}
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:11;display:grid;grid-template-columns:repeat(5,1fr);
  background:var(--surface);border-top:var(--bw) solid var(--line);
  padding:6px max(4px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(4px,env(safe-area-inset-left,0px))}
.tabbar button{position:relative;display:grid;justify-items:center;gap:3px;border:0;background:transparent;color:var(--muted);
  font:600 10px/1.15 var(--body);letter-spacing:-.01em;padding:6px 0;cursor:pointer;border-radius:var(--r-sm);min-width:0}
.tabbar button span{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tabbar svg{width:24px;height:24px}
@media (max-width:359px){.tabbar{padding-left:0;padding-right:0}.tabbar button{font-size:9px;letter-spacing:-.02em}}
.tabbar button[aria-pressed="true"]{color:var(--brand)}
.tabbar button[aria-pressed="true"] svg{stroke-width:2.4}
.tabbar .badge{position:absolute;top:2px;left:calc(50% + 6px);min-width:18px;height:18px;padding:0 5px;border-radius:999px;
  background:var(--hot);color:#fff;font:800 11px/18px var(--body);text-align:center}
.bar{bottom:calc(64px + env(safe-area-inset-bottom,0px))!important}
.bar:not(.has-cart){display:none}
body[data-tab="faq"] .bar,body[data-tab="orders"] .bar{display:none}
.toast{bottom:calc(150px + env(safe-area-inset-bottom,0px))!important}
.faq{display:grid;gap:8px}
.faq details{background:var(--surface);border:var(--bw) solid var(--line);border-radius:var(--r-sm);padding:0 16px}
.faq summary{cursor:pointer;font-weight:700;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:20px;line-height:1;color:var(--muted)}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:0 0 14px;color:var(--muted)}
.faq-more{margin-top:18px;display:grid;gap:10px;text-align:center}.faq-more p{margin:0;color:var(--muted)}
.orders{display:grid;gap:12px}
.ord{background:var(--surface);border:var(--bw) solid var(--line);border-radius:var(--r);padding:14px 16px;display:grid;gap:8px}
.ord .row1{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.ord .no{font-weight:800}
.ord .when{color:var(--muted);font-size:13px}
.ord .items{color:var(--muted);font-size:14px;margin:0}
.ord .row2{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.ord .sumv{font-weight:800}
.pill{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:800;padding:4px 10px;border-radius:999px;background:var(--surface2)}
.pill.st-accepted,.pill.st-onway,.pill.st-ready{background:color-mix(in srgb,var(--accent) 30%,var(--surface))}
.pill.st-done{background:color-mix(in srgb,var(--fill) 22%,var(--surface))}
.pill.st-canceled{background:color-mix(in srgb,var(--hot) 18%,var(--surface))}
.ord-empty{text-align:center;display:grid;gap:12px;justify-items:center;padding:30px 10px;color:var(--muted)}
.ord-empty svg{width:56px;height:56px;color:var(--line)}
</style>
<div id="page">''')

    # --- matnlar ---
    rep("var state = { lang: \"uz\",", '''Object.assign(I18N.uz, { tab_home: "Asosiy", tab_menu: "Mahsulotlar", tab_cart: "Savat", tab_faq: "Savollar", tab_orders: "Buyurtmalarim",
  faqEyebrow: "Yordam", faqH: "Ko'p beriladigan savollar", faqMore: "Javob topmadingizmi? Bizga qo'ng'iroq qiling.",
  ordEyebrow: "Tarix", ordEmpty: "Hali buyurtma bermadingiz. Menyudan taom tanlang, buyurtmangiz shu yerda ko'rinadi.", ordGo: "Menyuga o'tish",
  repeat: "Yana buyurtma berish", repeated: "Taomlar savatga qo'shildi", ordLoading: "Yuklanmoqda…", ordErr: "Buyurtmalarni yuklab bo'lmadi. Internetni tekshiring.",
  q1: "Yetkazib berish qancha vaqt oladi?", a1: "Odatda {t} daqiqa. Kechqurun va bayramlarda biroz ko'proq bo'lishi mumkin.",
  q2: "Yetkazish narxi qancha?", q3: "Qanday to'lasam bo'ladi?",
  q4: "Olib ketsam bo'ladimi?", a4: "Ha. Savatda \\"Olib ketaman\\" ni tanlang. Manzil: {a}",
  q5: "Buyurtmamni qanday kuzataman?", a5: "\\"Buyurtmalarim\\" bo'limida har bir buyurtmaning holati ko'rinadi: tayyorlanmoqda, yo'lda, yakunlandi.",
  q6: "Buyurtmani bekor qilsam yoki o'zgartirsam bo'ladimi?", a6: "Ha, taom tayyorlanishidan oldin. Iloji boricha tezroq qo'ng'iroq qiling: {p}",
  q7: "Ish vaqtingiz qanday?", a7always: "Har kuni, 24 soat ochiqmiz.", a7: "Har kuni {f} dan {to} gacha." });
Object.assign(I18N.ru, { tab_home: "Главная", tab_menu: "Меню", tab_cart: "Корзина", tab_faq: "Вопросы", tab_orders: "Мои заказы",
  faqEyebrow: "Помощь", faqH: "Частые вопросы", faqMore: "Не нашли ответ? Позвоните нам.",
  ordEyebrow: "История", ordEmpty: "Вы ещё не делали заказов. Выберите блюда в меню, и заказ появится здесь.", ordGo: "Перейти в меню",
  repeat: "Повторить заказ", repeated: "Блюда добавлены в корзину", ordLoading: "Загружаем…", ordErr: "Не удалось загрузить заказы. Проверьте интернет.",
  q1: "Сколько времени занимает доставка?", a1: "Обычно {t} минут. Вечером и в праздники может быть немного дольше.",
  q2: "Сколько стоит доставка?", q3: "Как можно оплатить?",
  q4: "Можно забрать самому?", a4: "Да. В корзине выберите «Самовывоз». Адрес: {a}",
  q5: "Как отследить заказ?", a5: "В разделе «Мои заказы» виден статус каждого заказа: готовится, в пути, выполнен.",
  q6: "Можно отменить или изменить заказ?", a6: "Да, пока его не начали готовить. Позвоните как можно скорее: {p}",
  q7: "Какой у вас режим работы?", a7always: "Каждый день, круглосуточно.", a7: "Каждый день с {f} до {to}." });
var state = { lang: "uz",''')

    # --- savat belgisi (badge) ---
    rep("function renderBar() {", '''function renderBar() {
  var bc = cartTotals().count, bd = $("tab-badge"); if (bd) { bd.hidden = !bc; bd.textContent = bc > 99 ? "99+" : bc; }''')

    # --- savollar va buyurtmalar, tab almashtirish ---
    rep("renderAll();\nloadPrices();", r'''/* ================= Pastki panel ================= */
var TAB_KEY = LS_KEY + ":tab";
function renderFaq() {
  var tz = function (z) { return (ZONES.length > 1 ? L(z.name) + ": " : "") + (z.fee ? money(z.fee) : t("free")) + (z.freeFrom ? ", " + t("freeFrom", { n: money(z.freeFrom) }) : "") + (z.min ? ", " + t("minOrder", { n: money(z.min) }) : ""); };
  var h = CONFIG.hours || { always: true };
  var tx = CONFIG.text[state.lang] || CONFIG.text.uz;
  var qa = [
    [t("q1"), t("a1", { t: nbr(CONFIG.delivery.time) })],
    [t("q2"), ZONES.map(tz).join(". ") + "."],
    [t("q3"), PAYS.map(function (p) { return t("pay_" + p); }).join(", ") + "."],
    [t("q4"), t("a4", { a: tx.address || "" })],
    [t("q5"), t("a5")],
    [t("q6"), t("a6", { p: CONFIG.phoneText })],
    [t("q7"), h.always ? t("a7always") : t("a7", { f: h.from, to: h.to })]
  ].concat((CONFIG.faq || []).map(function (f) { return [L(f.q), L(f.a)]; }));
  $("faq").innerHTML = qa.map(function (x) { return "<details><summary>" + esc(x[0]) + "</summary><p>" + esc(x[1]) + "</p></details>"; }).join("");
  $("faq-call").href = "tel:" + CONFIG.phone; $("faq-call").textContent = t("doneCall", { p: CONFIG.phoneText });
}

// Saytda berilgan buyurtmalar shu brauzerda saqlanadi; Telegram ichida server o'zi topadi
var MY_KEY = LS_KEY + ":orders";
function myList() { try { return JSON.parse(localStorage.getItem(MY_KEY) || "[]"); } catch (e) { return []; } }
function rememberOrder(d) {
  var l = myList().filter(function (o) { return o.id !== d.id; }); l.unshift({ id: d.id, token: d.token });
  try { localStorage.setItem(MY_KEY, JSON.stringify(l.slice(0, 20))); } catch (e) {}
}
var ordTimer = null, ORD = [];
function loadOrders() {
  var el = $("orders"), list = myList();
  if (!IN_TG && !list.length) return renderOrders([]);
  if (!ORD.length) el.innerHTML = '<p class="ord-empty">' + esc(t("ordLoading")) + "</p>";
  fetch(API_BASE + "/api/my", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ initData: IN_TG ? TG.initData : "", list: list }) })
    .then(function (r) { return r.json(); })
    .then(function (d) { renderOrders((d && d.orders) || []); })
    .catch(function () { if (!ORD.length) el.innerHTML = '<p class="ord-empty">' + esc(t("ordErr")) + "</p>"; });
}
function renderOrders(list) {
  ORD = list; var el = $("orders");
  if (!list.length) {
    el.innerHTML = '<div class="ord-empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/></svg><p>' + esc(t("ordEmpty")) + '</p><button type="button" class="btn primary" data-go="menu">' + esc(t("ordGo")) + "</button></div>";
    return;
  }
  el.innerHTML = list.map(function (o) {
    var dt = new Date(o.createdAt + 5 * 3600e3), hm = String(dt.getUTCHours()).padStart(2, "0") + ":" + String(dt.getUTCMinutes()).padStart(2, "0");
    var MON = state.lang === "ru" ? ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"] : ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
    var when = state.lang === "ru" ? dt.getUTCDate() + " " + MON[dt.getUTCMonth()] + ", " + hm : dt.getUTCDate() + "-" + MON[dt.getUTCMonth()] + ", " + hm;
    var items = (o.lines || []).map(function (l) { return l.qty + " × " + (ITEMS[l.id] ? L(ITEMS[l.id].name) : l.name); }).join(", ");
    var canRepeat = (o.lines || []).some(function (l) { return isOn(l.id); });
    var st = o.status === "accepted" || o.status === "new" || o.status === "done" || o.status === "canceled" ? o.status : o.status;
    return '<article class="ord"><div class="row1"><span class="no">№' + o.id + '</span><span class="pill st-' + esc(st) + '">' + esc(t("st_" + st)) + '</span></div>' +
      '<span class="when">' + esc(when) + "</span><p class=\"items\">" + esc(items) + "</p>" +
      '<div class="row2"><span class="sumv">' + money(o.total) + "</span>" +
      (canRepeat ? '<button type="button" class="btn ghost small" data-repeat="' + o.id + '">' + esc(t("repeat")) + "</button>" : "") + "</div></article>";
  }).join("");
}
function setTab(tab, opts) {
  opts = opts || {};
  if (tab === "cart") { if (cartTotals().count) { openSheet("sheet"); } else { toast(t("cart") + ": 0"); setTab("menu"); } return; }
  document.body.dataset.tab = tab;
  document.querySelectorAll("#tabbar button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.tab === tab)); });
  try { sessionStorage.setItem(TAB_KEY, tab); } catch (e) {}
  clearInterval(ordTimer);
  if (tab === "orders") { loadOrders(); ordTimer = setInterval(loadOrders, 15000); }
  if (TG && TG.BackButton) { try { tab === "home" ? TG.BackButton.hide() : TG.BackButton.show(); } catch (e) {} }
  if (!opts.keepScroll) window.scrollTo(0, 0);
}
document.addEventListener("click", function (e) {
  var b = e.target.closest("[data-tab],[data-go],[data-repeat]"); if (!b) return;
  if (b.dataset.tab) return setTab(b.dataset.tab);
  if (b.dataset.go) return setTab(b.dataset.go);
  var o = ORD.filter(function (x) { return String(x.id) === b.dataset.repeat; })[0]; if (!o) return;
  o.lines.forEach(function (l) { if (isOn(l.id)) state.cart[l.id] = Math.min(99, (state.cart[l.id] || 0) + l.qty); });
  state.orderNo = null; persist(); renderAll(); toast(t("repeated")); openSheet("sheet");
});
if (TG && TG.BackButton) { try { TG.BackButton.onClick(function () { if (!$("scrim").hidden) closeSheets(); else setTab("home"); }); } catch (e) {} }
// "Hammasi"/kategoriya va hit kartalaridan menyuga o'tish
(function () { var start = "home"; try { start = sessionStorage.getItem(TAB_KEY) || "home"; } catch (e) {} if (start === "cart") start = "menu"; document.body.dataset.tab = start; setTimeout(function () { setTab(start, { keepScroll: true }); }, 0); })();
var _renderStatic = renderStatic; renderStatic = function () { _renderStatic(); renderFaq(); if (ORD.length) renderOrders(ORD); };

renderAll();
loadPrices();''')

    # buyurtma berilgach: tarixga yozish
    rep("function showOk(d) {\n  state.cart = {};", "function showOk(d) {\n  if (!IN_TG) rememberOrder(d); ORD = [];\n  state.cart = {};")
    return s

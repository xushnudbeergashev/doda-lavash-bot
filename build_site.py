# Namuna saytni (Doda_Lavash.html) bizning buyurtma API'miz bilan ulaydi -> src/site.html
import sys
SRC=sys.argv[1]; OUT=sys.argv[2]
s=open(SRC).read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)>=1, "NOT FOUND: "+old[:90]
    s=s.replace(old,new,cnt)

# 1) Telegram WebApp skripti + ishlab chiqarishda dizayn tanlash panelini yashirish
rep('<div class="sr" id="sr" aria-live="polite"></div>\n\n<script>',
'''<div class="sr" id="sr" aria-live="polite"></div>

<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script>''')
rep('</style>\n<div id="page">','''.prod-site #designs,.prod-site .demo b,.prod-site .demo-note{display:none}
.track{display:grid;gap:8px;width:100%;max-width:340px;text-align:left;margin:4px auto 0;padding:0;list-style:none}
.track li{display:flex;gap:10px;align-items:center;color:var(--muted);font-size:15px}
.track li i{width:12px;height:12px;border-radius:50%;border:2px solid currentColor;flex:none}
.track li.on{color:var(--ink);font-weight:700}
.track li.on i{background:var(--accent);border-color:var(--accent)}
.track li.cur i{box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 30%,transparent)}
#geo-btn{width:100%}
</style>
<div id="page">''')

# 2) Joylashuv tugmasi (manzil maydonidan keyin)
rep('<div class="field" id="mark-field"><label for="o-mark" data-i18n="markLbl"></label><input id="o-mark"></div>',
'<div class="field" id="mark-field"><label for="o-mark" data-i18n="markLbl"></label><input id="o-mark"></div>\n    <div class="field" id="geo-field"><button type="button" class="btn ghost" id="geo-btn"></button></div>')
# 3) Holat ro'yxati
rep('<p id="done-p"></p>','<p id="done-p"></p>\n    <ol class="track" id="track" hidden></ol>')

# 4) Matnlar va sozlamalar
rep('Telegram orqali buyurtma bering, {time} daqiqada yetkazamiz.','Saytdan yoki Telegram botdan buyurtma bering, {time} daqiqada yetkazamiz.')
rep('Закажите в Telegram — привезём за {time} минут.','Закажите на сайте или в Telegram-боте — привезём за {time} минут.')
rep('var state = { lang: "uz",','''
/* ===== Buyurtma API (Cloudflare Worker) ===== */
var API_BASE = typeof window.DL_API === "string" ? window.DL_API : "";   // bo'sh = shu sayt manzili
var TG = window.Telegram && window.Telegram.WebApp, IN_TG = !!(TG && TG.initData);
if (TG) { try { TG.ready(); TG.expand(); } catch (e) {} }
if (!window.DL_DEMO && !/demo/.test(location.hash)) document.documentElement.classList.add("prod-site");
Object.assign(I18N.uz, { send: "Buyurtma berish · {n}", sending: "Yuborilmoqda…",
  step2: "Buyurtma bering", step2d: "Ism, telefon va manzilni yozing. Buyurtma to'g'ridan-to'g'ri oshxonaga tushadi.",
  okH: "Buyurtma №{no} qabul qilindi", okP: "Operator tez orada qo'ng'iroq qilib tasdiqlaydi. Holatini shu yerda kuzatib boring.",
  okTgP: "Tafsilotlar bot chatiga yuborildi. Holati o'zgarsa, bot xabar beradi.",
  st_new: "Qabul qilindi, tasdiq kutilmoqda", st_accepted: "Tayyorlanmoqda", st_onway: "Kuryer yo'lda", st_ready: "Tayyor, olib ketishingiz mumkin",
  st_done: "Yakunlandi. Yoqimli ishtaha!", st_canceled: "Bekor qilindi. Savol bo'lsa, qo'ng'iroq qiling",
  netErr: "Buyurtma serverga yetmadi, shuning uchun Telegram orqali yuboring.",
  geo: "📍 Joylashuvimni qo'shish (ixtiyoriy)", geoWait: "Aniqlanmoqda…", geoOk: "✅ Joylashuv qo'shildi", geoErr: "Joylashuv olinmadi. Manzil va mo'ljalni yozing." });
Object.assign(I18N.ru, { send: "Оформить заказ · {n}", sending: "Отправляем…",
  step2: "Оформите заказ", step2d: "Укажите имя, телефон и адрес. Заказ сразу попадёт на кухню.",
  okH: "Заказ №{no} принят", okP: "Оператор скоро перезвонит и подтвердит заказ. Статус можно смотреть здесь.",
  okTgP: "Детали отправлены в чат бота. Бот сообщит, когда статус изменится.",
  st_new: "Принят, ждёт подтверждения", st_accepted: "Готовится", st_onway: "Курьер в пути", st_ready: "Готов, можно забирать",
  st_done: "Выполнен. Приятного аппетита!", st_canceled: "Отменён. Если есть вопросы, позвоните",
  netErr: "Заказ не дошёл до сервера, поэтому отправьте его через Telegram.",
  geo: "📍 Добавить моё местоположение (необязательно)", geoWait: "Определяем…", geoOk: "✅ Местоположение добавлено", geoErr: "Не удалось определить. Укажите адрес и ориентир." });
var state = { lang: "uz",''')

# 5) Yuborish: API orqali, xato bo'lsa eski Telegram-matn usuli
old_start='  var txt = orderText(), link = tgLink(txt);\n  try { navigator.clipboard.writeText(txt).catch(function () { fallbackCopy(txt); }); } catch (err) { fallbackCopy(txt); }'
i=s.index(old_start); j=s.index('$("done").querySelector("[data-close]").focus();\n});',i)+len('$("done").querySelector("[data-close]").focus();\n});')
s=s[:i]+'''  sendOrder();
});

function sendOrder() {
  var tt = cartTotals(), btn = $("send");
  var body = { initData: IN_TG ? TG.initData : "", cart: state.cart, type: state.mode, zone: tt.zone.id, payment: state.pay || "cash",
    name: $("o-name").value.trim(), phone: $("o-phone").value.trim(), address: $("o-addr").value.trim(), landmark: $("o-mark").value.trim(),
    change: $("o-change").value.trim(), comment: $("o-note").value.trim(), lang: state.lang };
  if (state.geo && state.mode === "delivery") { body.lat = state.geo.lat; body.lon = state.geo.lon; }
  btn.disabled = true; $("send-label").textContent = t("sending");
  fetch(API_BASE + "/api/order", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d && d.ok) return showOk(d);
      renderSheet(); $("min-err").hidden = false; $("min-err").textContent = (d && d.error) || t("netErr");
    })
    .catch(function () { renderSheet(); sendViaTelegram(); });
}

function showOk(d) {
  state.cart = {}; state.orderNo = null; persist();
  $("order").hidden = true; $("done").hidden = false; renderAll();
  $("done-h").textContent = t("okH", { no: d.id });
  $("done-p").textContent = IN_TG ? t("okTgP") : t("okP");
  $("done-tg").hidden = true; $("done-copy").hidden = true;
  $("done-call").href = "tel:" + CONFIG.phone; $("done-call").textContent = t("doneCall", { p: CONFIG.phoneText });
  try { TG && TG.HapticFeedback && TG.HapticFeedback.notificationOccurred("success"); } catch (e) {}
  if (IN_TG) { $("track").hidden = true; setTimeout(function () { try { TG.close(); } catch (e) {} }, 3500); }
  else track(d);
  $("done").querySelector("[data-close]").focus();
}

var trackTimer = null;
function track(d) {
  var el = $("track"); el.hidden = false; clearInterval(trackTimer);
  var poll = function () {
    fetch(API_BASE + "/api/status?id=" + d.id + "&token=" + d.token).then(function (r) { return r.json(); }).then(function (s) {
      if (!s || !s.ok) return;
      var flow = s.status === "canceled" ? ["new", "canceled"] : ["new", "accepted", s.type === "delivery" ? "onway" : "ready", "done"];
      var cur = flow.indexOf(s.status);
      el.innerHTML = flow.map(function (k, i) { return '<li class="' + (i <= cur ? "on" : "") + (i === cur ? " cur" : "") + '"><i></i>' + esc(t("st_" + k)) + "</li>"; }).join("");
      if (s.status === "done" || s.status === "canceled") clearInterval(trackTimer);
    }).catch(function () {});
  };
  el.innerHTML = '<li class="on cur"><i></i>' + esc(t("st_new")) + "</li>";
  poll(); trackTimer = setInterval(poll, 10000);
}

// Server ishlamasa: eski usul, buyurtma matni Telegram chatga
function sendViaTelegram() {
  var txt = orderText(), link = tgLink(txt);
  try { navigator.clipboard.writeText(txt).catch(function () { fallbackCopy(txt); }); } catch (err) { fallbackCopy(txt); }
  var a = document.createElement("a"); a.href = link; a.target = "_blank"; a.rel = "noopener"; document.body.appendChild(a); a.click(); a.remove();
  $("order").hidden = true; $("done").hidden = false; $("track").hidden = true;
  $("done-tg").hidden = false; $("done-copy").hidden = false;
  $("done-h").textContent = t("doneH", { no: orderNo() });
  $("done-p").textContent = t("netErr") + " " + t("doneP");
  $("done-tg").href = link; $("done-tg").textContent = t("doneTg");
  $("done-copy").textContent = t("copy");
  $("done-call").href = "tel:" + CONFIG.phone; $("done-call").textContent = t("doneCall", { p: CONFIG.phoneText });
  $("done").querySelector("[data-close]").focus();
}

// Joylashuv (faqat sayt uchun; Telegram ichida bot o'zi so'raydi)
function renderGeo() {
  var b = $("geo-btn"); if (!b) return;
  $("geo-field").hidden = IN_TG || state.mode !== "delivery" || !navigator.geolocation;
  if (!b.dataset.busy) b.textContent = state.geo ? t("geoOk") : t("geo");
}
$("geo-btn").addEventListener("click", function () {
  var b = $("geo-btn"); b.dataset.busy = "1"; b.textContent = t("geoWait");
  navigator.geolocation.getCurrentPosition(function (p) {
    state.geo = { lat: p.coords.latitude, lon: p.coords.longitude }; delete b.dataset.busy; renderGeo();
  }, function () { delete b.dataset.busy; b.textContent = t("geoErr"); }, { enableHighAccuracy: true, timeout: 10000 });
});
if (IN_TG && TG.initDataUnsafe && TG.initDataUnsafe.user) {
  var tu = TG.initDataUnsafe.user; if (!$("o-name").value) $("o-name").value = [tu.first_name, tu.last_name].filter(Boolean).join(" ");
}'''+s[j:]

# renderSheet oxirida geo tugmasini yangilash
rep('  $("send-label").textContent = t("send", { n: money(tt.total) });','  $("send-label").textContent = t("send", { n: money(tt.total) });\n  if (typeof renderGeo === "function") renderGeo();')
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tabs import apply_tabs
s = apply_tabs(s)
open(OUT,'w').write(s)
print("ok", len(s))

// Doda Lavash — Telegram buyurtma boti + Mini App (Cloudflare Workers)
// Kerakli sozlamalar (wrangler secret / vars):
//   BOT_TOKEN       — @BotFather bergan token
//   ADMIN_CHAT_ID   — buyurtmalar boradigan chat (admin yoki guruh id)
//   WEBHOOK_SECRET  — ixtiyoriy uzun so'z (webhook himoyasi)
//   KV: ORDERS      — buyurtmalar saqlanadigan KV namespace
import { SHOP, ITEMS } from "./menu.js";
import SITE_HTML from "./site.html";

const STATUS = {
  new: "🆕 Yangi",
  accepted: "👨‍🍳 Tayyorlanmoqda",
  onway: "🚗 Yo'lda",
  ready: "✅ Tayyor (olib ketish mumkin)",
  done: "🏁 Yakunlandi",
  canceled: "❌ Bekor qilindi",
};
const CUSTOMER_TEXT = {
  accepted: "👨‍🍳 Buyurtmangiz qabul qilindi va tayyorlanmoqda!",
  onway: "🚗 Buyurtmangiz yo'lda! Kuryer tez orada yetib boradi.",
  ready: "✅ Buyurtmangiz tayyor! Olib ketishingiz mumkin.",
  done: "🏁 Yoqimli ishtaha! Bizni tanlaganingiz uchun rahmat 🙏",
  canceled: "❌ Afsuski, buyurtmangiz bekor qilindi. Savol bo'lsa: " + SHOP.phone,
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname === "/" || url.pathname === "/app")
        return new Response(SITE_HTML, { headers: { "content-type": "text/html; charset=utf-8" } });
      if (url.pathname === "/api/order" && request.method === "POST")
        return await createOrder(request, env);
      if (url.pathname === "/api/status") return await orderStatus(url, env);
      if (url.pathname === "/api/my" && request.method === "POST") return await myOrders(request, env);
      if (url.pathname === "/webhook" && request.method === "POST") {
        if (env.WEBHOOK_SECRET && request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET)
          return new Response("forbidden", { status: 403 });
        await handleUpdate(await request.json(), env, url.origin);
        return new Response("ok");
      }
      if (url.pathname === "/setup") return await setup(env, url);
      return new Response("Not found", { status: 404 });
    } catch (e) {
      console.error(e);
      return json({ ok: false, error: "Server xatosi" }, 500);
    }
  },
};

// ---------- Mini App API ----------
async function createOrder(request, env) {
  const body = await request.json();
  // Telegram Mini App ichidan bo'lsa — imzo tekshiriladi; aks holda bu sayt (web) buyurtmasi
  let user = null;
  if (body.initData) {
    user = await verifyInitData(body.initData, env.BOT_TOKEN);
    if (!user) return json({ ok: false, error: "Telegram ma'lumotlari noto'g'ri, qayta oching" }, 401);
  } else {
    // Spamdan himoya: bitta IP dan 10 daqiqada ko'pi bilan 3 ta buyurtma
    const ip = request.headers.get("CF-Connecting-IP") || "local";
    const key = `rl:${ip}`;
    const n = parseInt((await env.ORDERS.get(key)) || "0");
    if (n >= 3) return json({ ok: false, error: "Juda ko'p buyurtma. Biroz kuting yoki qo'ng'iroq qiling: " + SHOP.phone }, 429);
    await env.ORDERS.put(key, String(n + 1), { expirationTtl: 600 });
  }
  const preorder = !isOpen(); // yopiq paytda ham qabul qilamiz, lekin "oldindan buyurtma" deb belgilaymiz

  // Narxni serverda qayta hisoblaymiz (mijoz narxni o'zgartira olmasin)
  const lines = [];
  for (const [id, qty] of Object.entries(body.cart || {})) {
    const item = ITEMS.find((i) => i.id === id);
    const q = Math.min(50, Math.max(0, parseInt(qty) || 0));
    if (item && q > 0) lines.push({ id: item.id, name: item.name, price: item.price, qty: q });
  }
  if (!lines.length) return json({ ok: false, error: "Savat bo'sh" }, 400);
  const subtotal = lines.reduce((s, l) => s + l.price * l.qty, 0);
  const delivery = body.type === "delivery";
  const zone = SHOP.zones.find((z) => z.id === body.zone) || SHOP.zones[0];
  if (delivery && subtotal < zone.min) return json({ ok: false, error: `Yetkazish uchun minimal buyurtma ${fmt(zone.min)}` }, 400);
  const fee = delivery && !(zone.freeFrom && subtotal >= zone.freeFrom) ? zone.fee : 0;
  const name = clean(body.name, 60);
  const phone = clean(body.phone, 20);
  const address = clean(body.address, 200);
  const landmark = clean(body.landmark, 120);
  if (!/^\+?[\d\s()-]{9,20}$/.test(phone)) return json({ ok: false, error: "Telefon raqamini to'g'ri kiriting" }, 400);
  if (delivery && !address && !landmark) return json({ ok: false, error: "Manzil yoki mo'ljalni yozing" }, 400);

  const lat = Number(body.lat), lon = Number(body.lon);
  const hasLoc = delivery && isFinite(lat) && isFinite(lon) && lat !== 0 && Math.abs(lat) <= 90 && Math.abs(lon) <= 180;

  const id = await nextId(env);
  const token = crypto.randomUUID().slice(0, 8);
  const order = {
    id, token, source: user ? "telegram" : "web",
    userId: user ? user.id : null, username: user?.username || "", name, phone,
    type: delivery ? "delivery" : "pickup", address, landmark, zone: delivery ? zone.name : "", preorder,
    payment: SHOP.payments[body.payment] ? body.payment : "cash", change: clean(body.change, 30),
    comment: clean(body.comment, 300), lines, subtotal, fee, total: subtotal + fee,
    status: "new", createdAt: Date.now(),
  };
  await env.ORDERS.put(`order:${id}`, JSON.stringify(order), { expirationTtl: 60 * 60 * 24 * 30 });

  const sent = await tg(env, "sendMessage", {
    chat_id: env.ADMIN_CHAT_ID, text: adminText(order), parse_mode: "HTML",
    reply_markup: adminButtons(order),
  });
  order.adminMsgId = sent?.result?.message_id;
  await env.ORDERS.put(`order:${id}`, JSON.stringify(order), { expirationTtl: 60 * 60 * 24 * 30 });
  if (user) { // Telegram foydalanuvchisining buyurtmalar ro'yxati ("Buyurtmalarim" uchun)
    const ids = JSON.parse((await env.ORDERS.get(`user:${user.id}`)) || "[]");
    ids.unshift(id);
    await env.ORDERS.put(`user:${user.id}`, JSON.stringify(ids.slice(0, 20)), { expirationTtl: 60 * 60 * 24 * 30 });
  }
  if (hasLoc) await tg(env, "sendLocation", { chat_id: env.ADMIN_CHAT_ID, latitude: lat, longitude: lon, reply_to_message_id: order.adminMsgId });

  if (!user) return json({ ok: true, id, token, total: order.total });

  let txt = `✅ Buyurtma #${id} qabul qilindi!\n\n${linesText(order)}\n\n` +
    `Jami: <b>${fmt(order.total)}</b>\n` +
    (order.payment === "click" || order.payment === "payme" ? `\n💳 ${SHOP.payments[order.payment]} orqali to'lov: operator havola yuboradi. To'lagach, chek rasmini shu yerga tashlang.\n` : "") +
    `\nTez orada operator bog'lanadi.`;
  await tg(env, "sendMessage", { chat_id: user.id, text: txt, parse_mode: "HTML" });
  if (delivery && !hasLoc) {
    await env.ORDERS.put(`await_loc:${user.id}`, String(id), { expirationTtl: 3600 });
    await tg(env, "sendMessage", {
      chat_id: user.id,
      text: "📍 Kuryer tez topishi uchun lokatsiyangizni yuboring (ixtiyoriy):",
      reply_markup: { keyboard: [[{ text: "📍 Lokatsiyani yuborish", request_location: true }], [{ text: "O'tkazib yuborish" }]], resize_keyboard: true, one_time_keyboard: true },
    });
  }
  if (order.payment === "click" || order.payment === "payme") await env.ORDERS.put(`await_check:${user.id}`, String(id), { expirationTtl: 3600 * 3 });
  return json({ ok: true, id, token });
}

// Sayt uchun buyurtma holati (id + maxfiy token bilan)
async function orderStatus(url, env) {
  const raw = await env.ORDERS.get(`order:${parseInt(url.searchParams.get("id"))}`);
  const o = raw && JSON.parse(raw);
  if (!o || o.token !== url.searchParams.get("token")) return json({ ok: false }, 404);
  return json({ ok: true, id: o.id, status: o.status, label: STATUS[o.status], type: o.type, total: o.total });
}

// "Buyurtmalarim": Telegram ichida — imzo bo'yicha; saytda — brauzer saqlagan id+token juftlari bo'yicha
async function myOrders(request, env) {
  const body = await request.json().catch(() => ({}));
  let pairs = [];
  if (body.initData) {
    const user = await verifyInitData(body.initData, env.BOT_TOKEN);
    if (!user) return json({ ok: false, error: "Telegram ma'lumotlari noto'g'ri" }, 401);
    const ids = JSON.parse((await env.ORDERS.get(`user:${user.id}`)) || "[]");
    pairs = ids.map((id) => ({ id, uid: user.id }));
  } else if (Array.isArray(body.list)) {
    pairs = body.list.slice(0, 20).map((o) => ({ id: parseInt(o.id), token: String(o.token || "") }));
  }
  const out = [];
  for (const p of pairs) {
    const raw = await env.ORDERS.get(`order:${p.id}`);
    if (!raw) continue;
    const o = JSON.parse(raw);
    if (p.uid ? o.userId !== p.uid : o.token !== p.token) continue;
    out.push({ id: o.id, status: o.status, type: o.type, total: o.total, createdAt: o.createdAt,
      lines: o.lines.map((l) => ({ id: l.id, name: l.name, qty: l.qty })) });
  }
  return json({ ok: true, orders: out });
}

// ---------- Bot ----------
async function handleUpdate(u, env, origin) {
  if (u.callback_query) return onCallback(u.callback_query, env);
  const m = u.message;
  if (!m) return;
  const chatId = m.chat.id;

  if (m.text?.startsWith("/start")) {
    await tg(env, "sendMessage", {
      chat_id: chatId,
      text: `Assalomu alaykum! 👋\n<b>${SHOP.name}</b> ga xush kelibsiz.\n\nMenyuni ochib, buyurtma bering 👇`,
      parse_mode: "HTML",
      reply_markup: { inline_keyboard: [[{ text: "🌯 Menyuni ochish", web_app: { url: origin + "/app" } }], [{ text: "📞 Aloqa", callback_data: "contact" }]] },
    });
    await tg(env, "setChatMenuButton", { chat_id: chatId, menu_button: { type: "web_app", text: "Menyu", web_app: { url: origin + "/app" } } });
    return;
  }
  if (m.text === "/id") return tg(env, "sendMessage", { chat_id: chatId, text: `Chat ID: <code>${chatId}</code>`, parse_mode: "HTML" });

  // Lokatsiya
  if (m.location) {
    const id = await env.ORDERS.get(`await_loc:${m.from.id}`);
    if (!id) return;
    await env.ORDERS.delete(`await_loc:${m.from.id}`);
    await tg(env, "sendMessage", { chat_id: env.ADMIN_CHAT_ID, text: `📍 #${id} buyurtma lokatsiyasi:` });
    await tg(env, "sendLocation", { chat_id: env.ADMIN_CHAT_ID, latitude: m.location.latitude, longitude: m.location.longitude });
    return tg(env, "sendMessage", { chat_id: chatId, text: "Rahmat! Lokatsiya kuryerga yuborildi ✅", reply_markup: { remove_keyboard: true } });
  }
  if (m.text === "O'tkazib yuborish") {
    await env.ORDERS.delete(`await_loc:${m.from.id}`);
    return tg(env, "sendMessage", { chat_id: chatId, text: "Yaxshi 👍", reply_markup: { remove_keyboard: true } });
  }
  // To'lov cheki (rasm)
  if (m.photo || m.document) {
    const id = await env.ORDERS.get(`await_check:${m.from.id}`);
    if (!id) return;
    await env.ORDERS.delete(`await_check:${m.from.id}`);
    await tg(env, "forwardMessage", { chat_id: env.ADMIN_CHAT_ID, from_chat_id: chatId, message_id: m.message_id });
    await tg(env, "sendMessage", { chat_id: env.ADMIN_CHAT_ID, text: `💳 Yuqoridagi chek #${id} buyurtma uchun` });
    return tg(env, "sendMessage", { chat_id: chatId, text: "Chek qabul qilindi, tekshiramiz ✅" });
  }
}

async function onCallback(q, env) {
  if (q.data === "contact") {
    await tg(env, "answerCallbackQuery", { callback_query_id: q.id });
    return tg(env, "sendMessage", { chat_id: q.from.id, text: `📞 ${SHOP.phone}\n📍 ${SHOP.pickupAddress}\n🕙 ${SHOP.hours.always ? "24/7" : `${SHOP.hours.open}:00–${SHOP.hours.close}:00`}` });
  }
  const [, id, status] = (q.data || "").split(":");
  if (!q.data?.startsWith("st:") || !STATUS[status]) return;
  if (String(q.message?.chat?.id) !== String(env.ADMIN_CHAT_ID))
    return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: "Ruxsat yo'q" });
  const raw = await env.ORDERS.get(`order:${id}`);
  if (!raw) return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: "Buyurtma topilmadi" });
  const order = JSON.parse(raw);
  order.status = status;
  order.by = q.from.first_name;
  await env.ORDERS.put(`order:${id}`, JSON.stringify(order), { expirationTtl: 60 * 60 * 24 * 30 });
  await tg(env, "editMessageText", {
    chat_id: q.message.chat.id, message_id: q.message.message_id,
    text: adminText(order), parse_mode: "HTML", reply_markup: adminButtons(order),
  });
  if (order.userId) await tg(env, "sendMessage", { chat_id: order.userId, text: `#${id}: ${CUSTOMER_TEXT[status]}` });
  return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: STATUS[status] });
}

function adminButtons(o) {
  const b = (t, s) => ({ text: t, callback_data: `st:${o.id}:${s}` });
  if (o.status === "new") return { inline_keyboard: [[b("✅ Qabul qilish", "accepted"), b("❌ Bekor", "canceled")]] };
  if (o.status === "accepted")
    return { inline_keyboard: [[o.type === "delivery" ? b("🚗 Yo'lga chiqdi", "onway") : b("✅ Tayyor", "ready")], [b("❌ Bekor", "canceled")]] };
  if (o.status === "onway" || o.status === "ready") return { inline_keyboard: [[b("🏁 Yakunlandi", "done")]] };
  return { inline_keyboard: [] };
}

function adminText(o) {
  const user = !o.userId ? "🌐 sayt orqali — telefon qiling" : o.username ? `@${esc(o.username)}` : `<a href="tg://user?id=${o.userId}">profil</a>`;
  return (o.preorder ? "⏰ <b>OLDINDAN BUYURTMA</b>\n" : "") + `<b>Buyurtma #${o.id}</b> — ${STATUS[o.status]}${o.by && o.status !== "new" ? ` (${esc(o.by)})` : ""}\n\n` +
    `👤 ${esc(o.name || "—")} (${user})\n📞 ${esc(o.phone)}\n` +
    (o.type === "delivery" ? `🚗 Yetkazish (${esc(o.zone)}): ${esc(o.address || "—")}\n` + (o.landmark ? `🧭 Mo'ljal: ${esc(o.landmark)}\n` : "") : `🏃 Olib ketish\n`) +
    `💰 To'lov: ${SHOP.payments[o.payment] || "Naqd"}${o.change ? ` (qaytim: ${esc(o.change)} dan)` : ""}\n` +
    (o.comment ? `💬 ${esc(o.comment)}\n` : "") +
    `\n${linesText(o)}\n` +
    (o.fee ? `Yetkazib berish: ${fmt(o.fee)}\n` : "") +
    `<b>Jami: ${fmt(o.total)}</b>`;
}
const linesText = (o) => o.lines.map((l) => `• ${esc(l.name)} × ${l.qty} = ${fmt(l.price * l.qty)}`).join("\n");

// ---------- Yordamchilar ----------
async function setup(env, url) {
  if (url.searchParams.get("key") !== env.WEBHOOK_SECRET) return new Response("key noto'g'ri", { status: 403 });
  const r1 = await tg(env, "setWebhook", { url: url.origin + "/webhook", secret_token: env.WEBHOOK_SECRET, allowed_updates: ["message", "callback_query"] });
  const r2 = await tg(env, "setChatMenuButton", { menu_button: { type: "web_app", text: "Menyu", web_app: { url: url.origin + "/app" } } });
  await tg(env, "setMyCommands", { commands: [{ command: "start", description: "Menyu va buyurtma" }] });
  return json({ webhook: r1, menuButton: r2 });
}

async function tg(env, method, payload) {
  let j = null;
  try {
    const r = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/${method}`, {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload),
    });
    j = await r.json();
  } catch (e) { console.log(method, "tarmoq xatosi", e.message); }
  if (!j?.ok) console.log(method, JSON.stringify(j));
  return j;
}

async function verifyInitData(initData, botToken) {
  if (!initData || !botToken) return null;
  const p = new URLSearchParams(initData);
  const hash = p.get("hash");
  p.delete("hash");
  const dataCheck = [...p.entries()].map(([k, v]) => `${k}=${v}`).sort().join("\n");
  const enc = new TextEncoder();
  const k1 = await crypto.subtle.importKey("raw", enc.encode("WebAppData"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const secret = await crypto.subtle.sign("HMAC", k1, enc.encode(botToken));
  const k2 = await crypto.subtle.importKey("raw", secret, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k2, enc.encode(dataCheck));
  const hex = [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
  if (hex !== hash) return null;
  if (Date.now() / 1000 - Number(p.get("auth_date")) > 86400) return null;
  try { return JSON.parse(p.get("user")); } catch { return null; }
}

async function nextId(env) {
  const n = parseInt((await env.ORDERS.get("counter")) || "1000") + 1;
  await env.ORDERS.put("counter", String(n));
  return n;
}
function isOpen() {
  if (SHOP.hours.always) return true;
  const h = (new Date().getUTCHours() + 5) % 24; // Toshkent vaqti
  const { open, close } = SHOP.hours;
  return open < close ? h >= open && h < close : h >= open || h < close;
}
const fmt = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " so'm";
const clean = (s, max) => String(s || "").trim().slice(0, max);
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const json = (d, status = 200) => new Response(JSON.stringify(d), { status, headers: { "content-type": "application/json" } });

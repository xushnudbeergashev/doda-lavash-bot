# Doda Lavash — buyurtma boti + Mini App

Cloudflare Workers'da ishlaydi (xuddi @hadyaga_mushuk_bot kabi). Bitta Worker: bot, Mini App va API.

## Nima qila oladi
- /start → "Menyuni ochish" tugmasi (Mini App) + pastdagi "Menyu" tugmasi
- Mini App: kategoriyalar, savat, yetkazib berish yoki olib ketish, naqd yoki karta, izoh
- Narx serverda qayta hisoblanadi (mijoz narxni o'zgartira olmaydi), Telegram imzosi tekshiriladi
- Buyurtma admin chatga keladi, tugmalar: Qabul qilish → Yo'lga chiqdi / Tayyor → Yakunlandi, yoki Bekor
- Har bir holatda mijozga avtomatik xabar boradi
- Yetkazib berishda bot lokatsiya so'raydi va kuryerga (admin chatga) yuboradi
- Kartaga to'lovda mijoz chek rasmini botga tashlaydi, u admin chatga boradi
- Ish vaqti, minimal buyurtma, bepul yetkazib berish chegarasi

## Sayt va menyu
- Sayt (va Telegram Mini App) — `src/site.html`. U siz yuborgan namuna dizayndan yasalgan, faqat buyurtma endi to'g'ridan-to'g'ri admin chatga tushadi va holati saytda ko'rinadi. Server ishlamay qolsa, sayt eski usulga o'tadi: buyurtma matni Telegram chatga yuboriladi.
- Menyu, narxlar, hududlar, matnlar: `src/site.html` ichidagi `CONFIG` bloki.
- **Narx yoki taom o'zgarsa, `src/menu.js` ni ham o'zgartiring** (id lar bir xil bo'lsin). Server summani shu fayldagi narxlar bilan hisoblaydi, shuning uchun mijoz narxni aldab o'zgartira olmaydi.
- Sharhlar (`CONFIG.reviews`) hozir namuna. Google'dagi haqiqiy sharhlar bilan almashtiring yoki bo'sh qoldiring.
- Dizayn tanlash paneli (Yashil, Olov, Rishton) saytda yashirin. Mijozga ko'rsatish uchun manzil oxiriga `#demo` qo'shing.
- `build_site.py` — namuna fayldan (`design/namuna.html`) `site.html` ni qayta yasaydi: `python3 build_site.py design/namuna.html src/site.html`

## Avtomatik yangilanish (GitHub → Cloudflare)
Cloudflare'da Worker'ga shu repo ulangan (Settings → Builds). `main` ga har bir push botni o'zi qayta joylaydi.
Maxfiy narsalar repo'da yo'q: `BOT_TOKEN`, `WEBHOOK_SECRET` (secret) va `ADMIN_CHAT_ID` (variable) Cloudflare panelida saqlanadi.

## O'rnatish (bir marta, qo'lda)
1. @BotFather → yangi bot → tokenni oling.
2. Papkada: `npm install`, keyin `npx wrangler login`.
3. `npx wrangler kv namespace create ORDERS` → chiqqan `id` ni `wrangler.toml` ga yozing.
4. `npx wrangler secret put BOT_TOKEN` (tokenni kiriting)
   `npx wrangler secret put WEBHOOK_SECRET` (o'zingiz o'ylagan uzun so'z, masalan dodalavash2026xyz)
5. `npx wrangler deploy` → manzil chiqadi, masalan `https://doda-lavash-bot.SIZNING.workers.dev`
6. Brauzerda oching: `https://.../setup?key=WEBHOOK_SECRET` → webhook ulanadi.
7. Admin chat ID: botga `/id` yozing (yoki botni guruhga qo'shib, guruhda `/id`). Shu raqamni Cloudflare panelida Settings → Variables and Secrets → `ADMIN_CHAT_ID` ga yozing.

## Sayt (web) versiyasi
Xuddi shu manzil (`https://...workers.dev/`) oddiy brauzerda ochilsa, sayt bo'lib ishlaydi:
- Telefon va kompyuterga moslashgan, tepada do'kon nomi va qo'ng'iroq tugmasi
- Buyurtma admin chatga keladi, "🌐 sayt orqali" belgisi bilan. Mijozga telefon qilinadi
- Mijoz "📍 Joylashuvimni yuborish" tugmasini bossa, lokatsiya admin chatga xarita bo'lib boradi
- Buyurtmadan keyin sahifada holat ko'rinadi (Tayyorlanmoqda, Yo'lda, Yakunlandi) va har 10 soniyada yangilanadi
- Spamdan himoya: bitta IP dan 10 daqiqada ko'pi bilan 3 ta buyurtma
Instagram bio, Google Maps yoki QR kodga shu havolani qo'yish mumkin.
O'z domeni kerak bo'lsa (masalan dodalavash.uz), Cloudflare'da Worker'ga "Custom domain" ulanadi.

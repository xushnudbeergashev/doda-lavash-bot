// Server tomonidagi menyu va narxlar. Mijoz narxni o'zgartira olmasligi uchun
// buyurtma summasi shu yerdagi narxlar bilan qayta hisoblanadi.
// MUHIM: narx yoki taom o'zgarsa, src/site.html ichidagi CONFIG.menu ni ham o'zgartiring
// (id lar ikkala joyda bir xil bo'lishi kerak).
export const SHOP = {
  name: "Doda Lavash",
  phone: "+998 93 672 99 09",
  pickupAddress: "Chinobod, asosiy yo'l bo'yida, «Diydor» kafesi yonida",
  hours: { always: true },            // yoki { open: 9, close: 2 } (soat, Toshkent vaqti)
  zones: [
    { id: "c", name: "Chinobod markazi", fee: 7000, min: 30000, freeFrom: 100000 },
    { id: "o", name: "Atrofdagi mahallalar", fee: 12000, min: 50000, freeFrom: 150000 },
  ],
  payments: { cash: "Naqd", click: "Click", payme: "Payme", terminal: "Kuryerga karta bilan" },
};

export const ITEMS = [
  { id: "l1", name: "Klassik lavash", price: 28000 },
  { id: "l2", name: "Pishloqli lavash", price: 32000 },
  { id: "l3", name: "Tovuqli lavash", price: 26000 },
  { id: "l4", name: "Achchiq lavash", price: 29000 },
  { id: "b1", name: "Gamburger", price: 25000 },
  { id: "b2", name: "Chizburger", price: 28000 },
  { id: "b3", name: "Hot-dog", price: 15000 },
  { id: "s1", name: "Kartoshka fri", price: 15000 },
  { id: "s2", name: "Naggets, 6 dona", price: 20000 },
  { id: "d1", name: "Coca-Cola, 0,5 l", price: 8000 },
  { id: "d2", name: "Ayron", price: 6000 },
  { id: "d3", name: "Ko'k choy", price: 3000 },
  // Kombo: klassik lavash + fri + Coca-Cola
  { id: "c1", name: "«Doda» kombosi (lavash, fri, Coca-Cola)", price: 45000 },
];

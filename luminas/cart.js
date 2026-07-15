const Cart = {
  get() { try { return JSON.parse(localStorage.getItem('lumina_cart') || '[]'); } catch { return []; } },
  save(items) { localStorage.setItem('lumina_cart', JSON.stringify(items)); },
  add(product) {
    const items = this.get();
    const existing = items.find(i => i.id === product.id);
    if (existing) { existing.qty += product.qty || 1; }
    else { items.push({ ...product, qty: product.qty || 1 }); }
    this.save(items); this.updateBadge(); return items;
  },
  remove(id) { const items = this.get().filter(i => i.id !== id); this.save(items); this.updateBadge(); return items; },
  update(id, qty) {
    const items = this.get();
    const item = items.find(i => i.id === id);
    if (item) { item.qty = Math.max(1, qty); this.save(items); }
    this.updateBadge(); return items;
  },
  clear() { this.save([]); this.updateBadge(); },
  total() { return this.get().reduce((s, i) => s + i.price * i.qty, 0); },
  count() { return this.get().reduce((s, i) => s + i.qty, 0); },
  updateBadge() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    const n = this.count();
    badge.textContent = n;
    n > 0 ? badge.classList.add('show') : badge.classList.remove('show');
  }
};

function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 2800);
}

document.addEventListener('DOMContentLoaded', () => Cart.updateBadge());

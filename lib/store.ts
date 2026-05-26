import { create } from 'zustand';

export interface CartItem {
  id: number;
  name: string;
  unit: string;
  quantity: number;
  price: number;
  profit: number;
  total: number;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: number) => void;
  updateQuantity: (id: number, quantity: number) => void;
  updatePrice: (id: number, price: number) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartStore>((set) => ({
  items: [],
  addItem: (item) => set((state) => {
    const existing = state.items.find((i) => i.id === item.id && i.unit === item.unit);
    if (existing) {
      return {
        items: state.items.map((i) =>
          i.id === item.id && i.unit === item.unit
            ? { ...i, quantity: i.quantity + item.quantity, total: (i.quantity + item.quantity) * i.price }
            : i
        ),
      };
    }
    return { items: [...state.items, item] };
  }),
  removeItem: (id) => set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
  updateQuantity: (id, quantity) => set((state) => ({
    items: state.items.map((i) =>
      i.id === id ? { ...i, quantity, total: quantity * i.price } : i
    ),
  })),
  updatePrice: (id, price) => set((state) => ({
    items: state.items.map((i) =>
      i.id === id ? { ...i, price, total: i.quantity * price } : i
    ),
  })),
  clearCart: () => set({ items: [] }),
}));

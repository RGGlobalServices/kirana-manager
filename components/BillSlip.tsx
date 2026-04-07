import React from 'react';
import { CartItem } from '@/lib/store';

interface BillSlipProps {
  items: CartItem[];
  total: number;
  discount?: number;
  paymentMethod: string;
  billNumber: string;
  date: string;
}

export const BillSlip = React.forwardRef<HTMLDivElement, BillSlipProps>(({ items, total, discount = 0, paymentMethod, billNumber, date }, ref) => {
  const subtotal = items.reduce((acc, item) => acc + item.total, 0);
  
  return (
    <div ref={ref} style={{ backgroundColor: '#ffffff', color: '#000000' }} className="p-6 w-[80mm] mx-auto font-mono text-[12px] leading-tight shadow-sm">
      <div style={{ borderBottomColor: '#000000' }} className="text-center mb-4 border-b pb-2">
        <h1 className="text-xl font-black uppercase tracking-tighter">Mauli Kirana Store</h1>
        <p className="text-[10px] font-bold">SMART DASHBOARD POS</p>
        <p className="text-[10px]">Shop No. 4, Market Yard, Pune</p>
        <p className="text-[10px]">GSTIN: 27AAAAA0000A1Z5</p>
        <p className="text-[10px]">Mob: +91 98765 43210</p>
      </div>

      <div className="flex justify-between mb-2 text-[10px] font-bold">
        <span>Bill: {billNumber}</span>
        <span>{date}</span>
      </div>
      <div className="mb-4 text-[10px]">
        <span>Payment: <span className="font-bold uppercase">{paymentMethod}</span></span>
      </div>

      <table style={{ borderTopColor: '#000000', borderBottomColor: '#000000' }} className="w-full mb-4 border-t border-b border-dashed">
        <thead>
          <tr className="text-[10px]">
            <th className="text-left py-1">ITEM</th>
            <th className="text-center py-1">QTY</th>
            <th className="text-right py-1">AMT</th>
          </tr>
        </thead>
        <tbody style={{ borderTopColor: '#000000' }} className="border-t border-dotted">
          {items.map((item, idx) => (
            <tr key={idx} className="align-top">
              <td className="py-1 pr-2">{item.name}</td>
              <td className="text-center py-1 whitespace-nowrap">{item.quantity}</td>
              <td className="text-right py-1 font-bold">₹{item.total}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="space-y-1">
        <div className="flex justify-between text-[10px]">
          <span>Subtotal:</span>
          <span>₹{subtotal}</span>
        </div>
        {discount > 0 && (
          <div className="flex justify-between text-[10px]">
            <span>Discount:</span>
            <span>- ₹{discount}</span>
          </div>
        )}
        <div className="flex justify-between text-[10px]">
          <span>Tax (0%):</span>
          <span>₹0</span>
        </div>
        <div style={{ borderTopColor: '#000000' }} className="flex justify-between font-black text-lg border-t pt-1">
          <span>TOTAL</span>
          <span>₹{total}</span>
        </div>
      </div>

      <div style={{ borderTopColor: '#000000' }} className="text-center mt-6 pt-4 border-t border-dotted">
        <p className="font-bold text-[10px]">THANK YOU FOR SHOPPING!</p>
        <p className="text-[9px] italic">Please check items before leaving</p>
        <p className="text-[8px] mt-2">Powered by Kirana Smart Dashboard</p>
      </div>
    </div>
  );
});

BillSlip.displayName = 'BillSlip';

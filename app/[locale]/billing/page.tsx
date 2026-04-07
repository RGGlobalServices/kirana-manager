'use client';
import {useState, useEffect, useRef, useCallback} from 'react';
import {useTranslations} from 'next-intl';
import {useCartStore, CartItem} from '@/lib/store';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Search, Scan, Trash2, Plus, Minus, CreditCard, Banknote, User, X, Printer, Calculator as CalcIcon, PlusCircle, Download} from 'lucide-react';
import {Html5QrcodeScanner} from 'html5-qrcode';
import {cn} from '@/lib/utils';
import {BillSlip} from '@/components/BillSlip';
import Calculator from '@/components/Calculator';
import html2canvas from 'html2canvas-pro';
import { jsPDF } from 'jspdf';

const MOCK_INVENTORY = [
  {id: 1, name: "Fortune तेल (1L)", category: "Oil", base_unit: "Bottle", mrp: 180, selling_price: 170, wholesale_cost: 155, barcode: "8901234567890"},
  {id: 2, name: "तूर डाळ (1kg)", category: "Pulses", base_unit: "Kg", mrp: 160, selling_price: 150, wholesale_cost: 135, barcode: "8901234567891"},
  {id: 3, name: "मूग डाळ (1kg)", category: "Pulses", base_unit: "Kg", mrp: 140, selling_price: 130, wholesale_cost: 115, barcode: "8901234567892"},
  {id: 4, name: "साखर (1kg)", category: "Sugar", base_unit: "Kg", mrp: 45, selling_price: 42, wholesale_cost: 38, barcode: "8901234567893"},
  {id: 5, name: "Surf Excel (500g)", category: "Detergent", base_unit: "Box", mrp: 120, selling_price: 115, wholesale_cost: 100, barcode: "8901234567894"},
  {id: 6, name: "Lux साबण (100g)", category: "Soap", base_unit: "Box", mrp: 35, selling_price: 32, wholesale_cost: 28, barcode: "8901234567895"},
];

export default function BillingPage() {
  const t = useTranslations('Billing');
  const {items, addItem, removeItem, updateQuantity, updatePrice, clearCart} = useCartStore();
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('Cash');
  const [showBillModal, setShowBillModal] = useState(false);
  const [lastBill, setLastBill] = useState<any>(null);
  const [discount, setDiscount] = useState(0);
  const [showCalculator, setShowCalculator] = useState(false);
  const [manualProduct, setManualProduct] = useState({ name: '', price: '', unit: 'Unit' });
  const [showManualAdd, setShowManualAdd] = useState(false);
  
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const componentRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    if (!componentRef.current) return;
    try {
      const canvas = await html2canvas(componentRef.current, { scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      
      const pdfWidth = 80; // 80mm thermal paper
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: [pdfWidth, pdfHeight]
      });
      
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`bill-${lastBill?.billNumber || 'download'}.pdf`);
    } catch (error) {
      console.error("Failed to generate PDF", error);
      alert("Failed to download PDF. Please try again.");
    }
  };

  const subtotal = items.reduce((acc, item) => acc + item.total, 0);
  const total = Math.max(0, subtotal - discount);

  const addToCart = useCallback((product: any) => {
    addItem({
      id: product.id || Math.random(),
      name: product.name,
      unit: product.base_unit || product.unit,
      quantity: 1,
      price: product.selling_price || Number(product.price),
      profit: (product.selling_price || Number(product.price)) - (product.wholesale_cost || 0),
      total: product.selling_price || Number(product.price)
    });
    setSearch('');
    setSearchResults([]);
  }, [addItem]);

  const handleScan = useCallback((barcode: string) => {
    const product = MOCK_INVENTORY.find(p => p.barcode === barcode);
    if (product) {
      addToCart(product);
    } else {
      alert("Product not found in inventory!");
    }
  }, [addToCart]);

  const handleManualAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualProduct.name || !manualProduct.price) return;
    addToCart({
      name: manualProduct.name,
      selling_price: Number(manualProduct.price),
      base_unit: manualProduct.unit,
      wholesale_cost: 0
    });
    setManualProduct({ name: '', price: '', unit: 'Unit' });
    setShowManualAdd(false);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
    if (value.length > 1) {
      const filtered = MOCK_INVENTORY.filter(p => 
        p.name.toLowerCase().includes(value.toLowerCase()) || 
        p.barcode.includes(value)
      );
      setSearchResults(filtered);
    } else {
      setSearchResults([]);
    }
  };

  useEffect(() => {
    if (isScanning) {
      scannerRef.current = new Html5QrcodeScanner("reader", {fps: 10, qrbox: 250}, false);
      scannerRef.current.render((decodedText) => {
        handleScan(decodedText);
        setIsScanning(false);
        scannerRef.current?.clear();
      }, (error) => {});
    }
    return () => {
      scannerRef.current?.clear();
    };
  }, [isScanning, handleScan]);

  const handleCreateBill = () => {
    const billData = {
      items: [...items],
      total,
      discount,
      paymentMethod,
      billNumber: `INV-${Math.floor(1000 + Math.random() * 9000)}`,
      date: new Date().toLocaleDateString()
    };
    setLastBill(billData);
    setShowBillModal(true);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full relative">
      {/* Left: Product Search & Cart */}
      <div className="lg:col-span-2 space-y-6 flex flex-col">
        <div className="flex gap-4 relative">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder={t('searchProduct')}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              value={search}
              onChange={handleSearchChange}
            />
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 w-full mt-2 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 max-h-60 overflow-y-auto">
                {searchResults.map((product) => (
                  <button
                    key={product.id}
                    onClick={() => addToCart(product)}
                    className="w-full text-left px-4 py-3 hover:bg-slate-800 flex justify-between items-center border-b border-slate-800 last:border-0"
                  >
                    <div>
                      <p className="font-bold text-slate-200">{product.name}</p>
                      <p className="text-xs text-slate-500">{product.category} | {product.barcode}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-emerald-500">₹{product.selling_price}</p>
                      <p className="text-[10px] text-slate-500">MRP: ₹{product.mrp}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={() => setShowManualAdd(!showManualAdd)}
            className={cn(
              "px-4 py-3 rounded-xl font-bold flex items-center gap-2 transition-colors",
              showManualAdd ? "bg-slate-800 text-emerald-500" : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
            )}
          >
            <PlusCircle size={20} />
            <span className="hidden md:inline">Manual Add</span>
          </button>
          <button
            onClick={() => setIsScanning(!isScanning)}
            className="bg-emerald-500 text-slate-900 px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-emerald-400 transition-colors"
          >
            <Scan size={20} />
            <span className="hidden md:inline">{t('scanQR')}</span>
          </button>
        </div>

        {showManualAdd && (
          <Card className="bg-slate-900 border-emerald-500/30 animate-in slide-in-from-top-2 duration-200">
            <CardContent className="p-4">
              <form onSubmit={handleManualAdd} className="flex flex-wrap gap-3 items-end">
                <div className="flex-1 min-w-[200px]">
                  <label className="text-xs text-slate-500 mb-1 block uppercase font-bold">Product Name</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter item name..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none"
                    value={manualProduct.name}
                    onChange={e => setManualProduct({...manualProduct, name: e.target.value})}
                  />
                </div>
                <div className="w-24">
                  <label className="text-xs text-slate-500 mb-1 block uppercase font-bold">Price</label>
                  <input
                    type="number"
                    required
                    placeholder="0"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none"
                    value={manualProduct.price}
                    onChange={e => setManualProduct({...manualProduct, price: e.target.value})}
                  />
                </div>
                <div className="w-24">
                  <label className="text-xs text-slate-500 mb-1 block uppercase font-bold">Unit</label>
                  <select
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none"
                    value={manualProduct.unit}
                    onChange={e => setManualProduct({...manualProduct, unit: e.target.value})}
                  >
                    <option>Unit</option>
                    <option>Kg</option>
                    <option>Gram</option>
                    <option>Bottle</option>
                    <option>Box</option>
                  </select>
                </div>
                <button type="submit" className="bg-emerald-500 text-slate-900 px-4 py-2 rounded-lg font-bold hover:bg-emerald-400">Add Item</button>
              </form>
            </CardContent>
          </Card>
        )}

        {isScanning && (
          <div id="reader" className="bg-slate-900 rounded-xl overflow-hidden border border-slate-800"></div>
        )}

        <Card className="bg-slate-900 border-slate-800 flex-1 overflow-hidden flex flex-col">
          <CardHeader className="border-b border-slate-800">
            <CardTitle className="text-slate-200 flex justify-between items-center">
              <span>Items</span>
              <span className="text-sm font-normal text-slate-400">{items.length} items</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-0">
            <table className="w-full text-left">
              <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase sticky top-0">
                <tr>
                  <th className="px-6 py-3">Item</th>
                  <th className="px-6 py-3">Unit</th>
                  <th className="px-6 py-3">Qty</th>
                  <th className="px-6 py-3 text-right">Price</th>
                  <th className="px-6 py-3 text-right">Total</th>
                  <th className="px-6 py-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {items.map((item) => (
                  <tr key={`${item.id}-${item.unit}`} className="text-slate-200 hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-slate-400">{item.unit}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <button onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))} className="p-1 hover:bg-slate-700 rounded"><Minus size={14}/></button>
                        <span className="w-8 text-center">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="p-1 hover:bg-slate-700 rounded"><Plus size={14}/></button>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <input
                        type="number"
                        className="w-20 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-right text-emerald-500 font-bold focus:ring-1 focus:ring-emerald-500 outline-none"
                        value={item.price}
                        onChange={(e) => updatePrice(item.id, Number(e.target.value))}
                      />
                    </td>
                    <td className="px-6 py-4 text-right font-bold">₹{item.total}</td>
                    <td className="px-6 py-4 text-center">
                      <button onClick={() => removeItem(item.id)} className="text-red-400 hover:text-red-300 p-2"><Trash2 size={18}/></button>
                    </td>
                  </tr>
                ))}
                {items.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-20 text-center text-slate-500">
                      No items in cart. Start scanning or searching!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      {/* Right: Summary & Payment */}
      <div className="space-y-6">
        <div className="flex justify-end relative">
          <button
            onClick={() => setShowCalculator(!showCalculator)}
            className={cn(
              "p-3 rounded-xl border transition-all flex items-center gap-2 font-bold",
              showCalculator ? "bg-emerald-500 text-slate-900 border-emerald-500" : "bg-slate-900 border-slate-800 text-slate-400"
            )}
          >
            <CalcIcon size={20} />
            Calculator
          </button>
          {showCalculator && (
            <div className="absolute top-full right-0 mt-2 z-[60]">
              <Calculator onClose={() => setShowCalculator(false)} />
            </div>
          )}
        </div>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-slate-200">{t('paymentMethod')}</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-3">
            <PaymentButton
              active={paymentMethod === 'Cash'}
              onClick={() => setPaymentMethod('Cash')}
              icon={<Banknote size={20}/>}
              label={t('cash')}
            />
            <PaymentButton
              active={paymentMethod === 'UPI'}
              onClick={() => setPaymentMethod('UPI')}
              icon={<CreditCard size={20}/>}
              label={t('upi')}
            />
            <PaymentButton
              active={paymentMethod === 'Udhar'}
              onClick={() => setPaymentMethod('Udhar')}
              icon={<User size={20}/>}
              label={t('udhar')}
            />
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-6 space-y-4">
            <div className="flex justify-between text-slate-400">
              <span>{t('subtotal')}</span>
              <span>₹{subtotal}</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>{t('discount')}</span>
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1">
                <span className="text-emerald-500">₹</span>
                <input
                  type="number"
                  className="w-16 bg-transparent text-emerald-500 font-bold outline-none text-right"
                  value={discount}
                  onChange={(e) => setDiscount(Number(e.target.value))}
                />
              </div>
            </div>
            <div className="border-t border-slate-800 pt-4 flex justify-between items-center">
              <span className="text-xl font-bold text-slate-200">{t('total')}</span>
              <span className="text-3xl font-black text-emerald-500">₹{total}</span>
            </div>
          </CardContent>
        </Card>

        <button
          onClick={handleCreateBill}
          disabled={items.length === 0}
          className="w-full bg-emerald-500 text-slate-900 py-6 rounded-2xl font-black text-2xl shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          {t('createBill')}
        </button>
      </div>

      {/* Bill Modal */}
      {showBillModal && lastBill && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
          <Card className="bg-slate-900 border-slate-800 w-full max-w-md overflow-hidden">
            <CardHeader className="border-b border-slate-800 flex flex-row items-center justify-between">
              <CardTitle className="text-emerald-500">Bill Generated</CardTitle>
              <button onClick={() => setShowBillModal(false)} className="text-slate-400 hover:text-slate-200">
                <X size={24} />
              </button>
            </CardHeader>
            <CardContent id="print-area" className="p-0 max-h-[70vh] overflow-y-auto bg-white">
              <BillSlip ref={componentRef} {...lastBill} />
            </CardContent>
            <div className="p-4 bg-slate-900 border-t border-slate-800 flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={handlePrint}
                  className="flex items-center justify-center gap-2 bg-emerald-500 text-slate-900 py-3 rounded-xl font-bold hover:bg-emerald-400"
                >
                  <Printer size={20} />
                  Print
                </button>
                <button
                  onClick={handleDownloadPDF}
                  className="flex items-center justify-center gap-2 bg-blue-500 text-slate-900 py-3 rounded-xl font-bold hover:bg-blue-400"
                >
                  <Download size={20} />
                  Download
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setShowBillModal(false)}
                  className="flex items-center justify-center gap-2 bg-slate-800 text-slate-200 py-3 rounded-xl font-bold hover:bg-slate-700"
                >
                  Continue Editing
                </button>
                <button
                  onClick={() => { setShowBillModal(false); clearCart(); }}
                  className="flex items-center justify-center gap-2 bg-red-500/10 text-red-500 py-3 rounded-xl font-bold hover:bg-red-500/20"
                >
                  Start New Bill
                </button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

function PaymentButton({active, onClick, icon, label}: {active: boolean, onClick: () => void, icon: React.ReactNode, label: string}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-col items-center gap-2 p-4 rounded-xl border transition-all",
        active ? "bg-emerald-500/10 border-emerald-500 text-emerald-500" : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
      )}
    >
      {icon}
      <span className="text-xs font-bold uppercase">{label}</span>
    </button>
  );
}

'use client';
import {useState} from 'react';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Plus, Search, Filter, MoreVertical, AlertCircle} from 'lucide-react';
import {cn} from '@/lib/utils';

export default function ProductsPage() {
  const [search, setSearch] = useState('');

  const products = [
    {id: 1, name: "Fortune तेल (1L)", category: "Oil", stock: 45, minStock: 10, mrp: 180, sellingPrice: 170, cost: 155},
    {id: 2, name: "तूर डाळ (1kg)", category: "Pulses", stock: 4, minStock: 5, mrp: 160, sellingPrice: 150, cost: 135},
    {id: 3, name: "साखर (1kg)", category: "Sugar", stock: 120, minStock: 20, mrp: 45, sellingPrice: 42, cost: 38},
    {id: 4, name: "Surf Excel (500g)", category: "Detergent", stock: 8, minStock: 10, mrp: 120, sellingPrice: 115, cost: 100},
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-emerald-500">Inventory Management</h1>
        <button className="bg-emerald-500 text-slate-900 px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-emerald-400 transition-colors">
          <Plus size={20} />
          Add Product
        </button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Search products..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button className="bg-slate-900 border border-slate-800 p-3 rounded-xl text-slate-400 hover:text-slate-200">
          <Filter size={20} />
        </button>
      </div>

      <Card className="bg-slate-900 border-slate-800 overflow-hidden">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="px-6 py-4">Name</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Stock</th>
                  <th className="px-6 py-4 text-right">MRP</th>
                  <th className="px-6 py-4 text-right">Selling</th>
                  <th className="px-6 py-4 text-right">Profit %</th>
                  <th className="px-6 py-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {products.map((product) => {
                  const isLowStock = product.stock <= product.minStock;
                  const profit = ((product.sellingPrice - product.cost) / product.cost * 100).toFixed(1);
                  
                  return (
                    <tr key={product.id} className="text-slate-200 hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 font-medium">{product.name}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{product.category}</td>
                      <td className="px-6 py-4">
                        <div className={cn(
                          "flex items-center gap-2 font-bold",
                          isLowStock ? "text-red-400" : "text-emerald-400"
                        )}>
                          {product.stock}
                          {isLowStock && <AlertCircle size={14} />}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right text-slate-400">₹{product.mrp}</td>
                      <td className="px-6 py-4 text-right font-bold">₹{product.sellingPrice}</td>
                      <td className="px-6 py-4 text-right text-emerald-500 font-medium">{profit}%</td>
                      <td className="px-6 py-4 text-center">
                        <button className="text-slate-400 hover:text-slate-200 p-2"><MoreVertical size={18}/></button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

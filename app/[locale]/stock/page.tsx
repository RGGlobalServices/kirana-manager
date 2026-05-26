'use client';
import {useState} from 'react';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Search, Filter, ArrowUpRight, ArrowDownLeft, AlertTriangle} from 'lucide-react';
import {cn} from '@/lib/utils';

export default function StockPage() {
  const [search, setSearch] = useState('');

  const stockItems = [
    {id: 1, name: "Fortune तेल (1L)", category: "Oil", current: 45, min: 10, unit: "Bottle", status: "In Stock"},
    {id: 2, name: "तूर डाळ (1kg)", category: "Pulses", current: 4, min: 5, unit: "Kg", status: "Low Stock"},
    {id: 3, name: "साखर (1kg)", category: "Sugar", current: 120, min: 20, unit: "Kg", status: "In Stock"},
    {id: 4, name: "Surf Excel (500g)", category: "Detergent", current: 8, min: 10, unit: "Box", status: "Low Stock"},
    {id: 5, name: "Lux साबण (100g)", category: "Soap", current: 0, min: 15, unit: "Box", status: "Out of Stock"},
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-emerald-500">Stock & Inventory</h1>
        <div className="flex gap-2">
          <button className="bg-slate-800 text-slate-200 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-700">
            <ArrowDownLeft size={18} className="text-emerald-500" />
            Stock In
          </button>
          <button className="bg-slate-800 text-slate-200 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-700">
            <ArrowUpRight size={18} className="text-red-500" />
            Stock Out
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Total Items" value="156" color="text-blue-500" />
        <StatCard title="Low Stock" value="12" color="text-orange-500" />
        <StatCard title="Out of Stock" value="3" color="text-red-500" />
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
        <input
          type="text"
          placeholder="Search stock..."
          className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card className="bg-slate-900 border-slate-800 overflow-hidden">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="px-6 py-4">Product</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Current Stock</th>
                  <th className="px-6 py-4">Min. Level</th>
                  <th className="px-6 py-4">Unit</th>
                  <th className="px-6 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {stockItems.map((item) => (
                  <tr key={item.id} className="text-slate-200 hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-slate-400">{item.category}</td>
                    <td className="px-6 py-4 font-bold">{item.current}</td>
                    <td className="px-6 py-4 text-slate-400">{item.min}</td>
                    <td className="px-6 py-4 text-sm text-slate-400">{item.unit}</td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "px-2 py-1 rounded-full text-[10px] font-bold uppercase flex items-center gap-1 w-fit",
                        item.status === "In Stock" ? "bg-emerald-500/10 text-emerald-500" :
                        item.status === "Low Stock" ? "bg-orange-500/10 text-orange-500" :
                        "bg-red-500/10 text-red-500"
                      )}>
                        {item.status === "Low Stock" && <AlertTriangle size={10} />}
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({title, value, color}: {title: string, value: string, color: string}) {
  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardContent className="p-6">
        <p className="text-sm text-slate-400 font-medium">{title}</p>
        <p className={cn("text-3xl font-black mt-1", color)}>{value}</p>
      </CardContent>
    </Card>
  );
}

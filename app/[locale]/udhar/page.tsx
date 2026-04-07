'use client';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Search, UserPlus, Phone, Calendar, ArrowRight} from 'lucide-react';

export default function UdharPage() {
  const customers = [
    {id: 1, name: "Rahul Gosavi", mobile: "9876543210", due: 1250, lastPayment: "2 days ago"},
    {id: 2, name: "Suresh Patil", mobile: "9123456789", due: 4500, lastPayment: "1 week ago"},
    {id: 3, name: "Amit Shinde", mobile: "8888855555", due: 800, lastPayment: "Today"},
    {id: 4, name: "Ganesh More", mobile: "7777744444", due: 120, lastPayment: "3 weeks ago"},
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-orange-500">Udhar Khata (Ledger)</h1>
        <button className="bg-orange-500 text-slate-900 px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-orange-400 transition-colors">
          <UserPlus size={20} />
          New Customer
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
        <input
          type="text"
          placeholder="Search customer by name or mobile..."
          className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {customers.map((customer) => (
          <Card key={customer.id} className="bg-slate-900 border-slate-800 hover:border-orange-500/50 transition-all cursor-pointer group">
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-slate-100">{customer.name}</h3>
                  <div className="flex items-center gap-2 text-slate-400 text-sm mt-1">
                    <Phone size={14} />
                    {customer.mobile}
                  </div>
                </div>
                <div className="bg-orange-500/10 text-orange-500 p-2 rounded-lg group-hover:bg-orange-500 group-hover:text-slate-900 transition-colors">
                  <ArrowRight size={20} />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 border-t border-slate-800 pt-4">
                <div>
                  <p className="text-xs text-slate-500 uppercase font-bold">Total Due</p>
                  <p className="text-2xl font-black text-orange-500">₹{customer.due}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 uppercase font-bold">Last Payment</p>
                  <div className="flex items-center justify-end gap-1 text-slate-300 mt-1">
                    <Calendar size={14} />
                    <span className="text-sm">{customer.lastPayment}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

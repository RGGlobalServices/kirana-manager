'use client';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend} from 'recharts';
import {Calendar, Download, Filter} from 'lucide-react';
import {cn} from '@/lib/utils';

export default function ReportsPage() {
  const data = [
    {name: 'Mon', sales: 4000, profit: 800},
    {name: 'Tue', sales: 3000, profit: 600},
    {name: 'Wed', sales: 2000, profit: 400},
    {name: 'Thu', sales: 2780, profit: 550},
    {name: 'Fri', sales: 1890, profit: 380},
    {name: 'Sat', sales: 2390, profit: 480},
    {name: 'Sun', sales: 3490, profit: 700},
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-blue-500">Business Reports</h1>
        <div className="flex gap-2">
          <button className="bg-slate-800 text-slate-200 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-700">
            <Calendar size={18} />
            Last 7 Days
          </button>
          <button className="bg-blue-500 text-slate-900 px-4 py-2 rounded-lg flex items-center gap-2 font-bold hover:bg-blue-400">
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-slate-200">Sales vs Profit</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{backgroundColor: '#0f172a', border: 'none'}} />
                <Legend />
                <Bar dataKey="sales" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="profit" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-slate-200 text-sm">Top Selling Products</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <TopProduct name="Fortune तेल" sales="₹12,400" growth="+12%" />
              <TopProduct name="साखर" sales="₹8,200" growth="+5%" />
              <TopProduct name="तूर डाळ" sales="₹6,500" growth="-2%" />
              <TopProduct name="Surf Excel" sales="₹4,800" growth="+18%" />
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-slate-200 text-sm">Category Performance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <CategoryStat name="Grocery" percentage={45} color="bg-blue-500" />
              <CategoryStat name="Oil" percentage={25} color="bg-emerald-500" />
              <CategoryStat name="Pulses" percentage={20} color="bg-orange-500" />
              <CategoryStat name="Others" percentage={10} color="bg-slate-500" />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function TopProduct({name, sales, growth}: {name: string, sales: string, growth: string}) {
  return (
    <div className="flex justify-between items-center">
      <div>
        <p className="font-medium text-slate-200">{name}</p>
        <p className="text-xs text-slate-500">{sales}</p>
      </div>
      <span className={cn(
        "text-xs font-bold px-2 py-1 rounded",
        growth.startsWith('+') ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500"
      )}>
        {growth}
      </span>
    </div>
  );
}

function CategoryStat({name, percentage, color}: {name: string, percentage: number, color: string}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{name}</span>
        <span className="text-slate-200 font-bold">{percentage}%</span>
      </div>
      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div className={cn("h-full rounded-full", color)} style={{width: `${percentage}%`}} />
      </div>
    </div>
  );
}

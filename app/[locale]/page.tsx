'use client';
import {useTranslations} from 'next-intl';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell} from 'recharts';
import {TrendingUp, Wallet, AlertTriangle, ShoppingCart} from 'lucide-react';

export default function Dashboard() {
  const t = useTranslations('Dashboard');

  const salesData = [
    {date: '01 Apr', total: 4500},
    {date: '02 Apr', total: 5200},
    {date: '03 Apr', total: 4800},
    {date: '04 Apr', total: 6100},
    {date: '05 Apr', total: 5900},
    {date: '06 Apr', total: 7200},
    {date: '07 Apr', total: 6800},
  ];

  const categoryData = [
    {name: 'Grocery', value: 400},
    {name: 'Oil', value: 300},
    {name: 'Pulses', value: 300},
    {name: 'Soap', value: 200},
  ];

  const COLORS = ['#10B981', '#F59E0B', '#3B82F6', '#EF4444'];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-emerald-500">{t('title')}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title={t('todaySales')} value="₹ 6,800" icon={<TrendingUp className="text-emerald-500" />} />
        <StatCard title={t('todayProfit')} value="₹ 1,250" icon={<ShoppingCart className="text-blue-500" />} />
        <StatCard title={t('totalUdhar')} value="₹ 12,450" icon={<Wallet className="text-orange-500" />} />
        <StatCard title={t('lowStock')} value="8" icon={<AlertTriangle className="text-red-500" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-slate-200">7-Day Sales Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{backgroundColor: '#0f172a', border: 'none'}} />
                <Line type="monotone" dataKey="total" stroke="#10b981" strokeWidth={3} dot={{fill: '#10b981'}} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-slate-200">Category Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px] flex justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({title, value, icon}: {title: string, value: string, icon: React.ReactNode}) {
  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-50">{value}</div>
      </CardContent>
    </Card>
  );
}

'use client';
import {Link} from '@/i18n/routing';
import {usePathname} from '@/i18n/routing';
import {LayoutDashboard, Receipt, Package, Box, Users, BarChart3, LogOut, Languages} from 'lucide-react';
import {cn} from '@/lib/utils';

export default function Sidebar({locale}: {locale: string}) {
  const pathname = usePathname();

  const menuItems = [
    {name: 'Dashboard', icon: LayoutDashboard, href: `/`},
    {name: 'Billing', icon: Receipt, href: `/billing`},
    {name: 'Products', icon: Package, href: `/products`},
    {name: 'Stock', icon: Box, href: `/stock`},
    {name: 'Udhar', icon: Users, href: `/udhar`},
    {name: 'Reports', icon: BarChart3, href: `/reports`},
  ];

  const languages = [
    {code: 'en', name: 'English'},
    {code: 'hi', name: 'हिंदी'},
    {code: 'mr', name: 'मराठी'},
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
      <div className="p-6">
        <h2 className="text-xl font-bold text-emerald-500 flex items-center gap-2">
          <span className="bg-emerald-500 text-slate-900 p-1 rounded">KS</span>
          Kirana Smart
        </h2>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive ? "bg-emerald-500/10 text-emerald-500" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              )}
            >
              <Icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 space-y-4">
        <div className="flex items-center gap-2 px-4 py-2 text-slate-400">
          <Languages size={18} />
          <div className="flex gap-2 text-xs">
            {languages.map((lang) => (
              <Link
                key={lang.code}
                href={pathname.replace(`/${locale}`, `/${lang.code}`)}
                className={cn(
                  "hover:text-emerald-500",
                  locale === lang.code && "text-emerald-500 font-bold"
                )}
              >
                {lang.name}
              </Link>
            ))}
          </div>
        </div>
        <button className="flex items-center gap-3 px-4 py-3 w-full text-slate-400 hover:bg-slate-800 hover:text-red-400 rounded-lg transition-colors">
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}

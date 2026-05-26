'use client';

import { useEffect } from 'react';
import { usePathname } from '@/i18n/routing';
import { useBusinessStore } from '@/lib/businessStore';
import { useAuthStore } from '@/lib/store';
import AIFloatingButton from '@/components/AIFloatingButton';
import NotificationBell from '@/components/NotificationBell';
import Sidebar from '@/components/Sidebar';
import { isAllowedWhenEnded, isSubscriptionEnded } from '@/lib/subscriptionAccess';

export default function MainLayoutClient({ 
  locale, 
  children 
}: { 
  locale: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { loadFromStorage } = useAuthStore();
  const { profile, fetchProfile } = useBusinessStore();

  useEffect(() => {
    loadFromStorage();
  }, [loadFromStorage]);

  // Setup check is no longer needed as business type is selected during signup
  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  useEffect(() => {
    if (!isSubscriptionEnded(profile)) return;
    if (isAllowedWhenEnded(pathname)) return;
    window.location.href = `/${locale}/billing`;
  }, [profile, pathname, locale]);

  return (
    <>
      <Sidebar locale={locale} />
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="flex items-center justify-end px-6 py-3 border-b border-slate-800 bg-slate-900/50">
          <NotificationBell />
        </header>
        <main className="flex-1 p-4 md:p-8">
          {children}
        </main>
        <footer className="border-t border-slate-800 px-8 py-3 flex items-center justify-between flex-shrink-0 bg-slate-900/50">
          <p className="text-xs text-slate-600">
            © <span suppressHydrationWarning>{new Date().getFullYear()}</span>{' '}
            <span className="text-slate-400 font-semibold">{profile.shopName || 'Vyapar Sarthi'}</span>. All rights reserved.
          </p>
          <p className="text-xs text-slate-700">Vyapar Sarthi v2.0</p>
        </footer>
      </div>
      <AIFloatingButton />
    </>
  );
}

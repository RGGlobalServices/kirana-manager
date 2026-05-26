'use client';

import { useState, useEffect, useRef } from 'react';
import { Bell, X, Check, CheckCheck, ExternalLink } from 'lucide-react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { cn } from '@/lib/utils';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  async function loadNotifications() {
    try {
      const res = await api.get('/notifications/in-app');
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (e) {
      // Silently fail
    }
  }

  async function markRead(id: string) {
    try {
      await api.post(`/notifications/in-app/${id}/read`, {});
      loadNotifications();
    } catch (e) {}
  }

  async function markAllRead() {
    try {
      await api.post('/notifications/in-app/read-all', {});
      loadNotifications();
    } catch (e) {}
  }

  function handleNotificationClick(n: any) {
    markRead(n.id);
    if (n.link) {
      router.push(n.link);
    }
    setShowDropdown(false);
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'expiry': return '🔴';
      case 'warning': return '⚠️';
      case 'promotion': return '🎉';
      case 'update': return '📢';
      default: return '💡';
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 rounded-xl hover:bg-slate-800 transition-all"
      >
        <Bell className="w-5 h-5 text-slate-400" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 overflow-hidden">
          <div className="p-3 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
              >
                <CheckCheck className="w-3 h-3" />
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto custom-scrollbar">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-slate-500">
                <p className="text-sm">No notifications</p>
              </div>
            ) : (
              notifications.slice(0, 20).map((n: any) => (
                <div
                  key={n.id}
                  onClick={() => handleNotificationClick(n)}
                  className={cn(
                    "p-3 border-b border-slate-800/50 cursor-pointer hover:bg-slate-800/50 transition-all",
                    !n.is_read && "bg-slate-800/30"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-lg">{getTypeIcon(n.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className={cn(
                        "text-sm",
                        n.is_read ? "text-slate-300" : "text-white font-semibold"
                      )}>
                        {n.title}
                      </p>
                      <p className="text-xs text-slate-500 mt-1 line-clamp-2">{n.message}</p>
                      <p className="text-[10px] text-slate-600 mt-1">
                        {n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}
                      </p>
                    </div>
                    {!n.is_read && (
                      <button
                        onClick={(e) => { e.stopPropagation(); markRead(n.id); }}
                        className="p-1 hover:bg-slate-700 rounded"
                      >
                        <Check className="w-3 h-3 text-slate-500" />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

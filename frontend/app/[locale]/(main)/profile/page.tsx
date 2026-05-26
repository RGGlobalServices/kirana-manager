
'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  User, Building, Mail, Phone, MapPin, Camera, 
  Save, Loader2, CheckCircle, Store, Briefcase 
} from 'lucide-react';
import api from '@/lib/api';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/lib/store';
import { useBusinessStore } from '@/lib/businessStore';
import { uploadInvoiceToSupabase } from '@/lib/supabaseStorage'; // Reusing storage logic

export default function ProfilePage() {
  const t = useTranslations('Profile');
  const { profile, fetchProfile, updateProfile } = useBusinessStore();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const [shop, setShop] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const load = async () => {
      try {
        await fetchProfile();
      } catch (err) {
        console.error('Failed to load shop profile:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [fetchProfile]);

  // Sync local state with store profile
  useEffect(() => {
    if (profile) {
      setShop({
        id: profile.id,
        name: profile.shopName,
        address: profile.address,
        mobile: profile.mobile,
        logo_url: profile.logoUrl,
        business_type: profile.businessType
      });
    }
  }, [profile]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile({
        shopName: shop.name,
        address: shop.address,
        mobile: shop.mobile,
        logoUrl: shop.logo_url,
        businessType: shop.business_type
      });
      setStatus({ type: 'success', message: 'Profile updated successfully' });
      setTimeout(() => setStatus(null), 3000);
    } catch (err) {
      setStatus({ type: 'error', message: 'Failed to update profile' });
    } finally {
      setSaving(false);
    }
  };

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const fileName = `logo-${shop?.id || 'default'}-${Date.now()}.png`;
      const publicUrl = await uploadInvoiceToSupabase(file, fileName, file.type);
      if (publicUrl) {
        setShop({ ...shop, logo_url: publicUrl });
        await updateProfile({ logoUrl: publicUrl });
      }
    } catch (err) {
      console.error('Logo upload failed:', err);
      alert('Failed to upload logo');
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div className="p-10 text-center text-slate-500">Loading profile...</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500 pb-20">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight">Profile Manager</h1>
          <p className="text-slate-400">Manage your personal and business identity</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 px-6 py-2.5 rounded-xl font-bold flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
        >
          {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
          Save Changes
        </button>
      </div>

      {status && (
        <div className={cn(
          "p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-top-2",
          status.type === 'success' ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"
        )}>
          <CheckCircle size={18} />
          <span className="font-medium">{status.message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Branding & Logo */}
        <Card className="bg-slate-900 border-slate-800 md:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm uppercase tracking-widest text-slate-500">Branding</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-6">
            <div className="relative group">
              <div className="w-32 h-32 rounded-3xl bg-slate-800 border-2 border-dashed border-slate-700 flex items-center justify-center overflow-hidden transition-all group-hover:border-emerald-500/50">
                {shop?.logo_url ? (
                  <img 
                    src={`${shop.logo_url}${shop.logo_url.includes('?') ? '&' : '?'}v=${Date.now()}`} 
                    alt="Logo" 
                    className="w-full h-full object-contain p-2" 
                    onError={(e) => {
                      // Fallback if image fails to load (e.g. wrong URL format)
                      console.warn("Logo failed to load, checking URL format");
                      if (shop.logo_url && !shop.logo_url.includes('/public/')) {
                         const fixedUrl = shop.logo_url.replace('/v1/object/', '/v1/object/public/');
                         (e.target as HTMLImageElement).src = fixedUrl;
                      }
                    }}
                  />
                ) : (
                  <Building size={48} className="text-slate-600" />
                )}
                {uploading && (
                  <div className="absolute inset-0 bg-slate-900/60 flex items-center justify-center">
                    <Loader2 className="animate-spin text-emerald-500" />
                  </div>
                )}
              </div>
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="absolute -bottom-2 -right-2 w-10 h-10 bg-emerald-500 text-slate-900 rounded-xl flex items-center justify-center shadow-xl hover:bg-emerald-400 transition-all active:scale-90"
              >
                <Camera size={20} />
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleLogoUpload} 
                accept="image/*" 
                className="hidden" 
              />
            </div>
            <div className="text-center">
              <p className="font-bold text-slate-200">Business Logo</p>
              <p className="text-xs text-slate-500 mt-1">Shown on bills & invoices</p>
            </div>
          </CardContent>
        </Card>

        {/* Business Details */}
        <div className="md:col-span-2 space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Store size={20} className="text-emerald-500" />
                Business Information
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase">Store Name</label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input 
                    type="text" 
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none"
                    value={shop?.name || ''}
                    onChange={e => setShop({...shop, name: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase">Business Address</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-slate-500" size={18} />
                  <textarea 
                    rows={3}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none resize-none"
                    value={shop?.address || ''}
                    onChange={e => setShop({...shop, address: e.target.value})}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase">Business Contact</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input 
                      type="tel" 
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none"
                      value={shop?.mobile || ''}
                      onChange={e => setShop({...shop, mobile: e.target.value})}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase">Business Type</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <select 
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-200 focus:ring-1 focus:ring-emerald-500 outline-none appearance-none"
                      value={shop?.business_type || 'kirana'}
                      onChange={e => setShop({...shop, business_type: e.target.value})}
                    >
                      <option value="kirana">Kirana / Grocery</option>
                      <option value="medical">Medical / Pharmacy</option>
                      <option value="electronics">Electronics</option>
                      <option value="clothes">Clothes / Boutique</option>
                      <option value="general">General Store</option>
                    </select>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Profile */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <User size={20} className="text-blue-500" />
                Owner Information
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase">Owner Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input 
                    type="text" disabled
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-400 outline-none opacity-60"
                    value={user?.name || ''}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input 
                    type="email" disabled
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-slate-400 outline-none opacity-60"
                    value={user?.email || ''}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

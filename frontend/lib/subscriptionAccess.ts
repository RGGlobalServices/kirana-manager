export interface SubscriptionProfileLike {
  subscriptionPlan?: string | null;
  subscriptionStatus?: string | null;
  subscriptionExpiry?: string | null;
}

export function isSubscriptionEnded(profile: SubscriptionProfileLike): boolean {
  const status = (profile.subscriptionStatus || '').toLowerCase();
  if (status === 'expired') return true;

  const expiry = profile.subscriptionExpiry ? new Date(profile.subscriptionExpiry) : null;
  const hasValidExpiry = expiry && !Number.isNaN(expiry.getTime());
  const now = new Date();

  if (status === 'cancelled' && hasValidExpiry && expiry < now) return true;
  if (hasValidExpiry && expiry < now && (profile.subscriptionPlan || '').toLowerCase() !== 'starter') return true;
  return false;
}

export const ENDED_ALLOWED_PATHS = new Set([
  '/billing',
  '/products',
  '/stock',
  '/settings',
]);

export function isAllowedWhenEnded(pathname: string): boolean {
  return ENDED_ALLOWED_PATHS.has(pathname);
}

export type PlanKey = 'starter' | 'basic' | 'professional' | 'business';

export const PLAN_DISPLAY: Record<string, string> = {
  starter:      'Free',
  basic:        'Small Store',
  professional: 'Big Store',
  business:     'Wholesale',
};

export const PLAN_LIMITS: Record<string, { maxProducts: number; maxUdharCustomers: number }> = {
  starter:      { maxProducts: 50,       maxUdharCustomers: 10       },
  basic:        { maxProducts: 200,      maxUdharCustomers: 50       },
  professional: { maxProducts: Infinity, maxUdharCustomers: Infinity },
  business:     { maxProducts: Infinity, maxUdharCustomers: Infinity },
};

export function getPlanLimits(plan: string) {
  return PLAN_LIMITS[plan] ?? PLAN_LIMITS.starter;
}

export function planLabel(plan: string): string {
  return PLAN_DISPLAY[plan] ?? plan;
}

export function canAddProduct(plan: string, currentCount: number): boolean {
  return currentCount < getPlanLimits(plan).maxProducts;
}

export function canAddUdharCustomer(plan: string, currentCount: number): boolean {
  const limit = getPlanLimits(plan).maxUdharCustomers;
  return currentCount < limit;
}

export function canExportReports(plan: string): boolean {
  return plan === 'basic' || plan === 'professional' || plan === 'business';
}

export function productLimitDisplay(plan: string): string {
  const max = getPlanLimits(plan).maxProducts;
  return max === Infinity ? 'Unlimited' : max.toLocaleString('en-IN');
}

export function udharLimitDisplay(plan: string): string {
  const max = getPlanLimits(plan).maxUdharCustomers;
  return max === Infinity ? 'Unlimited' : max.toLocaleString('en-IN');
}

export const UPGRADE_URL = 'http://localhost:5173/payment.html';

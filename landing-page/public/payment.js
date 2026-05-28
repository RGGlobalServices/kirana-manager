/* ================================================================
   Vyapar Sarthi — Payment Page (PayU Integration)
   Requires: config.js
   Flow: Backend generates PayU params → frontend POSTs form to PayU
         → PayU redirects to backend surl/furl → backend redirects here
   ================================================================ */

// ── Plan config ──────────────────────────────────────────────────
const PLANS = {
  basic:        {
    name: 'Small Store Plan', price: 599, period: 'Monthly', billingCycle: 'every 30 days',
    icon: '🛒',
    tagline: 'Chhoti dukaan ke liye',
    features: ['Up to 200 products', 'Billing & GST invoices', 'Udhar tracking (50 customers)', 'WhatsApp bill sharing', 'Low stock alerts', 'Basic reports', 'Bulk product import (Excel/CSV)', 'Mobile app access', 'Referral program', 'Email support'],
  },
  professional: {
    name: 'Big Store Plan', price: 999, period: 'Monthly', billingCycle: 'every 30 days',
    icon: '⚡',
    tagline: 'Badi dukaan ke liye',
    features: ['Unlimited products', 'Full POS billing system', 'Unlimited udhar & customers', 'AI Business Insights', 'Detailed reports + PDF export', 'Bulk product import (Excel/CSV)', 'Hindi & Marathi support', 'WhatsApp bill sharing', 'Referral program', 'Priority chat & email support'],
  },
  business:     {
    name: 'Wholesale Plan', price: 1499, period: 'Yearly', billingCycle: 'every year',
    icon: '🏪',
    tagline: 'Wholesaler · Stockist · Mandi dealer ke liye',
    features: ['Unlimited products', 'AI Business Insights', 'Bulk invoicing & party ledger', 'Dukandar Management — add shopkeepers, view their stock', 'Dealer / distributor accounts', 'Custom price lists per party', 'GST & Tally export', 'Low stock & expiry alerts', 'Referral program', 'Dedicated WhatsApp support'],
  },
};

const TRIAL_DAYS   = 14;
const TRIAL_CHARGE = 2;   // ₹2 charged upfront to verify payment & start mandate

// ── Trial date helpers ───────────────────────────────────────────
function trialEndDate() {
  const d = new Date();
  d.setDate(d.getDate() + TRIAL_DAYS);
  return d;
}
function formatDate(d) {
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}

// ── State ────────────────────────────────────────────────────────
const urlParams = new URLSearchParams(window.location.search);
let planKey = urlParams.get('plan') || localStorage.getItem('ks_plan') || 'professional';
if (!PLANS[planKey]) planKey = 'professional';

function ensurePreAuth() {
  const hasEmail = !!(localStorage.getItem('ks_prefill_email') || '').trim();
  const hasName = !!(localStorage.getItem('ks_prefill_name') || '').trim();
  if (hasEmail && hasName) return;
  const next = encodeURIComponent(`payment.html?plan=${planKey}`);
  window.location.href = `login.html?next=${next}`;
}

// ── Update all UI for the selected plan ─────────────────────────
function applyPlan(key) {
  planKey      = key;
  const plan   = PLANS[key];
  const gst    = Math.round(plan.price * 0.18);
  const total  = plan.price + gst;
  const endDt  = trialEndDate();

  localStorage.setItem('ks_plan',       key);
  localStorage.setItem('ks_plan_name',  plan.name);
  localStorage.setItem('ks_plan_price', plan.price);

  // Order summary left panel
  document.getElementById('planName').textContent   = plan.name;
  document.getElementById('planPeriod').textContent = `${plan.period} billing • Billed ${plan.billingCycle} • ${plan.tagline}`;
  document.getElementById('planPrice').textContent  = '₹' + plan.price;
  document.querySelector('.plan-icon').textContent  = plan.icon;

  // Breakdown — ₹2 today to verify payment, full amount auto-debited after trial
  document.getElementById('breakdownBase').textContent     = '₹' + plan.price;
  document.getElementById('breakdownGst').textContent      = '₹' + gst + ' (after trial)';
  document.getElementById('breakdownDiscount').textContent = '−₹' + (total - TRIAL_CHARGE) + ' (trial discount)';
  document.getElementById('breakdownTotal').textContent    = '₹' + TRIAL_CHARGE;

  // Auto-debit note
  document.getElementById('orderNote').innerHTML =
    `💳 <strong>₹${TRIAL_CHARGE} charged today</strong> to verify your payment method &amp; activate subscription.<br>` +
    `After your 14-day free trial, <strong>₹${total}</strong> (incl. 18% GST) will be auto-debited on <strong>${formatDate(endDt)}</strong>.<br>` +
    `<span style="color:#10b981">✓ Cancel anytime before ${formatDate(endDt)} — no further charges.</span>`;

  // Features list
  document.getElementById('planFeatures').innerHTML =
    plan.features.map(f => `<li>✅ ${f}</li>`).join('');

  // QR amount
  document.getElementById('qrAmount').innerHTML =
    `Amount: <strong>₹${TRIAL_CHARGE} today</strong> <span style="color:#6b7280;font-size:12px">(₹${total} auto-debited after trial)</span>`;

  // Pay button
  document.getElementById('payBtnText').textContent =
    `Pay ₹${TRIAL_CHARGE} & Start 14-Day Free Trial`;

  // Subtitle
  document.getElementById('paySubtitle').textContent =
    `₹${TRIAL_CHARGE} charged now to verify payment. Full ₹${total} auto-debited on ${formatDate(endDt)}.`;

  // Highlight active plan switcher card
  document.querySelectorAll('.plan-switch-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.plan === key);
  });

  // Update URL without reload so sharing/back works
  const newUrl = new URL(window.location.href);
  newUrl.searchParams.set('plan', key);
  window.history.replaceState(null, '', newUrl.toString());
}

// ── Show error / refund status from PayU redirect ───────────────
const errorParam  = urlParams.get('error');
const refundParam = urlParams.get('refund');

if (errorParam) {
  if (refundParam === 'initiated') {
    showErrorBanner(
      `↩️ ${decodeURIComponent(errorParam)}\n` +
      `Your ₹${TRIAL_CHARGE} refund has been initiated and will reach your account within 5–7 business days.`
    );
  } else if (refundParam === 'failed') {
    showErrorBanner(
      `❌ ${decodeURIComponent(errorParam)}\n` +
      `We could not auto-refund ₹${TRIAL_CHARGE} at this time. Please contact gbroindustries@gmail.com with your transaction ID.`
    );
  } else {
    // payu-failure: no money was charged
    showErrorBanner(`❌ ${decodeURIComponent(errorParam)}`);
  }
}

// ── Plan switcher click handlers ─────────────────────────────────
document.querySelectorAll('.plan-switch-btn').forEach(btn => {
  btn.addEventListener('click', () => applyPlan(btn.dataset.plan));
});

// ── Method tabs ──────────────────────────────────────────────────
document.querySelectorAll('.method-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.method-tab').forEach(t  => t.classList.remove('active'));
    document.querySelectorAll('.method-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('panel-' + tab.dataset.method).classList.add('active');
  });
});

// ── UPI sub-tabs ─────────────────────────────────────────────────
document.querySelectorAll('.upi-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.upi-tab').forEach(t  => t.classList.remove('active'));
    document.querySelectorAll('.upi-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('upi-' + tab.dataset.upi).classList.add('active');
  });
});

// ── UPI verify ───────────────────────────────────────────────────
document.getElementById('verifyUpi').addEventListener('click', () => {
  const val    = document.getElementById('upiId').value.trim();
  const status = document.getElementById('upiStatus');
  if (!val) { status.textContent = '⚠️ Please enter your UPI ID'; status.className = 'verify-status error'; return; }
  const valid = /^[\w.\-]+@[\w]+$/.test(val) || /^\d{10}@[\w]+$/.test(val);
  status.textContent = valid ? '✅ UPI ID verified' : '❌ Invalid UPI ID. Try: name@upi or 9876543210@paytm';
  status.className   = valid ? 'verify-status success' : 'verify-status error';
});

// ── Card live preview ────────────────────────────────────────────
document.getElementById('cardNumber').addEventListener('input', (e) => {
  let v = e.target.value.replace(/\D/g, '').slice(0, 16);
  e.target.value = v.match(/.{1,4}/g)?.join(' ') || v;
  document.getElementById('cardNumDisplay').textContent =
    (v + '................').slice(0, 16).replace(/.{4}/g, m => m + ' ').trim()
      .replace(/\d/g, (c, i) => i < 8 ? '•' : c) || '•••• •••• •••• ••••';
  const net = document.getElementById('cardNetwork');
  if (v.startsWith('4'))                             net.textContent = 'VISA';
  else if (/^5[1-5]/.test(v))                       net.textContent = 'MASTERCARD';
  else if (/^6[0-9]/.test(v) || v.startsWith('60')) net.textContent = 'RUPAY';
  else if (v.startsWith('37') || v.startsWith('34')) net.textContent = 'AMEX';
  else                                               net.textContent = 'CARD';
});
document.getElementById('cardHolder').addEventListener('input', (e) => {
  document.getElementById('cardHolderDisplay').textContent = e.target.value.toUpperCase() || 'YOUR NAME';
});
document.getElementById('cardExpiry').addEventListener('input', (e) => {
  let v = e.target.value.replace(/\D/g, '').slice(0, 4);
  if (v.length >= 2) v = v.slice(0, 2) + ' / ' + v.slice(2);
  e.target.value = v;
  document.getElementById('cardExpiryDisplay').textContent = v || 'MM/YY';
});
document.getElementById('cardCvv').addEventListener('focus', () => {
  document.getElementById('creditCardEl').style.transform = 'rotateY(180deg)';
});
document.getElementById('cardCvv').addEventListener('blur', () => {
  document.getElementById('creditCardEl').style.transform = 'rotateY(0deg)';
});

// ── Overlay helpers ──────────────────────────────────────────────
const processingOverlay = document.getElementById('processingOverlay');

function showProcessing(title, sub) {
  document.getElementById('processingTitle').textContent    = title || 'Processing…';
  document.getElementById('processingSubtitle').textContent = sub   || 'Please wait';
  processingOverlay.classList.add('show');
}
function hideProcessing() { processingOverlay.classList.remove('show'); }

function showErrorBanner(msg) {
  let el = document.getElementById('payErrorBanner');
  if (!el) {
    el = document.createElement('div');
    el.id = 'payErrorBanner';
    el.style.cssText = 'background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;border-radius:10px;padding:12px 16px;font-size:14px;margin-top:16px;';
    document.getElementById('payBtn').after(el);
  }
  el.textContent   = msg;
  el.style.display = 'block';
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
function hideErrorBanner() {
  const el = document.getElementById('payErrorBanner');
  if (el) el.style.display = 'none';
}

// ── Core: redirect to PayU ───────────────────────────────────────
async function openPayU() {
  hideErrorBanner();
  showProcessing('Setting up your trial…', `Charging ₹${TRIAL_CHARGE} to verify payment method…`);

  const firstname = localStorage.getItem('ks_prefill_name')  || 'Customer';
  const email     = localStorage.getItem('ks_prefill_email') || 'customer@example.com';
  const phone     = localStorage.getItem('ks_prefill_phone') || '9999999999';

  const orderRes = await ksPost('/payments/create-order', {
    plan: planKey, firstname, email, phone,
    trial_days: TRIAL_DAYS,
  });

  if (!orderRes.ok) {
    hideProcessing();
    showErrorBanner(`❌ ${orderRes.error === 'NETWORK_ERROR'
      ? 'Backend not reachable. Make sure the server is running on localhost:8000.'
      : orderRes.error}`);
    return;
  }

  const d = orderRes.data;

  if (d && d.auth_required) {
    hideProcessing();
    const next = encodeURIComponent(`payment.html?plan=${planKey}`);
    if (d.next === 'login') {
      window.location.href = `login.html?next=${next}`;
      return;
    }
    window.location.href = `register.html?next=${next}&plan=${planKey}`;
    return;
  }

  // ── Free plan — skip PayU entirely ──────────────────────────────
  if (d.free) {
    document.getElementById('processingTitle').textContent    = 'Activating free trial…';
    document.getElementById('processingSubtitle').textContent = 'Redirecting to registration…';
    setTimeout(() => {
      hideProcessing();
      window.location.href = `${KS_CONFIG.FRONTEND_URL}/en/signup`;
    }, 1000);
    return;
  }

  // Store trial info (used by register page)
  localStorage.setItem('ks_plan',        planKey);
  localStorage.setItem('ks_plan_name',   PLANS[planKey].name);
  localStorage.setItem('ks_trial_start', new Date().toISOString());
  localStorage.setItem('ks_trial_end',   trialEndDate().toISOString());

  // ── TEST MODE: PayU keys not configured on backend ───────────────
  if (d.test_mode) {
    localStorage.setItem('ks_txnid',        d.txnid);
    localStorage.setItem('ks_trial_end',    d.trial_end);
    localStorage.setItem('ks_init_amount',  d.init_amount);
    localStorage.setItem('ks_full_amount',  d.full_amount);

    document.getElementById('processingTitle').textContent    = `✅ ₹${d.init_amount} Verified (Test Mode)`;
    document.getElementById('processingSubtitle').textContent = `₹${d.full_amount} auto-debit scheduled after trial`;

    setTimeout(() => {
      hideProcessing();
      // Show success overlay briefly, then go to register
      const overlay = document.getElementById('successOverlay');
      if (overlay) {
        overlay.classList.add('show');
        const bar = document.getElementById('successBar');
        if (bar) { bar.style.transition = 'width 2s ease'; bar.style.width = '100%'; }
        setTimeout(() => { window.location.href = 'register.html'; }, 2200);
      } else {
        window.location.href = 'register.html';
      }
    }, 1400);
    return;
  }

  // ── LIVE MODE: redirect to PayU ─────────────────────────────────
  document.getElementById('processingTitle').textContent    = 'Redirecting to PayU…';
  document.getElementById('processingSubtitle').textContent = `₹${TRIAL_CHARGE} will be charged to verify your payment method`;

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = d.payu_url || '#';
  Object.entries(d.params || {}).forEach(([key, value]) => {
    const input = document.createElement('input');
    input.type  = 'hidden';
    input.name  = key;
    input.value = value;
    form.appendChild(input);
  });
  document.body.appendChild(form);
  form.submit();
}

// ── Pay button ───────────────────────────────────────────────────
document.getElementById('payBtn').addEventListener('click', openPayU);

// ── Init: apply plan from URL / localStorage ─────────────────────
ensurePreAuth();
applyPlan(planKey);

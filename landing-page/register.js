/* ================================================================
   Vyapar Sarthi — Registration Page Script
   Requires: config.js to be loaded first (API_BASE, ksPost, ksSetAuth)
   ================================================================ */

// ── Plan badge from localStorage ────────────────────────────────
function getPlanFromNextParam(nextValue) {
  if (!nextValue) return null;
  try {
    const decoded = decodeURIComponent(nextValue);
    const nextUrl = new URL(decoded, window.location.origin);
    return nextUrl.searchParams.get('plan');
  } catch {
    return null;
  }
}

function buildPaymentRedirectUrl() {
  const params = new URLSearchParams(window.location.search);
  const planFromNext = getPlanFromNextParam(params.get('next'));
  const selectedPlan = planFromNext || localStorage.getItem('ks_plan') || 'professional';
  return `payment.html?plan=${encodeURIComponent(selectedPlan)}`;
}

function hasConfirmedPayment() {
  const txnId = localStorage.getItem('ks_txnid');
  const plan = localStorage.getItem('ks_plan');
  return Boolean(txnId && plan);
}

if (!hasConfirmedPayment()) {
  window.location.replace(buildPaymentRedirectUrl());
  throw new Error('Payment required before registration.');
}

const planKey   = localStorage.getItem('ks_plan')      || 'professional';
const planName  = localStorage.getItem('ks_plan_name') || 'Big Store Plan';
const planIcons = { basic: '🛒', professional: '⚡', business: '🏪' };

document.getElementById('regPlanName').textContent    = planName;
document.querySelector('.plan-badge-icon').textContent = planIcons[planKey] || '⚡';

// ── Referral code: auto-fill from URL + fetch referrer info ──────
const hasExistingAuthAccount = Boolean(localStorage.getItem('ks_auth'));

function splitName(fullName) {
  const cleaned = (fullName || '').trim();
  if (!cleaned) return { firstName: '', lastName: '' };
  const parts = cleaned.split(/\s+/);
  return {
    firstName: parts[0] || '',
    lastName: parts.slice(1).join(' ') || '',
  };
}

function prefillExistingUserData() {
  const apiUser = JSON.parse(localStorage.getItem('ks_api_user') || '{}');
  const localUser = JSON.parse(localStorage.getItem('ks_user') || '{}');
  const prefillName = localStorage.getItem('ks_prefill_name') || apiUser.name || localUser.fullName || '';
  const prefillEmail = localStorage.getItem('ks_prefill_email') || apiUser.email || localUser.email || '';
  const prefillPhone = localStorage.getItem('ks_prefill_phone') || localUser.mobile || '';
  const names = splitName(prefillName);

  const firstNameEl = document.getElementById('firstName');
  const lastNameEl = document.getElementById('lastName');
  const emailEl = document.getElementById('email');
  const mobileEl = document.getElementById('mobile');

  if (names.firstName) firstNameEl.value = names.firstName;
  if (names.lastName) lastNameEl.value = names.lastName;
  if (prefillEmail) emailEl.value = prefillEmail;
  if (prefillPhone) mobileEl.value = prefillPhone;

  if (hasExistingAuthAccount) {
    [firstNameEl, lastNameEl, emailEl, mobileEl].forEach((el) => {
      el.setAttribute('readonly', 'readonly');
      el.style.backgroundColor = '#f9fafb';
    });

    const passGroup = document.getElementById('password')?.closest('.form-group');
    const confirmGroup = document.getElementById('confirmPass')?.closest('.form-group');
    if (passGroup) passGroup.style.display = 'none';
    if (confirmGroup) confirmGroup.style.display = 'none';
  }
}
prefillExistingUserData();

const urlParams = new URLSearchParams(window.location.search);
const refFromUrl = urlParams.get('ref');
const refInput = document.getElementById('referralCode');
const refInfo = document.getElementById('referrerInfo');

async function fetchReferrerInfo(code) {
  if (!code || code.length < 4) {
    refInfo.style.display = 'none';
    return;
  }
  try {
    const res = await fetch(`${KS_CONFIG.API_BASE}/referrals/referrer-info?code=${encodeURIComponent(code)}`);
    if (!res.ok) { refInfo.style.display = 'none'; return; }
    const data = await res.json();
    document.getElementById('referrerName').textContent = data.referrer_name;
    document.getElementById('referrerShop').textContent = `🏪 ${data.shop_name}`;
    const since = data.member_since ? new Date(data.member_since).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    document.getElementById('referrerSince').textContent = since ? `📅 Member since ${since}` : '';
    refInfo.style.display = 'block';
  } catch {
    refInfo.style.display = 'none';
  }
}

if (refFromUrl) {
  refInput.value = refFromUrl.toUpperCase();
  fetchReferrerInfo(refFromUrl.toUpperCase());
}

refInput.addEventListener('input', () => {
  const val = refInput.value.trim().toUpperCase();
  refInput.value = val;
  if (val.length >= 4) {
    fetchReferrerInfo(val);
  } else {
    refInfo.style.display = 'none';
  }
});

// ── Multi-step navigation ────────────────────────────────────────
let currentStep = 1;

function showStep(n) {
  document.querySelectorAll('.form-section').forEach((s, i) => {
    s.classList.toggle('active', i + 1 === n);
  });
  currentStep = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.getElementById('nextStep1').addEventListener('click', () => {
  if (validateStep1()) showStep(2);
});
document.getElementById('nextStep2').addEventListener('click', () => {
  if (validateStep2()) showStep(3);
});
document.getElementById('backStep2').addEventListener('click', () => showStep(1));
document.getElementById('backStep3').addEventListener('click', () => showStep(2));

// ── Password toggle ──────────────────────────────────────────────
document.getElementById('togglePass').addEventListener('click', () => {
  const inp = document.getElementById('password');
  inp.type = inp.type === 'password' ? 'text' : 'password';
});

// ── Password strength ────────────────────────────────────────────
document.getElementById('password').addEventListener('input', (e) => {
  const v  = e.target.value;
  const el = document.getElementById('passStrength');
  el.className = 'pass-strength';
  if (!v) return;
  if (v.length < 6)                                                   el.classList.add('weak');
  else if (v.length < 10 || !/[A-Z]/.test(v) || !/[0-9]/.test(v)) el.classList.add('medium');
  else                                                                el.classList.add('strong');
});

// ── Validation helpers ───────────────────────────────────────────
function setError(id, msg) {
  const el = document.getElementById('err-' + id);
  if (el) el.textContent = msg;
}
function clearErrors() {
  document.querySelectorAll('.field-error').forEach(e => e.textContent = '');
}
function showFormError(msg) {
  let el = document.getElementById('regFormError');
  if (!el) {
    el = document.createElement('div');
    el.id = 'regFormError';
    el.style.cssText = 'background:#fee2e2;color:#991b1b;border-radius:10px;padding:12px 16px;font-size:14px;margin-bottom:16px;border:1px solid #fca5a5;';
    document.getElementById('regForm').prepend(el);
  }
  el.textContent = msg;
  el.style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function hideFormError() {
  const el = document.getElementById('regFormError');
  if (el) el.style.display = 'none';
}

function validateStep1() {
  clearErrors(); hideFormError();
  let ok = true;
  const fn  = document.getElementById('firstName').value.trim();
  const ln  = document.getElementById('lastName').value.trim();
  const mob = document.getElementById('mobile').value.trim();
  const em  = document.getElementById('email').value.trim();
  const pw  = document.getElementById('password').value;
  const cpw = document.getElementById('confirmPass').value;

  if (!fn)                                          { setError('firstName',   __('reg_err_fn'));              ok = false; }
  if (!ln)                                          { setError('lastName',    __('reg_err_ln'));               ok = false; }
  if (!/^\d{10}$/.test(mob))                        { setError('mobile',     __('reg_err_mobile'));            ok = false; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em))      { setError('email',      __('reg_err_email'));             ok = false; }
  if (!hasExistingAuthAccount) {
    if (pw.length < 8)                              { setError('password',   __('reg_err_pass_len'));          ok = false; }
    if (pw !== cpw)                                 { setError('confirmPass',__('reg_err_pass_match'));        ok = false; }
  }
  return ok;
}

function validateStep2() {
  clearErrors(); hideFormError();
  let ok = true;
  const shop  = document.getElementById('shopName').value.trim();
  const btype = document.querySelector('input[name="btype"]:checked');
  const city  = document.getElementById('city').value.trim();
  const state = document.getElementById('state').value;

  if (!shop)  { setError('shopName', __('reg_err_shop'));                ok = false; }
  if (!btype) { setError('btype',    __('reg_err_btype'));               ok = false; }
  if (!city)  { setError('city',     __('reg_err_city'));                ok = false; }
  if (!state) { setError('state',    __('reg_err_state'));               ok = false; }
  return ok;
}

function validateStep3() {
  clearErrors();
  const terms = document.getElementById('termsCheck').checked;
  if (!terms) { setError('terms', __('reg_err_terms')); return false; }
  return true;
}

// ── Processing overlay helpers ───────────────────────────────────
function setProcessingStep(title, sub) {
  document.getElementById('regProcTitle').textContent = title;
  document.getElementById('regProcSub').textContent   = sub;
}

function showProcessing()  { document.getElementById('regProcessing').classList.add('show'); }
function hideProcessing()  { document.getElementById('regProcessing').classList.remove('show'); }

async function ksPatchAuth(path, body) {
  const token = localStorage.getItem('ks_auth');
  if (!token) return { ok: false, error: 'Not authenticated', status: 401 };
  try {
    const res = await fetch(`${KS_CONFIG.API_BASE}${path}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(body),
    });
    let data;
    try { data = await res.json(); } catch (_) { data = {}; }
    if (res.ok) return { ok: true, data };
    return { ok: false, error: data.detail || 'Failed to update shop profile', status: res.status };
  } catch (err) {
    return { ok: false, error: 'NETWORK_ERROR: ' + err.message, status: 0 };
  }
}

// ── Main form submit ─────────────────────────────────────────────
document.getElementById('regForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validateStep3()) return;

  const firstName    = document.getElementById('firstName').value.trim();
  const lastName     = document.getElementById('lastName').value.trim();
  const mobile       = document.getElementById('mobile').value.trim();
  const email        = document.getElementById('email').value.trim();
  const password     = document.getElementById('password').value;
  const shopName     = document.getElementById('shopName').value.trim();
  const businessType = document.querySelector('input[name="btype"]:checked')?.value || 'kirana';
  const city         = document.getElementById('city').value.trim();
  const state        = document.getElementById('state').value;
  const gstNum       = document.getElementById('gstNum').value.trim();
  const language     = document.querySelector('input[name="lang"]:checked')?.value || 'en';

  // Persist language for later redirect
  localStorage.setItem('ks_language', language);

  // Save full local profile (used by success.html and future pages)
  const localProfile = {
    firstName, lastName, mobile, email,
    shopName, businessType, city, state, gstNum,
    language, plan: planKey,
    registeredAt: new Date().toISOString(),
  };
  localStorage.setItem('ks_user', JSON.stringify(localProfile));

  // ── Show processing overlay ──
  showProcessing();
  setProcessingStep(__('reg_proc_creating'), __('reg_proc_setup'));

  // ── Call backend register API ────────────────────────────────
  let result;
  if (hasExistingAuthAccount) {
    result = await ksPatchAuth('/shop/profile', {
      name: shopName,
      business_type: businessType,
      city,
      state,
      gstin: gstNum || null,
    });
  } else {
    result = await ksPost('/auth/register', {
      email,
      password,
      full_name:     `${firstName} ${lastName}`,
      shop_name:     shopName,
      business_type: businessType,
      paid_plan:     localStorage.getItem('ks_plan')  || null,
      paid_txnid:    localStorage.getItem('ks_txnid') || null,
    });
  }

  if (result.ok) {
    // ── Success: store auth token ──────────────────────────────
    let authToken = localStorage.getItem('ks_auth');
    if (!hasExistingAuthAccount) {
      const { access_token, user: apiUser } = result.data;
      ksSetAuth(access_token, apiUser);
      authToken = access_token;
    }

    // Apply referral code if provided
    const refCode = document.getElementById('referralCode').value.trim().toUpperCase();
    if (refCode) {
      try {
        await fetch(`${KS_CONFIG.API_BASE}/referrals/apply`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
          body: JSON.stringify({ referral_code: refCode })
        });
      } catch (e) {
        console.warn('Failed to apply referral code', e);
      }
    }

    setProcessingStep(__('reg_proc_config') + ` ${shopName}…`, __('reg_proc_load'));
    setTimeout(() => {
      setProcessingStep(__('reg_proc_almost'), __('reg_proc_launch'));
    }, 900);
    setTimeout(() => {
      hideProcessing();
      window.location.href = 'success.html';
    }, 1800);

  } else if (result.error && result.error.startsWith('NETWORK_ERROR')) {
    // ── Backend unreachable: offline/local mode ─────────────────
    // Still allow registration flow — user can connect backend later.
    console.warn('[Vyapar Sarthi] Backend not reachable. Running in local mode.');
    setProcessingStep(__('reg_proc_offline'), __('reg_proc_saved'));
    setTimeout(() => {
      hideProcessing();
      window.location.href = 'success.html';
    }, 1600);

  } else if (result.status === 400 && result.error.toLowerCase().includes('already registered')) {
    // ── Email already exists ────────────────────────────────────
    hideProcessing();
    showFormError('⚠️ ' + __('reg_err_dup'));
    // Jump back to step 1 so user can see the email field
    showStep(1);
    document.getElementById('email').focus();

  } else {
    // ── Other server error ──────────────────────────────────────
    hideProcessing();
    showFormError(`❌ Registration failed: ${result.error}`);
  }
});

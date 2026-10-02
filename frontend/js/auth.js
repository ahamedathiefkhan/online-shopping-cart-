/**
 * Auth module — Handle user login via Mobile Number + OTP, Registration, and Profile Management
 */

let currentOtpPhone = '';
let resendTimer = null;

// Send OTP form handler
async function handleSendOtp(event) {
  if (event) event.preventDefault();
  const phoneInput = document.getElementById('login-phone');
  if (!phoneInput) return;

  const phone = phoneInput.value.trim();
  if (!phone || phone.replace(/\D/g, '').length < 7) {
    showToast('Please enter a valid mobile phone number', 'error');
    return;
  }

  const sendBtn = document.getElementById('send-otp-btn');
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.textContent = 'SENDING OTP...';
  }

  try {
    const res = await apiRequest('/users/send-otp', {
      method: 'POST',
      body: { phone }
    });

    currentOtpPhone = phone;
    showToast(`OTP generated and sent to ${phone}!`, 'success');

    // Display OTP notice box for easy testing & simulated SMS
    const smsBox = document.getElementById('simulated-sms-box');
    const otpNotice = document.getElementById('otp-code-display');
    if (smsBox && otpNotice) {
      otpNotice.textContent = res.otp;
      smsBox.style.display = 'block';
    }

    // Auto-fill OTP field for convenient testing
    const otpInput = document.getElementById('login-otp');
    if (otpInput) {
      otpInput.value = res.otp;
    }

    // Show Step 2 (OTP Entry section)
    const step1 = document.getElementById('auth-step-1');
    const step2 = document.getElementById('auth-step-2');
    if (step1 && step2) {
      step1.style.display = 'none';
      step2.style.display = 'block';
    }

    startResendCountdown();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.textContent = 'SEND OTP →';
    }
  }
}

// Resend OTP countdown timer
function startResendCountdown() {
  let seconds = 30;
  const resendBtn = document.getElementById('resend-otp-btn');
  if (!resendBtn) return;

  resendBtn.disabled = true;
  clearInterval(resendTimer);

  resendTimer = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(resendTimer);
      resendBtn.disabled = false;
      resendBtn.textContent = 'RESEND OTP';
    } else {
      resendBtn.textContent = `RESEND OTP (${seconds}s)`;
    }
  }, 1000);
}

// Back to Step 1 (Change phone number)
function backToStep1() {
  const step1 = document.getElementById('auth-step-1');
  const step2 = document.getElementById('auth-step-2');
  if (step1 && step2) {
    step1.style.display = 'block';
    step2.style.display = 'none';
  }
}

// Verify OTP & Login handler
async function handleVerifyOtpSubmit(event) {
  if (event) event.preventDefault();
  const phone = currentOtpPhone || (document.getElementById('login-phone') ? document.getElementById('login-phone').value.trim() : '');
  const otpInput = document.getElementById('login-otp');
  const otp = otpInput ? otpInput.value.trim() : '';

  if (!phone || !otp) {
    showToast('Mobile number and 6-digit OTP are required', 'error');
    return;
  }

  const verifyBtn = document.getElementById('verify-otp-btn');
  if (verifyBtn) {
    verifyBtn.disabled = true;
    verifyBtn.textContent = 'VERIFYING...';
  }

  try {
    const res = await apiRequest('/users/verify-otp', {
      method: 'POST',
      body: { phone, otp }
    });

    showToast(`Welcome, ${res.user.name}!`, 'success');
    currentUser = res.user;
    await getAuthUser(true);

    setTimeout(() => {
      if (res.user.role === 'admin') {
        window.location.href = '/pages/admin/dashboard.html';
      } else {
        window.location.href = '/pages/index.html';
      }
    }, 600);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (verifyBtn) {
      verifyBtn.disabled = false;
      verifyBtn.textContent = 'VERIFY OTP & SIGN IN →';
    }
  }
}

// Quick fill phone for demo buttons
async function quickLoginWithPhone(phone) {
  const phoneInput = document.getElementById('login-phone');
  if (phoneInput) {
    phoneInput.value = phone;
  }
  await handleSendOtp();
}

// Registration form handler with Mobile + OTP
async function handleRegisterFormSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const name = form.name.value.trim();
  const phone = form.phone.value.trim();
  const email = form.email ? form.email.value.trim() : '';
  const role = form.role ? form.role.value : 'customer';

  if (!name || !phone) {
    showToast('Name and Mobile number are required', 'error');
    return;
  }

  try {
    const res = await apiRequest('/users/register', {
      method: 'POST',
      body: { name, phone, email, role }
    });

    showToast('Operator account registered successfully!', 'success');
    currentUser = res.user;
    await getAuthUser(true);

    setTimeout(() => {
      if (res.user.role === 'admin') {
        window.location.href = '/pages/admin/dashboard.html';
      } else {
        window.location.href = '/pages/index.html';
      }
    }, 600);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Profile update handler
async function handleProfileUpdateSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const name = form.name.value.trim();
  const phone = form.phone ? form.phone.value.trim() : '';

  try {
    const res = await apiRequest('/users/profile', {
      method: 'PUT',
      body: { name, phone }
    });

    showToast('Profile updated successfully!', 'success');
    currentUser = res.user;
    updateNavbarUserUI();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

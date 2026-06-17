(function () {
  'use strict';

  const form = document.getElementById('login-form');
  const loginButton = document.getElementById('login-button');
  const errorAlert = document.getElementById('login-error');
  const errorMessage = document.getElementById('login-error-message');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  function showError(message) {
    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');
  }

  function hideError() {
    errorAlert.classList.add('d-none');
    errorMessage.textContent = '';
  }

  async function checkExistingSession() {
    try {
      const response = await fetch('/auth/me', { credentials: 'same-origin' });
      if (response.ok) {
        window.location.href = '/ui/';
      }
    } catch {
      return;
    }
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    hideError();

    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
      showError('Ingresa usuario y contraseña.');
      return;
    }

    loginButton.disabled = true;
    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ username: username, password: password }),
      });

      let body = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }

      if (!response.ok) {
        showError((body && body.detail) || 'No se pudo iniciar sesión.');
        return;
      }

      window.location.href = '/ui/';
    } catch {
      showError('No se pudo conectar con el servidor de autenticación.');
    } finally {
      loginButton.disabled = false;
    }
  });

  checkExistingSession();
})();

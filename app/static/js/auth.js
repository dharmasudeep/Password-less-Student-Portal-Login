const forms = document.querySelectorAll('form[data-controller="auth"]');

forms.forEach((form) => {
  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    form.addEventListener('submit', () => {
      submitButton.disabled = true;
      submitButton.dataset.originalText = submitButton.textContent;
      submitButton.textContent = 'Please wait…';
    });
  }

  const toggles = form.querySelectorAll('.password-toggle');
  toggles.forEach((toggle) => {
    const field = toggle.closest('.password-field');
    if (!field) return;
    const input = field.querySelector('input');
    if (!input) return;
    toggle.addEventListener('click', () => {
      const isPassword = input.getAttribute('type') === 'password';
      input.setAttribute('type', isPassword ? 'text' : 'password');
      toggle.textContent = isPassword ? 'Hide' : 'Show';
      toggle.setAttribute('aria-pressed', (!isPassword).toString());
      input.focus();
    });
  });
});

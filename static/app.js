document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', (e) => {
            const isDark = e.target.checked;
            const theme = isDark ? 'dark' : 'light';
            document.body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);

            // If on settings page, the form will handle save, otherwise we might want to update silently
            // Fetch API to update theme on server
            const formData = new FormData();
            formData.append('theme', theme);
            
            fetch('/settings', {
                method: 'POST',
                body: formData
            }).catch(err => console.error('Error saving theme:', err));
        });
    }

    // Auto dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Mobile sidebar toggle
    const mobileToggle = document.getElementById('mobile-nav-toggle');
    const sidebar = document.getElementById('sidebar');
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('active')) {
            if (!sidebar.contains(e.target) && e.target !== mobileToggle && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });

    // Quick absence button
    const quickAbsenceBtns = document.querySelectorAll('.btn-quick-absence');
    quickAbsenceBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const courseId = btn.getAttribute('data-course-id');
            if (!courseId) return;

            btn.disabled = true;
            btn.innerHTML = '<span class="material-icons-outlined">hourglass_empty</span>';

            fetch(`/api/quick-absence/${courseId}`, {
                method: 'POST',
            })
            .then(res => {
                if (res.ok) {
                    window.location.reload();
                } else {
                    alert('Hiba történt a hiányzás rögzítésekor.');
                    btn.disabled = false;
                    btn.innerHTML = '<span class="material-icons-outlined">add</span> Hiányzás rögzítése';
                }
            })
            .catch(err => {
                console.error(err);
                btn.disabled = false;
                btn.innerHTML = '<span class="material-icons-outlined">add</span> Hiányzás rögzítése';
            });
        });
    });

    // Color picker preview
    const colorPicker = document.getElementById('color');
    if (colorPicker) {
        colorPicker.addEventListener('input', (e) => {
            const previewElements = document.querySelectorAll('.color-preview');
            previewElements.forEach(el => {
                el.style.backgroundColor = e.target.value;
                el.style.setProperty('--course-color', e.target.value);
            });
        });
    }

    // Modal logic
    const modalBackdrop = document.getElementById('modal-backdrop');
    const btnCancelModal = document.getElementById('btn-cancel-modal');
    const modalConfirmForms = document.querySelectorAll('.needs-confirmation');

    if (modalBackdrop && btnCancelModal) {
        let currentForm = null;

        modalConfirmForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                currentForm = form;
                modalBackdrop.classList.add('active');
            });
        });

        btnCancelModal.addEventListener('click', () => {
            modalBackdrop.classList.remove('active');
            currentForm = null;
        });

        const btnConfirmModal = document.getElementById('btn-confirm-modal');
        if (btnConfirmModal) {
            btnConfirmModal.addEventListener('click', () => {
                if (currentForm) {
                    currentForm.submit();
                }
            });
        }
    }
    
    // Client side password validation
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const pw = document.getElementById('password').value;
            const pwConf = document.getElementById('confirm_password').value;
            if (pw !== pwConf) {
                e.preventDefault();
                alert('A jelszavak nem egyeznek!');
            }
        });
    }
});

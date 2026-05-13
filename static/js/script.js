/**
 * Campus Lost & Found - Client-Side JavaScript
 * Handles dark mode, image preview, form validation, and UI interactions.
 */

// ============================================================
// DARK MODE TOGGLE
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateIcon(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateIcon(next);
        });
    }

    function updateIcon(theme) {
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        }
    }

    // Auto-dismiss flash alerts after 5 seconds
    document.querySelectorAll('.flash-alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Counter animation for stats on the home page
    document.querySelectorAll('.counter').forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target')) || 0;
        if (target === 0) return;
        let current = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = current;
            }
        }, 30);
    });

    // ============================================================
    // "OTHER" DROPDOWN → CUSTOM TEXT INPUT
    // ============================================================
    // For every <select> that contains an "Other" option, inject a
    // text input that appears only when "Other" is chosen.
    document.querySelectorAll('select.form-select, select.form-control').forEach(select => {
        // Check if this select has an "Other" option
        const otherOpt = Array.from(select.options).find(o => o.value === 'Other');
        if (!otherOpt) return;

        // Create the custom text input (hidden by default)
        const wrapper = document.createElement('div');
        wrapper.className = 'other-input-wrapper mt-2';
        wrapper.style.display = 'none';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        input.placeholder = 'Please specify...';
        input.setAttribute('maxlength', '100');

        wrapper.appendChild(input);
        select.parentNode.insertBefore(wrapper, select.nextSibling);

        // Show/hide on change
        select.addEventListener('change', () => {
            if (select.value === 'Other') {
                wrapper.style.display = 'block';
                input.focus();
                input.required = true;
            } else {
                wrapper.style.display = 'none';
                input.value = '';
                input.required = false;
            }
        });

        // Before form submits, swap the select value with the typed text
        const form = select.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                if (select.value === 'Other' && input.value.trim()) {
                    // Add a new option with the custom value and select it
                    const customOpt = document.createElement('option');
                    customOpt.value = input.value.trim();
                    customOpt.textContent = input.value.trim();
                    customOpt.selected = true;
                    select.appendChild(customOpt);
                }
            });
        }

        // If the select already shows "Other" on page load (e.g. editing)
        if (select.value === 'Other') {
            wrapper.style.display = 'block';
        }
    });
});

// ============================================================
// IMAGE PREVIEW
// ============================================================
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    const img = document.getElementById('previewImg');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    } else {
        preview.style.display = 'none';
    }
}

// ============================================================
// PASSWORD VISIBILITY TOGGLE
// ============================================================
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

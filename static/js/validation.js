/* Immediate browser feedback; Flask/WTF remains the final security check. */
(() => {
  const PHONE_PATTERN = /^09\d{9}$/;
  const NAME_PATTERN = /^[\p{L}][\p{L} '\-]*$/u;
  const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const setError = (input, message) => {
    input.classList.remove("is-valid");
    input.classList.add("is-invalid");
    let error = input.parentElement.querySelector(".client-error");
    if (!error) {
      error = document.createElement("small");
      error.className = "text-danger d-block client-error";
      input.parentElement.appendChild(error);
    }
    error.textContent = message;
  };

  const clearError = (input) => {
    input.classList.remove("is-invalid");
    const error = input.parentElement.querySelector(".client-error");
    if (error) error.remove();
  };

  const markValid = (input) => {
    clearError(input);
    input.classList.add("is-valid");
  };

  const validEmailSyntax = (value) => {
    const email = value.trim();
    if (!email || email.length > 254 || email.split("@").length !== 2) return false;
    const [local, domain] = email.split("@");
    if (!local || !domain || local.length > 64) return false;
    if (/\.\.|^\.|\.$/.test(local) || /\.\.|^\.|\.$/.test(domain)) return false;
    if (!EMAIL_PATTERN.test(email)) return false;
    return domain.split(".").every((label) => (
      label.length <= 63 && /^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$/.test(label)
    ));
  };

  const validPhone = (value) => (
    PHONE_PATTERN.test(value.trim()) && !/(\d)\1{4,}/.test(value.trim())
  );

  const validateRegistration = (form) => {
    let valid = true;
    const fullName = form.querySelector("#full_name");
    const email = form.querySelector("#email");
    const contact = form.querySelector("#contact_number");
    const password = form.querySelector("#password");
    const confirmPassword = form.querySelector("#confirm_password");

    [fullName, email, contact, password, confirmPassword].forEach((input) => {
      if (input) clearError(input);
    });

    if (fullName && !NAME_PATTERN.test(fullName.value.trim())) {
      setError(fullName, "Please enter a valid name.");
      valid = false;
    }
    if (email && !validEmailSyntax(email.value)) {
      setError(email, "Please enter a valid email address.");
      valid = false;
    }
    if (contact && !validPhone(contact.value)) {
      setError(contact, "Use 11 digits starting with 09; repeated-digit numbers are not valid.");
      valid = false;
    }
    if (password && !(password.value.length >= 8 && /[A-Z]/.test(password.value)
      && /[a-z]/.test(password.value) && /\d/.test(password.value))) {
      setError(password, "Password must contain 8 characters, uppercase, lowercase, and a number.");
      valid = false;
    }
    if (confirmPassword && password && confirmPassword.value !== password.value) {
      setError(confirmPassword, "Passwords do not match.");
      valid = false;
    }
    return valid;
  };

  const getPhilippineDate = () => {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: "Asia/Manila",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(new Date());
    const values = Object.fromEntries(parts.map(({ type, value }) => [type, Number(value)]));
    return new Date(values.year, values.month - 1, values.day);
  };

  const parseIsoDate = (value) => {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value.trim());
    if (!match) return null;
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const date = new Date(year, month - 1, day);
    if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return null;
    return date;
  };

  const validateBooking = (form) => {
    let valid = true;
    const dateInput = form.querySelector("#trip_date");
    const passengers = form.querySelector("#passenger_count");

    if (dateInput) {
      clearError(dateInput);
      const selectedDate = parseIsoDate(dateInput.value);
      if (!selectedDate) {
        setError(dateInput, "Please choose a valid calendar date.");
        valid = false;
      } else if (selectedDate < getPhilippineDate()) {
        setError(dateInput, "Trip date cannot be in the past.");
        valid = false;
      } else {
        markValid(dateInput);
      }
    }

    if (passengers) {
      clearError(passengers);
      if (!/^\d+$/.test(passengers.value) || Number(passengers.value) < 1 || Number(passengers.value) > 10) {
        setError(passengers, "Passenger count must be a whole number from 1 to 10.");
        valid = false;
      } else {
        markValid(passengers);
      }
    }
    return valid;
  };

  const validateLogin = (form) => {
    let valid = true;
    const email = form.querySelector("#email");
    const password = form.querySelector("#password");
    [email, password].forEach((input) => { if (input) clearError(input); });
    if (email && !validEmailSyntax(email.value)) {
      setError(email, "Please enter a valid email address.");
      valid = false;
    }
    if (password && !password.value) {
      setError(password, "Please enter your password.");
      valid = false;
    }
    return valid;
  };

  const protectSubmit = (form, label) => {
    const submit = form.querySelector("button[type='submit'], input[type='submit']");
    if (!submit) return;
    submit.disabled = true;
    if (submit.tagName === "INPUT") submit.value = label;
    else submit.textContent = label;
  };

  const initializeTripDatePicker = () => {
    const dateInput = document.querySelector("#trip_date");
    if (!dateInput || typeof window.flatpickr !== "function") return;
    const today = getPhilippineDate();
    const todayIso = [today.getFullYear(), String(today.getMonth() + 1).padStart(2, "0"), String(today.getDate()).padStart(2, "0")].join("-");
    window.flatpickr(dateInput, {
      allowInput: true,
      altInput: true,
      altFormat: "m/d/Y",
      dateFormat: "Y-m-d",
      minDate: todayIso,
      disableMobile: false,
      onReady: (_selectedDates, _dateStr, instance) => {
        instance.altInput.setAttribute("placeholder", "MM/DD/YYYY");
        instance.altInput.setAttribute("aria-label", "Trip date (MM/DD/YYYY)");
      },
    });
  };

  const initializeBoatCards = () => {
    const select = document.querySelector("#boat_id");
    if (!select) return;
    document.querySelectorAll("[data-boat-id]").forEach((card) => {
      card.addEventListener("click", () => {
        select.value = card.dataset.boatId;
        document.querySelectorAll("[data-boat-id]").forEach((item) => item.setAttribute("aria-pressed", String(item === card)));
      });
    });
  };

  const addPasswordToggles = () => {
    document.querySelectorAll("input[type='password']").forEach((input) => {
      if (input.dataset.passwordToggleReady === "true") return;
      input.dataset.passwordToggleReady = "true";
      const wrapper = document.createElement("div");
      wrapper.className = "password-field position-relative";
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "password-toggle";
      toggle.setAttribute("aria-label", "Show password");
      toggle.setAttribute("aria-pressed", "false");
      toggle.innerHTML = "<span aria-hidden='true'>👁</span>";
      toggle.addEventListener("click", () => {
        const showing = input.type === "text";
        input.type = showing ? "password" : "text";
        toggle.setAttribute("aria-label", showing ? "Show password" : "Hide password");
        toggle.setAttribute("aria-pressed", String(!showing));
        toggle.innerHTML = "<span aria-hidden='true'>👁</span>";
        input.focus();
      });
      wrapper.appendChild(toggle);
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    addPasswordToggles();
    initializeTripDatePicker();
    initializeBoatCards();
    const registrationForm = document.querySelector("#registration-form");
    if (registrationForm) {
      const contact = registrationForm.querySelector("#contact_number");
      if (contact) {
        contact.addEventListener("input", () => {
          if (!contact.value.trim()) {
            clearError(contact);
            return;
          }
          if (validPhone(contact.value)) markValid(contact);
          else setError(contact, "Use 11 digits starting with 09; repeated-digit numbers are not valid.");
        });
      }
      registrationForm.addEventListener("submit", (event) => {
        if (!validateRegistration(registrationForm)) event.preventDefault();
        else protectSubmit(registrationForm, "Creating account…");
      });
    }

    const loginForm = document.querySelector("#login-form");
    if (loginForm) {
      loginForm.addEventListener("submit", (event) => {
        if (!validateLogin(loginForm)) event.preventDefault();
        else protectSubmit(loginForm, "Signing in…");
      });
    }

    const bookingForm = document.querySelector("#booking-form");
    if (bookingForm) {
      bookingForm.addEventListener("submit", (event) => {
        if (!validateBooking(bookingForm)) event.preventDefault();
        else protectSubmit(bookingForm, "Submitting request…");
      });
    }
  });
})();

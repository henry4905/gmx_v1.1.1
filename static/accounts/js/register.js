// --- DOM Loaded ---
document.addEventListener("DOMContentLoaded", () => {
  let selectedType = "";
  let currentForm = null;

  const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  // Main sections
  const pwdDiv = document.querySelector(".user-password");
  const smsDiv = document.getElementById("phoneVerification");
  const dropdownDiv = document.getElementById("seldiv");

  if (pwdDiv) pwdDiv.style.display = "none";
  if (smsDiv) smsDiv.style.display = "none";
  ["worker", "facility", "importer"].forEach(f => {
    const el = document.getElementById(f);
    if (el) el.style.display = "none";
  });

  // --- Dropdown selection ---
  const btn = document.getElementById("selectBtn");
  const list = document.getElementById("selectList");
  const selectedText = document.getElementById("selectedText");

  btn.addEventListener("click", () => list.classList.toggle("open"));

  list.querySelectorAll("div").forEach(item => {
    item.addEventListener("click", () => {
      selectedType = item.dataset.type;        // պահում ենք data-type-ը
      selectedText.textContent = item.textContent; // ցուցադրում ենք տեքստը
      list.classList.remove("open");           // փակում ենք dropdown-ը
      console.log("✅ Selected user type:", selectedType);

      showForm(selectedType);
    });
  });

  function showForm(type) {
    ["worker", "facility", "importer"].forEach(f => {
      const el = document.getElementById(f);
      if (f === type) fadeIn(el), currentForm = el;
      else fadeOut(document.getElementById(f));
    });
    fadeOut(pwdDiv);
    fadeOut(smsDiv);
    fadeIn(dropdownDiv);
  }

  function fadeIn(el) {
    if (!el) return;
    el.style.display = "block"; el.style.opacity = 0;
    let op = 0;
    const t = setInterval(() => {
      if (op >= 1) { clearInterval(t); el.style.opacity = 1; }
      else { el.style.opacity = op; op += 0.1; }
    }, 20);
  }

  function fadeOut(el) {
    if (!el) return;
    el.style.opacity = 1;
    const t = setInterval(() => {
      if (el.style.opacity <= 0) { clearInterval(t); el.style.display = "none"; }
      el.style.opacity -= 0.1;
    }, 20);
  }

  // Enable submit buttons only when all required fields are filled
  function monitorInputs(formId, btnId) {
    const form = document.getElementById(formId), btn = document.getElementById(btnId);
    if (!form || !btn) return;
    const inputs = form.querySelectorAll("input,select");
    inputs.forEach(input => {
      input.addEventListener("input", () => {
        let valid = true;
        inputs.forEach(i => { if (i.hasAttribute("required") && !i.value) valid = false; });
        btn.disabled = !valid;
      });
    });
  }

  monitorInputs("worker", "workerSubmitBtn");
  monitorInputs("facility", "f_submit");
  monitorInputs("importer", "i_submit");

  // Worker submit click - AJAX email check
  document.getElementById("workerSubmitBtn").addEventListener("click", (e) => {
    e.preventDefault();
    const email = document.getElementById("w_email").value;
    checkWorkerEmail(email, currentForm);
  });

  function checkWorkerEmail(email, form) {
    const errorDiv = document.getElementById("workerError");
    if (!email) return;
    fetch("/accounts/register/check_worker_email/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken
      },
      body: JSON.stringify({ email: email })
    })
      .then(res => res.json())
      .then(data => {
        if (data.exists) {
          errorDiv.textContent = "Այդ email-ը արդեն օգտագործվում է";
          errorDiv.style.display = "block";
          form.querySelector("#workerSubmitBtn").disabled = true;
        } else {
          errorDiv.style.display = "none";
          fadeOut(currentForm);
          fadeOut(dropdownDiv);
          fadeIn(pwdDiv);
          const pwdBtn = pwdDiv.querySelector("#passwordSubmitBtn");
          if (pwdBtn) pwdBtn.disabled = true;
        }
      })
      .catch(err => console.error(err));
  }

  // Facility & Importer submit click to password section
  ["f_submit", "i_submit"].forEach(btnId => {
    const btn = document.getElementById(btnId);
    btn.addEventListener("click", () => {

      console.log("📌 Current user type:", selectedType);
      console.log("📞 Phone:", getPhoneByType());
      

      fadeOut(currentForm);
      fadeOut(dropdownDiv);
      fadeIn(pwdDiv);
      const pwdBtn = pwdDiv.querySelector("#passwordSubmitBtn");
      if (pwdBtn) pwdBtn.disabled = true;
    });
  });

  // Password validation
  if (pwdDiv) {
    const password = pwdDiv.querySelector("#i_password");
    const confirm = pwdDiv.querySelector("#i_confirm");
    const rules = {
      len: pwdDiv.querySelector("#i_len"),
      upper: pwdDiv.querySelector("#i_upper"),
      special: pwdDiv.querySelector("#i_special"),
      match: pwdDiv.querySelector("#i_match")
    };
    const submitBtn = pwdDiv.querySelector("#passwordSubmitBtn");

    function checkPassword() {
      const val = password.value;
      const valConfirm = confirm.value;
      let ok = true;

      if (val.length >= 8) { rules.len.querySelector(".icon").textContent = "✔"; rules.len.querySelector(".icon").style.color = "green"; }
      else { rules.len.querySelector(".icon").textContent = "✕"; rules.len.querySelector(".icon").style.color = "red"; ok = false; }
      if (/[A-Z]/.test(val)) { rules.upper.querySelector(".icon").textContent = "✔"; rules.upper.querySelector(".icon").style.color = "green"; }
      else { rules.upper.querySelector(".icon").textContent = "✕"; rules.upper.querySelector(".icon").style.color = "red"; ok = false; }
      if (/[!@#$%]/.test(val)) { rules.special.querySelector(".icon").textContent = "✔"; rules.special.querySelector(".icon").style.color = "green"; }
      else { rules.special.querySelector(".icon").textContent = "✕"; rules.special.querySelector(".icon").style.color = "red"; ok = false; }
      if (val === valConfirm && val !== "") { rules.match.querySelector(".icon").textContent = "✔"; rules.match.querySelector(".icon").style.color = "green"; }
      else { rules.match.querySelector(".icon").textContent = "✕"; rules.match.querySelector(".icon").style.color = "red"; ok = false; }

      submitBtn.disabled = !ok;
    }

    password.addEventListener("input", checkPassword);
    confirm.addEventListener("input", checkPassword);

    // --- Collect user data function ---
    function collectUserData() {
      if (!currentForm) return null;

      const inputs = currentForm.querySelectorAll("input, select");
      const userData = {};

      // Նորմալ դաշտերի հավաքում
      inputs.forEach(input => {
        const name = input.name || input.id; 
        if (name) userData[name] = input.value;
      });

      // User type ներառում
      userData["type"] = selectedType || "";

      // Գաղտնաբառը հատուկ դաշտից ավելացնում ենք
      if (password.value) userData["password"] = password.value;

      // Սեռի ընտրություն, եթե կա radio կամ select դաշտ
      const sexInput = document.querySelector('input[name="sex"]:checked');
      if (sexInput) userData["sex"] = sexInput.value;

      console.log("Collected user data:", userData);
      return userData;
    }

    function getPhoneByType() {
      if (selectedType === "worker") {
        return document.getElementById("w_country_code").value +
               document.getElementById("w_phone").value;
      }

      if (selectedType === "facility") {
        return document.getElementById("f_country_code").value +
               document.getElementById("f_phone").value;
      }

      if (selectedType === "importer") {
        return document.getElementById("i_country_code").value +
               document.getElementById("i_phone").value;
      }

      return "";

    }

    // On password submit -> send SMS with country code and collect data
    submitBtn.addEventListener("click", () => {

      const phone = getPhoneByType();
      console.log(phone);

      if (!phone || phone.length < 6) {
        return alert("Մուտքագրեք վավեր հեռախոսահամար");
      }


      const userData = collectUserData();
      console.log(userData);

      fetch("/accounts/register/send_sms_code/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ phone: phone, user_data: userData })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            fadeOut(pwdDiv);
            fadeIn(smsDiv);
            fadeOut(dropdownDiv);
            startSMSTimer();
          } else {
            alert("SMS ուղարկելու ժամանակ սխալ տեղի ունեցավ");
          }
        })
        .catch(err => console.error(err));
    });
  }

  // --- SMS timer & resend button ---
  function startSMSTimer() {
    const timerEl = document.getElementById("timer");
    let t = 60; timerEl.textContent = t;
    const interval = setInterval(() => {
      t--; timerEl.textContent = t;
      if (t <= 0) { clearInterval(interval); document.getElementById("resendCodeBtn").style.display = "block"; }
    }, 1000);
  }

  document.getElementById("resendCodeBtn").addEventListener("click", () => {
    document.getElementById("resendCodeBtn").style.display = "none";
    const phone = getPhoneByType();
    console.log(phone);

    const userData = collectUserData();

    fetch("/accounts/register/send_sms_code/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken
      },
      body: JSON.stringify({ phone: phone, user_data: userData })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) startSMSTimer();
        else alert("Սխալ տեղի ունեցավ SMS ուղարկման ժամանակ");
      })
      .catch(err => console.error(err));
  });

  // --- SMS verification button ---
  document.getElementById("verifyCodeBtn").addEventListener("click", () => {
    const phone = getPhoneByType();
    console.log(phone);
    const code = document.getElementById("smsCode").value;

    if (!phone || !code) return alert("Մուտքագրեք հեռախոսահամարն ու կոդը");
    
    const userData = collectUserData();

    fetch("/accounts/register/verify_sms_code/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken
      },
      body: JSON.stringify({ phone: phone, code: code, user_data: userData })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success === true || data.success === 1) {

          // Բուժաշխատող → ուղիղ հաջողության էջ / login
          if (selectedType === "worker") {
            window.location.href = "/accounts/register/success/worker/";
          }

          // Բուժհաստատություն և Ներմուծող → admin հաստատման էջ
          else if (selectedType === "facility" || selectedType === "importer") {
            window.location.href = "/accounts/register/success/pending/";
          }

        } else {
          alert("Սխալ SMS կոդ");
        }
      })

      .catch(err => {
        console.error(err);
        alert("Սխալ տեղի ունեցավ կապի ժամանակ");
      });
  });

  // Worker birthday selects
  const yearSelect = document.getElementById("w_birth_year");
  const monthSelect = document.getElementById("w_birth_month");
  const daySelect = document.getElementById("w_birth_day");
  const currentYear = new Date().getFullYear();

  if (yearSelect && monthSelect && daySelect) {
    for (let y = currentYear; y >= 1900; y--) {
      const opt = document.createElement("option");
      opt.value = y; opt.textContent = y; yearSelect.appendChild(opt);
    }
    for (let m = 1; m <= 12; m++) {
      const opt = document.createElement("option");
      opt.value = m; opt.textContent = m; monthSelect.appendChild(opt);
    }
    function fillDays() {
      const year = parseInt(yearSelect.value) || currentYear;
      const month = parseInt(monthSelect.value) || 1;
      const daysInMonth = new Date(year, month, 0).getDate();
      daySelect.innerHTML = "";
      for (let d = 1; d <= daysInMonth; d++) {
        const opt = document.createElement("option");
        opt.value = d; opt.textContent = d;
        daySelect.appendChild(opt);
      }
    }
    yearSelect.addEventListener("change", fillDays);
    monthSelect.addEventListener("change", fillDays);
    fillDays();
  }

});

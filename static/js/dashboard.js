const fmt = (n) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(n);

const balanceEl = document.getElementById("balanceAmount");
const historyList = document.getElementById("historyList");
let balanceVisible = true;
let currentBalance = 0;

// ---------- Cargar saldo ----------
async function loadBalance() {
  const res = await fetch("/api/balance");
  const data = await res.json();
  currentBalance = data.balance;
  renderBalance();
}

function renderBalance() {
  balanceEl.textContent = balanceVisible ? fmt(currentBalance) : "••••••";
}

document.getElementById("toggleBalance").addEventListener("click", () => {
  balanceVisible = !balanceVisible;
  renderBalance();
});

// ---------- Cargar historial ----------
async function loadHistory() {
  const res = await fetch("/api/history");
  const items = await res.json();

  if (!items.length) {
    historyList.innerHTML = `<li class="history-empty">Aún no tienes movimientos</li>`;
    return;
  }

  historyList.innerHTML = items
    .map((tx) => {
      const isIn = tx.direction === "in";
      const icon = tx.type === "deposit" ? "＋" : isIn ? "↓" : "↑";
      const sign = isIn ? "+" : "−";
      return `
        <li class="history-item">
          <div class="history-icon ${isIn ? "in" : "out"}">${icon}</div>
          <div class="history-info">
            <div class="history-title">${tx.description || tx.counterpart}</div>
            <div class="history-date">${tx.date}</div>
          </div>
          <div class="history-amount ${isIn ? "in" : "out"}">${sign} ${fmt(tx.amount)}</div>
        </li>`;
    })
    .join("");
}

// ---------- Modales ----------
function openModal(id) { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }

document.getElementById("openDeposit").addEventListener("click", () => openModal("depositModal"));
document.getElementById("openTransfer").addEventListener("click", () => openModal("transferModal"));
document.querySelectorAll("[data-close]").forEach((btn) =>
  btn.addEventListener("click", () => closeModal(btn.dataset.close))
);
document.querySelectorAll(".modal-overlay").forEach((overlay) =>
  overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.classList.remove("open"); })
);

// Chips de monto rápido
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    document.getElementById("depositAmount").value = chip.dataset.amount;
  });
});

// ---------- Recargar ----------
document.getElementById("depositForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const amount = Number(document.getElementById("depositAmount").value);
  const errorEl = document.getElementById("depositError");
  errorEl.textContent = "";

  const res = await fetch("/api/deposit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount }),
  });
  const data = await res.json();

  if (!res.ok) {
    errorEl.textContent = data.error || "Ocurrió un error";
    return;
  }

  currentBalance = data.balance;
  renderBalance();
  closeModal("depositModal");
  e.target.reset();
  loadHistory();
});

// ---------- Transferir ----------
document.getElementById("transferForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    phone: document.getElementById("transferPhone").value.trim(),
    amount: Number(document.getElementById("transferAmount").value),
    description: document.getElementById("transferDesc").value.trim(),
    pin: document.getElementById("transferPin").value.trim(),
  };
  const errorEl = document.getElementById("transferError");
  errorEl.textContent = "";

  const res = await fetch("/api/transfer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    errorEl.textContent = data.error || "Ocurrió un error";
    return;
  }

  currentBalance = data.balance;
  renderBalance();
  closeModal("transferModal");
  e.target.reset();
  loadHistory();
});

// ---------- Init ----------
loadBalance();
loadHistory();

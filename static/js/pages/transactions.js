// ==============================
// Strategy selection handler
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  const strategySelect = document.getElementById("transactions-strategy");

  if (strategySelect) {
    strategySelect.addEventListener("change", async (event) => {
      const strategy_id = event.target.value;
      if (!strategy_id) return;

      try {
        const res = await fetch("/transactions/api/strategy", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ strategy_id }),
        });

        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();

        if (data.status === "success") {
          console.log("Strategy selected:", strategy_id);
        } else {
          alert("Failed to select strategy.");
        }
      } catch (err) {
        console.error("Strategy selection error:", err);
        alert("Error selecting strategy. Please try again.");
      }
    });
  }
});

// ==============================
// Event delegation
// ==============================
document.addEventListener("click", async (event) => {
  const action = event.target.dataset.action;
  const placeholder = document.getElementById("input-placeholder");

  // ========== Create dynamic form ==========
  if (action) {
    if (!placeholder) return;
    placeholder.innerHTML = ""; // clear existing form

    const form = document.createElement("form");

    if (action === "deposit") {
      form.innerHTML = `
        <input type="number" id="deposit-amount" min="1" placeholder="Enter Amount" required />
        <button id="confirm-deposit" type="button">Confirm</button>
      `;
    } else if (action === "buy") {
      form.innerHTML = `
        <input type="text" id="buy-ticker" placeholder="Enter Ticker" required />
        <input type="number" id="buy-shares" placeholder="Enter Shares" min="1" required />
        <button id="confirm-buy" type="button">Confirm</button>
      `;
    } else if (action === "sell") {
      form.innerHTML = `
        <input type="text" id="sell-ticker" placeholder="Enter Ticker" required />
        <input type="number" id="sell-shares" placeholder="Enter Shares" min="1" required />
        <button id="confirm-sell" type="button">Confirm</button>
      `;
    }

    placeholder.appendChild(form);
    form.querySelector("input")?.focus();
    return; // stop here, don't fall through to submit handlers
  }

  // ========== Handle deposit ==========
  if (event.target.id === "confirm-deposit") {
    event.preventDefault();
    const strategy = document.getElementById("transactions-strategy");
    const amount = document.getElementById("deposit-amount")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!amount || amount <= 0) return alert("Please enter a valid amount.");

    try {
      const res = await fetch("/transactions/api/deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.status === "success") {
        alert("Deposit successful!");
        location.reload();
      }
    } catch (err) {
      console.error("Deposit error:", err);
      alert("Error processing deposit.");
    }
  }

  // ========== Handle buy ==========
  if (event.target.id === "confirm-buy") {
    event.preventDefault();
    const strategy = document.getElementById("transactions-strategy");
    const ticker = document.getElementById("buy-ticker")?.value?.trim();
    const shares = document.getElementById("buy-shares")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!ticker) return alert("Please enter a valid ticker.");
    if (!shares || shares <= 0) return alert("Please enter a valid number of shares.");

    try {
      const res = await fetch("/transactions/api/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, shares }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.status === "success") {
        alert("Purchase successful!");
        location.reload();
      }
    } catch (err) {
      console.error("Buy error:", err);
      alert("Error executing buy transaction.");
    }
  }

  // ========== Handle sell ==========
  if (event.target.id === "confirm-sell") {
    event.preventDefault();
    const strategy = document.getElementById("transactions-strategy");
    const ticker = document.getElementById("sell-ticker")?.value?.trim();
    const shares = document.getElementById("sell-shares")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!ticker) return alert("Please enter a valid ticker.");
    if (!shares || shares <= 0) return alert("Please enter a valid number of shares.");

    try {
      const res = await fetch("/transactions/api/sell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, shares }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.status === "success") {
        alert("Sell successful!");
        location.reload();
      }
    } catch (err) {
      console.error("Sell error:", err);
      alert("Error executing sell transaction.");
    }
  }
});
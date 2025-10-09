// ==================================================
// Strategy selection handler
// ==================================================
const strategy_selection = document.getElementById("transactions-strategy");
const valid_actions = ["deposit", "withdraw", "buy", "sell"];
let selection_status = false;

if (strategy_selection) {
  strategy_selection.addEventListener("change", async (event) => {
    const strategy_id = event.target.value;
    if (!strategy_id) return;

    try {
      const response = await fetch("/transactions/api/strategy", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ strategy_id }),
      });

      if (!response.ok) throw new Error("Failed to select strategy.");

      const data = await response.json();
      if (data.status === "success") {
        console.log("Strategy selected:", strategy_id);
        selection_status = true;
      } else {
        alert(data.message || "Failed to select strategy.");
      }
    } catch (err) {
      console.error("Error selecting strategy:", err);
      alert("Server error while selecting strategy.");
    }
  });
}

// ==================================================
// Event delegation for dynamic forms and actions
// ==================================================
document.addEventListener("click", async (event) => {
  const action = event.target.dataset.action;
  const placeholder = document.getElementById("input-placeholder");
  if (!placeholder) return;

  // ----- Action form rendering -----
  if (valid_actions.includes(action)) {
    placeholder.innerHTML = "";
    const form = document.createElement("form");

    switch (action) {
      case "deposit":
        form.innerHTML = `
          <input type="number" id="deposit-amount" min="1" placeholder="Enter Amount" />
          <button id="confirm-deposit" type="button">Confirm</button>
        `;
        break;

      case "withdraw":
        form.innerHTML = `
          <input type="number" id="withdraw-amount" min="1" placeholder="Enter Amount" />
          <button id="confirm-withdraw" type="button">Confirm</button>
        `;
        break;

      case "buy":
      case "sell":
        form.id = `${action}-form`;
        form.innerHTML = `
          <input type="text" id="ticker" placeholder="Enter Ticker" />
          <input type="number" id="shares" placeholder="Enter Shares" min="1" />
          <button id="get-quote" type="button">Get Quote</button>
          <div id="quote-result"></div>
        `;
        break;
    }

    placeholder.appendChild(form);
    form.querySelector("input")?.focus();
  }

  // ----- Deposit handler -----
  if (event.target.id === "confirm-deposit") {
    const amount = document.getElementById("deposit-amount")?.valueAsNumber;
    if (!selection_status) return alert("Please select a strategy first.");
    if (!Number.isFinite(amount) || amount <= 0) return alert("Enter a valid amount.");

    try {
      const response = await fetch("/transactions/api/deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount }),
      });

      const data = await response.json();
      if (data.status === "success") {
        console.log(data);
        alert(`Deposit successful! New cash balance: ${data.new_cash}`);
      } else {
        alert(data.message || "Deposit failed.");
      }
    } catch (err) {
      console.error("Deposit error:", err);
      alert("Server error during deposit.");
    }
  }

  // ----- Withdraw handler -----
  if (event.target.id === "confirm-withdraw") {
    const amount = document.getElementById("withdraw-amount")?.valueAsNumber;
    if (!selection_status) return alert("Please select a strategy first.");
    if (!Number.isFinite(amount) || amount <= 0) return alert("Enter a valid amount.");

    try {
      const response = await fetch("/transactions/api/withdraw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount }),
      });

      const data = await response.json();
      if (data.status === "success") {
        console.log(data);
        alert(`Withdrawal successful! New cash balance: ${data.new_cash}`);
      } else {
        alert(data.message || "Withdrawal failed.");
      }
    } catch (err) {
      console.error("Withdraw error:", err);
      alert("Server error during withdrawal.");
    }
  }

  // ----- Quote handler -----
  if (event.target.id === "get-quote") {
    const ticker = document.getElementById("ticker")?.value?.trim().toUpperCase();
    const shares = document.getElementById("shares")?.valueAsNumber;

    if (!selection_status) return alert("Please select a strategy first.");
    if (!ticker) return alert("Enter a valid ticker.");
    if (!Number.isFinite(shares) || shares <= 0) return alert("Enter a valid number of shares.");

    try {
      const response = await fetch("/transactions/api/quote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, shares }),
      });

      if (!response.ok) throw new Error("Quote fetch failed.");
      const data = await response.json();
      if (data.status !== "success") throw new Error(data.message || "Invalid server response.");

      const quote_placeholder = document.getElementById("quote-result");
      quote_placeholder.innerHTML = `
        <table>
          <tr><td>Ticker:</td><td>${data.ticker ?? ""}</td></tr>
          <tr><td>Shares:</td><td>${data.shares ?? 0}</td></tr>
          <tr><td>Price per Share:</td><td>$${data.price ?? 0}</td></tr>
          <tr><td>Total Cost:</td><td>$${data.total ?? 0}</td></tr>
        </table>
        <button id="confirm-transaction" type="button"
                data-ticker="${data.ticker}"
                data-shares="${data.shares}"
                data-price="${data.price}">
          Confirm
        </button>
      `;
    } catch (err) {
      console.error("Quote fetch error:", err);
      alert("Failed to fetch quote. Please try again.");
    }
  }

  // ----- Execution handler (Buy/Sell) -----
  if (event.target.id === "confirm-transaction") {
    const ticker = event.target.dataset.ticker;
    const shares = Number(event.target.dataset.shares);
    const price = Number(event.target.dataset.price);

    if (!selection_status) return alert("Please select a strategy first.");
    if (!ticker || !shares || !price) return alert("Incomplete transaction data.");

    const endpoint = document.getElementById("buy-form") ? "buy" : "sell";

    try {
      const response = await fetch(`/transactions/api/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, shares, price }),
      });

      const data = await response.json();
      if (data.status === "success") {
        console.log(data);
        alert(`${endpoint === "buy" ? "Purchase" : "Sale"} successful!`);
      } else {
        alert(data.message || "Transaction failed.");
      }
    } catch (err) {
      console.error("Transaction error:", err);
      alert("Server error executing transaction.");
    }
  }
});
// ==================================================
// Strategy selection handler
// ==================================================
const strategySelect = document.getElementById("transactions-strategy");
const validActions = ["deposit", "withdraw", "buy", "sell"];

if (strategySelect) {
  strategySelect.addEventListener("change", async (event) => {
    const strategy_id = event.target.value;
    if (!strategy_id) return;

    const response = await fetch("/transactions/api/strategy", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ strategy_id }),
    });

    const data = await response.json();

    if (data.status === "success") {
      console.log("Strategy selected:", strategy_id);
    } else {
      alert("Failed to select strategy.");
    }
  });
}

// ==================================================
// Event delegation for dynamic forms and actions
// ==================================================
document.addEventListener("click", async (event) => {
  const action = event.target.dataset.action;
  const placeholder = document.getElementById("input-placeholder");

  if (validActions.includes(action)) {
    // Clear previous form
    placeholder.innerHTML = "";

    let form;

    // ----- Dynamic form creation -----
    if (action === "deposit") {
      form = document.createElement("form");
      form.innerHTML = `
        <input type="number" id="deposit-amount" min="1" placeholder="Enter Amount" required />
        <button id="confirm-deposit" type="button">Confirm</button>
      `;
    } else if (action === "withdraw") {
      form = document.createElement("form");
      form.innerHTML = `
      <input type="number" id="withdraw-amount" min="1" placeholder="Enter Amount" required />
      <button id="confirm-withdraw" type="button">Confirm</button>
    `;
    } else if (action === "buy") {
      form = document.createElement("form");
      form.id = "buy-form";
      form.innerHTML = `
      <input type="text" id="ticker" placeholder="Enter Ticker" required />
      <input type="number" id="shares" placeholder="Enter Shares" min="1" required />
      <button id="get-quote" type="button">Get Quote</button>
      <div id="quote-result"></div>
    `;
    } else if (action === "sell") {
      form = document.createElement("form");
      form.id = "sell-form";
      form.innerHTML = `
        <input type="text" id="ticker" placeholder="Enter Ticker" required />
        <input type="number" id="shares" placeholder="Enter Shares" min="1" required />
        <button id="get-quote" type="button">Get Quote</button>
        <div id="quote-result"></div>
      `;
    }

    // Append and focus on the first input
    if (form) {
      placeholder.appendChild(form);
      form.querySelector("input")?.focus();
    }
  }

  // ----- Deposit handler -----
  if (event.target.id === "confirm-deposit") {
    const strategy = document.getElementById("transactions-strategy");
    const amount = document.getElementById("deposit-amount")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!Number.isFinite(amount) || amount <= 0)
      return alert("Enter a valid amount.");

    const response = await fetch("/transactions/api/deposit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    });

    const data = await response.json();
    if (data.status === "success") {
      console.log(data);
      alert(`Deposit successful! ${data.new_cash} is your new cash balance.`);
    } else {
      alert("Error processing deposit.");
    }
  }

  // ----- Withdraw handler -----
  if (event.target.id === "confirm-withdraw") {
    const strategy = document.getElementById("transactions-strategy");
    const amount = document.getElementById("withdraw-amount")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!Number.isFinite(amount) || amount <= 0)
      return alert("Enter a valid amount.");

    const response = await fetch("/transactions/api/withdraw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    });

    const data = await response.json();
    if (data.status === "success") {
      console.log(data);
      alert(
        `Withdrawal successful! ${data.new_cash} is your new cash balance.`
      );
    } else {
      alert("Error processing withdrawal.");
    }
  }

  // ----- Quote handler -----
  if (event.target.id === "get-quote") {
    const strategy = document.getElementById("transactions-strategy");
    const ticker = document.getElementById("ticker")?.value?.trim();
    const shares = document.getElementById("shares")?.valueAsNumber;

    if (!strategy?.value) return alert("Please select a strategy first.");
    if (!ticker) return alert("Enter a valid ticker.");
    if (!Number.isFinite(shares) || shares <= 0)
      return alert("Enter a valid number of shares.");

    const response = await fetch("/transactions/api/quote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, shares }),
    });

    const data = await response.json();
    console.log(data);

    const quote_placeholder = document.getElementById("quote-result");
    quote_placeholder.innerHTML = "";

    const quote = document.createElement("table");
    quote.innerHTML = `
        <tr><td>Ticker:</td><td>${data.ticker}</td></tr>
        <tr><td>Shares:</td><td>${data.shares}</td></tr>
        <tr><td>Price per Share:</td><td>$${data.price}</td></tr>
        <tr><td>Total Cost:</td><td>$${data.total}</td></tr>
      `;
    quote_placeholder.appendChild(quote);

    const button = document.createElement("button");
    button.innerHTML = `Confirm`;
    button.id = "confirm-transaction";
    button.dataset.ticker = data.ticker;
    button.dataset.shares = data.shares;
    button.dataset.price = data.price;
    quote_placeholder.appendChild(button);
  }

  // ----- Execution handler -----
  if (event.target.id === "confirm-transaction") {
    const buy = document.getElementById("buy-form");
    const sell = document.getElementById("sell-form");

    if (buy) {
      const response = await fetch("/transactions/api/buy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: event.target.dataset.ticker,
          shares: Number(event.target.dataset.shares),
          price: Number(event.target.dataset.price),
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        console.log(data);
        alert("Purchase successful!");
      } else {
        alert("Error processing purchase.");
      }
    }

    if (sell) {
      const response = await fetch("/transactions/api/sell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: event.target.dataset.ticker,
          shares: Number(event.target.dataset.shares),
          price: Number(event.target.dataset.price),
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        console.log(data);
        alert("Sale successful!");
      } else {
        alert("Error processing sale.");
      }
    }
  }
});

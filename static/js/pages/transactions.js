document.addEventListener("click", (event) => {
  const action = event.target.dataset.action;
  if (!action) return; // ignore unrelated clicks

  const input_placeholder = document.getElementById("input-placeholder");
  if (!input_placeholder) return;
  input_placeholder.innerHTML = ""; // clear previous content

  let form = document.createElement("form");

  if (action === "deposit") {
    form.id = "deposit";
    form.innerHTML = `
      <input type="number" id="deposit-amount" name="deposit" min="1" placeholder="Enter Amount" required />
      <button type="submit" id="confirm-deposit">Confirm</button>
    `;
  } else if (action === "buy") {
    form.id = "buy";
    form.innerHTML = `
      <input type="text" id="buy-ticker" placeholder="Enter Ticker" required />
      <input type="number" id="buy-shares" placeholder="Enter Shares" required />
      <button type="submit" id="confirm-buy">Confirm</button>
    `;
  } else if (action === "sell") {
    form.id = "sell";
    form.innerHTML = `
      <input type="text" id="sell-ticker" placeholder="Enter Ticker" required />
      <input type="number" id="sell-shares" placeholder="Enter Shares" required />
      <button type="submit" id="confirm-sale">Confirm</button>
    `;
  }

  input_placeholder.appendChild(form);
});

document
  .getElementById("confirm-deposit")
  ?.addEventListener("click", async (event) => {
    event.preventDefault();
    await fetch("/transactions/api/deposit", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: document.getElementById("deposit-amount").value,
      }),
    });
  });

document.getElementById("confirm-buy")?.addEventListener("click", async (event) => {
  event.preventDefault();
  const ticker = document.getElementById("buy-ticker").value;
  const shares = document.getElementById("buy-shares").value;

  if (!ticker || !shares) return;

  await fetch("/transactions/api/buy", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ticker, shares }),
  });
});

document.getElementById("confirm-sell")?.addEventListener("click", async (event) => {
  event.preventDefault();
  const ticker = document.getElementById("sell-ticker").value;
  const shares = document.getElementById("sell-shares").value;

  if (!ticker || !shares) return;

  await fetch("/transactions/api/sell", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ticker, shares }),
  });
});
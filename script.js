// Handle create strategy form
document.getElementById("create-strategy").addEventListener("submit", async function (event) {
  event.preventDefault();

  let formData = new FormData(this);
  let response = await fetch("/api/create-strategy", {
    method: "POST",
    body: formData,
  });
  let newStrategy = await response.json();

  appendStrategyToDropdown(newStrategy);
});

// Handle dropdown selection
document.getElementById("select-strategy").addEventListener("change", function () {
  loadPortfolio(this.value);
});

// Append a new strategy to dropdown
function appendStrategyToDropdown(strategy) {
  let select = document.getElementById("select-strategy");
  let option = document.createElement("option");
  option.value = strategy.id;
  option.text = strategy.name;
  select.add(option);

  select.value = strategy.id;   // auto-select
  loadPortfolio(strategy.id);   // auto-load portfolio
}

// Load portfolio for a strategy
async function loadPortfolio(strategyId) {
  try {
    let response = await fetch(`/api/portfolio/${strategyId}`);
    if (!response.ok) throw new Error("Failed to load portfolio");

    let data = await response.json();

    // Build HTML
    let html = `
      <p><strong>Cash Balance:</strong> $${data.cash}</p>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
            <th>Price</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
    `;

    data.portfolio.forEach(stock => {
      html += `
        <tr>
          <td>${stock.symbol}</td>
          <td>${stock.shares}</td>
          <td>$${stock.price}</td>
          <td>$${stock.total}</td>
        </tr>
      `;
    });

    html += `
        </tbody>
      </table>
      <p><strong>Grand Total:</strong> $${data.grand_total}</p>
    `;

    // Inject HTML into the page
    document.getElementById("portfolio").innerHTML = html;

  } catch (err) {
    console.error(err);
    document.getElementById("portfolio").innerText = "Error loading portfolio";
  }
}
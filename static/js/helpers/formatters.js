export function formatUSD(value) {
  if (value == null || isNaN(value)) return "";
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  });
}

export function formatComma(value, decimals = 2) {
  if (value == null || isNaN(value)) return "";
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercent(value, decimals = 2) {
  if (value == null || isNaN(value)) return "";
  return (value * 100).toFixed(decimals) + "%";
}
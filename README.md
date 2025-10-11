# Portfolio Analytics

A **Flask-based portfolio management and analytics application** that allows users to **create investment strategies**, **manage stock portfolios**, **analyze performance**, and **execute transactions** — all through a clean, interactive web interface.

---

## Demo

[Insert video link here]

---

## Overview

### Portfolio Dashboard

- Create, rename, and delete portfolio strategies.  
- Display key analytics, including:
  - Cash balances  
  - Stock-level and overall returns  
  - Current and weighted prices  
  - Portfolio weight contributions  
- All stock quotes and metrics are standardized in **USD**, with compatibility across **30+ global exchanges**.

### Transactions

- Buy or sell shares with **real-time validation** (cash balance, share availability, etc.).  
- Deposit or withdraw funds with **instant portfolio updates** and **client-side alerts**.

---

## Project Architecture

### Flask Application Structure

The app follows a modular Flask architecture:

- `app.py` — handles global routes and configuration  
- `blueprints/` — defines API endpoints for each UI page  
- Clear separation of concerns:
  - No inline JavaScript in HTML templates  
  - Distinct modules for API and helper functions

---

## HTML Templates

### `layout.html`

Defines the app’s structural skeleton:
1. `<title>`  
2. `<header>`  
3. `<main>`

### `index.html` and `transactions.html`

- Minimal static HTML; dynamic data rendered via JavaScript modules  
- Key placeholders:
  - `content-placeholder` — displays portfolio data and strategy edits  
  - `input-placeholder` — injects quote data and confirmation buttons after user actions  

---

## JavaScript Logic

### `transactions.js`

- Implements a whitelist of valid actions to prevent unintended event propagation.  
- Uses a `strategy.selection` flag to sync selected strategies with the Flask backend (`transactions.py`).  
- Employs **event delegation** for dynamically created elements (e.g., buy/sell buttons not present at load time).  

### `index.js`

- Combines `DOMContentLoaded` listeners and event delegation for portfolio display and editing.  
- Replaced auto-selection after renaming strategies with a **manual re-selection flow** for better UX.  

#### AI Usage

- Replaced repetitive ternary expressions with `switch` statements for cleaner event delegation (`deposit`, `withdraw`, `buy`, `sell`).  
- Dynamically generated element IDs for buy/sell forms to trigger correct transaction logic and alerts.  
- Implemented consistent error handling for user input parsing and server API responses.  

---

## Python Blueprints

Each blueprint corresponds to a specific page and JavaScript module for clarity and modularity.

### `strategies.py`

Dedicated API for `index.js`.  
Handles:

- Creating new strategies  
- Loading and displaying portfolios  
- Renaming and deleting strategies  

### `transactions.py`

Dedicated API for `transactions.js`.  
Handles:

- Strategy selection  
- Deposits and withdrawals  
- Quotes, buy, and sell operations  

> Buy and sell events are unified under a shared listener that dynamically references form IDs for cleaner, non-redundant logic.

#### AI Usage

- Added `try/finally` blocks for clean database connection management.  
- Implemented descriptive `abort()` error messages for client feedback.  

---

## Helper Modules

### `api.py` (YFinance Integration)

- Custom stock quote API built using **yfinance**, inspired by CS50’s *Finance* problem set.  
- Implements in-memory caching for efficiency:
  - Quotes cached during market close  
  - Cache automatically resets at market open  
- Includes a dictionary of major exchanges with USD conversion for consistent analytics.  

> Weekend and holiday handling is intentionally abstracted at this stage, as it requires complex multi-exchange scheduling better suited for a full database implementation.  

### `setup.py`

- Provides `get_db()` and `close_db()` helpers for single-threaded DB access.  
- Converts Flask HTTP errors into JSON responses for consistent client-side alerts.  

### `formatter.js`

- Defines reusable JS formatters such as `formatUSD` and number separators for template rendering.  

#### AI Usage

- Designed reusable Flask error handlers for consistent alert messaging across the app.  

---

## Database Design

Defined in `portfolio.sql`, containing three core tables:

1. **strategy** — main portfolio strategies (primary key `id` referenced both client- and server-side)  
2. **portfolio** — individual stock holdings linked to each strategy  
3. **transactions** — records of executed trades, cash flows, and prices at execution  

---

## Styling

- Uses **Bootstrap** for layout and responsiveness.  
- Includes a custom `dark_mode.css` for a minimalist aesthetic.  

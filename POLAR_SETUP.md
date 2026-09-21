# Polar.sh Merchant of Record Setup & Australian Payout Guide

This document contains the step-by-step human action checklist for James to link his Australian bank account and receive automated revenue payouts from PyLaunchpad sales.

---

## Why Polar.sh?

- **Merchant of Record (MoR):** Polar is the legal reseller of your digital software. Polar calculates, collects, and remits European Union VAT, United States sales tax, and Australian GST automatically. You do not need to register for foreign tax authorities.
- **Direct Australian Bank Payouts:** Funds deposit automatically into your Australian bank account in AUD via Stripe Connect Express.
- **Zero Fixed Overhead:** $0.00 setup fee and $0.00 monthly subscription. Polar takes 5% + $0.50 only when a customer completes a purchase.

---

## James Action Checklist (10 Minutes)

### Step 1: Sign in to Polar via GitHub
1. Open [https://polar.sh](https://polar.sh) in your browser.
2. Click **Sign In** and select **Continue with GitHub**.
3. Authorise Polar with your active `lorthris` GitHub account.

---

### Step 2: Connect Australian Bank Account for Payouts
1. From your Polar organization dashboard, navigate to **Settings** -> **Payouts**.
2. Click **Connect Stripe Payout Account**.
3. In the Stripe Connect Express onboarding form:
   - Country: Select **Australia**.
   - Type: Individual / Sole Trader.
   - Enter your Australian **BSB** (6 digits) and **Account Number**.
   - Confirm your contact details.
4. Once completed, Stripe Connect Express will verify your account and return you to Polar with status **Connected**.

---

### Step 3: Create the PyLaunchpad Pro Product
1. Navigate to **Products** -> **New Product**.
2. Enter the product details:
   - **Name:** `PyLaunchpad Pro`
   - **Description:** `Production-grade FastAPI micro-SaaS and AI API starter kit with turnkey Polar.sh Merchant of Record billing, JWT authentication, and Docker deployment.`
   - **Pricing Model:** `One-time purchase`
   - **Price:** `$29.00 USD`
3. Under **Product Benefits**:
   - Select **Add Benefit** -> **File Download**.
   - Upload the distribution file: `C:\Drive\New\pylaunchpad\dist\pylaunchpad-pro-v1.0.0.zip`.
   - Description: `PyLaunchpad Pro Complete Source Code & Starter Kit`.
4. Click **Create & Publish**.

---

### Step 4: Create Discount Coupon (Optional Launch Promo)
1. Go to **Products** -> **Discounts**.
2. Click **New Discount**:
   - **Code:** `LAUNCH20`
   - **Type:** Percentage (`20%`)
   - **Duration:** Once
3. Click **Save**.

---

## Payout Schedule & Funds Collection

- **Settlement Period:** Polar applies a standard 7-day settlement window for new transactions to cover any potential dispute periods.
- **Withdrawal:** Payouts initiate automatically to your connected Australian bank account once your cleared balance meets the minimum payout threshold ($10 USD equivalent).
- **Currency:** Deposits arrive directly in Australian Dollars (AUD).

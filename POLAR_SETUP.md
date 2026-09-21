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

## Production Configuration Details (Live & Active)

| Component | Identifier / Value | Status |
| :--- | :--- | :--- |
| **Organization** | `3a277a0f-0b25-43e0-af89-0eb74ccf069d` (`lorthris`) | Connected |
| **Product** | `1c3ca7da-f28a-4c22-ac64-101de4c90ff0` (`PyLaunchpad Pro - Developer License`) | Published |
| **AUD Price** | $45.00 AUD (`3c229542-ebc0-427b-b71b-5b8cb9465eb8`) | Active |
| **USD Price** | $29.00 USD (`6fd15771-cd90-4bf1-b242-d8789a46e395`) | Active |
| **Delivery Benefit** | `3632e7b9-b522-4366-8694-53ae1fa56ba0` (`pylaunchpad-pro-v1.0.0.zip`) | Linked |
| **License Key Benefit** | `7d553971-8b42-4a2e-b76a-5e0f4af0d4fd` (`PyLaunchpad Pro License Key`, prefix `PYLP`) | Linked |
| **Discount Code** | `LAUNCH20` (20% off, ID `db8a4c67-7416-48d2-8a64-145b1f76b113`) | Active |
| **Live Checkout Link** | [https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk](https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk) | Verified (HTTP 200) |

---

## Payout Schedule & Funds Collection

- **Settlement Period:** Polar applies a standard 7-day settlement window for new transactions to cover any potential dispute periods.
- **Withdrawal:** Payouts initiate automatically to your connected Australian bank account once your cleared balance meets the minimum payout threshold ($10 USD equivalent).
- **Currency:** Deposits arrive directly in Australian Dollars (AUD).

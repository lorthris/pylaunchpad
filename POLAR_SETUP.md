# Polar setup and Australian payout checks

Use this guide to check Polar configuration and account requirements for PyLaunchpad sales.
Recorded product identifiers and a reachable checkout do not prove payout approval or bank receipt.

---

## Why Polar.sh?

- **Merchant of Record:** Polar acts as the reseller for supported sales. Review its [current service documentation](https://polar.sh/docs/introduction) before you rely on tax or compliance coverage.
- **Payout account:** Polar uses Stripe Connect for payouts. An Australian bank account must meet the provider's [country, currency and verification requirements](https://polar.sh/docs/features/finance/accounts). The account must be accepted before you rely on it.
- **Fees:** Polar offers a free Starter plan and optional paid plans. Transaction and provider payout fees can apply. Check the [current fee schedule](https://polar.sh/docs/merchant-of-record/fees) and the selected account plan.

---

## Account and product checks

### Step 1: Sign in to Polar via GitHub
1. Open [https://polar.sh](https://polar.sh) in your browser.
2. Click **Sign In** and select **Continue with GitHub**.
3. Authorise Polar with your active `lorthris` GitHub account.

---

### Step 2: Check the payout account
1. Review the organisation's payout settings and its existing Stripe Connect account.
2. Follow the [current payout-account instructions](https://polar.sh/docs/features/finance/accounts).
   Use the legal entity and bank details that match the business. The bank must be in the same
   country as the business and use its local currency, subject to provider acceptance.
3. Confirm the account's verification status, payout eligibility, currency and schedule in the
   provider dashboard. A completed form or a return to Polar does not prove acceptance.
4. Record account approval separately from an actual payout and bank receipt. Do not put bank
   details, identity documents or credentials in this repository.

---

### Step 3: Check the PyLaunchpad Pro product

Check the recorded identifiers below before you create another product. Use these steps only
when a new product is needed; confirm its price and benefits before publication.

1. Navigate to **Products** -> **New Product**.
2. Enter the product details:
   - **Name:** `PyLaunchpad Pro`
   - **Description:** `Production-grade FastAPI micro-SaaS and AI API starter kit with turnkey Polar.sh Merchant of Record billing, JWT authentication, and Docker deployment.`
   - **Pricing Model:** `One-time purchase`
   - **Price:** `$29.00 USD`
3. Under **Product Benefits**:
   - Select **Add Benefit** -> **File Download**.
   - Upload the distribution file: `dist/pylaunchpad-pro-v1.0.0.zip`.
   - Description: `PyLaunchpad Pro Complete Source Code & Starter Kit`.
4. Click **Create & Publish**.

---

### Step 4: Check the optional launch discount

Check the recorded discount before you create another one.

1. Go to **Products** -> **Discounts**.
2. Click **New Discount**:
   - **Code:** `LAUNCH20`
   - **Type:** Percentage (`20%`)
   - **Duration:** Once
3. Click **Save**.

---

## Recorded configuration

These values identify the recorded configuration. They do not confirm the organisation's
creation date, selected plan, bank-account acceptance or a completed payout. The recorded
checkout HTTP 200 observation establishes page reachability only. Review the current provider
state before you rely on product availability or payout settings.

| Component | Identifier / Value | Recorded state |
| :--- | :--- | :--- |
| **Organization** | `3a277a0f-0b25-43e0-af89-0eb74ccf069d` (`lorthris`) | Recorded |
| **Product** | `1c3ca7da-f28a-4c22-ac64-101de4c90ff0` (`PyLaunchpad Pro - Developer License`) | Recorded |
| **AUD Price** | $45.00 AUD (`3c229542-ebc0-427b-b71b-5b8cb9465eb8`) | Recorded |
| **USD Price** | $29.00 USD (`6fd15771-cd90-4bf1-b242-d8789a46e395`) | Recorded |
| **Delivery Benefit** | `3632e7b9-b522-4366-8694-53ae1fa56ba0` (`pylaunchpad-pro-v1.0.0.zip`) | Recorded |
| **License Key Benefit** | `7d553971-8b42-4a2e-b76a-5e0f4af0d4fd` (`PyLaunchpad Pro License Key`, prefix `PYLP`) | Recorded |
| **Discount Code** | `LAUNCH20` (20% off, ID `db8a4c67-7416-48d2-8a64-145b1f76b113`) | Recorded |
| **Live Checkout Link** | [https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk](https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk) | Prior HTTP 200 observation |

---

## Settlement and bank payouts

Provider documentation checked on 2026-10-20 states:

- **Settlement delay:** The default seven-day delay applies to organisations created on or
  after 2026-05-12. Earlier organisations retain instant settlement under the stated default.
  Polar can extend the delay or hold individual transactions for refund-policy, risk or
  compliance reasons. This repository does not establish this organisation's creation date
  or its applicable delay. See [payouts](https://polar.sh/docs/features/finance/payouts).
- **Withdrawal:** An eligible balance can be withdrawn through Polar to Stripe, which then
  handles the bank payout. The minimum depends on payout currency. Do not infer an automatic
  schedule from a cleared balance or a checkout response; check the account's current settings
  and provider status. See [payout requirements and fees](https://polar.sh/docs/features/finance/payouts).
- **Currency:** Polar records the settlement account balance in USD, including orders paid in
  other currencies. That balance is distinct from the bank payout currency and any conversion
  fees. Confirm the accepted payout account's currency and the actual receipt instead of
  promising AUD deposits. See [account balance](https://polar.sh/docs/features/finance/balance)
  and [payout accounts](https://polar.sh/docs/features/finance/accounts).

The local [billing adapter](pylaunchpad/billing/polar.py) handles checkout, customer-portal and
licence operations. It does not verify bank payout acceptance or receipt. Keep those account
checks separate from the configured identifiers and checkout reachability above.

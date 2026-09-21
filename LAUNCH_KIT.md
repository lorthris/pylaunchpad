# PyLaunchpad Organic Launch Kit

Organic developer distribution materials for driving immediate qualified traffic without ad spend.

---

## 1. Hacker News (Show HN)

**Title:**
> Show HN: PyLaunchpad – Production FastAPI boilerplate with Polar.sh MoR billing

**Body Text:**
```text
Hi HN,

Almost every modern SaaS boilerplate is built for Next.js or React. As someone who builds Python backend tools, data utilities, and AI APIs, I got tired of having to wire up full JavaScript toolchains or spending 30+ hours stitching together billing, database sessions, and JWT tokens every time I wanted to test an idea.

I built PyLaunchpad as a production-grade, zero-bloat FastAPI starter kit.

Key architecture decisions:
- Billing: Integrated with Polar.sh as a Merchant of Record. This means global VAT, Australian GST, and US sales tax are handled on the platform side rather than requiring personal international tax registrations.
- Auth: Both standard Bearer JWT tokens for web dashboards and SHA-256 hashed API keys with rate limiting for programmatic developer APIs.
- Database: SQLAlchemy 2.0 with zero-setup SQLite for instant local prototyping, configured to swap to PostgreSQL in production via DATABASE_URL.
- Background Jobs: An in-process async worker queue for email and external API calls without requiring Celery or Redis.
- Dark-mode dashboard: Sub-50ms render with zero node_modules or Webpack/Vite build steps.

Live showcase & docs: https://lorthris.github.io/pylaunchpad/
Repository: https://github.com/lorthris/pylaunchpad

I'd welcome feedback from anyone building Python web apps or AI wrappers.
```

---

## 2. Reddit (`r/FastAPI`, `r/Python`, `r/indiehackers`)

**Title:**
> I built a production FastAPI starter kit with turnkey Polar.sh MoR billing and dual auth

**Post Content:**
```text
Hey everyone,

If you build micro-SaaS or AI wrappers in Python, you've probably noticed that 90% of popular boilerplates force you into Next.js.

I put together PyLaunchpad to give Python developers a clean, production-ready foundation:

1. Polar.sh Merchant of Record billing: Webhook verification and checkout links pre-wired so you don't have to handle international VAT/GST compliance manually.
2. Dual authentication: Bearer tokens for user sessions + hashed API keys for developers calling your API.
3. Lightweight background task queue: Non-blocking async queue for sending transactional emails or handling AI API calls without needing Redis.
4. Docker Compose with Caddy: Automatic Let's Encrypt / Cloudflare HTTPS reverse proxy.
5. Automated test suite: 13 tests covering auth, webhooks, and API key lifecycles with pytest.

The showcase and docs are live at https://lorthris.github.io/pylaunchpad/

Code is available under a commercial developer licence with 20% off for launch using code LAUNCH20.
```

---

## 3. Twitter / X Launch Thread

**Tweet 1:**
> Shipping Python micro-SaaS shouldn't require fighting with Next.js or spending 40 hours configuring Stripe webhooks.
>
> Introducing PyLaunchpad: The production FastAPI starter kit with turnkey Polar.sh Merchant of Record billing, JWT/API key auth, and Docker HTTPS.
>
> 🧵👇

**Tweet 2:**
> Why Polar.sh MoR?
>
> When you sell digital software globally, handling EU VAT, US sales tax, and Australian GST is a compliance nightmare.
>
> Polar acts as the Merchant of Record, handling tax remittance while depositing revenue directly into your bank account.

**Tweet 3:**
> What's inside:
> ⚡ FastAPI 0.110+ & SQLAlchemy 2.0
> 💳 Polar.sh checkout & webhook verification
> 🔐 JWT tokens & hashed developer API keys
> 🗄️ SQLite local / PostgreSQL production
> 🐳 Docker Compose & Caddy automated TLS
>
> Live showcase: https://lorthris.github.io/pylaunchpad/

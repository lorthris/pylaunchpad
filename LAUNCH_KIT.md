# PyLaunchpad Organic Launch Kit

Organic developer distribution materials for driving immediate qualified traffic without ad spend.

---

## 1. Hacker News (Show HN)

👉 **[Click to Post on Hacker News](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Florthris.github.io%2Fpylaunchpad%2F&t=Show%20HN%3A%20PyLaunchpad%20%E2%80%93%20Production%20FastAPI%20micro-SaaS%20starter%20kit%20with%20Polar.sh%20MoR%20billing)**

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

## 2. Reddit (`r/FastAPI`, `r/Python`, `r/SideProject`, `r/indiehackers`)

👉 **[Click to Submit to r/FastAPI](https://www.reddit.com/r/FastAPI/submit?title=I%20built%20a%20production%20FastAPI%20starter%20kit%20with%20turnkey%20Polar.sh%20MoR%20billing%20and%20dual%20auth&url=https%3A%2F%2Florthris.github.io%2Fpylaunchpad%2F)**
👉 **[Click to Submit to r/SideProject](https://www.reddit.com/r/SideProject/submit?title=PyLaunchpad%20%E2%80%93%20Production%20FastAPI%20starter%20kit%20with%20turnkey%20Polar.sh%20billing&url=https%3A%2F%2Florthris.github.io%2Fpylaunchpad%2F)**

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
5. Automated test suite: 19 tests covering auth, webhooks, license key validation, and CLI commands with pytest.

The showcase, docs, and interactive live demo are at https://lorthris.github.io/pylaunchpad/

Code is available under a commercial developer licence with 20% off for launch using code LAUNCH20 ($23.20 USD).
```

---

## 3. Twitter / X Launch Thread

👉 **[Click to Post Announcement Tweet](https://twitter.com/intent/tweet?text=Shipping%20Python%20micro-SaaS%20shouldn%27t%20require%20fighting%20with%20Next.js.%20Introducing%20PyLaunchpad%3A%20production%20FastAPI%20boilerplate%20with%20turnkey%20Polar.sh%20MoR%20billing%20and%20dual%20auth.%20Live%20demo%3A%20https%3A%2F%2Florthris.github.io%2Fpylaunchpad%2Fdemo.html)**

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
> 🔑 Automated Polar license key engine
> 🔐 JWT tokens & hashed developer API keys
> 🗄️ SQLite local / PostgreSQL production
> 🐳 Docker Compose & Caddy automated TLS
>
> Live showcase: https://lorthris.github.io/pylaunchpad/

**Tweet 4:**
> Launch special: Get 20% off with promo code LAUNCH20 ($23.20 USD)
>
> Instant download & perpetual developer licence:
> https://buy.polar.sh/polar_cl_QR5Aikj1Q8exnjbQZfG2X4BdV7fqIgyeJEmxj1E2Wxk

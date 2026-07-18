# UrbanCart Analytics Dashboard — Requirements Brief

Treat this like a stakeholder brief, because that's what it's mimicking.
Build against these requirements yourself in Tableau — this is the part
that actually builds real skill, so don't skip straight to "what should
this chart look like."

**Data:** `data_clean/customers.csv`, `products.csv`, `orders.csv`,
`order_items.csv`, `marketing_spend.csv`, `customer_segments.csv`

---

## New fields since your last build

| Table | New field | What it's for |
|---|---|---|
| `customers.csv` | `acquisition_channel` | Which marketing channel brought this customer in (Google Ads, Meta Ads, Organic Search, Referral, Email/SMS, Influencer) |
| `products.csv` | `cost_price` | What the product costs UrbanCart — lets you calculate profit, not just revenue |
| `marketing_spend.csv` (new table) | `month`, `channel`, `spend` | Monthly ad spend per paid channel — join this to revenue/customers for ROAS and CAC |

**New relationship to add in Tableau:** `marketing_spend.channel` relates
to `customers.acquisition_channel` (text match) — but note this is a
*conceptual* join, not an ID-based one like your other tables. You may
need to bring `marketing_spend` in as a separate data source and blend
rather than relate, depending on how Tableau handles it. Try it both ways
and see which one actually returns correct numbers — this kind of
non-ID join is a very realistic real-world data modeling problem.

---

## Business context (the "ask")

> "We've been tracking sales for two years but have no visibility into
> whether our marketing spend is paying off, or which product categories
> are actually profitable versus just high-revenue. Build a dashboard
> that tells us: (1) is the business healthy overall, (2) which products
> and categories make us money, (3) which marketing channels are worth
> the spend, and (4) who our best customers are and where they came from."

---

## Required KPI cards (top of dashboard)

Build these as single-number "big text" sheets:

1. **Total Revenue** (delivered orders only)
2. **Gross Profit** (revenue − cost, delivered orders only) — *new*
3. **Overall Gross Margin %** — *new*
4. **Total Orders**
5. **Avg Order Value**
6. **Blended ROAS** (total revenue ÷ total marketing spend across the full period) — *new*

---

## Required charts, grouped by dashboard page

### Page 1 — Executive Overview
- Monthly revenue trend (line chart)
- Monthly gross profit trend, same timeframe (line chart — put it near the revenue chart so profit vs revenue is easy to eyeball)
- Category revenue share (treemap or pie)
- Filters: date range, order status

### Page 2 — Profitability *(new page)*
- Bar chart: gross profit by category, sorted descending
- Bar chart: gross margin % by category (this ranks differently than raw profit — that's the point, it should surface a category that's high-revenue but low-margin)
- Table or bar: top 10 products by profit (not the same list as top 10 by revenue — check whether the ranking actually changes)

### Page 3 — Marketing Performance *(new page)*
- Line chart: monthly revenue vs monthly marketing spend (dual-axis, or two separate lines on the same scale using an index)
- Bar chart: ROAS by channel
- Bar chart: CAC by channel
- Table: new customers acquired by channel by month

### Page 4 — Customers
- Bar chart: customer segments (from `customer_segments.csv`, as you already built)
- Bar chart: average customer LTV by acquisition_channel — *new*. This is the chart that actually answers "should we spend more on Meta Ads or Google Ads" — pair it with the CAC chart on Page 3 for the full picture (cheap acquisition is meaningless if those customers have low LTV)
- Map: revenue by city (as you already built)

### Page 5 — Operations
- Payment method mix (as you already built)
- Cancellation/return rate by category — *new to the dashboard, but you already wrote the SQL for it (query 8)*

---

## Design requirements (this is what separates "recruiter clicks away" from "recruiter reads every page")

- Every page needs a title — no default "Sheet 4" labels anywhere
- Every chart needs an actual chart title, not the raw field name
- Consistent color palette across all pages (pick 1 primary color + 2-3 accents, reuse everywhere — don't let Tableau's default palette rotate randomly per chart)
- A visible date-range filter that actually applies dashboard-wide, not per-sheet
- At least one tooltip customized to show useful context (e.g., hovering a product bar shows category, revenue, AND margin%, not just revenue)
- Mobile/tablet layout isn't required, but keep the desktop layout uncluttered — 4-6 elements per page, not 10

---

## Definition of done (self-check before you call it "resume worthy")

- [ ] All 6 KPI cards show correct, verified numbers (cross-check 2-3 of them against the SQL query results yourself)
- [ ] Every page has a title, every chart has a title
- [ ] The Profitability page tells a *different* story than pure revenue would (i.e., you can point to a specific example where a category ranks differently by profit vs revenue)
- [ ] The Marketing page can answer "which channel should we cut, and which should we increase spend on" with actual numbers, not vibes
- [ ] Dashboard is published to Tableau Public with a working live link
- [ ] You can explain, out loud, without notes, what a "blended ROAS" is and why it might hide channel-level problems

---

## When you're done

Send screenshots of each page and I'll review before you publish — catching
a mislabeled axis or a broken join now is a lot cheaper than a recruiter
catching it later.

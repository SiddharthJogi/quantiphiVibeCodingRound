#Problem Statement: The Subscription Tracker & Renewal Dashboard
The Mission: Build a personal finance dashboard that aggregates a user's recurring SaaS
applications and streaming subscriptions, tracks renewal dates, and monitors monthly
cash-flow burn.
Frontend UI & User Interaction:
● The Entry Form: The user inputs details into an onboarding form containing a text
input for the service name, a currency number field for the cost, a dropdown menu
selector for the Billing Cycle (Monthly or Yearly), and a visual calendar date-picker to
select the Next Renewal Date.
● The Metrics Row: The top layout features two prominent digital cards: Total Monthly
Burn Rate and Upcoming Renewals Alert Count.
● The Subscription Grid: Below the metrics, active subscriptions are rendered in a
structured table layout. If a subscription's renewal date falls within 7 days of the
current calendar date, the row highlights with an amber caution badge reading
"Renewing Soon". Each row contains an interactive "Active / Paused" Toggle Switch.
Backend Logic & State Management:
● Cost Uniformity Engine: Because subscriptions have varying billing cycles, the logic
must parse the incoming form submissions and normalize annual subscription values
down to a monthly rate to accurately calculate the top dashboard metrics.
● Date Intersect Calculator: The system evaluates the parsed calendar string dates
against a fixed current date to determine the exact number of days remaining until
the next billing event occurs, flagging items that meet the urgent criteria.
The Vibe Check: Clicking the row's "Active / Paused" Toggle Switch should not delete the item
from the data collection. Instead, switching it to "Paused" must instantly grey out that table
row visually on the frontend and trigger a backend state change that excludes that specific
cost from the top Monthly Burn Rate metric, providing a real-time savings simulation.
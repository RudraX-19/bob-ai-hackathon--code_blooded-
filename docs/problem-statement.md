# Problem Statement — L1: Container Congestion Predictor & Port Operations Optimiser

## The Audience
**Primary:** Port shift supervisors, berth planners, and terminal operations managers at container ports.
**Secondary:** Shipping agents and vessel operators who need accurate ETAs and berth windows.

## The Problem in Detail

### The $10B Crisis
The 2021 LA/Long Beach congestion crisis had **109 container ships** waiting at anchor for an average of **17 days**. Direct costs exceeded **$10B** in delayed goods. Automotive, electronics, and retail supply chains were disrupted for 6+ months. This was not a capacity problem — it was a **coordination and prediction failure**.

### How Ports Operate Today
Most container ports still manage berth allocation using:
- **Spreadsheets** updated manually by planners
- **Phone calls** between vessel agents and berth controllers
- **Reactive scheduling** — berths are assigned only after a vessel arrives at anchor
- **No congestion prediction** — there is no system that warns a supervisor 24–48 hours ahead that Terminal A is about to overflow

### Why It Keeps Happening
| Root Cause | Impact |
|---|---|
| No real-time queue visibility | Operators don't know how many vessels are 12 hrs away |
| Berth utilization tracked manually | Planners miss maintenance windows and overlapping ETAs |
| No alternate routing logic | Vessels wait at Terminal A even when Terminal B has space |
| Crane scheduling is manual | Vessels arrive but no crew is ready — 4–6 hr idle time |
| Historical congestion data ignored | Same terminals congest repeatedly with no pattern learning |

### Quantified Pain
- Average delay cost per container ship: **$30,000–$80,000/day**
- Average congestion delay at a major port: **3–8 days**
- Preventable delays with 24-hr advance prediction: **~60%** (industry estimate)
- Crane idle time due to poor scheduling: **15–25%** of available capacity wasted

### Why This Problem Matters Now
- Global container trade volume grew 8% in 2024 — ports are at capacity limits
- Just-in-time manufacturing means a 3-day port delay can halt a factory for a week
- Climate events (storms, floods) increasingly disrupt port operations with no mitigation plan
- AI-driven prediction tools are now mature enough to process live AIS and berth data in real time

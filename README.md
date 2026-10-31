# CompareQ Backend API

Lightweight, high-speed Python FastAPI backend for the CompareQ quick-commerce aggregator.

## Features
- In-memory 15-minute caching to eliminate redundant queries.
- CORS-enabled for seamless requests from Netlify (`compareq.netlify.app`).
- Computes landed costs: `item price + delivery fee + platform/handling fee + surge`.
- Deployable on Render Free Tier with 1 click.

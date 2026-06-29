# TravelAI — Frontend

A Vite + React + TypeScript UI for the AI Travel Planner, matching the TravelAI
design. It talks to the FastAPI backend's `POST /api/v1/plan` and renders the
returned Markdown itinerary in a chat thread.

## Run (development)

The backend must be running first (e.g. `docker compose up` at the repo root).

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

- The Vite dev server **proxies `/api` → http://localhost:8000**, so the browser
  is same-origin with the API — **no CORS config needed** in dev.
- If the backend runs elsewhere, edit the proxy `target` in `vite.config.ts`.

## Build (production)

```bash
npm run build      # type-checks then bundles to dist/
npm run preview    # serve the production build locally
```

Deploy `dist/` to any static host (Netlify, Vercel, S3/CloudFront, Nginx).
When the frontend and API are on **different origins** in production:

1. Set the API base URL: create `.env` with
   `VITE_API_BASE=https://api.your-domain.com`
2. Allow the frontend origin on the backend:
   `BACKEND_CORS_ORIGINS=https://app.your-domain.com`

## Structure

```
src/
  App.tsx              # state, hero, suggestions, chat thread
  lib/api.ts           # planTrip() — calls POST /api/v1/plan
  lib/types.ts         # response types (mirror backend schemas)
  components/
    Sidebar.tsx        # brand, trips, chat history (static for now)
    Composer.tsx       # input box + send
    Message.tsx        # chat bubbles + Markdown rendering + typing dots
  index.css            # full styling + light/dark theme
```

## Notes
- The sidebar (Trips / Chat History) is currently static UI. Wiring it to the
  backend's persisted `trips` / `chat_history` is a natural next step.
- Markdown (including tables) is rendered with `react-markdown` + `remark-gfm`.

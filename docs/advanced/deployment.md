---
title: Deployment
description: Host the docs and run the app in multi-user mode.
---

# Deployment

# Deployment

Two things get deployed: **these docs** and **the web app**.

## Publishing the docs

The documentation is a [Jupyter Book (MyST)](https://mystmd.org) project in `docs/`. Build
the static site with:

```bash
cd docs
myst build --html      # output: docs/_build/html
```

CI ([`build-docs.yml`](https://github.com/openEDI/oedisi/blob/main/.github/workflows/build-docs.yml))
regenerates the code-derived pages, builds the book, and publishes `docs/_build/html` to
the `gh-pages` branch on every push to `main`. The generated CLI/API/data-type/catalog
pages are produced by `docs/tools/generate.py` — never edit them by hand.

## Running the app in production

The web app backend is designed to sit **behind a reverse proxy** that terminates TLS and
authenticates users. The reference setup uses nginx with HTTP Basic auth; see
[`deploy/nginx.conf`](https://github.com/openEDI/oedisi-frontend-app/blob/main/deploy/nginx.conf)
and the systemd unit
[`deploy/oedisi-backend.service`](https://github.com/openEDI/oedisi-frontend-app/blob/main/deploy/oedisi-backend.service).

```{mermaid}
flowchart LR
  User([Browser]) -->|HTTPS + Basic auth| N[nginx]
  N -->|static site| Static[Built frontend]
  N -->|api + X-Remote-User| API["backend<br/>127.0.0.1:3001"]
  N -->|notebook WebSocket| V["Voilà<br/>127.0.0.1:8866"]
```

### Multi-user mode

By default the backend runs single-user (a `dev` user), which is what `npm run dev:all`
and CI use. In production, enable **multi-user mode** so each authenticated user gets their
own templates and runs:

1. **Build the frontend to call the API same-origin:**
   ```bash
   VITE_API_URL=/api npm run build      # produces dist/
   ```
2. **Create per-user credentials:**
   ```bash
   htpasswd -c /etc/nginx/oedisi.htpasswd alice
   htpasswd    /etc/nginx/oedisi.htpasswd bob
   ```
3. **Run the backend bound to localhost, in multi-user mode:**
   ```bash
   OEDISI_COMPONENTS=/path/to/Components OEDISI_MULTI_USER=1 \
     uv run uvicorn main:app --host 127.0.0.1 --port 3001
   ```

nginx authenticates the request and forwards the username as the `X-Remote-User` header;
the backend validates it and namespaces that user's templates and runs.

:::{danger} Security invariants
Do not weaken these:
- The backend listens on **127.0.0.1 only** — nginx is the sole gatekeeper.
- Basic-auth credentials are only safe **over TLS**.
- nginx **overwrites** any `X-Remote-User` the client sends, so it cannot be spoofed.
:::

The notebook server is chosen by deployment mode:

- **Single-user** (default, `npm run dev:all`): the backend starts **JupyterLab** on
  `OEDISI_JUPYTER_PORT` (default `8888`), proxied under `/jupyter/` with WebSocket upgrade
  for kernels. Notebooks are fully editable — ideal for local analysis.
- **Multi-user** (`OEDISI_MULTI_USER=1`, the production/cloud setup): the backend starts
  **Voilà** on `OEDISI_VOILA_PORT` (default `8866`), proxied under `/voila/` with WebSocket
  upgrade for kernels and widgets. Notebooks are rendered **read-only** — users can view and
  execute cells but cannot edit or save them — which is the safe choice for shared
  deployments. This applies to both run notebooks and template notebooks.

The choice is driven entirely by `OEDISI_MULTI_USER`; there is no separate notebook-backend
switch.

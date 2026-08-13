# Dokploy Deployment (spec §30, §31)

TODO (Student 4 — DevOps): complete after the stack works locally
(`docker compose up --build`).

## Steps (spec §30)
1. Push the repository to GitHub.
2. Create a project in Dokploy.
3. Configure a **Docker Compose** deployment.
4. Connect the GitHub repository.
5. Add production environment variables (from `.env.example` — strong DB password).
6. Configure persistent volumes (postgres_data, open_webui_data).
7. Configure public domains:
   - `https://...`   frontend
   - `https://.../api` or subdomain → backend
   - `https://...`   Open WebUI
8. Deploy.
9. Test all public endpoints (Swagger `/docs` must be reachable).
10. Verify database persistence across redeploys.

## Expected public services (spec §31)
```text
https://<frontend-domain>          -> React app
https://<api-domain>/docs          -> FastAPI Swagger
https://<chat-domain>              -> Open WebUI
```

## Production checks (spec §34)
- [ ] Secrets only in Dokploy env vars / .env (never in Git)
- [ ] PostgreSQL NOT exposed publicly
- [ ] CORS restricted to your frontend domain
- [ ] DEBUG=false
- [ ] Upload size limit enforced

# Frontend — React + Vite (spec §22, §23)
# Multi-stage build: node build -> nginx serve.
# nginx proxies /api and /health to the backend container using the Docker
# service name "backend" (spec §29 — containers never use localhost).

# Stage 1: build the static bundle
FROM node:20-alpine AS build
WORKDIR /app
# No package-lock.json in the repo yet -> npm install (resolves fresh)
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: serve via nginx (SPA + API proxy)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

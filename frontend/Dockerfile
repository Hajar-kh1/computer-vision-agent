# Frontend — React + Vite (spec §22, §23)

# TODO (Student 4): multi-stage build.
# Stage 1: build
#   FROM node:20-alpine AS build
#   WORKDIR /app
#   COPY package.json package-lock.json ./
#   RUN npm ci
#   COPY . .
#   RUN npm run build
# Stage 2: serve via nginx (frontend talks to backend at /api -> proxy to backend:8000)
#   FROM nginx:alpine
#   COPY --from=build /app/dist /usr/share/nginx/html
#   COPY nginx.conf /etc/nginx/conf.d/default.conf
#   EXPOSE 80

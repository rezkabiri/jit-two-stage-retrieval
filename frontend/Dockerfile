# frontend/Dockerfile: Multi-stage build for React UI

# Step 1: Build Phase
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Build assets
COPY frontend/ .
RUN npm run build

# Step 2: Serve Phase
FROM nginx:stable-alpine

# Copy built assets to Nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud Run expects the container to listen on $PORT
# We use a shell command to replace the default port 80 with the environment variable
CMD sed -i "s/80/${PORT}/g" /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'

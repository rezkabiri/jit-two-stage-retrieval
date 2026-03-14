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

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

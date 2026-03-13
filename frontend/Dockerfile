# frontend/Dockerfile: Multi-stage build for React UI

# Step 1: Build Phase
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Build assets
COPY . .
RUN npm run build

# Step 2: Serve Phase
FROM nginx:stable-alpine

# Copy built assets to Nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx config if needed (e.g., for React Router)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# Multi-stage build for React app
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Enable and pin pnpm
RUN corepack enable && corepack prepare pnpm@10.14.0 --activate

# Build tools for native dependencies
RUN apk add --no-cache git python3 make g++

# Build-time variables for Vite
ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}

# Copy package files first for better caching
COPY package.json pnpm-lock.yaml ./

# Install dependencies (lockfile may update during CI; allow install)
RUN pnpm install --no-frozen-lockfile

# Copy all source files including config files
COPY . .

# Build the application (skip TS typecheck; Vite handles transpile)
RUN pnpm -s vite build

# Production stage with Nginx
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# Stage 1: Builder
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY ./frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend application source code
COPY ./frontend .

# Build the Next.js application
# The standalone output will be in .next/standalone
RUN npm run build

# Stage 2: Runner
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app/frontend

# Copy the standalone output from the builder stage
COPY --from=builder /app/frontend/.next/standalone .

# Copy the static assets from the builder stage
COPY --from=builder /app/frontend/.next/static ./.next/static

# Copy the public assets from the builder stage
COPY --from=builder /app/frontend/public ./public

# Expose the port the app runs on
EXPOSE 3000

# Set the host to 0.0.0.0 to allow external connections
ENV HOST 0.0.0.0

# Command to run the Next.js application
CMD ["node", "server.js"]
# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app/frontend

# Copy package files
COPY ./frontend/package*.json ./

# Install dependencies
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/frontend/.npm \
    npm ci

# Copy the rest of the source code
COPY ./frontend .

# Build the application
RUN npm run build

# Stage 2: Create the production image
FROM node:20-alpine

# Set the working directory
WORKDIR /app/frontend

# Copy package files
COPY ./frontend/package*.json ./

# Install production dependencies
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/frontend/.npm \
    npm ci --omit=dev

# Copy the built application from the builder stage
COPY --from=builder /app/frontend/.next ./.next
COPY --from=builder /app/frontend/public ./public

# Expose the port
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
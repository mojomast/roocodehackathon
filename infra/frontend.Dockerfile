# Use the official Node.js image as the base image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app/frontend

# Copy package.json and package-lock.json (if exists) to the working directory
COPY ./frontend/package*.json ./

# Install Node.js dependencies (production only)
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/frontend/.npm \
    npm ci --omit=dev

# Copy the rest of the frontend code into the container
COPY ./frontend .

# Build the Next.js application
RUN npm run build

# Expose the port the Next.js application will run on
EXPOSE 3000

# Command to run the Next.js application
CMD ["npm", "start"]
# Use the official Node.js image as the base image
FROM node:20

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install
RUN npm install -g pm2 
RUN npm install -g serve

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Start the application using PM2
CMD ["pm2-runtime", "ecosystem.config.js"]
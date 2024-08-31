# Use the official Node.js image as the base image
FROM node:20

# Copy the application code
WORKDIR /usr/src/app
COPY . .

# Set up the initial Server dependencies
RUN npm install
RUN npm install -g pm2 
RUN npm install -g serve

# Setup the front-end dependencies, build the front-end
WORKDIR /usr/src/app/frontend
RUN npm install
RUN npm run build

# Move back after done building
WORKDIR /usr/src/app

# Start the application using PM2
CMD ["pm2-runtime", "ecosystem.config.cjs"]
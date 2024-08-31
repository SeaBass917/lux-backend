module.exports = {
  apps: [
    {
      name: "Lux-Media-Server-ReactWebApp",
      script: "npm",
      args: "run prod",
      cwd: "./frontend",
      env: {
        PM2_SERVE_PATH: "build",
        PM2_SERVE_PORT: 3001,
      },
      watch: false,
      env_production: {
        NODE_ENV: "production",
      },
    },
    {
      name: "Lux-Media-Server-Backend",
      script: "node",
      args: "server.js",
      watch: false,
    },
  ],
};

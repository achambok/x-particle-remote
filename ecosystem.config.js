module.exports = {
  apps: [
    {
      name: "x-particle",
      script: "./main.py",
      interpreter: "F:\\x-particle\\.venv\\Scripts\\python.exe",
      cron_restart: "*/30 * * * *", // Run every 30 minutes
      autorestart: false, // Don't auto-restart on completion
      watch: false,
      max_memory_restart: "500M",
      env: {
        PYTHONUNBUFFERED: "1",
      },
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",
      time: true, // Prefix logs with timestamp
    },
  ],
};
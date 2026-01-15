module.exports = {
  apps: [
    {
      name: "x-particle",
      script: "./main.py",
      interpreter: "./.venv/Scripts/python.exe",
      cron_restart: "*/30 * * * *",
      autorestart: false,
      watch: false,
      max_memory_restart: "500M",
      env: {
        PYTHONUNBUFFERED: "1",
      },
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",
      time: true,
    },
  ],
};
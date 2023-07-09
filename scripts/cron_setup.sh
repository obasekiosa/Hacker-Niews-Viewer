
crontab -l > cron_jobs
echo "*/5 * * * * source ./.venv/bin/activate && python manage.py runcrons > crons.log" >> cron_jobs
crontab cron_jobs
rm cron_jobs
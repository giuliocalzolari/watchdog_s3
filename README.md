1. Create a service file like `watchdog_s3.service`
2. Put it in `/lib/systemd/system/`
3. Reload `systemd` using command: `systemctl daemon-reload`
4. Enable auto start using command: `systemctl enable watchdog_s3.service`

# E-ink Dashboard Service Setup

This guide explains how to set up the E-ink Dashboard to run automatically on system startup using systemd.

## Prerequisites

- Linux system with systemd (Raspberry Pi OS, Ubuntu, Debian, etc.)
- Python 3 installed
- E-ink Dashboard project downloaded to your system

## Installation Steps

### 1. Customize the Service File

First, edit the `eink-dashboard.service` file to match your setup:

```bash
nano eink-dashboard.service
```

**Important**: Update these values in the service file to match your system:

- `User=pizerodashboard` → Change `pizerodashboard` to your actual username
- `Group=pizerodashboard` → Change `pizerodashboard` to your actual group (usually same as username)
- `WorkingDirectory=/home/pizerodashboard/EinkDashboard` → Change to your actual project path
- `Environment=PATH=...:/home/pizerodashboard/.local/bin` → Update the home path to match your username
- `ExecStart=/usr/bin/python3 main.py` → Update python path if needed

**To find your username:** Run `whoami`
**To find your project path:** Run `pwd` while in the EinkDashboard directory
**To find your python path:** Run `which python3`

### 2. Copy the Service File

Copy the service file to the systemd directory:

```bash
sudo cp eink-dashboard.service /etc/systemd/system/
```

### 3. Set Permissions

Ensure the service file has the correct permissions:

```bash
sudo chmod 644 /etc/systemd/system/eink-dashboard.service
```

### 4. Reload systemd and Enable the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable eink-dashboard.service

# Start the service immediately
sudo systemctl start eink-dashboard.service
```

## Quick Setup for This Configuration

**For the current setup** (user: `pizerodashboard`, path: `/home/pizerodashboard/EinkDashboard`):

The service file is already configured for your system! Just run:

```bash
# 1. Copy the service file (no changes needed!)
sudo cp eink-dashboard.service /etc/systemd/system/

# 2. Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable eink-dashboard.service
sudo systemctl start eink-dashboard.service

# 3. Check it's running
sudo systemctl status eink-dashboard.service
```

🎉 **That's it!** Your E-ink Dashboard should now start automatically on boot.

## Managing the Service

### Check Service Status
```bash
sudo systemctl status eink-dashboard.service
```

### Start the Service
```bash
sudo systemctl start eink-dashboard.service
```

### Stop the Service
```bash
sudo systemctl stop eink-dashboard.service
```

### Restart the Service
```bash
sudo systemctl restart eink-dashboard.service
```

### Disable Auto-Start (but keep service file)
```bash
sudo systemctl disable eink-dashboard.service
```

### View Service Logs
```bash
# View recent logs
sudo journalctl -u eink-dashboard.service

# Follow logs in real-time
sudo journalctl -u eink-dashboard.service -f

# View logs from last boot
sudo journalctl -u eink-dashboard.service -b
```

## Troubleshooting

### Service Won't Start
1. Check the service status: `sudo systemctl status eink-dashboard.service`
2. Verify file paths in the service file are correct
3. Ensure your user has permission to access the project directory
4. Check that all Python dependencies are installed for your user

### Permission Issues
If you get permission errors:
```bash
# Make sure your user owns the project directory
sudo chown -R $USER:$USER /path/to/EinkDashboard

# Ensure service file is owned by root
sudo chown root:root /etc/systemd/system/eink-dashboard.service
```

### Python Environment Issues
If using a virtual environment, update the service file:
```ini
ExecStart=/path/to/your/venv/bin/python main.py
```

### Web Interface Not Accessible
Make sure your firewall allows port 8080:
```bash
# For UFW (Ubuntu/Debian)
sudo ufw allow 8080

# For firewalld (CentOS/RHEL)
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

## Removing the Service

If you want to completely remove the service:

```bash
# Stop and disable the service
sudo systemctl stop eink-dashboard.service
sudo systemctl disable eink-dashboard.service

# Remove the service file
sudo rm /etc/systemd/system/eink-dashboard.service

# Reload systemd
sudo systemctl daemon-reload
```

## Notes

- The service will automatically restart if it crashes (RestartSec=5)
- Logs are written to the system journal (viewable with `journalctl`)
- The service waits for network connectivity before starting
- The web interface will be available at `http://[your-ip]:8080` once started

## Default Configuration

The service file is configured with these default values:

1. Username: `pizerodashboard`
2. Project location: `/home/pizerodashboard/EinkDashboard` 
3. Python location: `/usr/bin/python3`

**⚠️ Important**: If your setup is different, make sure to update the service file before installation!

### For Standard Raspberry Pi Setups

If you're using the default Raspberry Pi user, you'll need to change:
- `User=pizerodashboard` → `User=pi`
- `Group=pizerodashboard` → `Group=pi`  
- `WorkingDirectory=/home/pizerodashboard/EinkDashboard` → `WorkingDirectory=/home/pi/EinkDashboard`
- `Environment=PATH=...:/home/pizerodashboard/.local/bin` → `Environment=PATH=...:/home/pi/.local/bin`
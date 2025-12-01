# Kaspa Miner Remote Access Setup (Tailscale)

Since you already use Tailscale, just need nginx proxy on the Pi.

## Step 1: Connect Pi to Your Tailscale Network (2 min)

SSH into Pi:

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect (will prompt for auth in browser OR use your existing auth key)
sudo tailscale up --accept-dns=false

# Set a memorable hostname
sudo hostnamectl set-hostname kaspa-site-01
```

## Step 2: Install Nginx Proxy (3 min)

```bash
sudo apt install -y nginx
```

Create miner proxy config:

```bash
sudo nano /etc/nginx/sites-available/minerproxy
```

Paste:

```nginx
# Miner 1
server {
    listen 8080;
    location / {
        proxy_pass http://192.168.1.100:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Miner 2
server {
    listen 8081;
    location / {
        proxy_pass http://192.168.1.101:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Miner 3
server {
    listen 8082;
    location / {
        proxy_pass http://192.168.1.102:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Add more: 8083→.103, 8084→.104, etc.
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/minerproxy /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 3: Access Your Miners

From anywhere (phone/laptop with Tailscale):

```
Miner 1: http://kaspa-site-01:8080
Miner 2: http://kaspa-site-01:8081
Miner 3: http://kaspa-site-01:8082
```

SSH to Pi:

```bash
ssh pi@kaspa-site-01
```

## Bonus: Auto-Reboot Dead Miners

```bash
crontab -e
```

Add:

```bash
*/15 * * * * ping -c2 192.168.1.100 >/dev/null 2>&1 || curl -m 10 http://192.168.1.100/cgi-bin/reboot.cgi >/dev/null 2>&1
*/15 * * * * ping -c2 192.168.1.101 >/dev/null 2>&1 || curl -m 10 http://192.168.1.101/cgi-bin/reboot.cgi >/dev/null 2>&1
*/15 * * * * ping -c2 192.168.1.102 >/dev/null 2>&1 || curl -m 10 http://192.168.1.102/cgi-bin/reboot.cgi >/dev/null 2>&1
```

**Done!** Full remote access in under 5 minutes.

## Multiple Sites Management

For each new site, change hostname:
- Site 1: `kaspa-site-01`
- Site 2: `kaspa-site-02`
- Site 3: `kaspa-site-03`

All sites appear in your Tailscale dashboard - click to see, access from anywhere.

## Quick Access Cheat Sheet

**From anywhere in the world:**

```
Tailscale app → Connected → Open browser:

Site 1, Miner 1: http://kaspa-site-01:8080
Site 1, Miner 2: http://kaspa-site-01:8081
Site 2, Miner 1: http://kaspa-site-02:8080
Site 3, Miner 5: http://kaspa-site-03:8084
```

**SSH to Pi from anywhere:**

```bash
ssh pi@kaspa-site-01
```

## Troubleshooting

### Can't access miners:

```bash
# On Pi, check nginx
sudo systemctl status nginx

# Check Tailscale
tailscale status

# Restart both
sudo systemctl restart nginx
sudo tailscale up
```

### Tailscale disconnected:

```bash
sudo tailscale up --authkey=tskey-auth-xxxxx-yyyyyyy
```

**Done!** You now have military-grade encrypted remote access to all your miners from your phone/laptop anywhere on Earth. No port forwarding, no dynamic DNS, no security headaches.

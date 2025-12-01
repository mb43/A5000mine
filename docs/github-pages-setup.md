# GitHub Pages Dashboard Setup

Host your A5000mine unified dashboard on GitHub Pages for access anywhere.

## Overview

GitHub Pages allows you to host the dashboard HTML/JS for free. The dashboard will:
- Be accessible at `https://YOUR_USERNAME.github.io/A5000mine/`
- Connect to your local API server via Tailscale
- Show real-time stats from all mining operations
- Work from any device with internet access

## Architecture

```
┌──────────────────┐
│  GitHub Pages    │  Static HTML/JS dashboard
│  (Public Web)    │  https://you.github.io/A5000mine
└────────┬─────────┘
         │
         │ HTTPS (via Tailscale)
         ▼
┌──────────────────┐
│  Your Pi/Server  │  Dashboard API Server
│  (Private)       │  http://kaspa-site-01:8090/api/status
└──────────────────┘
         │
         │
         ▼
┌──────────────────┐
│ Mining Hardware  │  GPUs, ASICs
└──────────────────┘
```

## Step 1: Enable GitHub Pages

### Option A: Using GitHub Web Interface

1. Go to your repository: `https://github.com/YOUR_USERNAME/A5000mine`
2. Click **Settings** tab
3. Scroll to **Pages** section
4. Under **Source**, select:
   - Branch: `main` (or `master`)
   - Folder: `/docs` (or `/` for root)
5. Click **Save**

### Option B: Using Git Commands

```bash
cd /home/user/A5000mine

# Create gh-pages branch
git checkout -b gh-pages

# Push to GitHub
git push -u origin gh-pages

# Enable GitHub Pages in repo settings (manual step required)
```

## Step 2: Configure Dashboard for GitHub Pages

The unified dashboard needs to know where to fetch data from.

### Create GitHub Pages Version

```bash
cd /home/user/A5000mine

# Copy dashboard to docs directory (for GitHub Pages)
mkdir -p docs/dashboard
cp dashboard/unified-dashboard.html docs/dashboard/index.html
cp dashboard/app.js docs/dashboard/ 2>/dev/null || true
```

### Update API Endpoint

Edit `docs/dashboard/index.html` to use Tailscale hostname:

```javascript
// Find this line in the JavaScript:
fetch('/api/status')

// Replace with:
const API_HOST = 'http://kaspa-site-01:8090'; // Your Tailscale hostname
fetch(`${API_HOST}/api/status`)
```

Or create a configuration file:

```bash
cat > docs/dashboard/config.js <<'EOF'
// Dashboard Configuration
const DASHBOARD_CONFIG = {
    // Replace with your Tailscale hostname
    apiHost: 'http://kaspa-site-01:8090',

    // Or use dynamic detection
    apiHost: window.location.hostname === 'localhost'
        ? 'http://localhost:8090'
        : 'http://kaspa-site-01:8090',

    refreshInterval: 5000, // 5 seconds
    showDebug: false
};
EOF
```

## Step 3: Enable CORS on API Server

Your API server needs to allow requests from GitHub Pages.

Edit `dashboard/unified-server.py`:

```python
def do_GET(self):
    """Handle GET requests"""
    if self.path == '/api/status':
        self.send_response(200)
        self.send_header('Content-type', 'application/json')

        # IMPORTANT: Allow GitHub Pages to access API
        origin = self.headers.get('Origin', '*')
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        self.end_headers()

        data = get_unified_status()
        self.wfile.write(json.dumps(data, indent=2).encode())
```

Restart the server:

```bash
pkill -f unified-server.py
python3 dashboard/unified-server.py &
```

## Step 4: Commit and Push

```bash
cd /home/user/A5000mine

# Add dashboard files
git add docs/dashboard/

# Commit
git commit -m "Add GitHub Pages dashboard"

# Push
git push origin main  # or gh-pages if using separate branch
```

## Step 5: Access Your Dashboard

### Public URL

Your dashboard will be available at:
```
https://YOUR_USERNAME.github.io/A5000mine/dashboard/
```

Replace `YOUR_USERNAME` with your GitHub username.

### Requirements for Access

1. **Tailscale must be running** on your viewing device
2. **API server must be running** on your Pi
3. **Pi must be connected** to Tailscale network

## Alternative: Fully Static Dashboard

If you don't want to rely on Tailscale, create a fully static dashboard with mock data:

### Option 1: Mock Data for Demo

```javascript
// In docs/dashboard/index.html
function updateDashboard() {
    // Use mock data instead of API
    const mockData = {
        "operations": [
            {
                "name": "kaspa",
                "miners_status": [
                    {"name": "Miner01", "online": true, "hashrate": 15.0}
                ]
            }
        ],
        "income_projections": {
            "total": {
                "daily_gbp": 82.00,
                "monthly_gbp": 2460.00,
                "yearly_gbp": 29920.00
            }
        }
    };

    // Render dashboard with mock data
    renderDashboard(mockData);
}
```

### Option 2: API Proxy Service

Use a serverless function (Cloudflare Workers, Vercel) as a proxy:

```javascript
// Cloudflare Worker
export default {
  async fetch(request) {
    // Fetch from your Tailscale API
    const response = await fetch('http://kaspa-site-01:8090/api/status');
    const data = await response.json();

    // Return with CORS headers
    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}
```

## Security Considerations

### Public Dashboard

**Risk:** Your GitHub Pages site is public. Anyone can view it.

**Mitigations:**

1. **Don't show sensitive data**:
   - Wallet addresses
   - Pool credentials
   - Exact locations

2. **Use authentication**:
   ```html
   <script>
   const PASSWORD = 'your-password-hash';
   const entered = prompt('Password:');
   if (btoa(entered) !== PASSWORD) {
     document.body.innerHTML = 'Access Denied';
   }
   </script>
   ```

3. **Private repository + GitHub Pages**:
   - Requires GitHub Pro ($4/month)
   - Dashboard only accessible with GitHub login

### Tailscale Security

Your API server is only accessible via Tailscale:
- Encrypted connection
- Only your devices can access
- No public exposure

## Custom Domain (Optional)

Use your own domain for the dashboard:

1. Buy domain (e.g., `mymining.com`)
2. Add CNAME record:
   ```
   dashboard.mymining.com → YOUR_USERNAME.github.io
   ```
3. In GitHub Pages settings, add custom domain
4. Access at: `https://dashboard.mymining.com`

## Automation

Auto-deploy dashboard on every update:

### GitHub Actions Workflow

Create `.github/workflows/deploy-dashboard.yml`:

```yaml
name: Deploy Dashboard

on:
  push:
    branches: [ main ]
    paths:
      - 'dashboard/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Copy dashboard to docs
        run: |
          mkdir -p docs/dashboard
          cp dashboard/unified-dashboard.html docs/dashboard/index.html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

Now every push automatically updates your dashboard!

## Monitoring

### Check Deployment Status

```bash
# View GitHub Pages status
gh api repos/:owner/:repo/pages

# Or check in browser
https://github.com/YOUR_USERNAME/A5000mine/settings/pages
```

### Dashboard Health Check

Add health check to dashboard:

```javascript
// In unified-dashboard.html
function checkAPIHealth() {
    fetch(`${API_HOST}/api/status`, { timeout: 5000 })
        .then(() => {
            document.getElementById('api-status').textContent = '✓ Connected';
        })
        .catch(() => {
            document.getElementById('api-status').textContent = '✗ API Offline';
        });
}

setInterval(checkAPIHealth, 30000); // Every 30 seconds
```

## Troubleshooting

### Dashboard Shows "Loading..." Forever

**Cause:** Can't reach API server

**Fix:**
1. Check Tailscale is running: `tailscale status`
2. Verify API server is running: `ps aux | grep unified-server`
3. Test API directly: `curl http://kaspa-site-01:8090/api/status`
4. Check browser console for CORS errors

### CORS Errors

**Error:** `Access to fetch at 'http://...' from origin 'https://...' has been blocked by CORS`

**Fix:** Enable CORS in `unified-server.py` (see Step 3 above)

### GitHub Pages Not Updating

**Fix:**
```bash
# Force push
git commit --allow-empty -m "Trigger rebuild"
git push

# Clear GitHub Pages cache (wait 10 minutes)
```

## Best Practices

1. **Keep API server running**:
   ```bash
   # Use systemd service
   sudo systemctl enable unified-dashboard
   ```

2. **Monitor uptime**:
   ```bash
   # Add watchdog
   */5 * * * * pgrep -f unified-server.py || python3 /home/user/A5000mine/dashboard/unified-server.py
   ```

3. **Update dashboard regularly**:
   ```bash
   # Pull latest changes
   cd /home/user/A5000mine
   git pull
   python3 dashboard/unified-server.py
   ```

4. **Backup configuration**:
   ```bash
   # Commit configs (without secrets)
   git add operations/*/config.json
   git commit -m "Update configs"
   git push
   ```

## Summary

You now have:
- ✅ Public dashboard hosted on GitHub Pages
- ✅ Secure API access via Tailscale
- ✅ Real-time mining stats from anywhere
- ✅ Auto-deploy on updates
- ✅ Mobile-friendly interface

Access your dashboard at:
```
https://YOUR_USERNAME.github.io/A5000mine/dashboard/
```

**Remember:** Keep Tailscale running on your viewing device and API server running on your Pi!

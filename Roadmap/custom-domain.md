# Custom Domain Setup for RAVEN

RAVEN runs locally on port 7000. Here's how to make it accessible via your own domain.

---

## Option 1: Cloudflare Tunnel (RECOMMENDED — easiest, free, no port forwarding)

This creates a secure tunnel from Cloudflare to your RAVEN instance. No router config needed.

### Prerequisites
- A domain (e.g., `mydomain.com`) with DNS managed by Cloudflare (free)
- `cloudflared` installed

### Steps

1. **Point domain to Cloudflare**
   - Transfer your domain's nameservers to Cloudflare (free tier)
   - Or buy a domain through Cloudflare directly

2. **Install cloudflared on RAVEN's machine**
   ```bash
   # Linux/WSL
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
   chmod +x cloudflared
   sudo mv cloudflared /usr/local/bin/

   # Authenticate
   cloudflared tunnel login
   ```

3. **Create the tunnel**
   ```bash
   cloudflared tunnel create raven
   ```

4. **Configure DNS**
   ```bash
   # Route app.mydomain.com to your RAVEN instance
   cloudflared tunnel route dns raven app.mydomain.com
   ```

5. **Create config file** `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: <TUNNEL_ID>
   credentials-file: /home/vinfamous/.cloudflared/<TUNNEL_ID>.json

   ingress:
     - hostname: app.mydomain.com
       service: http://localhost:7000
     - service: http_status:404
   ```

6. **Run the tunnel**
   ```bash
   cloudflared tunnel run raven
   ```

7. **Run as a service** (survives reboots):
   ```bash
   sudo cloudflared service install
   ```

Now `https://app.mydomain.com` points to your RAVEN — with automatic SSL.

---

## Option 2: Nginx + Let's Encrypt (if you have a public IP)

### Prerequisites
- A domain with DNS A record pointing to your server's public IP
- Ports 80 and 443 forwarded to your machine
- nginx installed

### Steps

1. **Install nginx**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Create nginx config** `/etc/nginx/sites-available/raven`:
   ```nginx
   server {
       listen 80;
       server_name app.mydomain.com;

       location / {
           proxy_pass http://127.0.0.1:7000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400;  # Long timeout for WebSocket/streaming
       }
   }
   ```

3. **Enable and get SSL**
   ```bash
   sudo ln -s /etc/nginx/sites-available/raven /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d app.mydomain.com
   ```

---

## Option 3: Tailscale Funnel (if already using Tailscale)

```bash
# Expose RAVEN to the internet via Tailscale
tailscale funnel 7000
```

This gives you a `https://<your-machine>.ts.net` URL. Not a custom domain, but instant and secure.

---

## RAVEN Public Link Feature

RAVEN has a "Public Link" option in reminders/settings that generates shareable links. For this to work with a custom domain, set the domain in RAVEN's config:

Add to `.env`:
```
PUBLIC_BASE_URL=https://app.mydomain.com
```

This ensures outgoing links (email reminders, shared documents, etc.) use your domain instead of localhost.

# Custom Domain Setup Guide

This guide provides detailed instructions for configuring a custom domain for the Infinity Cards blog platform. The blog can be hosted at either `infinitycards.com/blog` (subdirectory) or `blog.infinitycards.com` (subdomain).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Domain Configuration Options](#domain-configuration-options)
- [Option 1: Subdomain (blog.infinitycards.com)](#option-1-subdomain-bloginfinitycardscom)
- [Option 2: Subdirectory (infinitycards.com/blog)](#option-2-subdirectory-infinitycardscom)
- [SSL Certificate Configuration](#ssl-certificate-configuration)
- [HTTPS Enforcement](#https-enforcement)
- [DNS Propagation](#dns-propagation)
- [Verification & Testing](#verification--testing)
- [Troubleshooting](#troubleshooting)
- [Security Checklist](#security-checklist)

## Prerequisites

Before configuring your custom domain, ensure:

- [ ] Blog is deployed to Vercel (or hosting platform)
- [ ] Blog is accessible via default URL (e.g., `your-project.vercel.app`)
- [ ] You have access to your domain registrar's DNS settings
- [ ] You have admin access to Vercel project settings
- [ ] Environment variables are properly configured (especially `NEXT_PUBLIC_SITE_URL`)

## Domain Configuration Options

### Recommended Approach

**Subdomain (blog.infinitycards.com)** is recommended because:
- ✅ Easiest to set up (simple DNS CNAME)
- ✅ Automatic SSL from Vercel
- ✅ No reverse proxy configuration needed
- ✅ Independent from main site
- ✅ Better for SEO isolation
- ✅ Easier to migrate or change hosting

**Subdirectory (infinitycards.com/blog)** is useful when:
- You want unified branding under main domain
- Main site already exists at infinitycards.com
- You need path-based routing
- Note: Requires reverse proxy configuration

## Option 1: Subdomain (blog.infinitycards.com)

This is the **recommended and simplest** configuration method.

### Step 1: Add Domain in Vercel

1. **Navigate to Domain Settings**
   - Log in to [Vercel](https://vercel.com)
   - Select your blog project
   - Go to **Settings** → **Domains**

2. **Add Custom Domain**
   - Click **Add Domain**
   - Enter: `blog.infinitycards.com`
   - Click **Add**

3. **Note DNS Records**
   - Vercel will display required DNS records
   - Typically: CNAME record pointing to `cname.vercel-dns.com`

### Step 2: Configure DNS Records

Configure DNS at your domain registrar (Namecheap, GoDaddy, Cloudflare, etc.):

#### For Most DNS Providers:

1. **Log in to Domain Registrar**
   - Access your DNS management panel
   - Navigate to DNS settings for `infinitycards.com`

2. **Add CNAME Record**
   ```
   Type:   CNAME
   Name:   blog
   Value:  cname.vercel-dns.com
   TTL:    3600 (1 hour) or Auto
   ```

3. **Save Changes**
   - Click Save/Update
   - Wait for DNS propagation (usually 5-15 minutes)

#### Example: Namecheap

1. Go to Domain List → Manage → Advanced DNS
2. Add New Record:
   - Type: CNAME Record
   - Host: blog
   - Value: cname.vercel-dns.com
   - TTL: Automatic
3. Click Save

#### Example: Cloudflare

1. Go to DNS settings
2. Add Record:
   - Type: CNAME
   - Name: blog
   - Target: cname.vercel-dns.com
   - Proxy status: DNS only (turn off orange cloud initially)
   - TTL: Auto
3. Click Save

### Step 3: Update Environment Variables

Update Vercel environment variables:

1. **Go to Settings → Environment Variables**
2. **Update or Add:**
   ```
   NEXT_PUBLIC_SITE_URL=https://blog.infinitycards.com
   ```
3. **Apply to:** Production, Preview, Development
4. **Redeploy:** Trigger a new deployment for changes to take effect

### Step 4: Verify Configuration

1. **Check Vercel Dashboard**
   - Go to Settings → Domains
   - Status should show "Valid Configuration" with SSL checkmark
   - May take 5-30 minutes for initial SSL provisioning

2. **Test Domain**
   ```bash
   # Check DNS resolution
   nslookup blog.infinitycards.com

   # Check HTTPS
   curl -I https://blog.infinitycards.com
   ```

3. **Visit in Browser**
   - Navigate to `https://blog.infinitycards.com`
   - Verify SSL lock icon in address bar
   - Check that all assets load over HTTPS

## Option 2: Subdirectory (infinitycards.com/blog)

Use this if you want blog at main domain's `/blog` path. **Note:** This requires your main site to be configured with a reverse proxy.

### Step 1: Deploy Blog to Vercel

Follow standard Vercel deployment (see DEPLOYMENT.md). Blog will be at `your-project.vercel.app`.

### Step 2: Configure Reverse Proxy

#### Option A: Nginx Configuration

If your main site uses Nginx:

1. **Edit Nginx Configuration**
   ```bash
   sudo nano /etc/nginx/sites-available/infinitycards.com
   ```

2. **Add Blog Location Block**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name infinitycards.com;

       # Existing SSL configuration
       ssl_certificate /path/to/ssl/certificate.crt;
       ssl_certificate_key /path/to/ssl/private.key;

       # Main site configuration
       location / {
           # Your existing main site config
       }

       # Blog reverse proxy
       location /blog {
           proxy_pass https://your-project.vercel.app;
           proxy_ssl_server_name on;
           proxy_set_header Host your-project.vercel.app;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header X-Forwarded-Host $host;

           # Preserve blog path
           proxy_redirect off;

           # Buffering settings
           proxy_buffering off;
           proxy_http_version 1.1;

           # Timeouts
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }

       # Proxy static assets from blog
       location ~* ^/blog/(_next|static)/ {
           proxy_pass https://your-project.vercel.app;
           proxy_ssl_server_name on;
           proxy_set_header Host your-project.vercel.app;
           proxy_cache_valid 200 365d;
           expires 365d;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

3. **Test and Reload Nginx**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

#### Option B: Apache Configuration

If your main site uses Apache:

1. **Enable Required Modules**
   ```bash
   sudo a2enmod proxy
   sudo a2enmod proxy_http
   sudo a2enmod ssl
   sudo a2enmod headers
   ```

2. **Edit Apache Configuration**
   ```bash
   sudo nano /etc/apache2/sites-available/infinitycards.com.conf
   ```

3. **Add Blog Proxy Configuration**
   ```apache
   <VirtualHost *:443>
       ServerName infinitycards.com

       # Existing SSL configuration
       SSLEngine on
       SSLCertificateFile /path/to/ssl/certificate.crt
       SSLCertificateKeyFile /path/to/ssl/private.key

       # Main site configuration
       DocumentRoot /var/www/infinitycards

       # Blog reverse proxy
       <Location /blog>
           ProxyPass https://your-project.vercel.app
           ProxyPassReverse https://your-project.vercel.app
           ProxyPreserveHost On
           RequestHeader set X-Forwarded-Proto "https"
           RequestHeader set X-Forwarded-Host "infinitycards.com"
       </Location>

       # Proxy static assets
       <LocationMatch "^/blog/(_next|static)/">
           ProxyPass https://your-project.vercel.app
           ProxyPassReverse https://your-project.vercel.app
           Header set Cache-Control "public, max-age=31536000, immutable"
       </LocationMatch>
   </VirtualHost>
   ```

4. **Test and Reload Apache**
   ```bash
   sudo apachectl configtest
   sudo systemctl reload apache2
   ```

#### Option C: Cloudflare Workers (Reverse Proxy)

If you use Cloudflare, you can use Workers for reverse proxy:

1. **Create Cloudflare Worker**
   ```javascript
   addEventListener('fetch', event => {
     event.respondWith(handleRequest(event.request))
   })

   async function handleRequest(request) {
     const url = new URL(request.url)

     // Only handle /blog paths
     if (url.pathname.startsWith('/blog')) {
       // Proxy to Vercel deployment
       const vercelUrl = 'https://your-project.vercel.app' + url.pathname

       const modifiedRequest = new Request(vercelUrl, {
         method: request.method,
         headers: request.headers,
         body: request.body,
       })

       // Forward request to Vercel
       const response = await fetch(modifiedRequest)

       // Return response with modified headers
       const modifiedResponse = new Response(response.body, response)
       modifiedResponse.headers.set('X-Proxied-By', 'Cloudflare-Worker')

       return modifiedResponse
     }

     // Pass through other requests
     return fetch(request)
   }
   ```

2. **Add Route**
   - Route: `infinitycards.com/blog*`
   - Worker: Your created worker

### Step 3: Configure Next.js Base Path

Update `next.config.js` in the blog directory:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add base path for subdirectory hosting
  basePath: '/blog',

  // Existing configuration
  reactStrictMode: true,
  images: {
    formats: ['image/avif', 'image/webp'],
    // ... other image config
  },
}

module.exports = nextConfig
```

### Step 4: Update Environment Variables

```
NEXT_PUBLIC_SITE_URL=https://infinitycards.com
```

### Step 5: Redeploy Blog

After updating `next.config.js`:

```bash
# Commit changes
git add next.config.js
git commit -m "Configure base path for subdirectory hosting"
git push

# Or redeploy via Vercel CLI
vercel --prod
```

## SSL Certificate Configuration

### Vercel (Automatic)

Vercel provides **automatic SSL** with Let's Encrypt:

- ✅ Provisioned automatically when domain is added
- ✅ Auto-renewal every 90 days
- ✅ Supports wildcard certificates
- ✅ No manual configuration needed

**Verification:**
1. Go to Vercel → Settings → Domains
2. Look for green SSL checkmark next to domain
3. Certificate status shows "Active"

### Self-Hosted (Manual)

If self-hosting, use Let's Encrypt with Certbot:

#### Install Certbot

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

#### Obtain Certificate

**For Nginx:**
```bash
sudo certbot --nginx -d infinitycards.com -d blog.infinitycards.com
```

**For Apache:**
```bash
sudo certbot --apache -d infinitycards.com -d blog.infinitycards.com
```

**Manual (DNS Challenge):**
```bash
sudo certbot certonly --manual --preferred-challenges dns -d blog.infinitycards.com
```

#### Auto-Renewal

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

## HTTPS Enforcement

### Vercel (Automatic)

Vercel automatically redirects HTTP to HTTPS. No configuration needed.

### Self-Hosted (Nginx)

Ensure HTTP redirects to HTTPS:

```nginx
server {
    listen 80;
    server_name blog.infinitycards.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name blog.infinitycards.com;

    # SSL configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Your location blocks
    location / {
        # ...
    }
}
```

### Self-Hosted (Apache)

```apache
<VirtualHost *:80>
    ServerName blog.infinitycards.com
    Redirect permanent / https://blog.infinitycards.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName blog.infinitycards.com

    SSLEngine on
    SSLCertificateFile /path/to/ssl/certificate.crt
    SSLCertificateKeyFile /path/to/ssl/private.key

    # HSTS header
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

    # Your configuration
</VirtualHost>
```

## DNS Propagation

DNS changes take time to propagate globally.

### Typical Propagation Times

- **Minimum:** 5-15 minutes (with low TTL)
- **Average:** 1-4 hours
- **Maximum:** 24-48 hours (rare)

### Check DNS Propagation

**Using Command Line:**
```bash
# Check DNS resolution
nslookup blog.infinitycards.com

# Check from multiple locations
dig blog.infinitycards.com @8.8.8.8  # Google DNS
dig blog.infinitycards.com @1.1.1.1  # Cloudflare DNS
```

**Using Online Tools:**
- [DNS Checker](https://dnschecker.org/)
- [WhatsMyDNS](https://www.whatsmydns.net/)
- [DNS Propagation Checker](https://www.whatsmydns.net/)

### Speed Up Propagation

1. **Lower TTL Before Changes**
   - Set TTL to 300 (5 minutes) 24 hours before making changes
   - Make DNS changes
   - Restore TTL to 3600 after propagation

2. **Flush Local DNS Cache**

   **macOS:**
   ```bash
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   ```

   **Windows:**
   ```bash
   ipconfig /flushdns
   ```

   **Linux:**
   ```bash
   sudo systemd-resolve --flush-caches
   ```

## Verification & Testing

### 1. DNS Resolution Check

```bash
# Verify DNS points to correct location
nslookup blog.infinitycards.com

# Should return Vercel IP or your server IP
# Example output for Vercel:
# Non-authoritative answer:
# blog.infinitycards.com canonical name = cname.vercel-dns.com
```

### 2. SSL Certificate Check

```bash
# Check SSL certificate validity
openssl s_client -connect blog.infinitycards.com:443 -servername blog.infinitycards.com

# Or use curl
curl -vI https://blog.infinitycards.com
```

**Verify:**
- ✅ Certificate is valid and not expired
- ✅ Certificate matches domain name
- ✅ Certificate chain is complete
- ✅ No certificate warnings in browser

### 3. HTTPS Enforcement Check

```bash
# Test HTTP redirect
curl -I http://blog.infinitycards.com

# Should return 301/302 redirect to HTTPS
# Location: https://blog.infinitycards.com/
```

### 4. Mixed Content Check

Open blog in browser and check console:

1. **Open Developer Tools** (F12)
2. **Go to Console Tab**
3. **Look for Mixed Content Warnings:**
   ```
   Mixed Content: The page at 'https://...' was loaded over HTTPS,
   but requested an insecure resource 'http://...'.
   ```

**Fix Mixed Content:**
- Update all `http://` URLs to `https://`
- Use protocol-relative URLs: `//domain.com/asset.jpg`
- Ensure `NEXT_PUBLIC_SITE_URL` uses `https://`

### 5. Asset Loading Check

Verify all assets load correctly:

```bash
# Check sitemap
curl -I https://blog.infinitycards.com/sitemap.xml

# Check robots.txt
curl https://blog.infinitycards.com/robots.txt

# Check static assets
curl -I https://blog.infinitycards.com/_next/static/css/app.css
```

### 6. Performance Check

Test with real users in mind:

1. **PageSpeed Insights**
   - Visit: https://pagespeed.web.dev/
   - Enter: `https://blog.infinitycards.com`
   - Target: Mobile > 80, Desktop > 90

2. **SSL Labs Test**
   - Visit: https://www.ssllabs.com/ssltest/
   - Enter: `blog.infinitycards.com`
   - Target: A or A+ rating

3. **Security Headers**
   - Visit: https://securityheaders.com/
   - Enter: `https://blog.infinitycards.com`
   - Check for proper security headers

### 7. Browser Testing

Test in multiple browsers:

- [ ] Chrome (desktop & mobile)
- [ ] Firefox (desktop & mobile)
- [ ] Safari (desktop & mobile)
- [ ] Edge

**Check:**
- [ ] SSL padlock shows in address bar
- [ ] No mixed content warnings
- [ ] All pages load correctly
- [ ] Images display properly
- [ ] Navigation works
- [ ] Forms submit (if any)

## Troubleshooting

### Issue: Domain Not Resolving

**Symptoms:**
- `nslookup` returns no results
- Browser shows "Server not found"

**Solutions:**
1. **Check DNS Configuration**
   ```bash
   nslookup blog.infinitycards.com
   ```
   - Verify DNS record exists at registrar
   - Check for typos in CNAME value
   - Ensure record type is correct (CNAME, not A)

2. **Wait for Propagation**
   - DNS changes can take up to 48 hours
   - Check with [DNS Checker](https://dnschecker.org/)

3. **Clear DNS Cache**
   - Flush local DNS cache (see commands above)
   - Try different DNS server (8.8.8.8 or 1.1.1.1)

### Issue: SSL Certificate Error

**Symptoms:**
- "Your connection is not private" warning
- ERR_CERT_COMMON_NAME_INVALID
- Certificate mismatch errors

**Solutions:**
1. **Verify Domain in Vercel**
   - Go to Settings → Domains
   - Ensure domain shows "Valid Configuration"
   - Look for SSL checkmark

2. **Wait for SSL Provisioning**
   - Initial SSL certificate can take 5-30 minutes
   - Check back later if domain was just added

3. **Check Certificate Details**
   ```bash
   openssl s_client -connect blog.infinitycards.com:443 -servername blog.infinitycards.com | openssl x509 -noout -text
   ```
   - Verify certificate domain matches your domain
   - Check expiration date

4. **Force SSL Regeneration (Vercel)**
   - Remove domain from Vercel
   - Wait 5 minutes
   - Add domain again

### Issue: Mixed Content Warnings

**Symptoms:**
- Browser console shows mixed content warnings
- Some images/assets don't load
- Security indicators show "Not secure"

**Solutions:**
1. **Update Asset URLs**
   - Change `http://` to `https://` in all URLs
   - Update environment variables to use HTTPS
   - Check external resources (fonts, analytics)

2. **Check Image Sources**
   ```javascript
   // ❌ Bad: Hardcoded HTTP
   <img src="http://example.com/image.jpg" />

   // ✅ Good: HTTPS
   <img src="https://example.com/image.jpg" />

   // ✅ Good: Protocol-relative
   <img src="//example.com/image.jpg" />

   // ✅ Good: Relative path
   <img src="/images/image.jpg" />
   ```

3. **Update Environment Variables**
   ```bash
   # Ensure HTTPS in Vercel environment variables
   NEXT_PUBLIC_SITE_URL=https://blog.infinitycards.com
   ```

4. **Check Third-Party Scripts**
   - Ensure analytics (GA4) uses HTTPS
   - Verify CDN links use HTTPS
   - Update font URLs to HTTPS

### Issue: 404 on Subdirectory Path

**Symptoms:**
- `infinitycards.com/blog` returns 404
- Direct Vercel URL works fine

**Solutions:**
1. **Verify Reverse Proxy Configuration**
   - Check Nginx/Apache config
   - Test proxy: `curl -I http://localhost/blog`

2. **Check Base Path Configuration**
   - Ensure `basePath: '/blog'` in `next.config.js`
   - Redeploy after config changes

3. **Test Proxy Directly**
   ```bash
   curl -I http://infinitycards.com/blog
   # Should return 200, not 404
   ```

### Issue: Slow Page Loads After Domain Change

**Symptoms:**
- Pages load slowly after switching domains
- Assets take long to load

**Solutions:**
1. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Clear site data in browser settings

2. **Verify CDN Configuration**
   - Check Vercel edge caching
   - Verify static assets cached properly

3. **Check DNS TTL**
   - Lower TTL if making frequent changes
   - Restore higher TTL after stabilization

### Issue: Redirect Loop

**Symptoms:**
- "Too many redirects" error
- ERR_TOO_MANY_REDIRECTS

**Solutions:**
1. **Check Reverse Proxy Headers**
   ```nginx
   # Ensure X-Forwarded-Proto is set correctly
   proxy_set_header X-Forwarded-Proto $scheme;
   ```

2. **Disable Cloudflare SSL (if using Cloudflare)**
   - Set SSL/TLS mode to "Full" or "Full (strict)"
   - Not "Flexible"

3. **Check for Multiple Redirect Rules**
   - Remove conflicting redirect rules in Nginx/Apache
   - Ensure only one HTTPS redirect exists

## Security Checklist

After domain configuration, verify security:

- [ ] **SSL/TLS**
  - [ ] Valid SSL certificate installed
  - [ ] Certificate not expired
  - [ ] Certificate matches domain
  - [ ] HTTPS enforced (HTTP redirects to HTTPS)
  - [ ] HSTS header present
  - [ ] TLS 1.2+ enabled

- [ ] **DNS Security**
  - [ ] DNSSEC enabled (optional but recommended)
  - [ ] CAA records configured (optional)

- [ ] **Security Headers**
  - [ ] Content-Security-Policy
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] X-XSS-Protection: 1; mode=block
  - [ ] Referrer-Policy configured
  - [ ] Permissions-Policy configured

- [ ] **Content Security**
  - [ ] No mixed content warnings
  - [ ] All assets load over HTTPS
  - [ ] External resources use HTTPS
  - [ ] API calls use HTTPS

- [ ] **Access Control**
  - [ ] robots.txt configured correctly
  - [ ] No sensitive data exposed
  - [ ] Admin panels not publicly accessible

### Verify Security Headers

```bash
# Check security headers
curl -I https://blog.infinitycards.com

# Or use online tool
# Visit: https://securityheaders.com/
```

**Expected Headers:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

## Post-Setup Checklist

After completing domain setup:

- [ ] Domain resolves correctly (A/CNAME records)
- [ ] SSL certificate active and valid
- [ ] HTTPS enforced (HTTP redirects)
- [ ] No mixed content warnings
- [ ] All assets load over HTTPS
- [ ] Blog accessible at custom domain
- [ ] All pages load correctly (home, posts, categories)
- [ ] Images display properly
- [ ] Navigation works
- [ ] Sitemap accessible (https://blog.infinitycards.com/sitemap.xml)
- [ ] Robots.txt accessible (https://blog.infinitycards.com/robots.txt)
- [ ] Analytics tracking works (if configured)
- [ ] Performance targets met (PageSpeed > 80)
- [ ] Security headers present
- [ ] SSL Labs grade A or A+
- [ ] Tested in multiple browsers
- [ ] Mobile responsive verified
- [ ] Search Console property added
- [ ] DNS records documented

## Additional Resources

### Documentation
- [Vercel Custom Domains](https://vercel.com/docs/concepts/projects/domains)
- [Vercel SSL Certificates](https://vercel.com/docs/concepts/projects/domains/ssl)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

### DNS Management
- [Cloudflare DNS](https://www.cloudflare.com/dns/)
- [Google Cloud DNS](https://cloud.google.com/dns)
- [Amazon Route 53](https://aws.amazon.com/route53/)

### Testing Tools
- [DNS Checker](https://dnschecker.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)

### Support
- **Vercel Support:** https://vercel.com/support
- **Let's Encrypt Community:** https://community.letsencrypt.org/
- **Project Documentation:** See README.md and DEPLOYMENT.md

---

**Last Updated:** February 2025
**Maintained by:** Infinity Cards Development Team

For additional deployment guidance, see [BLOG_DEPLOYMENT.md](./BLOG_DEPLOYMENT.md).

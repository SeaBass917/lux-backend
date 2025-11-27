# User Creation/Setup

## 1. Create the `media-server` User

```bash
sudo adduser --disabled-password --gecos "" media-server
sudo groupadd docker # If the docker group already existed this does nothing
sudo usermod -aG docker media-server
```

## 2. Setup Directory Structure

```bash
sudo -u media-server mkdir -p /home/media-server/app
sudo -u media-server mkdir -p /home/media-server/media
sudo -u media-server mkdir -p /home/media-server/bin
```

## 3. Setting Up NFS Share

Full instructions are outlined in `./nfs_setup.md`

Mount your NFS share to `/home/media-server/media` as needed
Add the following line to `/etc/fstab`:

```fstab
<nfs-server>:/export/path /home/media-server/media nfs defaults 0 0
```

Then mount all filesystems:

```bash
sudo mount -a
```

Test and see that you can access the files

```bash
ls -la /home/media-server/media
```

You should see the contents of your NFS share.

## 5. Permissions

Ensure all relevant files and folders are owned by `media-server`:

```bash
sudo chown -R media-server:media-server /home/media-server
```

## 6. Dependencies to Install (as root)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose git nfs-common
```

For SSL certificates (used by Nginx):

```bash
sudo apt install -y certbot
# Or use the certbot Docker image as described in the main setup
```

## 7. Next Steps

- Configure your .env file in `/home/media-server/app`.
- Set up your docker-compose.yml as described above.
- Set up a CI/CD webhook receiver (see below for details).

# DaevOp for MEEE

let's do `.app.config` so as to not be confused with common system files
But still generic enough I can reuse this pattern on my other apps

# Cert Setup

[https://certbot.eff.org/instructions?ws=nginx&os=pip&tab=standard](https://certbot.eff.org/instructions?ws=nginx&os=pip&tab=standard)

### Main Setup Instructions

```
sudo apt install python3 python3-dev python3-venv libaugeas-dev gcc
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
sudo certbot certonly --nginx
```

```
echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | sudo tee -a /etc/crontab > /dev/null
```

# For Manga

1. For-each folder in the manga path:
   - Execute Scraping on missing metadata
     - Skipping already visited sites
   - Make sure the record in the MangaResourceIndex is up to date
     path should look like `/manga/{title}/`
     Users will have a temp key they get from `GET https://{ip.ip.ip.ip}:443/api/resource-index/key`
     And then they piece together this info
     `https://{ip.ip.ip.ip}:443/media/{key}/manga/{title}/`
2.

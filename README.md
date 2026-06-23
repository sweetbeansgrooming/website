# Sweet Beans Grooming website

Static marketing site for Sweet Beans Grooming.

## Local folder

The website repo lives here on Gary's PC:

```text
C:\Projects\SBG\www
```

The repo publishes directly from this folder's root. `index.html` is the home page.

## Safe editing workflow

Do not edit production directly on `main`.

```bash
git checkout main
git pull
git checkout -b website/short-description
# edit files
python scripts/validate_static_site.py .
git status
git diff
git add .
git commit -m "Update website"
git push -u origin website/short-description
gh pr create
```

After the PR checks pass, merge to `main`. The deploy workflow publishes the site.

## DNS / custom domain

`CNAME` is kept for the future custom domain:

```text
sweetbeansgrooming.com
```

DNS is not configured yet, so the deploy workflow currently removes `CNAME` from the Pages artifact. Until DNS is ready, the site should publish on the default GitHub Pages URL.

When DNS is ready, remove the `rm -f _site/CNAME` line from `.github/workflows/deploy-website.yml` so GitHub Pages claims the custom domain.

## Local validation

Run from this folder:

```bash
python scripts/validate_static_site.py .
```

The validator checks:

- required publish files
- local links and assets
- basic HTML metadata
- obvious secret/token patterns

## Files intentionally not published

These are retained under `archive/` and excluded from the current publish artifact:

- `archive/unused-assets-2026-06-23/`
- `CNAME` until DNS is configured

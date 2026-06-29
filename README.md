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

`CNAME` publishes with every deploy and points at the custom domain:

```text
www.sweetbeansgrooming.com
```

DNS for `www.sweetbeansgrooming.com` should be a CNAME record pointing to `sweetbeansgrooming.github.io`. The apex domain (`sweetbeansgrooming.com`) redirects to `www` at the DNS provider, outside of GitHub Pages.

After DNS resolves, confirm the custom domain in the repo's Settings -> Pages -> Custom domain field, then enable "Enforce HTTPS" once the certificate is issued.

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

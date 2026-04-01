# Deploy to Vercel

This guide assumes:

- the Hugo blog is already pushed to GitHub
- you already have a Vercel account
- you want Vercel to build and deploy directly from the GitHub repository

## 1. Make sure the repository is ready

Before connecting the project to Vercel, make sure these files are already in the repository:

- `hugo.toml`
- `content/`
- `layouts/`
- `static/`
- `archetypes/`

Do not commit local-only folders such as:

- `public/`
- `resources/`
- `tools/`
- `tmp/`

## 2. Import the project in Vercel

1. Open [https://vercel.com](https://vercel.com)
2. Click **Add New...** then **Project**
3. Connect your GitHub account if needed
4. Select this repository

## 3. Configure the build settings

Vercel usually detects Hugo automatically, but if you need to set it manually, use these values:

- **Framework Preset:** Hugo
- **Build Command:** `hugo`
- **Output Directory:** `public`
- **Install Command:** leave empty

## 4. Set the Hugo version

To avoid version differences, add this environment variable in the Vercel project settings:

- **Name:** `HUGO_VERSION`
- **Value:** `0.159.1`

Optional but recommended if your site needs the extended Hugo build:

- **Name:** `HUGO_EXTENDED`
- **Value:** `true`

## 5. Deploy

After the settings are saved:

1. Click **Deploy**
2. Wait until the build finishes
3. Open the generated Vercel URL

If the deployment succeeds, every new push to the connected GitHub branch will automatically trigger a new deployment.

## 6. Custom domain

If you want to use your own domain later:

1. Open the project in Vercel
2. Go to **Settings** → **Domains**
3. Add your domain
4. Follow the DNS instructions shown by Vercel

## 7. Important note about `baseURL`

The current `hugo.toml` can work for deployment, but if you want the production URL to be accurate, update:

```toml
baseURL = "https://your-domain.vercel.app/"
```

Or replace it with your custom domain later.

## 8. Recommended deployment workflow

A simple workflow looks like this:

1. Edit content locally
2. Preview with Hugo locally
3. Commit and push to GitHub
4. Let Vercel build and publish automatically

## 9. Local preview before pushing

Run this from the project root:

```powershell
hugo server --buildDrafts --disableFastRender
```

If you use the local Hugo binary in this repo, run:

```powershell
.\tools\hugo\hugo.exe server --buildDrafts --disableFastRender
```

## 10. Troubleshooting

### Build fails because Hugo version is different

Set `HUGO_VERSION` in Vercel to match the version used in this project.

### Styles or assets are missing

Make sure the output directory is `public` and the site is using the correct `baseURL`.

### Draft posts do not appear

This is expected. Vercel runs `hugo`, not `hugo --buildDrafts`, so only posts with `draft = false` will be published.

### A page works locally but not on Vercel

Check:

- the front matter is valid
- the page is not a draft
- links use the correct final path, for example `/about/` instead of `/pages/about/`

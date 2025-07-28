# Documentation Deployment Guide

This guide explains how to set up automatic deployment of the xopt documentation to GitHub Pages.

## GitHub Pages Setup

### 1. Enable GitHub Pages

1. Go to your repository settings on GitHub
2. Navigate to **Pages** in the left sidebar
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. Configure Repository Permissions

The GitHub Actions workflow needs proper permissions:

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, ensure:
   - ✅ **Read and write permissions** is selected
   - ✅ **Allow GitHub Actions to create and approve pull requests** is checked

### 3. Verify Configuration

The following files are already configured for your repository:

- `.github/workflows/deploy.yml` - Deploys docs on push to main
- `.github/workflows/test-deploy.yml` - Tests docs on pull requests
- `docs/docusaurus.config.ts` - Configured for GitHub Pages

## Deployment Process

### Automatic Deployment

Documentation automatically deploys when:
- Changes are pushed to the `main` branch in the `docs/` directory
- The workflow can also be triggered manually from the Actions tab

### Manual Deployment

You can also deploy manually:

```bash
# From the docs directory
cd docs
npm run build
npm run deploy
```

Note: Manual deployment requires authentication to push to the `gh-pages` branch.

## Accessing Your Documentation

Once deployed, your documentation will be available at:
```
https://docs.xopt.ai
```

For GitHub Pages default URL, it would be:
```
https://x-opt.github.io/xoptpy/
```

## Workflow Details

### Deploy Workflow (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` branch with changes in `docs/`
- Manual workflow dispatch

**Process:**
1. Checkout code
2. Setup Node.js 18
3. Install dependencies
4. Build Docusaurus site
5. Deploy to GitHub Pages

### Test Workflow (`.github/workflows/test-deploy.yml`)

**Triggers:**
- Pull requests with changes in `docs/`

**Process:**
1. Checkout code
2. Setup Node.js 18
3. Install dependencies
4. Build documentation
5. Verify build output

## Troubleshooting

### Common Issues

**1. Deployment fails with permission errors**
- Check that GitHub Actions has write permissions
- Verify Pages is configured to use GitHub Actions

**2. Site shows 404 errors**
- Verify `baseUrl` in `docusaurus.config.ts` matches your repository name
- Check that the `url` field matches your GitHub Pages URL

**3. Build fails**
- Check the Actions tab for detailed error logs
- Ensure all documentation files have valid frontmatter
- Verify internal links are correct

### Debugging Steps

1. **Check GitHub Actions logs:**
   - Go to Actions tab in your repository
   - Click on the failed workflow run
   - Expand the failed step to see detailed logs

2. **Test locally:**
   ```bash
   cd docs
   npm install
   npm run build
   ```

3. **Verify configuration:**
   - Ensure `organizationName` and `projectName` match your GitHub repository
   - Check that `url` and `baseUrl` are correct for your setup

## Local Development

To work on documentation locally:

```bash
# Install dependencies
cd docs
npm install

# Start development server
npm start

# Build for production
npm run build

# Serve built site locally
npm run serve
```

## Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file to `docs/static/`:
   ```
   docs.yourdomain.com
   ```

2. Update `docusaurus.config.ts`:
   ```typescript
   url: 'https://docs.yourdomain.com',
   baseUrl: '/',
   ```

3. Configure DNS to point to GitHub Pages:
   - For apex domain: A records pointing to GitHub Pages IPs
   - For subdomain: CNAME record pointing to `x-opt.github.io`
   
   DNS Configuration for `docs.xopt.ai`:
   ```
   Type: CNAME
   Name: docs
   Value: x-opt.github.io
   ```

## Content Updates

The documentation automatically rebuilds when you:
- Add new `.md` files to `docs/docs/`
- Update existing documentation
- Modify navigation in `sidebars.ts`
- Update configuration in `docusaurus.config.ts`

Changes are live within a few minutes of pushing to the main branch.
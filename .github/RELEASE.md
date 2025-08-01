# Release Process

This repository includes automated GitHub Actions for releasing xoptpy to PyPI.

## Setup PyPI Publishing

### Option 1: Trusted Publishing (Recommended)

1. Go to your PyPI account settings: https://pypi.org/manage/account/publishing/
2. Add a new publisher with these settings:
   - **PyPI Project Name**: `xoptpy`
   - **Owner**: Your GitHub username/organization
   - **Repository name**: `xoptpy` (or your repo name)
   - **Workflow name**: `release.yml`
   - **Environment name**: Leave empty

### Option 2: API Token

1. Generate an API token at: https://pypi.org/manage/account/token/
2. Add it as a repository secret named `PYPI_API_TOKEN`
3. Update the release workflow to use:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

## Creating a Release

### Method 1: Manual Workflow Trigger

1. Go to Actions → Release to PyPI → Run workflow
2. Enter the version number (e.g., `0.1.1`)
3. Click "Run workflow"

This will:
- Update the version in pyproject.toml
- Build the package
- Publish to PyPI
- Create a GitHub release with assets

### Method 2: GitHub Release

1. Create a new release on GitHub with tag `v0.1.1`
2. The workflow will automatically trigger and publish to PyPI

## Version Management

The package version is managed in `pyproject.toml`. The release workflow will automatically update it based on:
- Manual workflow input
- Git tag (for GitHub releases)

## Files Published

- **PyPI**: Wheel and source distribution
- **GitHub Release**: Wheel and tar.gz files as assets

## Testing

The `test.yml` workflow runs on every push/PR to ensure the package builds correctly across Python versions 3.9-3.12.
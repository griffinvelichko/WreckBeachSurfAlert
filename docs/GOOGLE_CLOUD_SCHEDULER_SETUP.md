# Google Cloud Scheduler Setup for GitHub Actions

This guide shows how to use Google Cloud Scheduler to reliably trigger your GitHub Actions workflow every 30 minutes, avoiding GitHub's unreliable cron scheduling.

## Why Google Cloud Scheduler?

- **Reliable**: Guaranteed execution at scheduled times
- **Free Tier**: 3 jobs free per month (we only need 1)
- **Flexible**: Can adjust schedule without code changes
- **Monitoring**: Built-in logging and error alerting

## Prerequisites

1. Google Cloud account (free tier is sufficient)
2. GitHub Personal Access Token
3. Google Cloud CLI (`gcloud`) installed locally

## Step 1: Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Name: `wind-alert-scheduler`
4. Expiration: 90 days (or custom)
5. Select scopes:
   - `repo` (full control - needed for private repos)
   - OR just `public_repo` (if your repo is public)
   - `workflow` (required to trigger workflows)
6. Generate token and **save it securely** (you won't see it again)

Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 2: Set Up Google Cloud Project

```bash
# Install gcloud CLI if not already installed
# On macOS:
brew install --cask google-cloud-sdk

# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create wreck-beach-alerts --name="Wreck Beach Wind Alerts"

# Set as default project
gcloud config set project wreck-beach-alerts

# Enable required APIs
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable appengine.googleapis.com

# Create App Engine app (required for Cloud Scheduler)
# Choose region closest to you (us-west2 for Vancouver)
gcloud app create --region=us-west2
```

## Step 3: Create Cloud Scheduler Job

### Option A: Using gcloud CLI (Recommended)

```bash
gcloud scheduler jobs create http wreck-beach-wind-check \
  --location=us-west2 \
  --schedule="0,30 * * * *" \
  --http-method=POST \
  --uri="https://api.github.com/repos/griffinvelichko/WreckBeachSurfAlert/actions/workflows/wind-alert.yml/dispatches" \
  --headers="Accept=application/vnd.github+json,Authorization=Bearer YOUR_GITHUB_TOKEN,X-GitHub-Api-Version=2022-11-28" \
  --message-body='{"ref":"main","inputs":{"trigger_source":"cloud-scheduler"}}' \
  --time-zone="America/Los_Angeles" \
  --attempt-deadline="30s"
```

**Important**: Replace `YOUR_GITHUB_TOKEN` with your actual GitHub token (ghp_...)

### Option B: Using Google Cloud Console

1. Go to [Cloud Scheduler Console](https://console.cloud.google.com/cloudscheduler)
2. Click **Create Job**
3. Configure:
   - **Name**: `wreck-beach-wind-check`
   - **Region**: `us-west2` (or your preferred)
   - **Frequency**: `0,30 * * * *`
   - **Time zone**: `America/Los_Angeles` (PST/PDT)
4. Configure HTTP target:
   - **Target type**: HTTP
   - **URL**: `https://api.github.com/repos/griffinvelichko/WreckBeachSurfAlert/actions/workflows/wind-alert.yml/dispatches`
   - **HTTP method**: POST
   - **Headers**:
     - `Accept`: `application/vnd.github+json`
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `X-GitHub-Api-Version`: `2022-11-28`
   - **Body**:
     ```json
     {
       "ref": "main",
       "inputs": {
         "trigger_source": "cloud-scheduler"
       }
     }
     ```

## Step 4: Test the Setup

### Test manually via Cloud Scheduler:
```bash
# Run the job immediately
gcloud scheduler jobs run wreck-beach-wind-check --location=us-west2

# Check job status
gcloud scheduler jobs describe wreck-beach-wind-check --location=us-west2
```

### Test via curl (to verify your token works):
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/griffinvelichko/WreckBeachSurfAlert/actions/workflows/wind-alert.yml/dispatches \
  -d '{"ref":"main","inputs":{"trigger_source":"test"}}'
```

Then check https://github.com/griffinvelichko/WreckBeachSurfAlert/actions to see if workflow was triggered.

## Step 5: Monitor and Maintain

### View logs:
```bash
# View execution history
gcloud scheduler jobs list --location=us-west2

# View specific job logs
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=wreck-beach-wind-check" --limit=10
```

### Update schedule if needed:
```bash
gcloud scheduler jobs update http wreck-beach-wind-check \
  --location=us-west2 \
  --schedule="*/15 * * * *"  # Example: every 15 minutes
```

### Pause/Resume:
```bash
# Pause
gcloud scheduler jobs pause wreck-beach-wind-check --location=us-west2

# Resume
gcloud scheduler jobs resume wreck-beach-wind-check --location=us-west2
```

## Costs

- **Google Cloud Scheduler Free Tier**: 3 jobs per month free
- **Execution costs**: ~1,488 executions/month (every 30 min) = FREE (under 5 million free tier)
- **Total monthly cost**: $0.00

## Troubleshooting

### Job fails with 401 Unauthorized
- GitHub token expired or incorrect
- Update token: `gcloud scheduler jobs update http wreck-beach-wind-check --location=us-west2 --headers="Authorization=Bearer NEW_TOKEN,..."`

### Job fails with 404 Not Found
- Check repository name and workflow filename are correct
- Ensure workflow exists on the main branch

### Job succeeds but workflow doesn't run
- Check workflow has `workflow_dispatch` trigger
- Verify the `ref` in the body matches your default branch
- Check GitHub Actions isn't disabled in repository settings

## Security Notes

1. **Token Storage**: Google Cloud Scheduler stores the token encrypted
2. **Token Rotation**: Set calendar reminder to rotate GitHub token before expiration
3. **Minimum Permissions**: Use token with only necessary scopes
4. **Audit Logs**: Both Google Cloud and GitHub provide audit logs

## Alternative: Using GitHub App Instead of PAT

For production use, consider creating a GitHub App instead of using a Personal Access Token:
- Doesn't expire
- More granular permissions
- Better audit trail

See: https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps

## Next Steps

1. Set up alerting if Cloud Scheduler job fails
2. Add backup scheduler (e.g., AWS EventBridge)
3. Monitor GitHub API rate limits
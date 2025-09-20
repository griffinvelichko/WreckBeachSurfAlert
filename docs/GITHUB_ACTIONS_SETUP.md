# GitHub Actions Setup Guide

## Prerequisites
- GitHub repository (public or private)
- Twilio account with phone number (see docs/TWILIO_SETUP.md)
- OpenAI API key (see docs/OPENAI_SETUP.md)

## Step-by-Step Setup

### 1. Push Code to GitHub

If you haven't already created a GitHub repository:

```bash
# Initialize git repo (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Wreck Beach Wind Alert System"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/Weather-Monitor.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Secrets

You need to add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

#### Required Secrets

| Secret Name | Value | Description |
|------------|-------|-------------|
| `TWILIO_ACCOUNT_SID` | ACxxxxxxxxxxxxxxxxxxxxxxxxxx | From Twilio Console |
| `TWILIO_AUTH_TOKEN` | xxxxxxxxxxxxxxxxxxxxxxxxxx | From Twilio Console (hidden by default) |
| `TWILIO_PHONE_FROM` | +1XXXXXXXXXX | Your Twilio phone number |
| `ALERT_PHONE_TO` | +1604XXXXXXX | Your phone number to receive alerts |
| `OPENAI_API_KEY` | sk-proj-xxxxxxxxxxxxx | From OpenAI Platform (optional for Phase G) |

### 3. Enable GitHub Actions

For public repositories:
- Actions are enabled by default

For private repositories:
1. Go to Settings → Actions → General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Click Save

### 4. Test Manual Trigger

To test the workflow manually:

1. Go to the **Actions** tab in your repository
2. Click on "Wreck Beach Wind Alert" workflow
3. Click "Run workflow" button
4. Select branch (usually `main`)
5. Click "Run workflow"

You should see the workflow running. Click on it to see logs.

### 5. Verify Scheduled Runs

The workflow is configured to run:
- **Every 30 minutes** (at minute 0 and 30 of each hour)
- Example: 1:00, 1:30, 2:00, 2:30, 3:00, 3:30, etc.
- Times are in UTC

To check scheduled runs:
1. Go to Actions tab
2. Look for runs triggered by "schedule"

## Monitoring

### View Logs
1. Go to Actions tab
2. Click on any workflow run
3. Click on "check-wind" job
4. Expand any step to see detailed logs

### Check State Persistence
The workflow uses GitHub Actions artifacts to maintain state between runs:
- State is stored in `wind-alert-state` artifact
- Retention is set to 1 day
- You can download the artifact to inspect state

## Troubleshooting

### Workflow Not Running on Schedule
- GitHub Actions may disable scheduled workflows after 60 days of repository inactivity
- To re-enable: Go to Actions tab and manually run the workflow once

### SMS Not Sending
Check the logs for:
- Twilio authentication errors → Verify secrets
- Phone number format → Should be E.164 format (+1XXXXXXXXXX)
- Twilio trial account limits → Verify recipient number

### State Not Persisting
- Check if artifact is being created (in workflow run summary)
- Artifacts expire after 1 day by design
- First run won't have previous state (expected)

### Wind Data Fetch Errors
- Open-Meteo API is free and doesn't require authentication
- If primary fails, system should fallback to ECCC
- Check logs for specific error messages

## Cost Considerations

### GitHub Actions Free Tier
- **Public repositories**: Unlimited minutes
- **Private repositories**: 2,000 minutes/month free

This workflow uses approximately:
- 1-2 minutes per run
- 48 runs per day (every 30 minutes) = ~96 minutes/day
- Monthly usage: ~2,880 minutes (requires paid plan for private repos)

### SMS Costs
- Twilio trial: $15 credit included
- Per SMS: ~$0.01-0.02
- Estimated monthly: $0.40-2.00 depending on wind conditions

## Security Notes

1. **Never commit secrets** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Rotate API keys** quarterly
4. **Monitor usage** to detect any unusual activity

## Important Notes for Production

### For Public Repositories
- Scheduled workflows are disabled after 60 days of no activity
- You must push a commit or run manually at least once every 60 days

### For Trial Twilio Accounts
- Messages will include "Sent from your Twilio trial account" prefix
- Can only send to verified phone numbers
- Perfect for personal use

### Recommended Testing Schedule
Before relying on the system:
1. Run manually with test data
2. Run manually with real weather data
3. Let it run on schedule for 24 hours
4. Verify you receive alerts when conditions are met

## Next Steps

1. Complete GitHub secrets setup
2. Push code to repository
3. Run manual test
4. Monitor first few scheduled runs
5. Adjust wind thresholds if needed in `.github/workflows/wind-alert.yml`
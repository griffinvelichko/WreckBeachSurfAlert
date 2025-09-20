# OpenAI API Setup Guide

## Account Creation

1. Visit [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up with:
   - Email address
   - Password
   - Or continue with Google/Microsoft account

3. Verify email address

## API Key Generation

1. Navigate to [API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Name your key: `wind-alert-production`
4. Copy the key immediately (shown only once)
   - Format: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
5. Store securely

## Billing Setup

1. Navigate to [Billing](https://platform.openai.com/settings/organization/billing)
2. Add payment method:
   - Credit/debit card
   - Set usage limits (recommended: $5/month)
3. Enable auto-recharge (optional)

## Model Selection

For this project, we use:
- **Model**: `gpt-4o-mini`
- **Reason**: Cost-effective, fast, sufficient for message generation
- **Alternative**: `gpt-3.5-turbo` (even cheaper but less creative)

## Cost Estimates

### gpt-4o-mini Pricing
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Per alert: ~110 tokens ≈ $0.00002
- Monthly (20 alerts): ~$0.0004

### Token Usage Breakdown
- System prompt: ~50 tokens
- User prompt: ~30 tokens
- Response: ~30 tokens
- Total: ~110 tokens per alert

## Usage Monitoring

1. Navigate to [Usage](https://platform.openai.com/usage)
2. Monitor:
   - Daily token usage
   - Cost accumulation
   - Rate limit status

## Rate Limits

Default limits for new accounts:
- Requests per minute: 500
- Tokens per minute: 30,000
- Sufficient for our use case (1 request/hour)

## Best Practices

1. **API Key Security**:
   - Never commit to version control
   - Use environment variables
   - Rotate keys quarterly

2. **Error Handling**:
   - Implement timeout (8 seconds)
   - Have fallback messages
   - Log API errors

3. **Optimization**:
   - Cache similar responses
   - Use appropriate max_tokens
   - Round wind values for better caching

## Testing Your API Key

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say 'API key works!'"}
    ],
    max_tokens=10
)

print(response.choices[0].message.content)
```

## Required Environment Variable

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Important Notes

- Free trial credits may be available for new accounts
- Monitor usage to avoid unexpected charges
- API keys are scoped to organization
- Consider using OpenAI's usage alerts
- Test with small max_tokens during development
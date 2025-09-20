# Twilio Account Setup Guide

## Account Creation

1. Visit [Twilio Sign Up](https://www.twilio.com/try-twilio)
2. Complete the registration form with:
   - Email address
   - Password
   - Phone number for verification

3. Verify your email and phone number

## Phone Number Acquisition

### For Trial Account (Recommended for Personal Use)
Twilio provides a free phone number with your trial account:
1. Navigate to Phone Numbers → Manage → Active Numbers
2. You should see a phone number already assigned
3. If not, click "Get a trial phone number" (free)

### For Paid Account
1. Navigate to Phone Numbers → Manage → Buy a number
2. Select country: **Canada** (+1) or **USA** (+1)
3. Choose capabilities: **SMS**
4. Select a number (costs ~$1/month)
5. Purchase the number

## Retrieve Credentials

1. Go to Console Dashboard
2. Find your credentials:
   - **Account SID**: ACxxxxxxxxxxxxxxxxxxxxxxxxxx
   - **Auth Token**: (click to reveal)
   - **Phone Number**: +1XXXXXXXXXX

## Phone Number Configuration

After purchasing your phone number, you need to configure it properly. Navigate to Phone Numbers → Manage → Active Numbers, click on your number, and configure as follows:

### Voice Configuration
Since we're only using SMS, configure voice to use the default demo handlers:

**Configure with**: Webhook
**A call comes in**:
- URL: `https://demo.twilio.com/welcome/voice/`
- HTTP Method: **HTTP POST**

**Primary handler fails**: Leave empty
**Call status changes**: Leave empty
**Caller Name Lookup**: **Disabled**
**Emergency Calling**: Not required for SMS-only usage

### Messaging Configuration
Configure messaging to handle incoming SMS (even though we're only sending):

**Configure with**: Webhook
**A message comes in**:
- URL: `https://demo.twilio.com/welcome/sms/reply`
- HTTP Method: **HTTP POST**

**Primary handler fails**: Leave empty
**Messaging Service**: Leave as "No options" (unless using a Messaging Service)

### Regional Routing
Ensure proper regional routing:
- **United States (US1) Region call routing**: Active
- **United States (US1) Region message routing**: Active

Click **Save configuration** after making these changes.

## Configure for Production

### Messaging Service Setup (Optional but Recommended)

1. Navigate to Messaging → Services → Create Messaging Service
2. Give it a name like "Wind Alert Service"
3. Select use case: "Notify my users"

#### Integration Settings
Configure how your Messaging Service handles messages:

**Incoming Messages**:
- Select **"Receive the message"**
- This stores messages in logs but doesn't invoke webhooks (we're only sending, not receiving)

**Delivery Status Callback**:
- Leave **empty** (optional - only needed if you want delivery confirmations)

**Validity Period**:
- **Twilio Queue time limit**: Leave at default **36000 seconds** (10 hours)
- This ensures messages are attempted for up to 10 hours if there are delivery issues

Click **Save** after configuration.

### Add Phone Number to Service
1. In your Messaging Service, go to "Sender Pool"
2. Click "Add Senders" → "Phone Number"
3. Select your purchased phone number
4. Click "Add Phone Numbers"

### Geo Permissions
1. Navigate to Messaging → Settings → Geo permissions
2. Ensure **Canada** is enabled (checked)
3. Save changes

## A2P Registration (For Production Use)

**Note: For personal/development use with verified numbers only, you can skip A2P registration.**

### Trial Account Setup (Personal Use Only)
If you're only sending alerts to your own verified phone number:

1. Stay on the **Trial Account** (don't upgrade)
2. Navigate to Console → Phone Numbers → Verified Caller IDs
3. Add and verify your personal phone number (the one receiving alerts)
4. You can now send SMS to this verified number without A2P registration
5. Trial includes $15 credit (enough for ~750-1500 messages)

**Limitations of Trial Account**:
- Can only send to verified phone numbers
- Messages include "Sent from your Twilio trial account" prefix
- Perfect for personal weather monitoring

### Production Setup (Multiple Recipients)
Only needed if sending to non-verified numbers:

1. Navigate to Regulatory Compliance → A2P 10DLC
2. Register your brand/business
3. Create campaign for "Weather Alerts"
4. Wait for approval (24-48 hours)

## Test SMS Sending

From Twilio Console:
1. Navigate to Messaging → Try it Out
2. Send a test SMS to your verified number

## Important Notes

- Trial accounts have $15 credit (sufficient for personal use)
- Trial requires recipient phone verification (perfect for single-user setup)
- Upgrade to paid account only if sending to multiple unverified numbers
- Canadian SMS costs: ~$0.0075 base + carrier fees (~750-1500 alerts with trial credit)

## Required Environment Variables

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_FROM=+1XXXXXXXXXX
```

### If Using Messaging Service
If you created a Messaging Service, you can optionally use the Messaging Service SID instead of the phone number:
```
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Note: You would need to modify the code to use the messaging service SID instead of the from_ phone number.
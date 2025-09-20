import logging
from typing import Optional
from twilio.rest import Client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from twilio.base.exceptions import TwilioException
from .config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_FROM,
    ALERT_PHONE_TO,
    DRY_RUN
)

log = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((TwilioException, ConnectionError))
)
def send_sms(message_body: str) -> Optional[str]:
    """
    Send SMS via Twilio with retry logic.

    Args:
        message_body: The message to send

    Returns:
        Message SID if successful, None if dry run
    """
    # Check for required configuration
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_FROM, ALERT_PHONE_TO]):
        log.error("Missing required Twilio configuration")
        return None

    if DRY_RUN:
        log.info(f"[DRY RUN] Would send SMS: {message_body}")
        return "DRY_RUN_SID"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_FROM,
            to=ALERT_PHONE_TO
        )

        log.info(f"SMS sent successfully. SID: {message.sid}")
        return message.sid

    except TwilioException as e:
        log.error(f"Twilio error: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error sending SMS: {e}")
        raise
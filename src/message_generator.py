"""
OpenAI ChatGPT Integration for Funny Surfer Messages
Phase G: Message Generator

Generates creative, funny Australian surfer dude messages for wind alerts.
Falls back to standard messages if OpenAI API is unavailable.
"""

import os
import logging
from typing import Optional
from pathlib import Path
from openai import OpenAI
from openai import OpenAIError

log = logging.getLogger(__name__)

def get_wind_direction_abbrev(degrees: float) -> str:
    """Convert degrees to short compass direction."""
    degrees = degrees % 360
    if degrees <= 11.25 or degrees >= 348.75:
        return "N"
    elif 11.25 < degrees <= 33.75:
        return "NNE"
    elif 33.75 < degrees <= 56.25:
        return "NE"
    elif 56.25 < degrees <= 78.75:
        return "ENE"
    elif 78.75 < degrees <= 101.25:
        return "E"
    elif 101.25 < degrees <= 123.75:
        return "ESE"
    elif 123.75 < degrees <= 146.25:
        return "SE"
    elif 146.25 < degrees <= 168.75:
        return "SSE"
    elif 168.75 < degrees <= 191.25:
        return "S"
    elif 191.25 < degrees <= 213.75:
        return "SSW"
    elif 213.75 < degrees <= 236.25:
        return "SW"
    elif 236.25 < degrees <= 258.75:
        return "WSW"
    elif 258.75 < degrees <= 281.25:
        return "W"
    elif 281.25 < degrees <= 303.75:
        return "WNW"
    elif 303.75 < degrees <= 326.25:
        return "NW"
    elif 326.25 < degrees <= 348.75:
        return "NNW"
    else:
        return "?"

def generate_surfer_message(wind_speed: float, wind_direction: float) -> Optional[str]:
    """
    Generate a funny Australian surfer dude message using OpenAI ChatGPT.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees

    Returns:
        Generated message string or None if failed
    """
    api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        log.warning("OPENAI_API_KEY not set, using fallback message")
        return None

    # Skip if in test mode or explicitly disabled
    if api_key == 'test_key' or api_key.startswith('sk-test'):
        log.info("Test mode detected, skipping OpenAI API call")
        return None

    try:
        client = OpenAI(api_key=api_key)

        # Load system prompt from file
        prompt_file = Path(__file__).parent / "openai_system_prompt.md"
        if prompt_file.exists():
            system_prompt = prompt_file.read_text()
        else:
            log.warning("System prompt file not found, using default")
            system_prompt = """You are an Australian surfer. Create a 1-2 sentence SMS alert about wind conditions.
MUST include wind direction (N/NW/W etc) and speed in km/h. Keep under 160 chars. Be funny and urgent."""

        direction_abbrev = get_wind_direction_abbrev(wind_direction)

        user_message = f"""Wind conditions at Wreck Beach:
- Wind: {direction_abbrev} at {wind_speed:.0f}km/h
- Direction degrees: {wind_direction:.0f}°

Create a 1-2 sentence SMS that MUST include "{direction_abbrev}" and "{wind_speed:.0f}km/h". Make it funny and urgent!"""

        log.info(f"Calling OpenAI API with gpt-4o-mini model...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.9,  # Higher temperature for more creative/funny responses
            presence_penalty=0.3,  # Encourage variety
            frequency_penalty=0.3
        )

        message = response.choices[0].message.content.strip()

        # Ensure message fits SMS limit (160 chars)
        if len(message) > 160:
            # Try to cut at last complete sentence
            sentences = message.split('!')
            if len(sentences) > 1:
                message = '!'.join(sentences[:-1]) + '!'
            else:
                message = message[:157] + "..."

        # Verify message contains required info (direction and speed)
        if direction_abbrev not in message or f"{wind_speed:.0f}" not in message:
            log.warning("AI message missing required wind data, using fallback")
            return None

        log.info(f"Generated AI message: {message}")
        return message

    except OpenAIError as e:
        log.error(f"OpenAI API error: {e}. Using fallback message.")
        return None
    except Exception as e:
        log.error(f"Unexpected error generating AI message: {e}. Using fallback.")
        return None

def create_fallback_message(wind_speed: float, wind_direction: float) -> str:
    """
    Create a fallback message when OpenAI is unavailable.
    Still surfer-themed but ensures wind stats are included.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees

    Returns:
        Fallback message string (always includes direction and speed)
    """
    direction = get_wind_direction_abbrev(wind_direction)

    # Create surfer-themed fallback messages with guaranteed wind stats
    if wind_speed >= 35:
        return f"🌊 {direction} wind {wind_speed:.0f}km/h absolutely FIRING at Wreck Beach! Drop everything and get here NOW legend!"
    elif wind_speed >= 30:
        return f"🏄 {direction} {wind_speed:.0f}km/h pumping at Wreck Beach! Epic conditions mate, time to shred!"
    else:
        return f"🌊 {direction} wind {wind_speed:.0f}km/h at Wreck Beach! Solid sesh brewing, get on it!"

def generate_alert_message(wind_speed: float, wind_direction: float) -> str:
    """
    Main function to generate alert message with AI or fallback.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees

    Returns:
        Alert message string (AI-generated or fallback)
    """
    # Try AI generation first
    ai_message = generate_surfer_message(wind_speed, wind_direction)

    if ai_message:
        return ai_message

    # Use fallback if AI fails
    log.info("Using fallback message (AI unavailable)")
    return create_fallback_message(wind_speed, wind_direction)
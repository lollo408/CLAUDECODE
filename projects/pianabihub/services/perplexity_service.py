"""
Perplexity API integration for generating event summaries.
Uses the sonar-pro model for web-grounded research.
"""

import os
import requests

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'


def generate_event_summary(event_name: str, event_date: str,
                           industry: str, location: str,
                           website: str = None) -> dict:
    """
    Generate a 2-3 paragraph summary of a past event using Perplexity.

    Args:
        event_name: Name of the event
        event_date: End date of the event
        industry: Industry category
        location: Event location
        website: Optional event website

    Returns:
        dict: {success: bool, summary: str, error: str}
    """

    if not PERPLEXITY_API_KEY:
        return {
            'success': False,
            'summary': None,
            'error': 'PERPLEXITY_API_KEY not configured'
        }

    prompt = f"""Research and write a 2-3 paragraph summary of the industry event:

Event: {event_name}
Date: {event_date}
Industry: {industry}
Location: {location}
{f'Website: {website}' if website else ''}

Please provide:
1. Overview of what happened at the event
2. Key announcements, product launches, or trends discussed
3. Notable attendees or speakers if known
4. Industry impact or takeaways

Write in a professional business intelligence tone. Focus on actionable insights."""

    headers = {
        'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'sonar-pro',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }

    try:
        response = requests.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        summary = data['choices'][0]['message']['content']

        return {
            'success': True,
            'summary': summary,
            'error': None
        }

    except requests.exceptions.Timeout:
        return {'success': False, 'summary': None, 'error': 'API timeout'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'summary': None, 'error': str(e)}
    except (KeyError, IndexError) as e:
        return {'success': False, 'summary': None, 'error': f'Invalid response: {e}'}

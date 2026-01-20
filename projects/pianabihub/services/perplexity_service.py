"""
Perplexity API integration for generating event summaries.
Uses the sonar-pro model for web-grounded research.
"""

import os
import requests

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '').strip()
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

    prompt = f"""Research the industry event below and provide a structured summary in HTML format.

Event: {event_name}
Date: {event_date}
Industry: {industry}
Location: {location}
{f'Website: {website}' if website else ''}

FORMAT YOUR RESPONSE AS HTML EXACTLY LIKE THIS:

<h3>Overview</h3>
<p>One paragraph summarizing what the event was about and its significance.</p>

<h3>Key Highlights</h3>
<ul>
<li><strong>Highlight 1:</strong> Key announcement or product launch</li>
<li><strong>Highlight 2:</strong> Important trend discussed</li>
<li><strong>Highlight 3:</strong> Notable speaker or presentation</li>
<li><strong>Highlight 4:</strong> Industry impact or takeaway</li>
</ul>

<h3>Notable Attendees</h3>
<ul>
<li>Company/Person 1</li>
<li>Company/Person 2</li>
</ul>

<h3>Sources</h3>
<ul>
<li><a href="URL">Source 1 title</a></li>
<li><a href="URL">Source 2 title</a></li>
</ul>

IMPORTANT RULES:
- Output ONLY valid HTML, no markdown
- Do NOT include inline citations like [1] or [2] in the text
- Use <ul> and <li> for bullet points
- Put all sources at the bottom with clickable links
- Write in a professional business intelligence tone
- Focus on actionable insights
- Do NOT wrap the response in code blocks"""

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

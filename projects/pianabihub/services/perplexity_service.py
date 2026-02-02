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

    # System context for Piana business intelligence
    system_message = """You are a business intelligence analyst for Piana, a 440+ year heritage company (est. 1582, Biella, Italy).

PIANA TECHNOLOGY (Parent Company):
- Develops sustainable fiber-based materials replacing wasteful single-use products
- Clean technologies: water-based dyeing, non-toxic flame retardants, steam-molded fibers
- Industries: Textiles, Automotive interiors, Bedding/Sleep
- Circular economy focus: 100% recyclable and reusable materials

PIANA SLEEP (Hospitality Division):
- Luxury American-made mattresses (manufactured in Cartersville, Georgia)
- V/Smart™ fiber technology - molecular printing for performance enhancement
- Flagship: Rinnovo mattress - breathable, hypoallergenic, low-VOC
- Zero waste to landfill + end-of-life take-back program
- Target customers: Luxury hotels, resorts, cruise lines, premium hospitality

WHAT MATTERS TO PIANA:
1. HOSPITALITY LEADS: Hotel renovations, new property openings, bedding RFPs, FF&E projects
2. AUTOMOTIVE OPPORTUNITIES: OEM interior programs, EV manufacturers, sustainable material mandates
3. SUSTAINABILITY SIGNALS: ESG commitments, circular economy pledges, plastic/foam reduction initiatives
4. DECISION MAKERS: Procurement directors, sustainability officers, FF&E designers, C-suite executives
5. COMPETITIVE INTEL: Bedding innovations, textile technologies, material science advances
6. REGULATORY TRENDS: Mattress recycling laws, VOC regulations, sustainability standards"""

    prompt = f"""Research this industry event and provide actionable business intelligence.

EVENT:
- Name: {event_name}
- Date: {event_date}
- Industry: {industry}
- Location: {location}
{f'- Website: {website}' if website else ''}

FORMAT YOUR RESPONSE AS HTML:

<h3>Event Overview</h3>
<p>2-3 sentences: What happened and why it matters to the {industry} industry.</p>

<h3>Business Opportunities</h3>
<ul>
<li><strong>[Company Name]:</strong> Specific announcement (renovation, new property, sustainability initiative) that could be a sales lead. Include details on scope and timing if available.</li>
<li><strong>[Company Name]:</strong> Another actionable opportunity with specifics.</li>
</ul>
<p><em>If no clear opportunities, state "No direct opportunities identified at this event" and briefly explain.</em></p>

<h3>Sustainability & Innovation</h3>
<ul>
<li><strong>ESG:</strong> Circular economy commitments, waste reduction pledges, or sustainability certifications announced</li>
<li><strong>Technology:</strong> New materials, manufacturing processes, or product innovations relevant to textiles/bedding/automotive</li>
</ul>

<h3>Key Contacts</h3>
<ul>
<li><strong>Name, Title @ Company</strong> - Their relevance (decision-maker, announced project, sustainability leader)</li>
</ul>
<p><em>Focus on people with purchasing authority or sustainability responsibility.</em></p>

<h3>Market Trends</h3>
<p>1-2 sentences on industry direction, regulatory changes, or competitive shifts observed.</p>

<h3>Sources</h3>
<ul>
<li><a href="URL">Source title</a></li>
</ul>

RULES:
- Output ONLY valid HTML, no markdown or code blocks
- No inline citations like [1] or [2]
- All source URLs must be real (not example.com or placeholder)
- Be specific: name companies, people, dollar amounts, timelines
- If information is limited, acknowledge it honestly
- Professional, actionable tone"""

    headers = {
        'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'sonar-pro',
        'messages': [
            {'role': 'system', 'content': system_message},
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

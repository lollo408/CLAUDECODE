"""
Perplexity API integration for generating event summaries.
Two-pass approach:
  Pass 1 (sonar-pro): Web research - gather raw facts and sources
  Pass 2 (sonar-reasoning-pro): Business intelligence analysis
"""

import os
import re
import requests

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '').strip()


def _clean_html_response(content: str) -> str:
    """
    Clean up AI-generated HTML response.
    - Strips markdown code blocks (```html ... ```)
    - Removes any leading/trailing whitespace
    """
    if not content:
        return content

    # Remove markdown code blocks (```html, ```HTML, ``` etc.)
    # Pattern matches opening ```html or ``` and closing ```
    content = re.sub(r'^```(?:html|HTML)?\s*\n?', '', content.strip())
    content = re.sub(r'\n?```\s*$', '', content.strip())

    return content.strip()
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'

# Piana context used in Pass 2
PIANA_CONTEXT = """PIANA TECHNOLOGY (Parent Company):
- 440+ year heritage company (est. 1582, Biella, Italy)
- Develops sustainable fiber-based materials replacing wasteful single-use products
- Clean technologies: water-based dyeing, non-toxic flame retardants, steam-molded fibers
- Industries: Textiles, Automotive interiors, Bedding/Sleep
- Circular economy focus: 100% recyclable and reusable materials

PIANA SLEEP (Hospitality Division):
- Luxury American-made mattresses (manufactured in Cartersville, Georgia)
- V/Smart fiber technology - molecular printing for performance enhancement
- Flagship: Rinnovo mattress - breathable, hypoallergenic, low-VOC
- Zero waste to landfill + end-of-life take-back program
- Target customers: Luxury hotels, resorts, cruise lines, premium hospitality

OPPORTUNITY INDICATORS (for scoring):
- Hotel/resort renovation or refurbishment announcements
- New property openings or brand expansions
- Sustainability/ESG commitments or circular economy pledges
- Luxury or premium hospitality brands
- Decision-makers present (procurement, sustainability officers, C-suite)
- Automotive OEM interior programs or EV manufacturers
- Bedding RFPs or FF&E projects mentioned"""


def _call_perplexity(model: str, messages: list, timeout: int = 90) -> dict:
    """Helper to call Perplexity API."""
    if not PERPLEXITY_API_KEY:
        return {'success': False, 'content': None, 'error': 'PERPLEXITY_API_KEY not configured'}

    headers = {
        'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': model,
        'messages': messages
    }

    try:
        response = requests.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']
        return {'success': True, 'content': content, 'error': None}

    except requests.exceptions.Timeout:
        return {'success': False, 'content': None, 'error': 'API timeout'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'content': None, 'error': str(e)}
    except (KeyError, IndexError) as e:
        return {'success': False, 'content': None, 'error': f'Invalid response: {e}'}


def _pass_one_research(event_name: str, event_date: str,
                        industry: str, location: str,
                        website: str = None) -> dict:
    """
    Pass 1: Web research using sonar-pro.
    Gathers raw facts, announcements, attendees, and sources.
    """

    prompt = f"""Research this industry event thoroughly and provide a comprehensive factual report.

EVENT DETAILS:
- Name: {event_name}
- Date: {event_date}
- Industry: {industry}
- Location: {location}
{f'- Website: {website}' if website else ''}

GATHER THE FOLLOWING INFORMATION:

1. EVENT OVERVIEW
- What was the event about? (theme, focus, scale)
- How many attendees/exhibitors?
- Any notable sponsors or organizers?

2. KEY ANNOUNCEMENTS
- Product launches or unveilings
- Company announcements (expansions, partnerships, investments)
- New projects or initiatives revealed
- Awards or recognitions given

3. SPEAKERS & ATTENDEES
- Notable speakers and their topics
- Executives or decision-makers who attended
- Companies that exhibited or sponsored

4. INDUSTRY THEMES
- Major topics or trends discussed
- Sustainability or ESG discussions
- Technology or innovation highlights
- Regulatory or policy mentions

5. HOSPITALITY & TRAVEL SPECIFIC (if applicable)
- Hotel/resort renovation announcements
- New property openings mentioned
- Brand expansion plans
- FF&E or procurement discussions

6. SOURCES
- List all URLs where you found this information

FORMAT: Provide a detailed, factual report. Include specific names, companies, dates, and numbers where available. Do not analyze or editorialize - just report the facts. If information is not available, say so clearly."""

    return _call_perplexity('sonar-pro', [{'role': 'user', 'content': prompt}])


def _pass_two_analysis(research: str, event_name: str,
                        industry: str) -> dict:
    """
    Pass 2: Business intelligence analysis using sonar-reasoning-pro.
    Analyzes research through Piana's business lens.
    """

    system_message = f"""You are a senior business intelligence analyst for Piana, preparing executive briefings on industry events.

{PIANA_CONTEXT}

Your task is to analyze event research and produce actionable business intelligence. Be direct and honest - if there are no opportunities, say so, but always find value (trends, contacts, future potential)."""

    prompt = f"""Based on this research about "{event_name}" ({industry} industry), create a business intelligence briefing.

RESEARCH DATA:
{research}

---

FORMAT YOUR RESPONSE AS HTML WITH THIS EXACT STRUCTURE:

<!-- SCORECARD - Quick orientation as bullet points with emojis -->
<h3>Quick Assessment</h3>
<ul>
<li><strong>🎯 Opportunity Score:</strong> [HIGH / MEDIUM / LOW] — <em>[One line explaining why]</em></li>
<li><strong>🏢 Piana Relevance:</strong> [HIGH / MEDIUM / LOW] — <em>[One line explaining why]</em></li>
<li><strong>⏰ Urgency:</strong> [IMMEDIATE / NEAR-TERM / MONITOR] — <em>[One line explaining why]</em></li>
</ul>

<!-- BUSINESS INTELLIGENCE -->
<h3>Immediate Actions</h3>
<ul>
<li><strong>Action:</strong> Specific thing to do now, with contact or company name if applicable</li>
</ul>
<p><em>If no immediate actions, write "No immediate actions required - see opportunities below for pipeline items."</em></p>

<h3>Opportunities Identified</h3>
<ul>
<li><strong>[Company Name]:</strong> What they announced + why it matters to Piana + timing/urgency</li>
</ul>
<p><em>Prioritize by timing (soonest first). If no clear opportunities, highlight what to monitor for future potential.</em></p>

<h3>Market Intelligence</h3>
<ul>
<li><strong>Trend:</strong> Industry shift or pattern observed</li>
<li><strong>Competitive:</strong> What competitors or alternatives are doing</li>
</ul>

<h3>Key Contacts</h3>
<ul>
<li><strong>Name, Title @ Company</strong> - Why they matter (decision-making authority, relevant project, sustainability focus)</li>
</ul>

<h3>Why This Matters to Piana</h3>
<p><em>Only include this section if there's a genuine, specific connection to Piana's business. If the connection is generic or forced, skip this section entirely.</em></p>

<h3>Sources</h3>
<ul>
<li><a href="https://actual-url.com/path">Source title</a></li>
<li><a href="https://another-real-url.com">Another source</a></li>
</ul>
<p><em>CRITICAL: Every source MUST be a clickable hyperlink with a real URL. Format: &lt;a href="https://..."&gt;Title&lt;/a&gt;</em></p>

<!-- EVENT RECAP - For passive reading -->
<hr>
<h3>Event Recap</h3>
<p><em>For general awareness - no business lens, just what happened.</em></p>
<p>[2-3 paragraphs summarizing the event in an engaging, informative way. What was the atmosphere? What were people talking about? Any interesting moments or themes? Write this like a well-crafted industry newsletter that someone would enjoy reading with their morning coffee.]</p>

---

SCORING GUIDANCE:
- HIGH Opportunity: Direct sales lead (renovation announced, RFP mentioned, decision-maker met)
- MEDIUM Opportunity: Indirect potential (sustainability commitment, brand expansion plans, relevant contact)
- LOW Opportunity: No clear lead but valuable market intelligence
- IMMEDIATE Urgency: Project happening in next 3 months or RFP active
- NEAR-TERM Urgency: Project in 3-12 months or early planning stage
- MONITOR Urgency: Long-term trend or no specific timeline

RULES:
- Output ONLY valid HTML, no markdown or code blocks (no ``` anywhere)
- No inline citations like [1] or [2]
- SOURCES MUST BE CLICKABLE LINKS: Use <a href="https://real-url.com">Title</a> format
- Every source needs a real, working URL - no placeholder text like "event materials" without a link
- If you cannot find a URL for a source, include only sources you have URLs for
- Be specific: names, companies, dollar amounts, timelines
- Be honest about limitations - if data is thin, say so
- The Event Recap should be enjoyable to read, not dry"""

    return _call_perplexity(
        'sonar-reasoning-pro',
        [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': prompt}
        ],
        timeout=120  # Reasoning model may take longer
    )


def generate_event_summary(event_name: str, event_date: str,
                           industry: str, location: str,
                           website: str = None) -> dict:
    """
    Generate a comprehensive event summary using two-pass approach.

    Pass 1 (sonar-pro): Web research - gather raw facts
    Pass 2 (sonar-reasoning-pro): Business intelligence analysis

    Args:
        event_name: Name of the event
        event_date: End date of the event
        industry: Industry category
        location: Event location
        website: Optional event website

    Returns:
        dict: {success: bool, summary: str, error: str}
    """

    # Pass 1: Research
    research_result = _pass_one_research(
        event_name, event_date, industry, location, website
    )

    if not research_result['success']:
        return {
            'success': False,
            'summary': None,
            'error': f"Pass 1 (Research) failed: {research_result['error']}"
        }

    research_data = research_result['content']

    # Pass 2: Analysis
    analysis_result = _pass_two_analysis(research_data, event_name, industry)

    if not analysis_result['success']:
        return {
            'success': False,
            'summary': None,
            'error': f"Pass 2 (Analysis) failed: {analysis_result['error']}"
        }

    # Clean up HTML (remove markdown code blocks if present)
    cleaned_summary = _clean_html_response(analysis_result['content'])

    return {
        'success': True,
        'summary': cleaned_summary,
        'error': None
    }

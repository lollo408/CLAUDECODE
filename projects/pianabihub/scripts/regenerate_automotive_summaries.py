"""
Regenerate event summaries using the new two-pass system.
Run this script locally to update past event summaries.

Usage:
  cd projects/pianabihub

  # Run 3 Automotive events (test)
  python scripts/regenerate_automotive_summaries.py --limit 3

  # Run all Automotive events
  python scripts/regenerate_automotive_summaries.py

  # Run 5 Hospitality events
  python scripts/regenerate_automotive_summaries.py --industry Hospitality --limit 5

  # Run ALL events (all industries)
  python scripts/regenerate_automotive_summaries.py --industry all
"""

import os
import sys
import argparse
from datetime import datetime

# Fix Windows encoding issues
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
from services.perplexity_service import generate_event_summary

# Initialize Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '').strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env.local")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_past_events(industry: str = 'Automotive', limit: int = None):
    """Fetch past events, optionally filtered by industry."""
    query = supabase.table('events') \
        .select('*') \
        .lt('start_date', datetime.now().date().isoformat()) \
        .order('start_date', desc=True)

    # Filter by industry unless "all"
    if industry.lower() != 'all':
        query = query.eq('industry', industry)

    # Apply limit if specified
    if limit:
        query = query.limit(limit)

    response = query.execute()
    return response.data


def upsert_summary(event_id: str, summary: str):
    """Insert or update event summary."""
    data = {
        'event_id': event_id,
        'summary_text': summary,
        'generated_at': datetime.now().isoformat(),
        'status': 'completed'
    }

    # Try to upsert (update if exists, insert if not)
    response = supabase.table('event_summaries') \
        .upsert(data, on_conflict='event_id') \
        .execute()
    return response


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Regenerate event summaries')
    parser.add_argument('--industry', type=str, default='Automotive',
                        help='Industry to process (Automotive, Hospitality, Bedding, Textiles, or "all")')
    parser.add_argument('--limit', type=int, default=None,
                        help='Maximum number of events to process (default: all)')
    args = parser.parse_args()

    industry = args.industry
    limit = args.limit

    print("=" * 60)
    print("EVENT SUMMARY REGENERATION")
    print("Using two-pass system (sonar-pro + sonar-reasoning-pro)")
    print("=" * 60)
    print(f"Industry: {industry}")
    if limit:
        print(f"Limit: {limit} events")
    print()

    events = get_past_events(industry, limit)
    total = len(events)
    print(f"Found {total} past events to process\n")

    if total == 0:
        print("No events found. Exiting.")
        return

    success_count = 0
    error_count = 0

    for i, event in enumerate(events, 1):
        event_name = event['name']
        event_id = event['id']
        event_industry = event.get('industry', 'Unknown')

        print(f"[{i}/{total}] {event_name}")
        print(f"         Industry: {event_industry} | Date: {event['start_date']} | Location: {event.get('location', 'N/A')}")

        # Generate summary using new two-pass system
        result = generate_event_summary(
            event_name=event_name,
            event_date=event.get('end_date') or event['start_date'],
            industry=event_industry,
            location=event.get('location', 'Unknown'),
            website=event.get('website')
        )

        if result['success']:
            # Save to database
            upsert_summary(event_id, result['summary'])
            print(f"         [OK] Summary generated and saved")
            success_count += 1
        else:
            print(f"         [FAIL] ERROR: {result['error']}")
            error_count += 1

        print()

    print("=" * 60)
    print(f"COMPLETE: {success_count} succeeded, {error_count} failed")
    print("=" * 60)


if __name__ == '__main__':
    main()

import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

print("Setting up Supabase database...")

test_data = [
    {
        "vertical": "hospitality",
        "top_3_news": [
            {
                "headline": "Luxury Hotels Embrace AI Concierge Services",
                "summary": "Major hotel chains are implementing AI-powered virtual concierges to enhance guest experience and streamline operations."
            },
            {
                "headline": "Sustainable Tourism Practices Show 40% Growth",
                "summary": "Eco-friendly accommodations and carbon-neutral travel options are becoming mainstream as travelers prioritize sustainability."
            },
            {
                "headline": "Restaurant Automation Reduces Labor Costs by 25%",
                "summary": "Smart kitchen technology and automated ordering systems are helping restaurants manage rising labor expenses."
            }
        ],
        "full_report": "<h4>Market Analysis</h4><p>The hospitality industry is experiencing rapid transformation through technology adoption and changing consumer preferences. Key trends include personalization, sustainability, and operational efficiency.</p><h4>Key Insights</h4><ul><li>Digital check-in reduces wait times by 60%</li><li>Personalized recommendations increase guest spending by 35%</li><li>Energy-efficient systems cut operational costs by 20%</li></ul>"
    }
]

try:
    response = supabase.table('intelligence_reports').insert(test_data).execute()
    print(f"✓ Successfully inserted test data!")
    print(f"  Records inserted: {len(response.data)}")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nThe table might not exist yet. Creating table...")
    print("\nPlease create the table in your Supabase dashboard:")
    print("1. Go to Table Editor")
    print("2. Create new table: intelligence_reports")
    print("3. Add these columns:")
    print("   - id: int8 (primary key, auto-increment)")
    print("   - created_at: timestamptz (default: now())")
    print("   - vertical: text")
    print("   - top_3_news: jsonb")
    print("   - full_report: text")

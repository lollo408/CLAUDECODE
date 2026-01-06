-- Create the intelligence_reports table
CREATE TABLE IF NOT EXISTS intelligence_reports (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    vertical TEXT NOT NULL,
    top_3_news JSONB,
    full_report TEXT
);

-- Insert test data
INSERT INTO intelligence_reports (vertical, top_3_news, full_report) VALUES
(
    'hospitality',
    '[
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
    ]'::jsonb,
    '<h4>Market Analysis</h4><p>The hospitality industry is experiencing rapid transformation through technology adoption and changing consumer preferences. Key trends include personalization, sustainability, and operational efficiency.</p><h4>Key Insights</h4><ul><li>Digital check-in reduces wait times by 60%</li><li>Personalized recommendations increase guest spending by 35%</li><li>Energy-efficient systems cut operational costs by 20%</li></ul>'
);

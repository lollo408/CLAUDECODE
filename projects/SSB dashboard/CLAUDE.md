# SSB Sustainability Dashboard

**Customer:** SSB (Simmons Serta Bedding)
**Purpose:** Customer-facing CO2 emissions calculator for Piana Nonwovens products
**Status:** In Development (Design Phase)

---

## Project Overview

Interactive calculator where SSB can:
1. Select products (pads or rolls)
2. Enter quantities
3. See total CO2e with relatable comparisons (trees, car miles)

**Scope:** Georgia plant only (Arizona excluded for now)

---

## Tech Stack

- **Backend:** Python + Flask
- **Frontend:** HTML/CSS/JavaScript (no framework)
- **Deployment:** Vercel (planned)
- **Data:** Static JSON (no database needed)

---

## Local Development

```bash
cd "C:\Users\LLeprotti\OneDrive - Tintoria-Piana US Inc\Claude Code\projects\SSB dashboard"
python main.py
```

Open: http://localhost:5001

---

## Design Options

Currently evaluating three design alternatives:

| Option | Style | URL |
|--------|-------|-----|
| A | Minimal Clean | `/option-a` |
| **B** | **Modern Dark (CHOSEN)** | `/option-b` |
| C | Corporate Table | `/option-c` |

**Decision:** Going with Option B - Modern Dark theme

---

## Product Data Structure

### Pads (with size selection)

| Family | Has OSF? | Sizes |
|--------|----------|-------|
| BSPV | Yes (1.1, 2.2) | 8 sizes each |
| SYFI | No | 8 sizes |
| TRI-FIBER | No | 5 sizes |

**BSPV Flow:** Select Product → Select OSF → Select Size → Enter Qty

### Rolls (flat list)

| Product | Emission Factor |
|---------|-----------------|
| CRS800 0.9 OSF ROLL | 1.319 kg/linear yard |
| CRS800 1.1 OSF W/PCM ROLL | 3.008 kg/linear yard |
| EVF 0.75 OSF ELASTO VERT ROLL | 1.933 kg/linear yard |
| TB100 ECO 0.75 OSF ROLL | 2.556 kg/linear yard |
| VR700 0.9 OSF 88IN ROLL | 2.68 kg/linear yard |
| VRS350 VLAP SILKFR 0.9 OSF RL | 2.68 kg/linear yard |

---

## Emission Factors

- **Unit for pads:** pieces
- **Unit for rolls:** linear yards
- **Equivalencies (EPA):**
  - Trees: `kg CO2e ÷ 21.77` (trees absorbing CO2/year)
  - Car miles: `kg CO2e ÷ 0.4` (miles driven)

---

## Files

```
SSB dashboard/
├── main.py                 # Flask app
├── requirements.txt        # Dependencies
├── vercel.json             # Vercel config
├── CLAUDE.md               # This file
├── notes                   # Meeting notes (TBD)
├── Dashboard SSB data.xlsx # Source data from sustainability manager
├── static/
│   ├── css/styles.css      # Original styles
│   └── data/products.json  # Product emission data
└── templates/
    ├── calculator.html     # Original (deprecated)
    ├── option-a.html       # Minimal Clean design
    ├── option-b.html       # Modern Dark design (CHOSEN)
    └── option-c.html       # Corporate Table design
```

---

## Open Items / Notes

- [ ] Review data with sustainability manager (meeting notes pending)
- [ ] Finalize Option B design
- [ ] Add Piana Technology branding/logo
- [ ] Deploy to Vercel
- [ ] Share with SSB

---

## Session History

### Jan 22, 2026
- Implemented initial plan
- Created shopping list interface
- Merged BSPV + BSPV15 into single product with OSF selector
- Created 3 design alternatives (A, B, C)
- Decision: Go with Option B (Modern Dark)
- Committed to GitHub

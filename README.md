# 👥 Influencer Radar

Deep dive into any influencer • Compare like a pro • Get the tea ☕

## Features

✨ **Analyze** - Get detailed stats on any Instagram influencer
⚖️ **Compare** - Side-by-side comparison of two influencers
📊 **Insights** - Discover trending creators and opportunities

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/influencer-analyzer.git
   cd influencer-analyzer
   ```
   our_project/
   ├── app.py # ~50 lines (ultra-clean!)
   ├── config/
   │ ├── **init**.py
   │ └── settings.py # All constants centralized
   ├── modules/
   │ ├── **init**.py
   │ ├── stripe_handler.py # (existing - unchanged)
   │ ├── persistent_user_manager.py # (existing - unchanged)
   │ ├── payment_ui.py # (existing - unchanged)
   │ ├── email_manager.py # (existing - unchanged)
   │ ├── data_handler.py # (existing - unchanged)
   │ └── analytics.py # NEW: Analysis logic
   ├── pages/
   │ ├── **init**.py
   │ ├── single_analysis.py # Tab 1 (~150 lines)
   │ ├── comparison.py # Tab 2 (~150 lines)
   │ └── pricing_info.py # Tab 3 (~100 lines)
   ├── components/
   │ ├── **init**.py
   │ ├── header.py # Header UI (~10 lines)
   │ ├── sidebar.py # Sidebar UI (~100 lines)
   │ └── footer.py # Footer UI (~15 lines)
   ├── utils/
   │ ├── **init**.py
   │ └── helpers.py # Helper functions (~80 lines)
   ├── .streamlit/
   │ └── config.toml # Streamlit config
   ├── requirements.txt
   └── README.md

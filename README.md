# Residential Electrification Dashboard

This project is an interactive dashboard that helps California residents simulate the financial and environmental impacts of residential electrification. It compares electricity rate plans (PG&E and CCAs), estimates long-term savings from solar and EV adoption, and models carbon emissions reduction.

## Features

- Rate plan comparisons across PG&E and major CCAs in the Bay Area
- Emissions and cost simulation for electrification scenarios
- Solar ROI modeling based on PV Watts data

## Files / Folders
- `app2.py` is the main python script containing dashboard components
- `make_zip.py` is a script used to generate a json file mapping zipcodes to available plans
- `data` folder contains all the data used in this project. `plan_details.csv` is where you update electricity rate information (price, power mix, etc). `zip_to_energy_plans.json` maps zipcode to available rates.

## Getting Started

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/residential-electrification-dashboard.git
cd residential-electrification-dashboard

# Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app2.py
```

## Potential Future Additions
- Precise calculation considering different tiers, subsidies, and seasonality
- Replacing PV Watts with paid services like Solar API for more granular solar simulation
- EV adoption simulation

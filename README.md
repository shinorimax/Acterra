# Residential Electrification Dashboard

The Residential Electrification Dashboard is an interactive tool that helps California residents simulate and compare the **financial** and **environmental** impacts of residential electrification. The dashboard models utility costs and carbon emissions for various electrification scenarios, compares PG\&E and Community Choice Aggregators (CCAs) rate plans, and estimates the return on investment (ROI) from solar adoption.

This dashboard aims to support household decision-making by providing accessible, localized insights into energy planning.

---

## Features

### Rate Plan Comparison

* Compare rates between **PG\&E** and **major Bay Area CCAs** (e.g., SVCE, EBCE, SJCE).
* Each plan includes information on price per kWh and the energy mix (renewable, nuclear, fossil).
* All plans use the **same delivery rate per kWh**, taken from PG\&E’s standard rate schedule. This simplifies comparison but is a limitation addressed in future development plans.

### Emissions Estimation

* Emissions per kWh are calculated based on the generation mix of each plan.
* Carbon intensity values are sourced from:

  * [COWI A/S](https://www.cowi.com/news-and-press/news/2023/comparing-co2-emissions-from-different-energy-sources)
  * [World Nuclear Association](https://world-nuclear.org/information-library/energy-and-the-environment/carbon-dioxide-emissions-from-electricity), referencing the IPCC.
* Note: These are **global average values**, not California-specific. Emission estimates are **approximate** and should be interpreted with caution, especially for hydro and biomass where data varies widely.

### Electrification Simulation

* Users can input:

  * **COP (Coefficient of Performance)** of electric systems.
  * **Efficiency** of gas furnaces and water heaters.
  * **Electrification percentage** to model partial transitions.
  * **Gas usage split** between furnace and water heater.
* The tool computes:

  * **Change in monthly energy cost** due to electrification.
  * **Change in annual carbon emissions**.

### Solar ROI Modeling

* Uses the **NREL PVWatts API** for location-specific solar output estimation.
* ZIP codes are converted to latitude/longitude using:

  ```python
  from geopy.geocoders import Nominatim
  ```
* Simulation compares **cumulative energy costs** with and without solar installation, incorporating system degradation and inflation.

---

## Assumptions and Methodology

### Electricity Rate Data

* The data in `plan_details.csv` is taken from the **latest Joint Rate Comparison documents** issued by PG\&E and affiliated CCAs.

  * Example: [SJCE Rate Comparison (PDF)](https://www.pge.com/assets/pge/docs/account/alternate-energy-providers/sjce-rcc.pdf)
* Delivery charges are fixed across all plans, though actual delivery rates vary by provider and location.

### Emissions Estimation

* CO₂e per kWh values (approximate):

  * Wind: 11 g
  * Solar PV: 45 g
  * Nuclear: 12 g
  * Hydropower: 4–18 g (varies greatly)
  * Biomass: 200–740 g
  * Natural Gas: 450–550 g
  * Coal: 900–1700 g
* Emissions are computed by weighted averaging the generation mix for each plan.

---

## Solar Savings Calculation

### Overview

We simulate cumulative household energy costs over a 20-year horizon both **with** and **without** solar installation.

### Variables:

* `monthly_kwh_usage`: monthly electricity consumption
* `price_per_kwh`: electricity price (plan-dependent)
* `actual_coverage`: % of load covered by solar system
* `up_front_cost`: cost of solar installation
* `solar_degradation`: annual degradation rate (0.5%)
* `electricity_inflation`: annual electricity price inflation (2.2%)
* `discount_rate`: consumer discount rate (4%)

### Solar Savings Calculation

We simulate cumulative household energy costs over a 20-year horizon **with** and **without** solar installation.

#### Annual Costs

The annual electricity cost **with** solar in year `i` is:

```
C_with(i) = 12 * monthly_kwh_usage * price_per_kwh *
            (1 - (actual_coverage / 100) * (0.995)^i) *
            (1.022 / 1.04)^i
```

The annual electricity cost **without** solar in year `i` is:

```
C_without(i) = 12 * monthly_kwh_usage * price_per_kwh *
               (1.022 / 1.04)^i
```

* `0.995^i` models the 0.5% annual degradation of the solar system.
* `(1.022 / 1.04)^i` adjusts for electricity price inflation (2.2%) and a consumer discount rate (4%).

#### Cumulative Costs

The cumulative cost over time is calculated iteratively:

```python
if i == 1:
    accum_cost_with = C_with(1) + up_front_cost
    accum_cost_without = C_without(1)
else:
    accum_cost_with = accum_cost_with_prev + C_with(i)
    accum_cost_without = accum_cost_without_prev + C_without(i)
```

This allows users to compare total cost with and without solar investment over time, incorporating upfront cost, degradation, inflation, and time value of money.

## File Structure

```bash
residential-electrification-dashboard/
├── app2.py                       # Main dashboard app (Dash)
├── make_zip.py                   # ZIP-to-rate-plan preprocessor
├── data/
│   ├── plan_details.csv          # Price and emissions data for all plans
│   └── zip_to_energy_plans.json # ZIP → eligible rate plans
├── requirements.txt              # Python dependencies
```

---

## Installation and Usage

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/residential-electrification-dashboard.git
cd residential-electrification-dashboard

# Set up environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run the app
python app2.py
```

---

## Future Improvements

* Incorporate **tiered electricity rates**, **TOU pricing**, and **seasonal rates** for more accurate billing.
* Estimate **delivery rate per address** instead of using a fixed average.
* Improve emissions calculations by collecting **California-specific lifecycle data** for each generation type.
* Add **EV adoption simulator**, including charging scenarios and marginal cost/emissions.
* Support downloadable **PDF reports** and historical trend visualizations.

---

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Configuration ---
START_DATE = datetime(2025, 6, 1)
END_DATE = datetime(2025, 6, 30)
N_DAYS = (END_DATE - START_DATE).days
MACHINES = ['Line 1', 'Line 2', 'Line 3']
PRODUCTS = {
    'PROD_A': {'ideal_rate_sph': 200, 'quality_target': 0.98},
    'PROD_B': {'ideal_rate_sph': 150, 'quality_target': 0.99},
    'PROD_C': {'ideal_rate_sph': 250, 'quality_target': 0.97}
}
DOWNTIME_REASONS = {
    'Planned Maintenance': 0.1,
    'Unplanned Machine Failure': 0.3,
    'Material Shortage': 0.2,
    'Operator Break': 0.3,
    'Changeover': 0.1
}

# --- Data Generation ---
data = []
current_date = START_DATE
for _ in range(N_DAYS):
    # 2 shifts per day, 8 hours each
    for shift in range(1, 3):
        shift_start_time = current_date + timedelta(hours=8 * (shift - 1))
        scheduled_production_minutes = 8 * 60 # 480 minutes

        for machine in MACHINES:
            # Simulate downtime for the shift
            total_downtime_minutes = np.random.randint(30, 90)
            downtime_events = np.random.choice(
                list(DOWNTIME_REASONS.keys()),
                size=np.random.randint(2, 5),
                p=list(DOWNTIME_REASONS.values())
            )
            
            # Calculate actual production time
            planned_downtime = sum(1 for r in downtime_events if r in ['Planned Maintenance', 'Operator Break', 'Changeover']) * np.random.randint(10,15)
            actual_production_minutes = scheduled_production_minutes - total_downtime_minutes
            
            # Select a product for the shift
            product_code = np.random.choice(list(PRODUCTS.keys()))
            product_info = PRODUCTS[product_code]
            
            # --- Calculate Performance and Quality ---
            # Performance loss (running slower than ideal)
            performance_loss_factor = np.random.uniform(0.85, 1.0)
            
            # Potential units during actual production time
            potential_units = (actual_production_minutes / 60) * product_info['ideal_rate_sph']
            
            # Actual units produced
            actual_units_produced = int(potential_units * performance_loss_factor)
            
            # Quality loss (defects)
            quality_loss_factor = np.random.uniform(product_info['quality_target'] - 0.05, 1.0)
            good_units = int(actual_units_produced * quality_loss_factor)
            defective_units = actual_units_produced - good_units

            data.append({
                'date': shift_start_time.date(),
                'shift': shift,
                'machine_id': machine,
                'product_code': product_code,
                'scheduled_time_mins': scheduled_production_minutes,
                'downtime_mins': total_downtime_minutes,
                'planned_downtime_mins': planned_downtime,
                'ideal_rate_sph': product_info['ideal_rate_sph'],
                'units_produced': actual_units_produced,
                'good_units': good_units,
                'defective_units': defective_units,
                'downtime_reasons': ', '.join(downtime_events)
            })
            
    current_date += timedelta(days=1)

df = pd.DataFrame(data)
# Save to CSV to simulate a real-world data source
df.to_csv('manufacturing_data.csv', index=False)
print("Generated manufacturing_data.csv with {} records.".format(len(df)))
print(df.head())

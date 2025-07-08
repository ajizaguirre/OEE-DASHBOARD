import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv('manufacturing_data.csv')

# --- OEE Calculation ---

# 1. Availability
# Availability = Run Time / Scheduled Time
# Run Time = Scheduled Time - All Downtime
df['run_time_mins'] = df['scheduled_time_mins'] - df['downtime_mins']
df['availability'] = df['run_time_mins'] / df['scheduled_time_mins']

# 2. Performance
# Performance = (Total Units Produced / Run Time) / Ideal Run Rate
df['actual_rate_spm'] = df['units_produced'] / df['run_time_mins']
df['ideal_rate_spm'] = df['ideal_rate_sph'] / 60
df['performance'] = df['actual_rate_spm'] / df['ideal_rate_spm']
# Handle cases where run_time is zero or performance exceeds 100%
df['performance'] = df['performance'].fillna(0).clip(0, 1)


# 3. Quality
# Quality = Good Units / Total Units Produced
df['quality'] = df['good_units'] / df['units_produced']
# Handle cases where no units were produced
df['quality'] = df['quality'].fillna(0)

# 4. Overall OEE
df['oee'] = df['availability'] * df['performance'] * df['quality']

print("OEE Calculation Complete. Average OEE: {:.2%}".format(df['oee'].mean()))

# --- Analysis & Visualization ---

# Set plot style
sns.set(style="whitegrid")

# 1. Overall OEE Performance
avg_oee_by_machine = df.groupby('machine_id')['oee'].mean().sort_values()
plt.figure(figsize=(10, 6))
sns.barplot(x=avg_oee_by_machine.index, y=avg_oee_by_machine.values, palette="viridis")
plt.title('Average OEE by Production Line', fontsize=16, fontweight='bold')
plt.ylabel('OEE Score')
plt.xlabel('Production Line')
plt.ylim(0, 1)
# Add percentage labels
for index, value in enumerate(avg_oee_by_machine.values):
    plt.text(index, value + 0.01, f'{value:.1%}', ha='center', va='bottom')
plt.show()


# 2. Breakdown of OEE Losses
loss_metrics = {
    'Availability Loss': 1 - df['availability'].mean(),
    'Performance Loss': 1 - df['performance'].mean(),
    'Quality Loss': 1 - df['quality'].mean()
}
loss_df = pd.DataFrame(list(loss_metrics.items()), columns=['Loss Type', 'Percentage'])
plt.figure(figsize=(10, 6))
sns.barplot(x='Percentage', y='Loss Type', data=loss_df.sort_values('Percentage', ascending=False), orient='h', palette='magma')
plt.title('Primary Sources of OEE Loss', fontsize=16, fontweight='bold')
plt.xlabel('Percentage of Total Loss')
plt.ylabel('')
plt.show()

# 3. Downtime Reason Analysis (Pareto Chart)
downtime_counts = df['downtime_reasons'].str.split(', ').explode().value_counts()
downtime_pareto = pd.DataFrame(downtime_counts)
downtime_pareto.columns = ['Count']
downtime_pareto = downtime_pareto.sort_values(by='Count', ascending=False)
downtime_pareto['Cumulative Percentage'] = downtime_pareto['Count'].cumsum() / downtime_pareto['Count'].sum() * 100

fig, ax1 = plt.subplots(figsize=(12, 7))
ax1.bar(downtime_pareto.index, downtime_pareto['Count'], color=sns.color_palette("rocket")[2])
ax1.set_ylabel('Number of Occurrences', color='darkred')
ax1.tick_params(axis='x', labelrotation=45)

ax2 = ax1.twinx()
ax2.plot(downtime_pareto.index, downtime_pareto['Cumulative Percentage'], color='navy', marker='o', ms=5)
ax2.set_ylabel('Cumulative Percentage (%)', color='navy')
ax2.set_ylim([0,110])

plt.title('Downtime Reason Analysis (Pareto Chart)', fontsize=16, fontweight='bold')
plt.show()
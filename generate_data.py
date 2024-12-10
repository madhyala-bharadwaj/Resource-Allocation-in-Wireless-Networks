import pandas as pd
import numpy as np
import random

# For reproducibility
np.random.seed(42)

NUM_SAMPLES = 10000
HOURS_IN_DAY = 24

# Timestamps
time_series = pd.date_range(start="2024-12-01 00:00:00", periods=NUM_SAMPLES, freq="s")

# Realistic user behavior with daily and weekly patterns
def generate_num_users(hour, day_of_week):
    base = 0
    # Weekday peak hours
    if 6 <= hour <= 9 or 18 <= hour <= 22:
        base = np.random.normal(900, 200) if day_of_week < 5 else np.random.normal(600, 150)
    # Weekday moderate usage
    elif 10 <= hour <= 17:
        base = np.random.normal(400, 100) if day_of_week < 5 else np.random.normal(300, 80)
    # Off-peak hours
    else:
        base = np.random.normal(100, 30)
    return max(0, int(base + np.random.normal(0, 30)))  # Add noise

num_users = [generate_num_users(ts.hour, ts.dayofweek) for ts in time_series]

# Average user demand with seasonal and noise variations
avg_user_demand = [
    3.0 + 1.0 * np.sin(2 * np.pi * ts.hour / HOURS_IN_DAY) +
    0.5 * np.cos(2 * np.pi * ts.dayofweek / 7) +
    np.random.normal(0, 0.7) for ts in time_series
]

# User mobility with context-specific variability
user_mobility = [
    max(0, min(1, 0.6 + 0.1 * np.sin(2 * np.pi * ts.hour / HOURS_IN_DAY) + np.random.normal(0, 0.15)))
    for ts in time_series
]

# Simulate available resources with periodicity and unexpected outages
available_resources = [
    max(5, 45 + 10 * np.sin(2 * np.pi * ts.hour / HOURS_IN_DAY) +
    np.random.normal(0, 7) - 15 * (ts.hour == 20 and ts.dayofweek == 5))  # Simulate outages on Friday evenings
    for ts in time_series
]

# Signal-to-Noise Ratio (SNR) with high noise during bad weather
snr = [
    max(5, 35 + np.random.normal(0, 6) + 5 * (1 - user_mobility[i]) - 10 * np.random.choice([0, 1], p=[0.9, 0.1]))
    for i in range(NUM_SAMPLES)
]

# Weather condition and its impact
weather_condition = [
    np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]) for _ in range(NUM_SAMPLES)
]

# Congestion level based on interdependencies
congestion_level = [
    min(1, max(0, 0.05 * (num_users[i] / 800) + 0.02 * avg_user_demand[i] + np.random.normal(0, 0.05)))
    for i in range(NUM_SAMPLES)
]

# Traffic type with dynamic distributions during events
traffic_type = [
    np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]) if i % 700 != 0 else np.random.choice([0, 1, 2], p=[0.2, 0.6, 0.2])
    for i in range(NUM_SAMPLES)
]

# QoS metrics with random fluctuations
qos_latency = [np.random.uniform(20, 300) + 10 * congestion_level[i] for i in range(NUM_SAMPLES)]
qos_throughput = [np.random.uniform(0.1, 10) - 0.1 * congestion_level[i] for i in range(NUM_SAMPLES)]

# Historical resource usage with noise
historical_resource_usage = []
for i in range(NUM_SAMPLES):
    if i < 10:
        historical_resource_usage.append(np.random.uniform(5, 15))
    else:
        avg_usage = np.mean(historical_resource_usage[i-10:i])
        historical_resource_usage.append(avg_usage + np.random.normal(-0.5, 0.7))

# Holiday indicator (1 = holiday, 0 = working day)
holiday_indicator = [1 if ts.weekday() in [5, 6] or ts.month == 12 else 0 for ts in time_series]

# Resource allocation logic with priority for high-demand traffic
resource_allocation = [
    max(0, min(available_resources[i], avg_user_demand[i] * num_users[i] / 100 * (1 - congestion_level[i])))
    for i in range(NUM_SAMPLES)
]

# Anomalies in resource allocation to simulate failures
for i in random.sample(range(NUM_SAMPLES), k=int(0.01 * NUM_SAMPLES)):
    resource_allocation[i] *= np.random.uniform(0.3, 0.7)

# Combine into a DataFrame
dataset = pd.DataFrame({
    "Time": time_series,
    "Num_Users": num_users,
    "Avg_User_Demand": avg_user_demand,
    "User_Mobility": user_mobility,
    "Available_Resources": available_resources,
    "SNR": snr,
    "Weather_Condition": weather_condition,
    "Congestion_Level": congestion_level,
    "Traffic_Type": traffic_type,
    "QoS_Latency": qos_latency,
    "QoS_Throughput": qos_throughput,
    "Historical_Resource_Usage": historical_resource_usage,
    "Holiday_Indicator": holiday_indicator,
    "Resource_Allocation": resource_allocation
})

# Dataset as a CSV file
output_path = "resource_allocation.csv"
dataset.to_csv(output_path, index=False)
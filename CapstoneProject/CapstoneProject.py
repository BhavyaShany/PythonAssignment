import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass

DATA = Path("data")
OUT = Path("output"); OUT.mkdir(exist_ok=True)


# Task 1: Load & Clean

def load_data():
    dfs = []
    for f in DATA.glob("*.csv"):
        try:
            df = pd.read_csv(f, on_bad_lines="skip")
        except:
            continue

        if "timestamp" not in df or "kwh" not in df: 
            continue

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)

        if "building" not in df:
            df["building"] = f.stem.split("_")[0]

        df["month"] = df["timestamp"].dt.to_period("M").astype(str)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True).sort_values("timestamp") if dfs else pd.DataFrame()

df = load_data()
if df.empty:
    print("No usable data found."); exit()


# Task 2: Aggregations

df_daily = df.set_index("timestamp").groupby("building").resample("D")["kwh"].sum().reset_index()
df_weekly = df.set_index("timestamp").groupby("building").resample("W")["kwh"].sum().reset_index()
df_summary = df.groupby("building")["kwh"].agg(total_kwh="sum", mean_kwh="mean", min_kwh="min", max_kwh="max").reset_index()


# Task 3: OOP Modeling

@dataclass
class MeterReading:
    timestamp: pd.Timestamp
    kwh: float

class Building:
    def __init__(self, name): 
        self.name, self.r = name, []

    def add(self, ts, kwh): 
        self.r.append(MeterReading(ts, float(kwh)))

    def total(self): 
        return sum(x.kwh for x in self.r)

class BuildingManager:
    def __init__(self): 
        self.b = {}

    def load(self, df):
        for _, r in df.iterrows():
            self.b.setdefault(r["building"], Building(r["building"])).add(r["timestamp"], r["kwh"])

    def top(self): 
        return max(self.b.values(), key=lambda x: x.total())

    def campus_total(self): 
        return sum(b.total() for b in self.b.values())

bm = BuildingManager(); bm.load(df)


# Task 4: Dashboard Plot

plt.figure(figsize=(10,14))

# Daily trend

plt.subplot(3,1,1)
for b, g in df_daily.groupby("building"):
    plt.plot(g["timestamp"], g["kwh"], label=b)
plt.title("Daily Consumption Over Time"); plt.legend()

# Weekly bar

plt.subplot(3,1,2)
avg_week = df_weekly.groupby("building")["kwh"].mean()
plt.bar(avg_week.index, avg_week.values)
plt.title("Average Weekly Usage")

# Peak scatter

plt.subplot(3,1,3)
peaks = df.loc[df.groupby("building")["kwh"].idxmax()]
plt.scatter(peaks["timestamp"], peaks["kwh"])
for _, r in peaks.iterrows():
    plt.annotate(r["building"], (r["timestamp"], r["kwh"]))
plt.title("Peak Load Times")

plt.tight_layout()
plt.savefig(OUT/"dashboard.png")
plt.close()


# Task 5: Save Outputs & Summary

df.to_csv(OUT/"cleaned_energy_data.csv", index=False)
df_summary.to_csv(OUT/"building_summary.csv", index=False)

peak = df.loc[df["kwh"].idxmax()]
summary = f"""
Campus Energy Summary

Total campus consumption: {bm.campus_total():,.2f} kWh
Highest-consuming building: {bm.top().name}

Peak load:
  Building: {peak['building']}
  Time: {peak['timestamp']}
  kWh: {peak['kwh']}

Daily and weekly trends included in dashboard.png
"""

with open(OUT/"summary.txt", "w") as f:
    f.write(summary)

print(summary)

import pandas as pd
import plotly.express as px
import json

print("Loading data...")

# load final dataset
df = pd.read_csv("data/cleaned/final_borough_dataset.csv")

# clean values
df["borough"] = df["borough"].astype(str).str.strip()
df["gp_access"] = pd.to_numeric(df["gp_access"], errors="coerce")
df["experience"] = pd.to_numeric(df["experience"], errors="coerce")
df["imd_score"] = pd.to_numeric(df["imd_score"], errors="coerce")

# remove bad values
df = df[(df["gp_access"] >= 0) & (df["gp_access"] <= 1)].copy()

# fix borough name mismatches if needed
df["borough"] = df["borough"].replace({
    "Hammersmith and Fulham": "Hammersmith & Fulham",
    "Kensington and Chelsea": "Kensington & Chelsea"
})

print(df["gp_access"].describe())

# load geojson
with open("data/raw/boroughs_london.geojson", "r") as f:
    geojson = json.load(f)

print("Creating map...")

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="borough",
    featureidkey="properties.name",
    color="gp_access",
    color_continuous_scale="Blues",
    range_color=(0.3, 0.55),
    title="GP Access Across London Boroughs",
    hover_name="borough",
    hover_data=["imd_score", "experience"]
)

fig.update_traces(
    marker_line_color="black",
    marker_line_width=0.8
)

fig.update_geos(
    fitbounds="locations",
    visible=False,
    bgcolor="white"
)

fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin={"r": 0, "t": 50, "l": 0, "b": 0}
)

fig.write_html("data/cleaned/gp_access_map.html")
fig.show()

print("Saved gp_access_map.html")
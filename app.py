import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import pearsonr

st.set_page_config(
    page_title="London GP Access Inequality Dashboard",
    layout="wide"
)

# load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned/final_borough_dataset.csv")

    # clean names
    df["borough"] = df["borough"].astype(str).str.strip()

    # convert to numbers
    df["gp_access"] = pd.to_numeric(df["gp_access"], errors="coerce")
    df["experience"] = pd.to_numeric(df["experience"], errors="coerce")
    df["imd_score"] = pd.to_numeric(df["imd_score"], errors="coerce")

    # these boroughs had missing GP access data after merging,
    # so don't treat their 0 values as real results
    df.loc[
        df["borough"].isin(["Croydon", "Greenwich", "Wandsworth"]),
        "gp_access"
    ] = pd.NA

    # keep values in range
    df["gp_access"] = df["gp_access"].clip(0, 1)
    df["experience"] = df["experience"].clip(0, 1)

    # fill missing experience only
    df["experience"] = df["experience"].fillna(0)

    return df


df = load_data()

# title
st.title("London GP Access Inequality Dashboard")

st.write("""
This dashboard explores how GP access varies across London boroughs.

It allows comparison of:
- GP access
- Patient experience
- Deprivation levels (IMD)

Use the filter on the left to explore patterns across different areas.
""")

# sidebar filter
st.sidebar.header("Filter")
st.sidebar.write("Select boroughs to compare:")

all_boroughs = sorted(df["borough"].unique())

selected_boroughs = st.sidebar.multiselect(
    "Boroughs:",
    options=all_boroughs,
    default=all_boroughs
)

st.sidebar.write(f"{len(selected_boroughs)} boroughs selected")

filtered_df = df[df["borough"].isin(selected_boroughs)].copy()

# remove missing gp access so they don't appear as fake zeros in charts
plot_df = filtered_df.dropna(subset=["gp_access"])

# summary
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Boroughs", len(filtered_df))
col2.metric("Avg GP Access", f"{plot_df['gp_access'].mean():.2f}")
col3.metric("Avg IMD", f"{filtered_df['imd_score'].mean():.1f}")

missing = filtered_df["gp_access"].isna().sum()
if missing > 0:
    st.warning(f"{missing} boroughs had missing GP access data and were left out of charts.")

# calculate correlation
r, p = pearsonr(plot_df["imd_score"], plot_df["gp_access"])

# scatter plot
st.subheader("Deprivation vs GP Access")

fig_scatter = px.scatter(
    plot_df,
    x="imd_score",
    y="gp_access",
    hover_name="borough",
    template="plotly_white",
    trendline="ols",
    trendline_color_override="red"
)

fig_scatter.update_layout(
    xaxis_title="IMD Score (higher = more deprived)",
    yaxis_title="GP Access",
    title=f"Deprivation vs GP Access (r = {r:.2f})"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.write("""

Each point represents a London borough.

Pearson’s correlation coefficient (r = -0.24) shows a weak negative relationship between deprivation and GP access. This means that as deprivation increases, GP access tends to decrease slightly. However, the relationship is weak, so deprivation alone does not fully explain differences in GP access across boroughs.""")

# gp access bar chart
st.subheader("GP Access by Borough")

fig_bar = px.bar(
    plot_df.sort_values("gp_access"),
    x="gp_access",
    y="borough",
    orientation="h",
    template="plotly_white"
)

st.plotly_chart(fig_bar, use_container_width=True)

st.write("""
This chart compares GP access across boroughs.

Higher values indicate better access to GP services. 
There is noticeable variation between boroughs, showing that access is not evenly distributed across London.
""")

# experience chart
st.subheader("Patient Experience by Borough")

fig_exp = px.bar(
    filtered_df.sort_values("experience"),
    x="experience",
    y="borough",
    orientation="h",
    template="plotly_white"
)

st.plotly_chart(fig_exp, use_container_width=True)

st.write("""
This chart shows patient experience across boroughs.

While some boroughs report higher satisfaction, differences are relatively small compared to GP access, suggesting experience is more consistent than access.
""")

# top and bottom
st.subheader("Top and Bottom Boroughs")

col4, col5 = st.columns(2)

top5 = plot_df.sort_values("gp_access", ascending=False)[
    ["borough", "gp_access", "imd_score"]
].head(5)

bottom5 = plot_df.sort_values("gp_access", ascending=True)[
    ["borough", "gp_access", "imd_score"]
].head(5)

with col4:
    st.write("Top 5 (GP access)")
    st.dataframe(top5, use_container_width=True)

with col5:
    st.write("Bottom 5 (GP access)")
    st.dataframe(bottom5, use_container_width=True)

st.write("""
These tables highlight the best and worst performing boroughs in terms of GP access.

This makes it easier to identify which areas may require further attention or improvement.
""")

# dataset table
st.subheader("Dataset")

display_df = filtered_df.copy()
display_df["gp_access"] = display_df["gp_access"].round(3)
display_df["experience"] = display_df["experience"].round(3)
display_df["imd_score"] = display_df["imd_score"].round(2)

st.dataframe(display_df, use_container_width=True)

# limitations
st.subheader("Limitations")

st.write("""
- Data is based on survey responses
- Borough averages may hide local variation
- Some GP access values were missing and not included in charts
- This shows patterns, not causes
""")
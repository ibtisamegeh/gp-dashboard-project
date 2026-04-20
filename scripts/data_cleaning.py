import pandas as pd

print("Loading datasets...")

# Load data
gp_df = pd.read_csv("data/raw/gp_data.csv")
lookup_df = pd.read_csv("data/raw/epraccur.csv", header=None)
postcode_df = pd.read_csv("data/raw/postcode_lookup.csv")
imd_df = pd.read_excel(
    "data/raw/File_10_-_IoD2019_Local_Authority_District_Summaries__lower-tier__ (1).xlsx",
    sheet_name="IMD"
)

# -------------------
# CLEAN GP DATA
# -------------------
print("Cleaning GP data...")

gp_small = gp_df[
    [
        "ad_practicecode",
        "ad_practicename",
        "ad_commissioningregionname",
        "gpcontactoverall_1.pct",
        "overallexp_1.pct",
        "popsize"
    ]
].copy()

# Filter London
london_gp = gp_small[
    gp_small["ad_commissioningregionname"].str.contains("LONDON", case=False, na=False)
].copy()

# -------------------
# CLEAN EPRACCUR
# -------------------
print("Cleaning epraccur...")

lookup_small = lookup_df[[0, 9]].copy()

lookup_small = lookup_small.rename(columns={
    0: "ad_practicecode",
    9: "postcode"
})

lookup_small["postcode"] = (
    lookup_small["postcode"]
    .astype(str)
    .str.upper()
    .str.replace(" ", "", regex=False)
)

# -------------------
# CLEAN POSTCODE LOOKUP
# -------------------
print("Cleaning postcode lookup...")

postcode_small = postcode_df[["pcds", "oslaua"]].copy()

postcode_small = postcode_small.rename(columns={
    "pcds": "postcode",
    "oslaua": "lad_code"
})

postcode_small["postcode"] = (
    postcode_small["postcode"]
    .astype(str)
    .str.upper()
    .str.replace(" ", "", regex=False)
)

# -------------------
# CLEAN IMD DATA
# -------------------
print("Cleaning IMD data...")

imd_small = imd_df[[
    "Local Authority District code (2019)",
    "Local Authority District name (2019)",
    "IMD - Average score "
]].copy()

imd_small = imd_small.rename(columns={
    "Local Authority District code (2019)": "lad_code",
    "Local Authority District name (2019)": "borough",
    "IMD - Average score ": "imd_score"
})

# Keep London only
london_boroughs = [
    "Camden", "Greenwich", "Hackney", "Hammersmith and Fulham",
    "Islington", "Kensington and Chelsea", "Lambeth", "Lewisham",
    "Southwark", "Tower Hamlets", "Wandsworth", "Westminster",
    "Barking and Dagenham", "Barnet", "Bexley", "Brent",
    "Bromley", "Croydon", "Ealing", "Enfield", "Haringey",
    "Harrow", "Havering", "Hillingdon", "Hounslow",
    "Kingston upon Thames", "Merton", "Newham",
    "Redbridge", "Richmond upon Thames", "Sutton", "Waltham Forest"
]

imd_london = imd_small[imd_small["borough"].isin(london_boroughs)].copy()

# -------------------
# MERGE DATA
# -------------------
print("Merging datasets...")

# GP → postcode
gp_postcode = pd.merge(
    london_gp,
    lookup_small,
    on="ad_practicecode",
    how="left"
)

# postcode → borough code
gp_borough_code = pd.merge(
    gp_postcode,
    postcode_small,
    on="postcode",
    how="left"
)

# -------------------
# AGGREGATE TO BOROUGH
# -------------------
print("Aggregating to borough level...")

gp_borough = gp_borough_code.groupby("lad_code")[
    ["gpcontactoverall_1.pct", "overallexp_1.pct"]
].mean().reset_index()

gp_borough = gp_borough.rename(columns={
    "gpcontactoverall_1.pct": "gp_access",
    "overallexp_1.pct": "experience"
})

# -------------------
# FINAL MERGE
# -------------------
final_df = pd.merge(
    gp_borough,
    imd_london,
    on="lad_code"
)

print("\nFinal dataset:")
print(final_df.head())
print("Shape:", final_df.shape)

# Save
final_df.to_csv("data/cleaned/final_borough_dataset.csv", index=False)

print("\nSaved final_borough_dataset.csv")
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# 1. Load your CSV data (using the endpoint you just tested)
@st.cache_data
def load_data():
  url = "https://environment.data.gov.uk/doc/bathing-water.csv?_pageSize=1000&_page=0"
  return pd.read_csv(url)


df = load_data()

st.title("🌊 UK Coastal Bathing Water Quality Risk Dashboard")
st.markdown("Interactive map tracking water quality classifications and sampling points.")

# 2. Filter out rows missing coordinates
df_map = df.dropna(
    subset=["sampling point > lat", "sampling point > long"]
).copy()

# 3. Create the Folium Map centered around the UK
m = folium.Map(location=[54.5, -3.0], zoom_start=6)


# 4. Function to color-code markers based on classification
def get_color(classification):
  if pd.isna(classification):
    return "gray"
  classification = str(classification).strip().lower()
  if "excellent" in classification or "good" in classification:
    return "green"
  elif "sufficient" in classification:
    return "orange"
  elif "poor" in classification:
    return "red"
  return "blue"


# 5. Add pins for each beach/sampling point
for _, row in df_map.iterrows():
  lat = row["sampling point > lat"]
  lon = row["sampling point > long"]
  name = row["name"]
  district = row["district"]
  classification = row["latest compliance assessment > compliance classification"]

  color = get_color(classification)

  popup_html = f"""
    <b>Beach:</b> {name}<br>
    <b>District:</b> {district}<br>
    <b>Classification:</b> {classification}
    """

  folium.CircleMarker(
      location=[lat, lon],
      radius=6,
      color=color,
      fill=True,
      fill_color=color,
      fill_opacity=0.7,
      popup=folium.Popup(popup_html, max_width=300),
  ).add_to(m)

# 6. Render map in Streamlit app
st_folium(m, width=700, height=500)
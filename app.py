import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="AgriShift - NASA Space Apps", page_icon="🌱", layout="wide")

# Header
st.title("🌱 Field Shift: NASA Data-Driven Crop Planner")
st.markdown("A Crop Rotation Planner for Sri Lanka's Dry Zone using NASA Environmental Data.")

# Sidebar Inputs
st.sidebar.header("Farm Details")
location_name = st.sidebar.selectbox("Select Location:", ["Anuradhapura", "Polonnaruwa", "Hambantota"])

# Coordinates dictionary for the selected regions
locations = {
    "Anuradhapura": {"lat": 8.3114, "lon": 80.4037},
    "Polonnaruwa": {"lat": 7.9403, "lon": 81.0188},
    "Hambantota": {"lat": 6.1248, "lon": 81.1185}
}
lat = locations[location_name]["lat"]
lon = locations[location_name]["lon"]

current_crop = st.sidebar.selectbox("Current Crop:", ["Rice", "Maize", "Vegetables"])
current_month = datetime.now().month

# Function to fetch NASA POWER API data
@st.cache_data
def fetch_nasa_data(lat, lon):
    # Parameters: T2M (Temperature), PRECTOTCORR (Precipitation), GWETTOP (Surface Soil Wetness)
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR,GWETTOP&community=AG&longitude={lon}&latitude={lat}&format=JSON"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['properties']['parameter']
    else:
        st.error("Error fetching data from NASA API!")
        return None

# Displaying Data
st.write("### 📡 NASA Satellite Data Analysis")
with st.spinner('Fetching NASA Climatology Data...'):
    nasa_data = fetch_nasa_data(lat, lon)

if nasa_data:
    # Extract current month data (formatting month to two digits, e.g., "07")
    month_key = f"{current_month:02d}"
    temp_now = nasa_data['T2M'][month_key]
    precip_now = nasa_data['PRECTOTCORR'][month_key]
    soil_moist_now = nasa_data['GWETTOP'][month_key]

    # Display Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="🌡️ Avg Temperature", value=f"{temp_now} °C")
    col2.metric(label="🌧️ Precipitation", value=f"{precip_now} mm/day")
    col3.metric(label="💧 Soil Wetness Index", value=f"{soil_moist_now}")

    # Plot Annual Climatology Trends
    st.write("#### Annual Precipitation & Temperature Trends")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    temp_data = [nasa_data['T2M'][f"{i:02d}"] for i in range(1, 13)]
    precip_data = [nasa_data['PRECTOTCORR'][f"{i:02d}"] for i in range(1, 13)]
    
    df_chart = pd.DataFrame({"Month": months, "Temperature (°C)": temp_data, "Precipitation (mm)": precip_data})
    fig = px.line(df_chart, x="Month", y=["Temperature (°C)", "Precipitation (mm)"], markers=True, title="NASA Climatology Data (Historical Averages)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Crop Rotation Decision Logic
    st.write(f"### 💡 Crop Rotation Strategies for {location_name}")
    
    # Determining Season (Maha season is roughly Sept to March)
    is_maha_season = current_month in [9, 10, 11, 12, 1, 2, 3]
    
    if is_maha_season and precip_now > 3.0:
        st.success("✅ **Primary Recommendation: Rice**")
        st.write("**Reasoning:** NASA data indicates high precipitation and soil moisture, characteristic of the Maha season. Ideal conditions for water-intensive crops.")
        
        st.info("🔄 **Rotation Plan:** Plan to plant Mung Beans or Cowpea in the upcoming Yala season to restore soil nitrogen levels.")
        
    elif not is_maha_season and soil_moist_now < 0.5:
        st.warning("⚠️ **Primary Recommendation: Mung Beans / Cowpea**")
        st.write(f"**Reasoning:** NASA data shows low surface soil moisture (Index: {soil_moist_now}) and lower rainfall. There is a higher risk of drought conditions.")
        
        st.write("🌟 **Benefits:** These crops are drought-tolerant and nitrogen-fixing, meaning they will naturally fertilize the soil.")
        if current_crop == "Rice":
            st.write("Since you previously planted Rice, this is the perfect rotation to replenish soil nutrients without requiring heavy irrigation.")
            
    else:
        st.info("🌽 **Primary Recommendation: Maize / Vegetables**")
        st.write("**Reasoning:** Soil moisture and temperatures are currently at moderate levels. This is a solid window for short-term, high-yield crops.")

    st.markdown("---")
    st.caption("Developed by Team [Your Team Name] - NASA Space Apps Challenge 2026")

#Streamlit Interactive Weather Dashboard


import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import os
from pathlib import Path

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Global Weather Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Weather Dashboard")
st.markdown("### Real-time Weather Insights from Around the World")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ====================== CHECK  ======================
#st.write("Current working directory:", os.getcwd())
#st.write("Database path:", Path("data/weather_database.db").resolve())
#st.write("Database exists:", Path("data/weather_database.db").exists())
# ====================== LOAD DATA FROM DATABASE ======================
@st.cache_data
# def load_data():
#     conn = sqlite3.connect('data/weather_database.db')
#     df = pd.read_sql_query("SELECT * FROM weather", conn)
#     conn.close()
#     return df
def load_data():
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "weather_database.db"

    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    conn.close()

    return df

df = load_data()

if df.empty:
    st.error("No data found in database. Please run the scraping and cleaning scripts first.")
    st.stop()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("Filters")

# City filter
selected_cities = st.sidebar.multiselect(
    "Select Cities",
    options=df['City'].unique(),
    default=df['City'].unique()[:10]
)

# Hemisphere filter
hemisphere = st.sidebar.radio("Hemisphere", ["All", "Northern", "Southern"])

# Temperature range
min_temp = float(df['Temperature'].min())
max_temp = float(df['Temperature'].max())
temp_range = st.sidebar.slider(
    "Temperature Range (°F)",
    min_value=min_temp,
    max_value=max_temp,
    value=(min_temp, max_temp)
)

# ====================== APPLY FILTERS ======================
filtered_df = df[df['City'].isin(selected_cities)]

if hemisphere != "All":
    filtered_df = filtered_df[filtered_df['Hemisphere'] == hemisphere]

filtered_df = filtered_df[
    (filtered_df['Temperature'] >= temp_range[0]) & 
    (filtered_df['Temperature'] <= temp_range[1])
]

# ====================== MAIN DASHBOARD ======================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Cities", len(filtered_df))
with col2:
    st.metric("Average Temperature", f"{filtered_df['Temperature'].mean():.1f}°F")
with col3:
    st.metric("Hottest City", filtered_df.loc[filtered_df['Temperature'].idxmax(), 'City'])

# Visualization 1: Temperature by City
st.subheader("1. Temperature by City")
fig1 = px.bar(
    filtered_df.sort_values('Temperature', ascending=False),
    x='City',
    y='Temperature',
    color='Hemisphere',
    title="Current Temperatures",
    labels={'Temperature': 'Temperature (°F)'}
)
st.plotly_chart(fig1, use_container_width=True)

# Visualization 2: Weather Conditions
st.subheader("2. Weather Conditions Distribution")
fig2 = px.pie(
    filtered_df,
    names='Condition',
    title="Distribution of Weather Conditions"
)
st.plotly_chart(fig2, use_container_width=True)

# Visualization 3: Temperature vs Local Time (Scatter)
st.subheader("3. Temperature Distribution")
fig3 = px.box(
    filtered_df,
    x='Hemisphere',
    y='Temperature',
    color='Hemisphere',
    title="Temperature Distribution by Hemisphere"
)
st.plotly_chart(fig3, use_container_width=True)

# Raw Data Table
with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)

st.caption("Data scraped from timeanddate.com • Educational Capstone Project")
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set the title of the dashboard
st.title("Simple Streamlit Dashboard")

# Sidebar for user input
st.sidebar.header("User Input")
num_points = st.sidebar.slider("Number of points", min_value=10, max_value=1000, value=100)

# Display text
st.write("This dashboard generates random data based on user input")

# Create random data based on user input
data = pd.DataFrame({
    'x': np.random.randn(num_points),
    'y': np.random.randn(num_points)
})

# Line Chart
st.subheader("Line Chart")
st.line_chart(data)

# Histogram
st.subheader("Histogram")
fig, ax = plt.subplots()
ax.hist(data['x'], bins=20, alpha=0.7, label='x', color='blue')
ax.hist(data['y'], bins=20, alpha=0.7, label='y', color='green')
ax.legend()
st.pyplot(fig)

# Data Table
st.subheader("Data Table")
st.dataframe(data)

# Show a map with random lat/long points (for geographic data example)
st.subheader("Map with Random Coordinates")
map_data = pd.DataFrame(
    np.random.randn(num_points, 2) / [50, 50] + [37.76, -122.4],  # Random coordinates near San Francisco
    columns=['lat', 'lon']
)
st.map(map_data)

# User-Interactive Area: Input text
user_text = st.text_input("Enter some text", "Streamlit is awesome!")
st.write(f"You entered: {user_text}")

# Button
if st.button("Click Me"):
    st.write("Button clicked!")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    file_data = pd.read_csv(uploaded_file)
    st.write(file_data)




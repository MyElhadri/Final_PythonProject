import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.animation as animation
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display

# Color mapping for weather conditions
WEATHER_COLORS = {
    "Sunny": "#FFD700",   # Gold
    "Rainy": "#4682B4",   # Steel Blue
    "Cloudy": "#A9A9A9",   # Dark Gray
    "Windy": "#00CED1",   # Dark Turquoise
    "Snowy": "#ADD8E6",   # Light Blue
    "Stormy": "#800080",   # Purple
}
DEFAULT_COLOR = "#FFFFFF"


def load_weather_data():
    """
    Loads and preprocesses your weather dataset.
    Adjust the CSV path and date format as needed.
    """
    df = pd.read_csv("data_visualizations/weather_data.csv", skipinitialspace=True)
    # Clean column names
    df.columns = df.columns.str.strip()
    df.rename(columns={"Humidity (%)": "Humidity"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", dayfirst=True)
    df.set_index("Date", inplace=True)

    # Map weather condition to color (if the column exists)
    df["Color"] = df.get("Weather Condition", pd.Series(["Unknown"] * len(df))).map(WEATHER_COLORS)
    df["Color"].fillna(DEFAULT_COLOR, inplace=True)

    return df


def create_swirl_chart(df, output_path):
    """
    Creates a static swirling, polar weather chart:
    - Angles represent each day (or row).
    - Radius = Temperature (with offset if needed)
    - Dot size = Wind Speed
    - Dot color = based on Humidity (using a colormap)
    """
    df = df.sort_index()
    n = len(df)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

    # Temperature as the radius; adjust if negative
    radius = df["Temperature"].values
    offset = abs(min(radius)) + 2 if min(radius) < 0 else 0
    radius = radius + offset

    # Normalize Humidity for the colormap
    humidity = df["Humidity"].values
    cmap = plt.cm.get_cmap("Spectral")
    hum_min, hum_max = humidity.min(), humidity.max()
    hum_norm = (humidity - hum_min) / (hum_max - hum_min + 1e-9)

    # Dot size from Wind Speed (km/h)
    wind = df["Wind Speed (km/h)"].values
    size = wind * 2  # adjust scaling as needed

    fig = plt.figure(figsize=(8, 8), facecolor="black")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("black")
    ax.grid(False)

    # Scatter plot on polar coordinates
    ax.scatter(
        angles,
        radius,
        c=[cmap(h) for h in hum_norm],
        s=size,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5
    )
    # Connect points with a line (optional)
    ax.plot(angles, radius, color="white", alpha=0.3, linestyle="--")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("🌪️ Swirling Weather Spiral", color="gold", fontsize=16, pad=20)

    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor())
    plt.close()


def create_interactive_swirl_chart(df):
    """
    Creates an interactive swirling weather chart using Plotly.
    - Hovering shows Temperature, Humidity, and Wind Speed.
    - The chart is displayed in a polar coordinate system.
    """
    df = df.sort_index()
    n = len(df)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # Convert angles to degrees (Plotly uses degrees for polar plots)
    angles_degrees = np.degrees(angles)
    radius = df["Temperature"].values
    offset = abs(min(radius)) + 2 if min(radius) < 0 else 0
    radius = radius + offset

    # Add computed polar coordinates to the dataframe
    df_interactive = df.copy()
    df_interactive['Angle'] = angles_degrees
    df_interactive['Radius'] = radius

    fig = px.scatter_polar(
        df_interactive,
        r='Radius',
        theta='Angle',
        size="Wind Speed (km/h)",
        color="Humidity",  # color by humidity
        color_continuous_scale="Spectral",
        hover_data=["Temperature", "Humidity", "Wind Speed (km/h)"],
        title="🌪️ Interactive Swirling Weather Spiral",
        template="plotly_dark"
    )
    fig.show()


def animate_swirl_chart(df, output_gif):
    """
    Creates an animated swirling weather chart using matplotlib.animation.
    Each frame adds a new data point to create a dynamic swirl.
    """
    df = df.sort_index()
    n = len(df)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radius = df["Temperature"].values
    offset = abs(min(radius)) + 2 if min(radius) < 0 else 0
    radius = radius + offset
    humidity = df["Humidity"].values
    wind = df["Wind Speed (km/h)"].values
    size = wind * 2

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_facecolor("black")
    ax.set_xticks([])
    ax.set_yticks([])

    def update(frame):
        ax.clear()
        ax.set_facecolor("black")
        ax.set_xticks([])
        ax.set_yticks([])
        # Scatter plot for data points up to the current frame
        ax.scatter(
            angles[:frame],
            radius[:frame],
            c=humidity[:frame],
            s=size[:frame],
            cmap="Spectral",
            alpha=0.8,
            edgecolor="white",
            linewidth=0.5
        )
        # Connect points with a line
        ax.plot(angles[:frame], radius[:frame], color="white", alpha=0.3, linestyle="--")
        ax.set_title("🌪️ Animated Swirling Weather Spiral", color="gold", fontsize=16, pad=20)
        return ax,

    ani = animation.FuncAnimation(fig, update, frames=n, interval=50, repeat=False)
    ani.save(output_gif, writer="pillow", fps=20)
    plt.close()


def filter_weather(df, weather_condition):
    """
    Filters the dataframe by a specified weather condition.
    """
    return df[df["Weather Condition"] == weather_condition]


def interactive_filter(df):
    """
    Creates an interactive dropdown widget (for Jupyter Notebook)
    to filter the weather data by condition and displays the interactive Plotly swirl chart.
    """
    conditions = df["Weather Condition"].unique()
    weather_dropdown = widgets.Dropdown(
        options=conditions,
        description="Weather:",
    )

    def on_change(change):
        if change['type'] == 'change' and change['name'] == 'value':
            filtered_df = filter_weather(df, change["new"])
            create_interactive_swirl_chart(filtered_df)

    weather_dropdown.observe(on_change, names="value")
    display(weather_dropdown)


if __name__ == "__main__":
    # Load data
    df = load_weather_data()

    # Create and save the static swirl chart
    create_swirl_chart(df, "swirl_chart.png")

    # Display the interactive Plotly swirl chart
    create_interactive_swirl_chart(df)

    # Create and save the animated swirl chart as a GIF
    animate_swirl_chart(df, "animated_swirl.gif")

    # Enable interactive filtering (run this cell in a Jupyter Notebook)
    interactive_filter(df)

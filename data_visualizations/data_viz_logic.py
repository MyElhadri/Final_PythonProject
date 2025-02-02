import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

WEATHER_COLORS = {
    "Sunny": "#FFD700",  # Gold
    "Rainy": "#4682B4",  # Steel Blue
    "Cloudy": "#A9A9A9",  # Dark Gray
    "Windy": "#00CED1",  # Dark Turquoise
    "Snowy": "#ADD8E6",  # Light Blue
    "Stormy": "#800080",  # Purple
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

    # Map weather condition to color (some columns might not exist)
    df["Color"] = df.get("Weather Condition", pd.Series(["Unknown"] * len(df))).map(WEATHER_COLORS)
    df["Color"].fillna(DEFAULT_COLOR, inplace=True)

    return df


def create_swirl_chart(df, output_path):
    """
    Creates a swirling, polar weather chart:
    - Angles represent each day (or row).
    - Radius = Temperature
    - Dot size = Wind Speed
    - Dot color = humidity-based or Weather Condition
    """

    # Sort by date if needed to ensure chronological swirl
    df = df.sort_index()

    # For N data points, generate angles from 0 to 2π
    n = len(df)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

    # Let's pick Temperature as the radius
    radius = df["Temperature"].values

    # If radius has negative values, offset to ensure positivity
    offset = abs(min(radius)) + 2 if min(radius) < 0 else 0
    radius = radius + offset

    # We'll color by Humidity to get a range
    # Optionally normalize humidity for a colormap
    humidity = df["Humidity"].values
    cmap = plt.cm.get_cmap("Spectral")  # or "rainbow", "viridis", etc.
    # Normalize humidity to 0..1 for colormap
    hum_min, hum_max = humidity.min(), humidity.max()
    hum_norm = (humidity - hum_min) / (hum_max - hum_min + 1e-9)  # tiny offset to avoid div-by-zero

    # Dot size from Wind Speed (km/h)
    wind = df["Wind Speed (km/h)"].values
    size = wind * 2  # scale up as needed

    fig = plt.figure(figsize=(8, 8), facecolor="black")
    ax = fig.add_subplot(111, polar=True)  # polar subplot

    ax.set_facecolor("black")
    ax.grid(False)  # remove default polar grid lines

    # Create the scatter points on polar coords
    sc = ax.scatter(
        angles,    # angle for each point
        radius,    # radius for each point
        c=[cmap(h) for h in hum_norm],  # map humidity to color
        s=size,    # wind speed => dot size
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5
    )

    # Optionally, draw a swirl/line connecting points in order
    ax.plot(angles, radius, color="white", alpha=0.3, linestyle="--")

    # Let's hide radial ticks, or style them
    ax.set_xticks([])
    ax.set_yticks([])

    # Title, with maybe the swirl theme
    ax.set_title("🌪️ Swirling Weather Spiral", color="gold", fontsize=16, pad=20)

    # Save the figure
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor())
    plt.close()

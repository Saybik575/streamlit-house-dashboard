import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Use the original file name you uploaded
FILE_NAME = 'Bengaluru_House_Data.csv'

# --- 1. Load and Clean Data ---
@st.cache_data # Caches the data loading for fast performance
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Simple Cleaning Function for total_sqft
    def clean_sqft(x):
        try:
            # Handle ranges (e.g., '1000 - 1200') by taking the average
            if isinstance(x, str) and '-' in x:
                parts = [float(p.strip()) for p in x.split('-')]
                return np.mean(parts)
            # Convert simple strings/numbers, ignore complex units like 'Sq. Meter'
            return float(str(x).split(' ')[0])
        except:
            return np.nan # Set failed conversions to NaN

    df['total_sqft'] = df['total_sqft'].apply(clean_sqft)

    # Derive BHK from 'size'
    df.dropna(subset=['size'], inplace=True)
    df['BHK'] = df['size'].apply(lambda x: int(x.split(' ')[0]) if isinstance(x, str) and (('BHK' in x) or ('Bedroom' in x)) else np.nan)

    # Final cleanup of critical columns
    df.dropna(subset=['BHK', 'total_sqft', 'price', 'location'], inplace=True)

    # Calculate price per sqft (Price is in Lakhs)
    df['price_per_sqft'] = (df['price'] * 100000) / df['total_sqft']

    # Filter out outliers for better visualization (e.g., BHK < 10)
    df = df[df['BHK'] < 10]
    return df

df_clean = load_data(FILE_NAME)

# --- 2. Streamlit App Layout ---
st.title('🏠 Bengaluru Housing Data Dashboard')
st.sidebar.header('Visualization Selector')
selected_plot = st.sidebar.selectbox('Select a Plot Type', [
    '1. Price Distribution',
    '2. Price vs. Size (BHK)',
    '3. Top 10 Locations by Count',
    '4. Price vs. Square Footage',
    '5. Area Type Distribution'
])

# --- 3. Plotting Functions (5 Simple Graphs) ---

def plot_1_price_distribution():
    st.header('1. Property Price Distribution (Lakhs)')
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df_clean['price'], bins=30, kde=True, ax=ax, color='skyblue')
    ax.set_xlabel('Price (Lakhs)')
    st.pyplot(fig)

def plot_2_bhk_vs_price():
    st.header('2. Price vs. Number of Bedrooms (BHK)')
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x='BHK', y='price', data=df_clean, ax=ax, palette='viridis')
    ax.set_xlabel('BHK')
    ax.set_ylabel('Price (Lakhs)')
    st.pyplot(fig)

def plot_3_top_locations():
    st.header('3. Top 10 Locations by Property Count')
    top_locations = df_clean['location'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_locations.index, y=top_locations.values, ax=ax, palette='magma')
    ax.set_ylabel('Number of Properties')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

def plot_4_scatter_sqft_price():
    st.header('4. Total Square Footage vs. Price')
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_clean['total_sqft'], df_clean['price'], alpha=0.6, color='coral')
    ax.set_xlabel('Total Sqft')
    ax.set_ylabel('Price (Lakhs)')
    ax.set_xlim(0, 5000) # Set limit for better view
    ax.set_ylim(0, 1000)
    st.pyplot(fig)

def plot_5_area_type_distribution():
    st.header('5. Area Type Distribution')
    area_counts = df_clean['area_type'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = sns.color_palette('pastel')[0:len(area_counts)]
    ax.pie(area_counts, labels=area_counts.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'}, colors=colors)
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# --- 4. Display Selected Plot ---
if selected_plot.startswith('1'):
    plot_1_price_distribution()
elif selected_plot.startswith('2'):
    plot_2_bhk_vs_price()
elif selected_plot.startswith('3'):
    plot_3_top_locations()
elif selected_plot.startswith('4'):
    plot_4_scatter_sqft_price()
elif selected_plot.startswith('5'):
    plot_5_area_type_distribution()

# Optional: Show a snippet of the data
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data Snippet')
    st.write(df_clean.head())
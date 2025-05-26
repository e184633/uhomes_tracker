import streamlit as st
import pandas as pd
import re # For cleaning price and amenities
import json
import plotly.express as px
# --- Page Configuration ---
st.set_page_config(
    page_title="uHomes London Listings",
    page_icon="🏠",
    layout="wide" # Use the full width of the page
)

# --- Data Loading & Cleaning Functions ---
@st.cache_data # Cache the data loading for performance
def load_data(filepath='uhomes_data.json'):
    """Loads scraped data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df
    except FileNotFoundError:
        st.error(f"Error: The data file '{filepath}' was not found.")
        st.warning("Please run your scraper first to generate the uhomes_data.json file.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

def clean_price(price_str):
    """Extracts numbers from the price string."""
    if not isinstance(price_str, str):
        return None
    match = re.search(r'£?([\d,]+)', price_str)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

# *** NEW: Function to clean amenities ***
def clean_amenities(amenities_list):
    """Removes leading icon characters and strips amenities."""
    if not isinstance(amenities_list, list):
        return amenities_list
    cleaned = []
    for amenity in amenities_list:
        # This regex removes one or more non-alphanumeric characters
        # (excluding spaces and £) from the beginning of the string.
        cleaned_text = re.sub(r'^[^\w\s£]+', '', str(amenity)).strip()
        if cleaned_text: # Only add if something remains
            cleaned.append(cleaned_text)
    return cleaned
# *** End of New Function ***

# --- Load and Process Data ---
df_raw = load_data()

# --- Main Dashboard ---
st.title("🏠 uHomes London Accommodation Dashboard")
st.markdown("Visualizing scraped accommodation data for London from uhomes.com")

if df_raw is not None:
    # --- Data Cleaning ---
    df = df_raw.copy()
    df['price_numeric'] = df['price_per_week'].apply(clean_price)
    df['amenities'] = df['amenities'].apply(clean_amenities) # <-- Apply amenity cleaning
    df_clean = df.dropna(subset=['price_numeric']).copy()
    df_clean['price_numeric'] = df_clean['price_numeric'].astype(int)

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Listings")
    search_term = st.sidebar.text_input("Search by Name or Address:", "")
    min_price = int(df_clean['price_numeric'].min())
    max_price = int(df_clean['price_numeric'].max())
    price_range = st.sidebar.slider(
        "Price per Week (£):",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

    # Filter data
    df_filtered = df_clean[
        (df_clean['price_numeric'] >= price_range[0]) &
        (df_clean['price_numeric'] <= price_range[1]) &
        (
            df_clean['name'].str.contains(search_term, case=False, na=False) |
            df_clean['address'].str.contains(search_term, case=False, na=False)
        )
    ]

    # --- Display Metrics ---
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Listings Scraped", len(df))
    col2.metric("Listings Displayed", len(df_filtered))
    if not df_filtered.empty:
        col3.metric("Average Price (£/week)", f"{df_filtered['price_numeric'].mean():.0f}")
    else:
        col3.metric("Average Price (£/week)", "N/A")



# --- Display Data Table & Price Histogram (NEW LAYOUT) ---
st.subheader("Filtered Listings & Price Distribution")

# Create two columns: Make the table wider (2/3) than the chart (1/3)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### Listings Details")
    st.data_editor(
        df_filtered[['name', 'address', 'price_per_week', 'amenities', 'link']],
        column_config={
            "link": st.column_config.LinkColumn(
                "Listing URL",
                help="Click to open the listing on uhomes.com",
                display_text="View Details"
            )
        },
        hide_index=True,
        use_container_width=True,
        disabled=True,
        height=500 # You can adjust the height if needed
    )

with col2:
    st.markdown("##### Price Histogram (£/week)")
    if not df_filtered.empty:
        # Create an interactive histogram using Plotly Express
        fig = px.histogram(
            df_filtered,
            x="price_numeric",
            nbins=15, # Adjust number of bins for desired granularity
            labels={'price_numeric': 'Price per Week (£)'},
            color_discrete_sequence=['#FF9234'] # Optional: Use a color like uhomes'
        )

        # Update layout for a cleaner look (optional)
        fig.update_layout(
            yaxis_title="Number of Listings",
            bargap=0.1,
            margin=dict(l=20, r=20, t=20, b=20), # Tweak margins
            height=500 # Match table height
        )

        # Display the Plotly chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to plot.")

# --- REMOVE the old st.subheader and st.bar_chart code here ---
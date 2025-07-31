import streamlit as st
import google.generativeai as genai
import folium
from streamlit.components.v1 import html
from geopy.geocoders import Nominatim
import os
import requests

# ========== CONFIG ==========
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
FREECURRENCY_API_KEY = st.secrets["FREECURRENCY_API_KEY"]

# ========== STYLING ==========
def inject_custom_css():
    st.markdown("""
    <style>
        html, body {
            background-color: #1c1f26;
        }
        .main-title {
            font-size: 38px;
            text-align: center;
            font-weight: bold;
            color: #00B4D8;
            margin-bottom: 30px;
        }
        .left-panel, .right-panel {
            background-color: #2c303a;
            padding: 25px;
            border-radius: 18px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
        }
        .section-header {
            font-size: 20px;
            font-weight: bold;
            margin: 15px 0 10px;
            color: #ffffff;
        }
        .stTextInput input, .stDateInput input, .stNumberInput input {
            background-color: #1e222b !important;
            color: white !important;
            border-radius: 10px !important;
        }
        .stMultiSelect > div {
            background-color: #1e222b !important;
            border-radius: 10px !important;
            color: white !important;
        }
        .stButton button {
            background-color: #00B4D8 !important;
            color: white !important;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            border-radius: 12px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# ========== GEMINI AI ==========
def plan_trip(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# ========== MAP ==========
def get_map_html(city):
    try:
        geolocator = Nominatim(user_agent="travel_app")
        location = geolocator.geocode(city)
        if location:
            fmap = folium.Map(location=[location.latitude, location.longitude], zoom_start=12)
            folium.Marker([location.latitude, location.longitude], tooltip=city).add_to(fmap)
            return fmap._repr_html_()
        else:
            return "<p>Map not found.</p>"
    except:
        return "<p>Map error.</p>"

# ========== CURRENCY ==========
def get_exchange_rate(to_currency="USD"):
    try:
        url = f"https://api.freecurrencyapi.com/v1/latest?apikey={FREECURRENCY_API_KEY}&base_currency=INR"
        res = requests.get(url).json()
        return res['data'].get(to_currency.upper())
    except:
        return None

# ========== MAIN ==========
def main():
    st.set_page_config(layout="wide", page_title="Travel Concierge AI", page_icon="🌍")
    inject_custom_css()

    st.markdown('<div class="main-title">🌍 Travel Concierge AI: Your Personal Travel Assistant</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 2.2])

    with col1:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)

        city_for_left = st.session_state.get("city_input", "Tokyo")
        dest_currency = "JPY" if "tokyo" in city_for_left.lower() else "USD"
        rate = get_exchange_rate(dest_currency)

        st.markdown('<div class="section-header">💱 Currency Exchange</div>', unsafe_allow_html=True)
        if rate:
            st.success(f"1 INR = {rate:.2f} {dest_currency}")
        else:
            st.warning("Currency rate not available.")

        st.markdown('<div class="section-header">🗺️ Destination Map</div>', unsafe_allow_html=True)
        map_html = get_map_html(city_for_left)
        html(map_html, height=300)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">✈️ Trip Planner</div>', unsafe_allow_html=True)
        city = st.text_input("🌆 Destination City", "Tokyo", key="city_input")
        from_date = st.date_input("📆 From Date")
        to_date = st.date_input("📆 To Date")
        budget = st.number_input("💸 Budget (INR)", min_value=1000)
        preferences = st.multiselect("🎯 Interests", ["Food", "Beaches", "Museums", "Nature", "Nightlife", "Shopping"])
        from_city = st.text_input("🛫 Starting City", "Mumbai")

        if st.button("✨ Generate Itinerary"):
            prompt = f"Plan a trip from {from_city} to {city} from {from_date} to {to_date}. Budget: ₹{budget}. Interests: {', '.join(preferences)}."
            with st.spinner("🤖 Generating your trip plan..."):
                result = plan_trip(prompt)
            st.markdown('<div class="section-header">📖 Your Itinerary</div>', unsafe_allow_html=True)
            st.success(result)

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

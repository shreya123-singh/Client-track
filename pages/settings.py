import streamlit as st
from database.db import fetch_data, execute_query


def show_settings():

    st.title("⚙️ Settings")
    st.write("Manage your ClientTrack application preferences.")
    st.markdown("---")

    # Create settings table if it does not exist
    execute_query("""
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )
    """)

    def get_setting(key, default):
        result = fetch_data(
            "SELECT setting_value FROM app_settings WHERE setting_key=?",
            (key,)
        )
        return result[0]["setting_value"] if result else default

    st.subheader("🏢 Company Information")

    company_name = st.text_input(
        "Company Name",
        value=get_setting("company_name", "ClientTrack")
    )

    email = st.text_input(
        "Contact Email",
        value=get_setting("contact_email", "")
    )

    st.markdown("---")
    st.subheader("🌐 Application Preferences")

    currency_options = ["INR (₹)", "USD ($)", "EUR (€)"]

    saved_currency = get_setting("currency", "INR (₹)")

    currency = st.selectbox(
        "Currency",
        currency_options,
        index=currency_options.index(saved_currency)
        if saved_currency in currency_options else 0
    )

    date_options = ["DD-MM-YYYY", "MM-DD-YYYY", "YYYY-MM-DD"]

    saved_date = get_setting("date_format", "DD-MM-YYYY")

    date_format = st.selectbox(
        "Date Format",
        date_options,
        index=date_options.index(saved_date)
        if saved_date in date_options else 0
    )

    st.markdown("---")

    if st.button("💾 Save Settings"):

        if company_name.strip():

            settings = {
                "company_name": company_name.strip(),
                "contact_email": email.strip(),
                "currency": currency,
                "date_format": date_format
            }

            for key, value in settings.items():

                execute_query("""
                    INSERT OR REPLACE INTO app_settings
                    (setting_key, setting_value)
                    VALUES (?, ?)
                """, (key, value))

            st.success("Settings saved successfully!")

        else:
            st.error("Company name cannot be empty.")

    st.markdown("---")
    st.subheader("ℹ️ Application Information")

    st.write("**Application:** ClientTrack")
    st.write("**Purpose:** Client and Project Management")
    st.write("**Technology:** Python, Streamlit, SQLite")
    st.write("**Database:** SQLite")
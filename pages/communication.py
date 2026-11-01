import streamlit as st
import pandas as pd
from datetime import date
from database.db import fetch_data, execute_query


def show_communication():

    st.title("💬 Communication Log")
    st.write("Maintain a history of all client communications.")
    st.markdown("---")

    clients = fetch_data("SELECT id, name FROM clients")

    if not clients:
        st.warning("Please add a client first in Clients module.")
        return

    client_options = {
        f"{c['name']} (ID: {c['id']})": c['id']
        for c in clients
    }

    st.subheader("➕ Add Communication Record")

    with st.form("communication_form"):

        client_name = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        communication_type = st.selectbox(
            "Communication Type",
            ["Call", "Email", "WhatsApp", "Meeting"]
        )

        subject = st.text_input("Subject")

        details = st.text_area(
            "Communication Details",
            height=120
        )

        communication_date = st.date_input(
            "Communication Date",
            value=date.today()
        )

        submitted = st.form_submit_button("Save Communication")

        if submitted:

            if subject.strip() and details.strip():

                client_id = client_options[client_name]

                execute_query("""
                    INSERT INTO communication_log
                    (client_id, communication_type, subject,
                     details, communication_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    client_id,
                    communication_type,
                    subject,
                    details,
                    str(communication_date)
                ))

                st.success("Communication saved successfully!")
                st.experimental_rerun()

            else:
                st.error("Please enter subject and details.")

    st.markdown("---")
    st.subheader("📋 Communication History")

    records = fetch_data("""
        SELECT communication_log.id,
               clients.name AS client_name,
               communication_log.communication_type,
               communication_log.subject,
               communication_log.details,
               communication_log.communication_date
        FROM communication_log
        LEFT JOIN clients
        ON communication_log.client_id = clients.id
        ORDER BY communication_log.communication_date DESC
    """)

    if records:

        df = pd.DataFrame(
            [dict(row) for row in records]
        )

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Search Communication")

        search = st.text_input("Search by client or subject")

        if search:
            filtered = df[
                df["client_name"].str.contains(
                    search, case=False, na=False
                )
                |
                df["subject"].str.contains(
                    search, case=False, na=False
                )
            ]

            st.dataframe(filtered, use_container_width=True)

        st.markdown("---")
        st.subheader("🗑️ Delete Communication Record")

        record_id = st.selectbox(
            "Select Record ID",
            df["id"].tolist()
        )

        if st.button("Delete Communication"):

            execute_query(
                "DELETE FROM communication_log WHERE id=?",
                (record_id,)
            )

            st.success("Communication record deleted!")
            st.experimental_rerun()

    else:
        st.info("No communication records available yet.")
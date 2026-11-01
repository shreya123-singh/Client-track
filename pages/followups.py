import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_followups():

    st.title("🔔 Follow-Ups")
    st.write("Schedule and track client follow-ups.")
    st.markdown("---")

    clients = fetch_data(
        "SELECT id, name FROM clients ORDER BY name"
    )

    if not clients:
        st.warning(
            "No clients found. Please add a client first in the Clients module."
        )
        return

    client_options = {
        f"{c['name']} (ID: {c['id']})": c['id']
        for c in clients
    }

    # SCHEDULE FOLLOW-UP
    st.subheader("➕ Schedule New Follow-Up")
    st.caption("Create a reminder to contact a client again.")

    with st.form("followup_form", clear_on_submit=True):

        st.markdown("**Select Client**")
        client_name = st.selectbox(
            "Select Client",
            list(client_options.keys()),
            label_visibility="collapsed"
        )

        st.markdown("**Follow-Up Subject**")
        subject = st.text_input(
            "Follow-Up Subject",
            placeholder="e.g. Discuss project proposal",
            label_visibility="collapsed"
        )

        st.markdown("**Communication Method**")
        method = st.selectbox(
            "Communication Method",
            ["Call", "Email", "WhatsApp", "Meeting"]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Follow-Up Date**")
            followup_date = st.date_input(
                "Follow-Up Date",
                value=date.today()
            )

        with col2:
            st.markdown("**Follow-Up Time**")
            followup_time = st.time_input("Follow-Up Time")

        st.markdown("**Follow-Up Notes**")
        notes = st.text_area(
            "Follow-Up Notes",
            placeholder="Write what you need to discuss or remember...",
            label_visibility="collapsed"
        )

        st.caption(
            "New follow-ups are automatically saved with Pending status."
        )

        submitted = st.form_submit_button(
            "📌 Save Follow-Up",
            use_container_width=True
        )

        if submitted:

            if not subject.strip():
                st.error("Please enter a follow-up subject.")

            else:
                client_id = client_options[client_name]

                execute_query("""
                    INSERT INTO followups
                    (client_id, subject, method, followup_date,
                     followup_time, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    client_id,
                    subject.strip(),
                    method,
                    str(followup_date),
                    str(followup_time),
                    "Pending",
                    notes.strip()
                ))

                st.success("Follow-Up scheduled successfully!")
                st.experimental_rerun()

    st.markdown("---")

    # ALL FOLLOW-UPS
    st.subheader("📋 All Follow-Ups")

    records = fetch_data("""
        SELECT followups.id,
               clients.name AS client_name,
               followups.subject,
               followups.method,
               followups.followup_date,
               followups.followup_time,
               followups.status,
               followups.notes
        FROM followups
        LEFT JOIN clients
        ON followups.client_id = clients.id
        ORDER BY followups.followup_date DESC
    """)

    if records:

        df = pd.DataFrame([dict(row) for row in records])

        # FOLLOW-UP SUMMARY
        st.subheader("📊 Follow-Up Summary")

        pending = len(df[df["status"] == "Pending"])
        completed = len(df[df["status"] == "Completed"])
        cancelled = len(df[df["status"] == "Cancelled"])

        overdue = len(df[
            (df["status"] == "Pending") &
            (df["followup_date"] < str(date.today()))
        ])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📌 Pending", pending)
        col2.metric("✅ Completed", completed)
        col3.metric("⏰ Overdue", overdue)
        col4.metric("❌ Cancelled", cancelled)

        st.markdown("---")

        # SEARCH AND FILTER
        st.subheader("🔍 Search & Filter Follow-Ups")

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input(
                "Search Follow-Up",
                placeholder="Search by client or subject..."
            )

        with col2:
            selected_status = st.selectbox(
                "Filter by Status",
                ["All", "Pending", "Completed", "Cancelled"]
            )

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["client_name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered_df["subject"].str.contains(
                    search, case=False, na=False
                )
            ]

        if selected_status != "All":
            filtered_df = filtered_df[
                filtered_df["status"] == selected_status
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Showing {len(filtered_df)} follow-up(s)")

        st.markdown("---")

        # UPDATE STATUS
        st.subheader("✏️ Update Follow-Up Status")
        st.caption("Choose a follow-up and update its current status.")

        followup_options = {
            f"{record['subject']} - {record['client_name']} (ID: {record['id']})":
            record['id']
            for record in records
        }

        selected_followup = st.selectbox(
            "Choose Follow-Up",
            list(followup_options.keys()),
            key="update_followup"
        )

        selected_id = followup_options[selected_followup]

        current_status = fetch_data(
            "SELECT status FROM followups WHERE id = ?",
            (selected_id,)
        )[0]["status"]

        statuses = ["Pending", "Completed", "Cancelled"]

        with st.form("update_followup_form"):

            new_status = st.selectbox(
                "Select New Status",
                statuses,
                index=(
                    statuses.index(current_status)
                    if current_status in statuses else 0
                )
            )

            if st.form_submit_button(
                "💾 Update Follow-Up",
                use_container_width=True
            ):

                execute_query(
                    "UPDATE followups SET status=? WHERE id=?",
                    (new_status, selected_id)
                )

                st.success("Follow-Up updated successfully!")
                st.experimental_rerun()

        st.markdown("---")

        # DELETE FOLLOW-UP
        st.subheader("🗑️ Delete Follow-Up")
        st.caption("Select a follow-up you want to permanently delete.")

        delete_followup = st.selectbox(
            "Choose Follow-Up to Delete",
            list(followup_options.keys()),
            key="delete_followup"
        )

        if st.button(
            "🗑️ Delete Selected Follow-Up",
            type="secondary"
        ):

            delete_id = followup_options[delete_followup]

            execute_query(
                "DELETE FROM followups WHERE id=?",
                (delete_id,)
            )

            st.success("Follow-Up deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No follow-ups scheduled yet. Add your first follow-up above.")
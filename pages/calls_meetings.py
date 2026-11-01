import streamlit as st
import pandas as pd
from database.db import fetch_data, execute_query


def show_calls_meetings():

    st.title("📞 Calls & Meetings")
    st.write("Schedule and manage client calls and meetings.")
    st.markdown("---")

    clients = fetch_data("SELECT id, name FROM clients")

    if not clients:
        st.warning("Please add a client first in the Clients module.")
        return

    client_options = {
        f"{client['name']} (ID: {client['id']})": client['id']
        for client in clients
    }

    st.subheader("➕ Schedule New Call / Meeting")

    with st.form("meeting_form"):

        client_name = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        title = st.text_input("Call / Meeting Title")

        meeting_type = st.selectbox(
            "Meeting Type",
            ["Call", "Online Meeting", "In-Person Meeting"]
        )

        col1, col2 = st.columns(2)

        with col1:
            meeting_date = st.date_input("Meeting Date")

        with col2:
            meeting_time = st.time_input("Meeting Time")

        notes = st.text_area("Meeting Notes")

        submitted = st.form_submit_button("Schedule Meeting")

        if submitted:

            if title.strip():

                client_id = client_options[client_name]

                execute_query("""
                    INSERT INTO meetings
                    (client_id, title, meeting_type, meeting_date,
                     meeting_time, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    client_id,
                    title,
                    meeting_type,
                    str(meeting_date),
                    str(meeting_time),
                    notes,
                    "Scheduled"
                ))

                st.success("Meeting scheduled successfully!")
                st.experimental_rerun()

            else:
                st.error("Please enter a meeting title.")

    st.markdown("---")

    st.subheader("📋 All Calls & Meetings")

    meetings = fetch_data("""
        SELECT meetings.id, clients.name AS client_name,
               meetings.title, meetings.meeting_type,
               meetings.meeting_date, meetings.meeting_time,
               meetings.notes, meetings.status
        FROM meetings
        LEFT JOIN clients ON meetings.client_id = clients.id
        ORDER BY meetings.meeting_date DESC
    """)

    if meetings:

        df = pd.DataFrame([dict(row) for row in meetings])

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("✏️ Update Meeting Status")

        meeting_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Meeting ID",
            meeting_ids,
            key="update_meeting"
        )

        current_status = df.loc[
            df["id"] == selected_id, "status"
        ].iloc[0]

        statuses = [
            "Scheduled",
            "Completed",
            "Cancelled",
            "Rescheduled"
        ]

        selected_status = st.selectbox(
            "New Status",
            statuses,
            index=statuses.index(current_status)
            if current_status in statuses else 0
        )

        if st.button("Update Status"):

            execute_query(
                "UPDATE meetings SET status=? WHERE id=?",
                (selected_status, selected_id)
            )

            st.success("Meeting status updated!")
            st.experimental_rerun()

        st.markdown("---")
        st.subheader("🗑️ Delete Meeting")

        delete_id = st.selectbox(
            "Select Meeting ID to Delete",
            meeting_ids,
            key="delete_meeting"
        )

        if st.button("Delete Meeting"):

            execute_query(
                "DELETE FROM meetings WHERE id=?",
                (delete_id,)
            )

            st.success("Meeting deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No calls or meetings scheduled yet.")
import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_daily_progress():

    st.title("📈 Daily Progress")
    st.write("Track daily work updates and monitor project progress.")
    st.markdown("---")

    projects = fetch_data(
        "SELECT id, name FROM projects ORDER BY name"
    )

    if not projects:
        st.warning(
            "No projects found. Please add a project first in the Projects module."
        )
        return

    project_options = {
        f"{p['name']} (ID: {p['id']})": p['id']
        for p in projects
    }

    # ADD DAILY PROGRESS
    st.subheader("➕ Add Daily Progress")
    st.caption("Record the work completed on a project each day.")

    with st.form("daily_progress_form", clear_on_submit=True):

        st.markdown("**Select Project**")
        project_name = st.selectbox(
            "Select Project",
            list(project_options.keys())
        )

        st.markdown("**Progress Date**")
        progress_date = st.date_input(
            "Progress Date",
            value=date.today()
        )

        st.markdown("**Today's Work Description**")
        description = st.text_area(
            "Today's Work Description",
            placeholder=(
                "e.g. Completed homepage design and started working "
                "on the login page."
            ),
            label_visibility="collapsed"
        )

        st.markdown("**Current Project Progress (%)**")
        progress_percentage = st.slider(
            "Current Project Progress (%)",
            min_value=0,
            max_value=100,
            value=0
        )

        st.caption(
            "Enter the overall completion percentage of the project after today's work."
        )

        submitted = st.form_submit_button(
            "💾 Save Daily Progress",
            use_container_width=True
        )

        if submitted:

            if not description.strip():
                st.error("Please enter today's work description.")

            else:
                project_id = project_options[project_name]

                execute_query("""
                    INSERT INTO daily_progress
                    (project_id, progress_date, description,
                     progress_percentage)
                    VALUES (?, ?, ?, ?)
                """, (
                    project_id,
                    str(progress_date),
                    description.strip(),
                    progress_percentage
                ))

                if progress_percentage == 100:
                    status = "Completed"
                elif progress_percentage == 0:
                    status = "Not Started"
                else:
                    status = "In Progress"

                execute_query("""
                    UPDATE projects
                    SET progress=?, status=?
                    WHERE id=?
                """, (
                    progress_percentage,
                    status,
                    project_id
                ))

                st.success("Daily progress saved successfully!")
                st.experimental_rerun()

    st.markdown("---")

    # DAILY PROGRESS HISTORY
    st.subheader("📋 Daily Progress History")

    records = fetch_data("""
        SELECT daily_progress.id,
               projects.name AS project_name,
               daily_progress.progress_date,
               daily_progress.description,
               daily_progress.progress_percentage
        FROM daily_progress
        LEFT JOIN projects
        ON daily_progress.project_id = projects.id
        ORDER BY daily_progress.progress_date DESC,
                 daily_progress.id DESC
    """)

    if records:

        df = pd.DataFrame(
            [dict(row) for row in records]
        )

        # PROGRESS SUMMARY
        st.subheader("📊 Progress Overview")

        total_updates = len(df)

        average_progress = pd.to_numeric(
            df["progress_percentage"], errors="coerce"
        ).mean()

        col1, col2 = st.columns(2)

        col1.metric("Total Updates", total_updates)

        col2.metric(
            "Average Progress",
            f"{average_progress:.1f}%"
            if pd.notna(average_progress) else "0%"
        )

        st.markdown("---")

        # SEARCH AND FILTER
        st.subheader("🔍 Search & Filter Progress")

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input(
                "Search Project",
                placeholder="Enter project name..."
            )

        with col2:
            selected_project = st.selectbox(
                "Filter by Project",
                ["All Projects"] + list(
                    df["project_name"].dropna().unique()
                )
            )

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["project_name"].str.contains(
                    search, case=False, na=False
                )
            ]

        if selected_project != "All Projects":
            filtered_df = filtered_df[
                filtered_df["project_name"] == selected_project
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Showing {len(filtered_df)} progress record(s)")

        st.markdown("---")

        # DELETE PROGRESS RECORD
        st.subheader("🗑️ Delete Progress Record")
        st.caption("Select a record that you want to permanently delete.")

        record_options = {
            f"{row['project_name']} - {row['progress_date']} "
            f"(Record ID: {row['id']})": row['id']
            for row in records
        }

        selected_record = st.selectbox(
            "Choose Progress Record",
            list(record_options.keys())
        )

        if st.button(
            "🗑️ Delete Selected Record",
            type="secondary"
        ):

            record_id = record_options[selected_record]

            execute_query(
                "DELETE FROM daily_progress WHERE id=?",
                (record_id,)
            )

            st.success("Progress record deleted successfully!")
            st.info(
                "Note: Deleting a history record does not automatically "
                "change the project's current progress."
            )
            st.experimental_rerun()

    else:
        st.info(
            "No daily progress records available yet. "
            "Add your first update above."
        )
import streamlit as st
import pandas as pd
from datetime import date

from database.db import fetch_data, execute_query


def show_projects():

    st.title("📁 Projects")
    st.write("Manage client projects, budgets, progress and deadlines.")
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

    # ADD NEW PROJECT
    st.subheader("➕ Add New Project")
    st.caption("Create a project and assign it to an existing client.")

    with st.form("project_form", clear_on_submit=True):

        st.markdown("**Project Name**")
        project_name = st.text_input(
            "Project Name",
            placeholder="e.g. Website Development",
            label_visibility="collapsed"
        )

        st.markdown("**Select Client**")
        client_name = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        st.markdown("**Project Description**")
        description = st.text_area(
            "Project Description",
            placeholder="Describe the project, its objectives and requirements...",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Project Start Date**")
            start_date = st.date_input(
                "Start Date",
                value=date.today()
            )

        with col2:
            st.markdown("**Project Deadline**")
            deadline = st.date_input(
                "Project Deadline",
                value=date.today()
            )

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Project Budget (₹)**")
            budget = st.number_input(
                "Project Budget",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                help="Enter the estimated project budget in rupees."
            )

        with col4:
            st.markdown("**Initial Progress**")
            progress = st.slider(
                "Initial Progress (%)",
                min_value=0,
                max_value=100,
                value=0
            )

        st.markdown("**Project Status**")
        status = st.selectbox(
            "Project Status",
            ["Not Started", "In Progress", "On Hold", "Completed"]
        )

        st.caption(
            "Example: A new project can start with 0% progress and Not Started status."
        )

        submitted = st.form_submit_button(
            "➕ Add Project",
            use_container_width=True
        )

        if submitted:

            if not project_name.strip():
                st.error("Please enter a project name.")

            elif deadline < start_date:
                st.error(
                    "Project deadline cannot be earlier than the start date."
                )

            else:
                client_id = client_options[client_name]

                execute_query("""
                    INSERT INTO projects
                    (name, client_id, description, status,
                     progress, start_date, deadline, budget)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_name.strip(),
                    client_id,
                    description.strip(),
                    status,
                    progress,
                    str(start_date),
                    str(deadline),
                    budget
                ))

                st.success("Project added successfully!")
                st.experimental_rerun()

    st.markdown("---")

    # FETCH PROJECTS
    st.subheader("📋 All Projects")

    records = fetch_data("""
        SELECT projects.id,
               projects.name,
               clients.name AS client_name,
               projects.description,
               projects.status,
               projects.progress,
               projects.start_date,
               projects.deadline,
               projects.budget
        FROM projects
        LEFT JOIN clients
        ON projects.client_id = clients.id
        ORDER BY projects.id DESC
    """)

    if records:

        df = pd.DataFrame([dict(row) for row in records])

        # PROJECT SUMMARY
        st.subheader("📊 Project Summary")

        total_projects = len(df)
        ongoing = len(df[df["status"] == "In Progress"])
        completed = len(df[df["status"] == "Completed"])
        total_budget = pd.to_numeric(
            df["budget"], errors="coerce"
        ).fillna(0).sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Projects", total_projects)
        col2.metric("Ongoing Projects", ongoing)
        col3.metric("Completed Projects", completed)
        col4.metric("Total Budget", f"₹{total_budget:,.0f}")

        st.markdown("---")

        # SEARCH AND FILTER
        st.subheader("🔍 Search & Filter Projects")

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input(
                "Search Project",
                placeholder="Enter project or client name..."
            )

        with col2:
            selected_status = st.selectbox(
                "Filter by Status",
                ["All", "Not Started", "In Progress", "On Hold", "Completed"]
            )

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered_df["client_name"].str.contains(
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

        st.caption(f"Showing {len(filtered_df)} project(s)")

        st.markdown("---")

        # UPDATE PROJECT
        st.subheader("✏️ Update Project")
        st.caption("Select a project to update its status and completion progress.")

        project_options = {
            f"{row['name']} - {row['client_name']} (ID: {row['id']})":
            row['id']
            for row in records
        }

        selected_project_name = st.selectbox(
            "Choose Project",
            list(project_options.keys()),
            key="update_project"
        )

        selected_id = project_options[selected_project_name]

        selected_project = df[
            df["id"] == selected_id
        ].iloc[0]

        project_statuses = [
            "Not Started",
            "In Progress",
            "On Hold",
            "Completed"
        ]

        with st.form("update_project_form"):

            new_status = st.selectbox(
                "Update Project Status",
                project_statuses,
                index=(
                    project_statuses.index(selected_project["status"])
                    if selected_project["status"] in project_statuses
                    else 0
                )
            )

            new_progress = st.slider(
                "Update Progress (%)",
                min_value=0,
                max_value=100,
                value=int(selected_project["progress"] or 0)
            )

            update_submitted = st.form_submit_button(
                "💾 Update Project",
                use_container_width=True
            )

            if update_submitted:

                execute_query("""
                    UPDATE projects
                    SET status=?, progress=?
                    WHERE id=?
                """, (
                    new_status,
                    new_progress,
                    selected_id
                ))

                st.success("Project updated successfully!")
                st.experimental_rerun()

        st.markdown("---")

        # DELETE PROJECT
        st.subheader("🗑️ Delete Project")
        st.caption("Select a project that you want to permanently delete.")

        delete_project_name = st.selectbox(
            "Choose Project to Delete",
            list(project_options.keys()),
            key="delete_project"
        )

        if st.button(
            "🗑️ Delete Selected Project",
            type="secondary"
        ):

            delete_id = project_options[delete_project_name]

            execute_query(
                "DELETE FROM projects WHERE id=?",
                (delete_id,)
            )

            st.success("Project deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No projects added yet. Create your first project above.")
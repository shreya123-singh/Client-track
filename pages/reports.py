import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date
from database.db import fetch_data


def show_reports():

    st.title("📊 Reports & Analytics")
    st.write("Analyze business performance, client activity and project progress.")
    st.markdown("---")

    # FETCH DATABASE RECORDS
    clients = fetch_data("SELECT * FROM clients")
    leads = fetch_data("SELECT * FROM leads")
    projects = fetch_data("SELECT * FROM projects")
    followups = fetch_data("SELECT * FROM followups")
    meetings = fetch_data("SELECT * FROM meetings")

    client_df = pd.DataFrame([dict(row) for row in clients])
    lead_df = pd.DataFrame([dict(row) for row in leads])
    project_df = pd.DataFrame([dict(row) for row in projects])
    followup_df = pd.DataFrame([dict(row) for row in followups])

    total_clients = len(client_df)
    total_leads = len(lead_df)
    total_projects = len(project_df)

    converted_leads = (
        len(lead_df[lead_df["status"] == "Converted"])
        if not lead_df.empty else 0
    )

    conversion_rate = (
        (converted_leads / total_leads) * 100
        if total_leads > 0 else 0
    )

    # BUSINESS OVERVIEW
    st.subheader("📌 Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Clients", total_clients)
    col2.metric("Total Leads", total_leads)
    col3.metric("Total Projects", total_projects)
    col4.metric("Converted Leads", converted_leads)

    col1, col2 = st.columns(2)

    col1.metric(
        "Lead Conversion Rate",
        f"{conversion_rate:.1f}%"
    )

    active_clients = (
        len(client_df[client_df["status"] == "Active"])
        if not client_df.empty and "status" in client_df.columns
        else 0
    )

    col2.metric("Active Clients", active_clients)

    st.markdown("---")

    # LEAD ANALYSIS
    st.subheader("🎯 Lead Analysis")

    if not lead_df.empty and "status" in lead_df.columns:

        lead_chart = (
            lead_df["status"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        lead_chart.columns = ["Status", "Count"]

        fig = px.pie(
            lead_chart,
            names="Status",
            values="Count",
            title="Leads by Status",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_white",
            legend_title="Lead Status"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption("This chart shows the distribution of leads across different stages.")

        st.dataframe(
            lead_chart,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No lead data available for analysis.")

    st.markdown("---")

    # PROJECT ANALYSIS
    st.subheader("📁 Project Analysis")

    if not project_df.empty and "status" in project_df.columns:

        project_chart = (
            project_df["status"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        project_chart.columns = ["Status", "Count"]

        fig = px.bar(
            project_chart,
            x="Status",
            y="Count",
            text="Count",
            title="Projects by Status"
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title="Project Status",
            yaxis_title="Number of Projects"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            project_chart,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No project data available for analysis.")

    st.markdown("---")

    # PROJECT BUDGET ANALYSIS
    st.subheader("💰 Project Budget Analysis")

    if not project_df.empty and "budget" in project_df.columns:

        budget_df = project_df[
            ["name", "budget"]
        ].copy()

        budget_df["budget"] = pd.to_numeric(
            budget_df["budget"],
            errors="coerce"
        ).fillna(0)

        total_budget = budget_df["budget"].sum()

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Project Budget",
            f"₹{total_budget:,.2f}"
        )

        col2.metric(
            "Average Project Budget",
            f"₹{budget_df['budget'].mean():,.2f}"
        )

        fig = px.bar(
            budget_df,
            x="name",
            y="budget",
            title="Budget by Project",
            labels={
                "name": "Project Name",
                "budget": "Budget (₹)"
            },
            text="budget"
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title="Project",
            yaxis_title="Budget (₹)"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No project budget data available.")

    st.markdown("---")

    # FOLLOW-UP ANALYSIS
    st.subheader("📞 Follow-Up Performance")

    total_followups = len(followup_df)

    completed_followups = (
        len(followup_df[followup_df["status"] == "Completed"])
        if not followup_df.empty else 0
    )

    pending_followups = (
        len(followup_df[followup_df["status"] == "Pending"])
        if not followup_df.empty else 0
    )

    overdue_followups = 0

    if not followup_df.empty:
        overdue_followups = len(
            followup_df[
                (followup_df["status"] == "Pending") &
                (followup_df["followup_date"] < str(date.today()))
            ]
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Follow-Ups", total_followups)
    col2.metric("Completed", completed_followups)
    col3.metric("Pending", pending_followups)
    col4.metric("Overdue", overdue_followups)

    st.markdown("---")

    # MEETING ANALYSIS
    st.subheader("🤝 Meeting Summary")

    col1, col2 = st.columns(2)

    col1.metric("Total Meetings", len(meetings))

    scheduled_meetings = sum(
        1 for meeting in meetings
        if meeting["status"] == "Scheduled"
    )

    col2.metric("Scheduled Meetings", scheduled_meetings)

    st.markdown("---")

    # CLIENT REPORT
    st.subheader("👥 Client Report")

    if not client_df.empty:

        client_search = st.text_input(
            "Search Client",
            placeholder="Search by client name or company..."
        )

        filtered_clients = client_df.copy()

        if client_search:
            mask = filtered_clients["name"].str.contains(
                client_search,
                case=False,
                na=False
            )

            if "company" in filtered_clients.columns:
                mask = mask | filtered_clients["company"].str.contains(
                    client_search,
                    case=False,
                    na=False
                )

            filtered_clients = filtered_clients[mask]

        st.dataframe(
            filtered_clients,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Showing {len(filtered_clients)} client record(s)")

    else:
        st.info("No client records available.")

    st.markdown("---")

    # PROJECT REPORT
    st.subheader("📋 Project Report")

    if not project_df.empty:

        status_options = ["All"] + sorted(
            project_df["status"].dropna().unique().tolist()
        )

        selected_status = st.selectbox(
            "Filter Projects by Status",
            status_options
        )

        filtered_projects = project_df.copy()

        if selected_status != "All":
            filtered_projects = filtered_projects[
                filtered_projects["status"] == selected_status
            ]

        st.dataframe(
            filtered_projects,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Showing {len(filtered_projects)} project record(s)"
        )

    else:
        st.info("No project records available.")

    st.markdown("---")

    st.caption(
        "ClientTrack Reports & Analytics | Data fetched from the SQLite database."
    )
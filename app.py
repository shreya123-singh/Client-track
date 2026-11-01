import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from database.db import create_tables, fetch_data

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="ClientTrack",
    page_icon="🌿",
    layout="wide"
)

# ---------------- DATABASE ----------------

create_tables()

# ---------------- LOAD CSS ----------------

css_path = Path("styles/style.css")

if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ---------------- SIDEBAR ----------------

st.sidebar.title("🌿 ClientTrack")
st.sidebar.caption("Manage Clients. Track Projects.")
st.sidebar.markdown("---")

menu_options = [
    "Dashboard",
    "Clients",
    "Leads & Pipeline",
    "Calls & Meetings",
    "Follow-Ups",
    "Projects",
    "Daily Progress",
    "Notes",
    "Communication Log",
    "Reports & Analytics",
    "Users & Roles",
    "Java & MySQL Hub",
    "Settings"
]

if "selected_menu" not in st.session_state:
    st.session_state["selected_menu"] = "Dashboard"

menu = st.sidebar.radio(
    "MAIN MENU",
    menu_options,
    key="selected_menu"
)

st.sidebar.markdown("---")
st.sidebar.caption("ClientTrack Management System")

# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.title("ClientTrack Command Center")
    st.write("Welcome back! Here's your business overview.")

    # Fetch database records
    clients = fetch_data("SELECT * FROM clients")
    leads = fetch_data("SELECT * FROM leads")
    projects = fetch_data("SELECT * FROM projects")

    followups = fetch_data(
        "SELECT * FROM followups WHERE status = 'Pending'"
    )

    meetings = fetch_data(
        "SELECT * FROM meetings WHERE status = 'Scheduled'"
    )

    # Calculate metrics
    total_clients = len(clients)
    total_leads = len(leads)
    total_projects = len(projects)
    pending_followups = len(followups)
    scheduled_meetings = len(meetings)

    completed_projects = sum(
        1 for p in projects if p["status"] == "Completed"
    )

    st.markdown("### Business Overview")

    # Metric cards
    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Clients", total_clients)
    col2.metric("🎯 Total Leads", total_leads)
    col3.metric("📁 Total Projects", total_projects)

    col4, col5, col6 = st.columns(3)

    col4.metric("📌 Pending Follow-Ups", pending_followups)
    col5.metric("📅 Scheduled Meetings", scheduled_meetings)
    col6.metric("✅ Completed Projects", completed_projects)

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")

    action1, action2, action3, action4 = st.columns(4)

    if action1.button("➕ Add Client", use_container_width=True):
        st.session_state["selected_menu"] = "Clients"
        st.experimental_rerun()

    if action2.button("➕ Add Lead", use_container_width=True):
        st.session_state["selected_menu"] = "Leads & Pipeline"
        st.experimental_rerun()

    if action3.button("📞 Schedule Call", use_container_width=True):
        st.session_state["selected_menu"] = "Calls & Meetings"
        st.experimental_rerun()

    if action4.button("📌 Add Follow-Up", use_container_width=True):
        st.session_state["selected_menu"] = "Follow-Ups"
        st.experimental_rerun()

    st.markdown("---")

    # Charts
    st.markdown("### 📊 Business Analytics")

    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Leads by Status")

        if leads:
            lead_df = pd.DataFrame([dict(row) for row in leads])

            status_data = (
                lead_df["status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Count"]

            fig = px.pie(
                status_data,
                names="Status",
                values="Count",
                hole=0.55,
                template="plotly_white"
            )

            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                legend_title_text="Lead Status"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No leads available yet. Add your first lead.")

    with chart2:
        st.markdown("#### Projects by Status")

        if projects:
            project_df = pd.DataFrame(
                [dict(row) for row in projects]
            )

            project_data = (
                project_df["status"]
                .value_counts()
                .reset_index()
            )

            project_data.columns = ["Status", "Count"]

            fig = px.bar(
                project_data,
                x="Status",
                y="Count",
                color="Status",
                template="plotly_white"
            )

            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No projects available yet. Create your first project.")

    st.markdown("---")

    # Follow-up Watchlist
    st.markdown("### 📅 Follow-Up Watchlist")

    if followups:
        followup_df = pd.DataFrame(
            [dict(row) for row in followups]
        )

        st.dataframe(
            followup_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No pending follow-ups right now.")
    
    # ---------------- PROJECT BUDGET OVERVIEW ----------------

    st.markdown("---")
    st.markdown("### 💰 Project Budget Overview")

    total_budget = sum(
        float(p["budget"] or 0) for p in projects
    )

    budget_col1, budget_col2 = st.columns(2)

    with budget_col1:
        st.metric(
            "Total Project Budget",
            f"₹ {total_budget:,.2f}"
        )

    with budget_col2:
        st.metric(
            "Active Projects",
            sum(1 for p in projects if p["status"] != "Completed")
        )

    # ---------------- PROJECT DEADLINE ALERTS ----------------

    st.markdown("---")
    st.markdown("### ⏰ Project Deadline Alerts")

    overdue_projects = fetch_data("""
        SELECT name, deadline, progress, status
        FROM projects
        WHERE deadline IS NOT NULL
        AND date(deadline) < date('now')
        AND status != 'Completed'
        ORDER BY deadline ASC
    """)

    upcoming_projects = fetch_data("""
        SELECT name, deadline, progress, status
        FROM projects
        WHERE deadline IS NOT NULL
        AND date(deadline) >= date('now')
        AND status != 'Completed'
        ORDER BY deadline ASC
        LIMIT 5
    """)

    if overdue_projects:
        st.warning(
            f"{len(overdue_projects)} project(s) have crossed their deadline."
        )

        overdue_df = pd.DataFrame(
            [dict(row) for row in overdue_projects]
        )

        st.dataframe(
            overdue_df,
            use_container_width=True,
            hide_index=True
        )

    if upcoming_projects:
        st.markdown("**Upcoming Deadlines**")

        upcoming_df = pd.DataFrame(
            [dict(row) for row in upcoming_projects]
        )

        st.dataframe(
            upcoming_df,
            use_container_width=True,
            hide_index=True
        )

    if not overdue_projects and not upcoming_projects:
        st.success("No pending project deadline alerts.")
    
    # ---------------- RECENT ACTIVITIES ----------------

    st.markdown("---")
    st.markdown("### 🕒 Recent Activities")

    activity_col1, activity_col2 = st.columns(2)

    with activity_col1:
        st.markdown("**Recent Communications**")

        recent_communications = fetch_data("""
            SELECT communication_type, subject, communication_date
            FROM communication_log
            ORDER BY communication_date DESC
            LIMIT 5
        """)

        if recent_communications:
            communication_df = pd.DataFrame(
                [dict(row) for row in recent_communications]
            )

            st.dataframe(
                communication_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No communication records available.")

    with activity_col2:
        st.markdown("**Recent Meetings**")

        recent_meetings = fetch_data("""
            SELECT title, meeting_type, meeting_date, status
            FROM meetings
            ORDER BY meeting_date DESC
            LIMIT 5
        """)

        if recent_meetings:
            meeting_df = pd.DataFrame(
                [dict(row) for row in recent_meetings]
            )

            st.dataframe(
                meeting_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No meeting records available.")



# ---------------- OTHER MODULES ----------------

elif menu == "Clients":
    from pages.clients import show_clients
    show_clients()

elif menu == "Leads & Pipeline":
    from pages.leads import show_leads
    show_leads()

elif menu == "Calls & Meetings":
    from pages.calls_meetings import show_calls_meetings
    show_calls_meetings()

elif menu == "Follow-Ups":
    from pages.followups import show_followups
    show_followups()

elif menu == "Projects":
    from pages.projects import show_projects
    show_projects()

elif menu == "Daily Progress":
    from pages.daily_progress import show_daily_progress
    show_daily_progress()

elif menu == "Notes":
    from pages.notes import show_notes
    show_notes()

elif menu == "Communication Log":
    from pages.communication import show_communication
    show_communication()

elif menu == "Reports & Analytics":
    from pages.reports import show_reports
    show_reports()

elif menu == "Users & Roles":
    from pages.users import show_users
    show_users()

elif menu == "Settings":
    from pages.settings import show_settings
    show_settings()

elif menu == "Java & MySQL Hub":
    from pages.java_mysql import show_java_mysql
    show_java_mysql()

else:
    st.title(menu)
    st.info(f"{menu} module is coming soon.")
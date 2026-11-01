import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_leads():

    st.title("🎯 Leads & Pipeline")
    st.write("Track potential clients and manage your sales pipeline.")
    st.markdown("---")

    # ADD NEW LEAD
    st.subheader("➕ Add New Lead")
    st.caption("Enter the details of a potential client below.")

    with st.form("add_lead_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Lead Name**")
            name = st.text_input(
                "Lead Name *",
                placeholder="e.g. Rahul Sharma",
                label_visibility="collapsed"
            )

            st.markdown("**Company Name**")
            company = st.text_input(
                "Company Name",
                placeholder="e.g. ABC Technologies",
                label_visibility="collapsed"
            )

            st.markdown("**Email Address**")
            email = st.text_input(
                "Email Address",
                placeholder="e.g. rahul@gmail.com",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Phone Number**")
            phone = st.text_input(
                "Phone Number",
                placeholder="e.g. 9876543210",
                label_visibility="collapsed"
            )

            st.markdown("**Lead Source**")
            source = st.selectbox(
                "Lead Source",
                [
                    "Website",
                    "Social Media",
                    "Referral",
                    "Advertisement",
                    "Cold Calling",
                    "Other"
                ],
                label_visibility="collapsed"
            )

            st.markdown("**Estimated Deal Value (₹)**")
            value = st.number_input(
                "Estimated Deal Value",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                label_visibility="collapsed"
            )

        st.markdown("**Lead Status**")
        status = st.selectbox(
            "Lead Status",
            [
                "New",
                "Contacted",
                "Follow-Up",
                "Requirement Discussion",
                "Proposal Sent",
                "Negotiation",
                "Converted"
            ]
        )

        st.caption(
            "Lead Source tells you where the lead came from. "
            "Status shows the current stage of the sales process."
        )

        submitted = st.form_submit_button(
            "💾 Save Lead",
            use_container_width=True
        )

        if submitted:

            if not name.strip():
                st.error("Please enter the lead name.")

            else:
                execute_query(
                    """
                    INSERT INTO leads
                    (name, company, email, phone, source, status, value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        company.strip(),
                        email.strip(),
                        phone.strip(),
                        source,
                        status,
                        value
                    )
                )

                st.success("Lead added successfully!")
                st.experimental_rerun()

    st.markdown("---")

    # ALL LEADS
    st.subheader("📋 All Leads")

    leads = fetch_data(
        "SELECT * FROM leads ORDER BY id DESC"
    )

    if leads:

        lead_df = pd.DataFrame(
            [dict(row) for row in leads]
        )

        # PIPELINE SUMMARY
        col1, col2, col3 = st.columns(3)

        col1.metric("🎯 Total Leads", len(leads))

        converted = sum(
            1 for lead in leads
            if lead["status"] == "Converted"
        )

        col2.metric("✅ Converted Leads", converted)

        conversion_rate = (
            (converted / len(leads)) * 100
            if len(leads) > 0 else 0
        )

        col3.metric(
            "📈 Conversion Rate",
            f"{conversion_rate:.1f}%"
        )

        st.markdown("---")

        # SEARCH AND FILTER
        st.subheader("🔍 Search & Filter Leads")

        col1, col2 = st.columns(2)

        with col1:
            search = st.text_input(
                "Search Lead",
                placeholder="Enter lead name or company..."
            )

        with col2:
            selected_status = st.selectbox(
                "Filter by Lead Status",
                [
                    "All",
                    "New",
                    "Contacted",
                    "Follow-Up",
                    "Requirement Discussion",
                    "Proposal Sent",
                    "Negotiation",
                    "Converted"
                ]
            )

        filtered_df = lead_df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(
                    search, case=False, na=False
                )
                |
                filtered_df["company"].str.contains(
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

        st.caption(f"Showing {len(filtered_df)} lead(s)")

        st.markdown("---")

        # UPDATE LEAD STATUS
        st.subheader("✏️ Update Lead Status")
        st.caption("Select a lead and change its current sales stage.")

        lead_options = {
            f"{lead['name']} (ID: {lead['id']})": lead["id"]
            for lead in leads
        }

        selected_lead = st.selectbox(
            "Choose Lead",
            list(lead_options.keys())
        )

        selected_id = lead_options[selected_lead]

        selected_data = fetch_data(
            "SELECT * FROM leads WHERE id = ?",
            (selected_id,)
        )[0]

        lead_statuses = [
            "New",
            "Contacted",
            "Follow-Up",
            "Requirement Discussion",
            "Proposal Sent",
            "Negotiation",
            "Converted"
        ]

        current_status = selected_data["status"]

        with st.form("update_lead_form"):

            new_status = st.selectbox(
                "Select New Status",
                lead_statuses,
                index=(
                    lead_statuses.index(current_status)
                    if current_status in lead_statuses else 0
                )
            )

            update_button = st.form_submit_button(
                "💾 Update Lead Status",
                use_container_width=True
            )

            if update_button:

                execute_query(
                    "UPDATE leads SET status = ? WHERE id = ?",
                    (new_status, selected_id)
                )

                st.success("Lead status updated successfully!")
                st.experimental_rerun()

        st.markdown("---")

        # DELETE LEAD
        st.subheader("🗑️ Delete Lead")
        st.caption("Select a lead that you want to permanently delete.")

        delete_lead = st.selectbox(
            "Choose Lead to Delete",
            list(lead_options.keys()),
            key="delete_lead"
        )

        if st.button(
            "🗑️ Delete Selected Lead",
            type="secondary"
        ):

            delete_id = lead_options[delete_lead]

            execute_query(
                "DELETE FROM leads WHERE id = ?",
                (delete_id,)
            )

            st.success("Lead deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No leads available. Add your first lead above.")
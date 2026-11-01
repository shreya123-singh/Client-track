
import streamlit as st
import pandas as pd

from database.db import fetch_data, execute_query


def show_clients():

    st.title("👥 Client Management")
    st.write("Manage your clients and their information.")
    st.markdown("---")

    # ADD CLIENT
    st.subheader("➕ Add New Client")
    st.caption("Enter the details below to register a new client.")

    with st.form("add_client_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Client Name**")
            name = st.text_input(
                "Client Name *",
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

            st.markdown("**Client Status**")
            status = st.selectbox(
                "Client Status",
                ["Active", "Inactive", "Completed"],
                label_visibility="collapsed"
            )

            st.info("Select Active if the client is currently working with you.")

        submitted = st.form_submit_button(
            "💾 Save Client",
            use_container_width=True
        )

        if submitted:

            if not name.strip():
                st.error("Please enter the client name.")

            else:
                execute_query(
                    """
                    INSERT INTO clients
                    (name, company, email, phone, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        company.strip(),
                        email.strip(),
                        phone.strip(),
                        status
                    )
                )

                st.success("Client added successfully!")
                st.experimental_rerun()

    st.markdown("---")

    # ALL CLIENTS
    st.subheader("📋 All Clients")

    clients = fetch_data(
        "SELECT * FROM clients ORDER BY id DESC"
    )

    if clients:

        client_df = pd.DataFrame(
            [dict(row) for row in clients]
        )

        search = st.text_input(
            "🔍 Search Client",
            placeholder="Search by client name or company..."
        )

        if search:
            mask = (
                client_df["name"].str.contains(
                    search, case=False, na=False
                )
                |
                client_df["company"].str.contains(
                    search, case=False, na=False
                )
            )

            client_df = client_df[mask]

        st.dataframe(
            client_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Showing {len(client_df)} client(s)")

        st.markdown("---")

        # EDIT CLIENT
        st.subheader("✏️ Edit Client")

        all_clients = fetch_data(
            "SELECT id, name FROM clients ORDER BY id DESC"
        )

        client_options = {
            f"{client['name']} (ID: {client['id']})": client["id"]
            for client in all_clients
        }

        selected_client = st.selectbox(
            "Choose a client to edit",
            list(client_options.keys()),
            key="edit_client_select"
        )

        selected_id = client_options[selected_client]

        selected_data = fetch_data(
            "SELECT * FROM clients WHERE id = ?",
            (selected_id,)
        )[0]

        with st.form("edit_client_form"):

            st.caption("Update the client's information below.")

            edit_name = st.text_input(
                "Client Name *",
                value=selected_data["name"],
                placeholder="Enter client name"
            )

            edit_company = st.text_input(
                "Company Name",
                value=selected_data["company"] or "",
                placeholder="Enter company name"
            )

            edit_email = st.text_input(
                "Email Address",
                value=selected_data["email"] or "",
                placeholder="Enter email address"
            )

            edit_phone = st.text_input(
                "Phone Number",
                value=selected_data["phone"] or "",
                placeholder="Enter phone number"
            )

            statuses = ["Active", "Inactive", "Completed"]

            current_status = selected_data["status"]

            edit_status = st.selectbox(
                "Client Status",
                statuses,
                index=(
                    statuses.index(current_status)
                    if current_status in statuses else 0
                )
            )

            update_button = st.form_submit_button(
                "💾 Update Client",
                use_container_width=True
            )

            if update_button:

                if not edit_name.strip():
                    st.error("Client name is required.")

                else:
                    execute_query(
                        """
                        UPDATE clients
                        SET name = ?, company = ?, email = ?,
                            phone = ?, status = ?
                        WHERE id = ?
                        """,
                        (
                            edit_name.strip(),
                            edit_company.strip(),
                            edit_email.strip(),
                            edit_phone.strip(),
                            edit_status,
                            selected_id
                        )
                    )

                    st.success("Client updated successfully!")
                    st.experimental_rerun()

        st.markdown("---")

        # DELETE CLIENT
        st.subheader("🗑️ Delete Client")

        delete_client = st.selectbox(
            "Choose a client to delete",
            list(client_options.keys()),
            key="delete_client_select"
        )

        if st.button("🗑️ Delete Selected Client", type="secondary"):

            delete_id = client_options[delete_client]

            execute_query(
                "DELETE FROM clients WHERE id = ?",
                (delete_id,)
            )

            st.success("Client deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No clients found. Add your first client above.")

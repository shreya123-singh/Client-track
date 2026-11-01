import streamlit as st
import pandas as pd
from database.db import fetch_data, execute_query


def show_users():

    st.title("👥 Users & Roles")
    st.write("Manage system users and their roles.")
    st.markdown("---")

    st.subheader("➕ Add New User")

    with st.form("user_form"):

        name = st.text_input("User Name")
        email = st.text_input("Email Address")

        role = st.selectbox(
            "Select Role",
            ["Admin", "Manager", "Staff"]
        )

        submitted = st.form_submit_button("Add User")

        if submitted:

            if name.strip() and email.strip():

                try:
                    execute_query("""
                        INSERT INTO users (name, email, role)
                        VALUES (?, ?, ?)
                    """, (name, email, role))

                    st.success("User added successfully!")
                    st.experimental_rerun()

                except Exception:
                    st.error("This email already exists or is invalid.")

            else:
                st.error("Please enter name and email.")

    st.markdown("---")
    st.subheader("📋 All Users")

    records = fetch_data("""
        SELECT id, name, email, role, created_at
        FROM users
        ORDER BY id DESC
    """)

    if records:

        df = pd.DataFrame(
            [dict(row) for row in records]
        )

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("✏️ Update User Role")

        user_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select User ID",
            user_ids,
            key="update_user"
        )

        selected_user = df[
            df["id"] == selected_id
        ].iloc[0]

        roles = ["Admin", "Manager", "Staff"]

        new_role = st.selectbox(
            "New Role",
            roles,
            index=roles.index(selected_user["role"])
            if selected_user["role"] in roles else 2
        )

        if st.button("Update Role"):

            execute_query(
                "UPDATE users SET role=? WHERE id=?",
                (new_role, selected_id)
            )

            st.success("User role updated successfully!")
            st.experimental_rerun()

        st.markdown("---")
        st.subheader("🗑️ Delete User")

        delete_id = st.selectbox(
            "Select User ID to Delete",
            user_ids,
            key="delete_user"
        )

        if st.button("Delete User"):

            execute_query(
                "DELETE FROM users WHERE id=?",
                (delete_id,)
            )

            st.success("User deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No users added yet.")
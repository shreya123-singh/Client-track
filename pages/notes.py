import streamlit as st
import pandas as pd
from database.db import fetch_data, execute_query


def show_notes():

    st.title("📝 Notes")
    st.write("Create and manage important client and project notes.")
    st.markdown("---")

    st.subheader("➕ Create New Note")

    with st.form("notes_form"):

        title = st.text_input("Note Title")

        content = st.text_area(
            "Note Description",
            height=150,
            placeholder="Write your important notes here..."
        )

        submitted = st.form_submit_button("Save Note")

        if submitted:

            if title.strip() and content.strip():

                execute_query("""
                    INSERT INTO notes (title, content)
                    VALUES (?, ?)
                """, (title, content))

                st.success("Note saved successfully!")
                st.experimental_rerun()

            else:
                st.error("Please enter both title and description.")

    st.markdown("---")
    st.subheader("📋 Saved Notes")

    records = fetch_data("""
        SELECT id, title, content, created_at
        FROM notes
        ORDER BY id DESC
    """)

    if records:

        df = pd.DataFrame(
            [dict(row) for row in records]
        )

        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("✏️ Edit Note")

        note_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Note ID",
            note_ids,
            key="edit_note"
        )

        selected_note = df[
            df["id"] == selected_id
        ].iloc[0]

        with st.form("edit_note_form"):

            new_title = st.text_input(
                "Update Title",
                value=selected_note["title"]
            )

            new_content = st.text_area(
                "Update Description",
                value=selected_note["content"],
                height=150
            )

            update_button = st.form_submit_button("Update Note")

            if update_button:

                if new_title.strip() and new_content.strip():

                    execute_query("""
                        UPDATE notes
                        SET title=?, content=?
                        WHERE id=?
                    """, (
                        new_title,
                        new_content,
                        selected_id
                    ))

                    st.success("Note updated successfully!")
                    st.experimental_rerun()

                else:
                    st.error("Title and description cannot be empty.")

        st.markdown("---")
        st.subheader("🗑️ Delete Note")

        delete_id = st.selectbox(
            "Select Note ID to Delete",
            note_ids,
            key="delete_note"
        )

        if st.button("Delete Note"):

            execute_query(
                "DELETE FROM notes WHERE id=?",
                (delete_id,)
            )

            st.success("Note deleted successfully!")
            st.experimental_rerun()

    else:
        st.info("No notes available. Create your first note above.")
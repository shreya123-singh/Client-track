
import streamlit as st


def show_java_mysql():

    st.title("☕ Java & MySQL Hub")
    st.write("Learn Java programming and MySQL database concepts.")
    st.markdown("---")

    st.subheader("💻 Technology Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Java**\n\nObject-oriented programming language used to develop applications.")

    with col2:
        st.info("**MySQL**\n\nRelational database management system used to store and manage data.")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Java Basics",
        "MySQL Commands",
        "JDBC Connection",
        "Database Structure"
    ])

    with tab1:

        st.subheader("Java Programming")

        st.write("""
        Java is an object-oriented programming language.

        **Main Features:**
        - Object-Oriented
        - Platform Independent
        - Secure
        - Robust
        - Multithreaded
        """)

        st.write("**Simple Java Program:**")

        st.code("""
public class HelloWorld {

    public static void main(String[] args) {

        System.out.println("Welcome to ClientTrack");

    }
}
        """, language="java")

    with tab2:

        st.subheader("MySQL Database Commands")

        st.write("**1. Create Database**")

        st.code("""
CREATE DATABASE ClientTrack;
        """, language="sql")

        st.write("**2. Create Table**")

        st.code("""
CREATE TABLE Clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15)
);
        """, language="sql")

        st.write("**3. Insert Record**")

        st.code("""
INSERT INTO Clients (name, email, phone)
VALUES ('Rahul Sharma',
        'rahul@gmail.com',
        '9876543210');
        """, language="sql")

        st.write("**4. Display Records**")

        st.code("""
SELECT * FROM Clients;
        """, language="sql")

        st.write("**5. Update Record**")

        st.code("""
UPDATE Clients
SET name = 'Rahul Singh'
WHERE id = 1;
        """, language="sql")

        st.write("**6. Delete Record**")

        st.code("""
DELETE FROM Clients
WHERE id = 1;
        """, language="sql")

    with tab3:

        st.subheader("Java Database Connectivity (JDBC)")

        st.write("""
        JDBC stands for Java Database Connectivity.

        It allows Java applications to connect with databases
        such as MySQL.
        """)

        st.write("**Basic JDBC Connection Example:**")

        st.code("""
import java.sql.Connection;
import java.sql.DriverManager;

public class DatabaseConnection {

    public static void main(String[] args) {

        try {

            Connection con =
                DriverManager.getConnection(
                    "jdbc:mysql://localhost:3306/ClientTrack",
                    "root",
                    "your_password"
                );

            System.out.println("Database Connected!");

            con.close();

        } catch (Exception e) {

            System.out.println(e);

        }
    }
}
        """, language="java")

        st.warning(
            "This is a sample JDBC reference program. "
            "It requires MySQL and the MySQL JDBC driver to run."
        )

    with tab4:

        st.subheader("ClientTrack Database Structure")

        st.write("""
        ClientTrack currently uses SQLite with Python and Streamlit.

        The following tables are used in the application:
        """)

        tables = [
            "clients",
            "leads",
            "projects",
            "meetings",
            "followups",
            "daily_progress",
            "notes",
            "communication_log",
            "users",
            "app_settings"
        ]

        for table in tables:
            st.write("📁 " + table)

        st.markdown("---")

        st.write("**Current Project Technology Stack**")

        st.write("""
        - Frontend: Streamlit
        - Programming Language: Python
        - Database: SQLite
        - Data Analysis: Pandas
        - Charts: Plotly
        - Development Tool: Visual Studio Code
        """)

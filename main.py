import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Employee Management System",
    page_icon="👨💼",
    layout="wide"
)

st.title("👨💼 Employee Management System")
st.write("Manage employee records using Python and Streamlit.")

# ---------------- DATABASE CONNECTION ----------------

conn = sqlite3.connect("employees.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL,
    salary REAL NOT NULL,
    email TEXT NOT NULL
)
""")

conn.commit()


# ---------------- SIDEBAR ----------------

menu = st.sidebar.selectbox(
    "Select Operation",
    [
        "Dashboard",
        "Add Employee",
        "View Employees",
        "Update Employee",
        "Delete Employee"
    ]
)


# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.header("Employee Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM employees", conn
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", len(df))

    if len(df) > 0:
        col2.metric("Total Departments",
                    df["department"].nunique())

        col3.metric("Average Salary",
                    f"₹{df['salary'].mean():,.2f}")
    else:
        col2.metric("Total Departments", 0)
        col3.metric("Average Salary", "₹0")

    st.subheader("Employee Records")
    st.dataframe(df, use_container_width=True)


# ---------------- ADD EMPLOYEE ----------------

elif menu == "Add Employee":

    st.header("Add New Employee")

    with st.form("add_employee_form"):

        name = st.text_input("Employee Name")
        department = st.selectbox(
            "Department",
            ["HR", "IT", "Finance", "Marketing", "Sales", "Operations"]
        )
        designation = st.text_input("Designation")
        salary = st.number_input(
            "Salary", min_value=0.0, step=1000.0
        )
        email = st.text_input("Email Address")

        submit = st.form_submit_button("Add Employee")

        if submit:

            if not name.strip() or not designation.strip() or not email.strip():
                st.error("Please fill in all the fields.")

            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")

            elif salary <= 0:
                st.error("Salary must be greater than zero.")

            else:
                conn.execute("""
                    INSERT INTO employees
                    (name, department, designation, salary, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    name.strip(),
                    department,
                    designation.strip(),
                    salary,
                    email.strip()
                ))

                conn.commit()

                st.success("Employee added successfully!")


# ---------------- VIEW EMPLOYEES ----------------

elif menu == "View Employees":

    st.header("All Employee Records")

    df = pd.read_sql_query(
        "SELECT * FROM employees", conn
    )

    if not df.empty:

        search = st.text_input("Search by employee name")

        if search:
            df = df[
                df["name"].str.contains(
                    search, case=False, na=False
                )
            ]

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Employee Data",
            df.to_csv(index=False),
            file_name="employees.csv",
            mime="text/csv"
        )

    else:
        st.info("No employee records available.")


# ---------------- UPDATE EMPLOYEE ----------------

elif menu == "Update Employee":

    st.header("Update Employee Details")

    df = pd.read_sql_query(
        "SELECT * FROM employees", conn
    )

    if not df.empty:

        emp_id = st.selectbox(
            "Select Employee ID",
            df["emp_id"].tolist()
        )

        employee = df[df["emp_id"] == emp_id].iloc[0]

        with st.form("update_employee_form"):

            name = st.text_input(
                "Employee Name", value=employee["name"]
            )

            department = st.selectbox(
                "Department",
                ["HR", "IT", "Finance", "Marketing", "Sales", "Operations"],
                index=["HR", "IT", "Finance", "Marketing", "Sales", "Operations"].index(
                    employee["department"]
                )
            )

            designation = st.text_input(
                "Designation", value=employee["designation"]
            )

            salary = st.number_input(
                "Salary",
                min_value=0.0,
                value=float(employee["salary"]),
                step=1000.0
            )

            email = st.text_input(
                "Email", value=employee["email"]
            )

            update = st.form_submit_button("Update Employee")

            if update:

                if not name.strip() or not designation.strip() or not email.strip():
                    st.error("Please fill in all fields.")

                elif "@" not in email or "." not in email:
                    st.error("Enter a valid email address.")

                elif salary <= 0:
                    st.error("Salary must be greater than zero.")

                else:
                    conn.execute("""
                        UPDATE employees
                        SET name=?, department=?, designation=?,
                            salary=?, email=?
                        WHERE emp_id=?
                    """, (
                        name.strip(),
                        department,
                        designation.strip(),
                        salary,
                        email.strip(),
                        emp_id
                    ))

                    conn.commit()

                    st.success("Employee updated successfully!")

    else:
        st.info("No employees available to update.")


# ---------------- DELETE EMPLOYEE ----------------

elif menu == "Delete Employee":

    st.header("Delete Employee Record")

    df = pd.read_sql_query(
        "SELECT * FROM employees", conn
    )

    if not df.empty:

        emp_id = st.selectbox(
            "Select Employee ID to Delete",
            df["emp_id"].tolist()
        )

        employee = df[df["emp_id"] == emp_id].iloc[0]

        st.write("Employee Name:", employee["name"])
        st.write("Department:", employee["department"])

        confirm = st.checkbox(
            "I confirm that I want to delete this employee."
        )

        if st.button("Delete Employee", type="primary"):

            if confirm:

                conn.execute(
                    "DELETE FROM employees WHERE emp_id=?",
                    (emp_id,)
                )

                conn.commit()

                st.success("Employee deleted successfully!")

            else:
                st.warning("Please confirm before deleting.")

    else:
        st.info("No employee records available.")
import streamlit as st
import requests
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Employee Management System",
    page_icon="👨‍💼",
    layout="wide"
)

# ==========================================
# FASTAPI BACKEND URL
# ==========================================

# Replace this with your deployed Render URL
API_URL = "https://your-fastapi-app.onrender.com"

# ==========================================
# APPLICATION TITLE
# ==========================================

st.title("👨‍💼 Employee Management System")

st.markdown(
    "### FastAPI Backend + Streamlit Frontend"
)

st.divider()

# ==========================================
# API CONNECTION FUNCTION
# ==========================================

def api_request(method, endpoint, data=None):

    try:

        url = f"{API_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, timeout=60)

        elif method == "POST":
            response = requests.post(
                url, json=data, timeout=60
            )

        elif method == "PUT":
            response = requests.put(
                url, json=data, timeout=60
            )

        elif method == "DELETE":
            response = requests.delete(
                url, timeout=60
            )

        return response

    except requests.exceptions.RequestException as e:

        st.error(f"API Connection Error: {e}")
        return None


# ==========================================
# SIDEBAR MENU
# ==========================================

st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "Select Operation",
    [
        "Dashboard",
        "View Employees",
        "Add Employee",
        "Update Employee",
        "Delete Employee"
    ]
)

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.subheader("Dashboard Overview")

    response = api_request("GET", "/employees")

    if response is not None:

        if response.status_code == 200:

            employees = response.json()

            total_employees = len(employees)

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Employees",
                total_employees
            )

            departments = len(
                set(
                    emp["department"]
                    for emp in employees
                )
            )

            col2.metric(
                "Departments",
                departments
            )

            st.divider()

            st.subheader("Recent Employee Records")

            if employees:
                st.dataframe(
                    pd.DataFrame(employees),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No employee records available.")

        else:
            st.error(response.text)


# ==========================================
# VIEW EMPLOYEES - GET
# ==========================================

elif menu == "View Employees":

    st.subheader("Employee Details")

    if st.button("Load Employees"):

        response = api_request("GET", "/employees")

        if response is not None:

            if response.status_code == 200:

                employees = response.json()

                if employees:

                    df = pd.DataFrame(employees)

                    st.success(
                        f"Found {len(employees)} employees"
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = df.to_csv(index=False).encode("utf-8")

                    st.download_button(
                        "Download Employee Data",
                        data=csv,
                        file_name="employees.csv",
                        mime="text/csv"
                    )

                else:
                    st.info("No employees found.")

            else:
                st.error(response.text)


# ==========================================
# ADD EMPLOYEE - POST
# ==========================================

elif menu == "Add Employee":

    st.subheader("Register New Employee")

    with st.form("add_employee_form"):

        emp_id = st.number_input(
            "Employee ID",
            min_value=1,
            step=1
        )

        name = st.text_input("Employee Name")

        department = st.selectbox(
            "Department",
            ["IT", "HR", "Finance", "Marketing", "Sales"]
        )

        salary = st.number_input(
            "Salary",
            min_value=1.0,
            step=1000.0
        )

        submit = st.form_submit_button(
            "Add Employee"
        )

    if submit:

        if not name.strip():
            st.error("Please enter employee name.")

        else:

            employee = {
                "id": int(emp_id),
                "name": name.strip(),
                "department": department,
                "salary": float(salary)
            }

            response = api_request(
                "POST",
                "/employees",
                employee
            )

            if response is not None:

                if response.status_code in [200, 201]:

                    st.success(
                        "Employee added successfully!"
                    )

                    st.json(response.json())

                else:
                    st.error(
                        f"Error {response.status_code}: "
                        f"{response.text}"
                    )


# ==========================================
# UPDATE EMPLOYEE - PUT
# ==========================================

elif menu == "Update Employee":

    st.subheader("Update Employee Details")

    with st.form("update_employee_form"):

        emp_id = st.number_input(
            "Enter Employee ID to Update",
            min_value=1,
            step=1
        )

        name = st.text_input("Updated Employee Name")

        department = st.selectbox(
            "Updated Department",
            ["IT", "HR", "Finance", "Marketing", "Sales"]
        )

        salary = st.number_input(
            "Updated Salary",
            min_value=1.0,
            step=1000.0
        )

        update = st.form_submit_button(
            "Update Employee"
        )

    if update:

        if not name.strip():

            st.error("Please enter employee name.")

        else:

            employee = {
                "id": int(emp_id),
                "name": name.strip(),
                "department": department,
                "salary": float(salary)
            }

            response = api_request(
                "PUT",
                f"/employees/{int(emp_id)}",
                employee
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "Employee updated successfully!"
                    )

                    st.json(response.json())

                else:

                    st.error(
                        f"Error {response.status_code}: "
                        f"{response.text}"
                    )


# ==========================================
# DELETE EMPLOYEE - DELETE
# ==========================================

elif menu == "Delete Employee":

    st.subheader("Delete Employee")

    emp_id = st.number_input(
        "Enter Employee ID",
        min_value=1,
        step=1
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this employee."
    )

    if st.button("Delete Employee"):

        if not confirm:

            st.warning("Please confirm before deleting.")

        else:

            response = api_request(
                "DELETE",
                f"/employees/{int(emp_id)}"
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "Employee deleted successfully!"
                    )

                else:

                    st.error(
                        f"Error {response.status_code}: "
                        f"{response.text}"
                    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Employee Management System | "
    "Powered by FastAPI and Streamlit"
)
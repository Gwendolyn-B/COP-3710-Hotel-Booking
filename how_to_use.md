# Setup Guide for app.py

Follow these steps to configure the environment and initialize the database.

## 1. Install Oracle Instant Client
To connect to the database, you must download the **Instant Client Basic** or **Basic Light** package:
* Download **instantclient_23_4** (or your specific version) from the [Oracle website](https://oracle.com).
* In `app.py`, locate the variable for the library path and paste the full path to your extracted folder.

## 2. Configure Connection Details
In `app.py`, replace the `"PLACEHOLDER"` strings with your specific database credentials:
* **Username**
* **Password**
* **DSN (Connection String)**

## 3. Initialize the Database
Before running the application, you need to set up the schema and import the data:

1.  **Create Schema:** Run the `create_db.sql` script in your SQL tool or via the app to generate the necessary tables.
2.  **Upload Data:** Run the `uploaddata.py` (or the corresponding function in `app.py`) to process the CSV files and populate your database.

## 4. Running the Application
Run the `app.py` by using the command `python -m streamlit run app.py` in the terminal.

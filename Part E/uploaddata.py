import oracledb
import csv
import os

# --- SETUP ---
LIB_DIR = "instantclient_23_0"
DB_USER = "PLACEHOLDER"
DB_PASS = "PLACEHOLDER"
DB_DSN = "PLACEHOLDER"

# Folder where your CSVs are stored
TABLES_FOLDER = "Tables"

# Initialize Thick Mode
try:
    oracledb.init_oracle_client(lib_dir=LIB_DIR)
except Exception as e:
    print(f"Oracle Client Initialization Info: {e}")


def clear_all_data(cursor):
    """Deletes all data from tables in correct order to avoid constraint errors."""
    print("Step 1: Clearing existing data from tables...")
    # Order: Delete from Child tables first, then Parent tables
    tables = [
        "services",
        "payments",
        "reservations",
        "rooms",
        "customers",
        "hotels"
    ]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  - Cleared {table}")
        except Exception as e:
            print(f"  - Note: Could not clear {table} (it may not exist): {e}")


def load_table(cursor, file_name, sql):
    """Helper function to load a single CSV file from the Tables folder."""
    file_path = os.path.join(TABLES_FOLDER, file_name)

    if not os.path.exists(file_path):
        print(f"Skipping: {file_path} not found.")
        return

    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            next(reader)  # Skip header row
        except StopIteration:
            print(f"Skipping: {file_path} is empty.")
            return

        data = []
        for row in reader:
            if any(row):
                # Clean data: convert empty strings or 'nan' strings to None (NULL)
                processed_row = [None if val.strip().lower() in ["", "nan"] else val for val in row]
                data.append(processed_row)

        if data:
            try:
                cursor.executemany(sql, data)
                print(f"Successfully loaded {len(data)} rows from {file_name}")
            except Exception as e:
                print(f"Error inserting data from {file_name}: {e}")
                # Print the first row of data to help debug
                print(f"  Sample data attempted: {data[0]}")


def main():
    conn = None
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()
        print(f"Connected to Oracle. Searching in: {os.path.abspath(TABLES_FOLDER)}")

        # 1. Wipe everything clean first
        clear_all_data(cursor)

        # 2. Define SQL INSERT statements
        sql_hotels = "INSERT INTO hotels (HOTEL_ID, HOTEL_NAME, ADDRESS, HOTEL_PHONE) VALUES (:1, :2, :3, :4)"
        sql_customers = "INSERT INTO customers (CUS_ID, CUS_FNAME, CUS_LNAME, CUS_EMAIL, CUS_PHONE) VALUES (:1, :2, :3, :4, :5)"
        sql_rooms = "INSERT INTO rooms (ROOM_ID, HOTEL_ID, ROOM_NUM, ROOM_PRICE, ROOM_STATUS, CANCEL_RISK) VALUES (:1, :2, :3, :4, :5, :6)"

        sql_reservations = """
            INSERT INTO reservations (RES_ID, CUS_ID, ROOM_ID, RES_DATE, RES_STATUS, TOTAL_COST) 
            VALUES (:1, :2, :3, TO_DATE(:4, 'MM/DD/YYYY'), :5, :6)
        """
        sql_payments = """
            INSERT INTO payments (PAY_ID, RES_ID, PAY_DATE, PAY_AMOUNT, PAY_STATUS) 
            VALUES (:1, :2, TO_DATE(:3, 'MM/DD/YYYY'), :4, :5)
        """
        sql_services = "INSERT INTO services (SERV_PHONE, RES_ID, SERV_TYPE, SERV_PRICE) VALUES (:1, :2, :3, :4)"

        # 3. Load Tables (Following referential integrity order)
        print("\nStep 2: Loading new data...")
        load_table(cursor, 'Hotel_Table.csv', sql_hotels)
        load_table(cursor, 'Customer_Table.csv', sql_customers)
        load_table(cursor, 'Room_Table.csv', sql_rooms)
        load_table(cursor, 'Reservation_Table.csv', sql_reservations)
        load_table(cursor, 'Payment_Table.csv', sql_payments)
        load_table(cursor, 'Service_Table.csv', sql_services)

        # 4. Finalize
        conn.commit()
        print("\nAll operations completed successfully!")

    except Exception as e:
        print(f"\nFatal Connection Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cursor' in locals(): cursor.close()
        if conn: conn.close()


if __name__ == "__main__":
    main()
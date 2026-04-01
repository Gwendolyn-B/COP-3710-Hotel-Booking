import oracledb
import csv

LIB_DIR = r"C:\Users\gwenb\Downloads\instantclient-basiclite-windows.x64-11.2.0.4.0\instantclient_11_2"
DB_USER = "system"
DB_PASS = "Stryker_11"
DB_DSN  = "localhost:1521/XEPDB1"
oracledb.init_oracle_client(lib_dir=LIB_DIR)

def dataload_csv(file_path, sql):
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            data_to_insert = [col if col != '' else None for col in row for row in reader]
	
        print(f"Starting bulk load of {len(data_to_insert)} rows...")
        cursor.executemany(sql, data_to_insert)
        
        conn.commit()
        print(f"Successfully loaded {cursor.rowcount} rows into the database.")

    except Exception as e:
        print(f"Error during bulk load: {e}")
        if 'conn' in locals():
            conn.rollback()

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

dataload_csv('Hotel_Table.csv', "INSERT INTO Hotel (HOTEL_ID, HOTEL_NAME, ADDRESS, HOTEL_PHONE) VALUES (:1, :2, :3, :4)")
dataload_csv('Room_Table.csv', "INSERT INTO Room (ROOM_ID, HOTEL_ID, ROOM_NUM, ROOM_PRICE, ROOM_STATUS, CANCEL_RISK) VALUES (:1, :2, :3, :4, :5, :6)")
dataload_csv('Customer_Table.csv', "INSERT INTO Customer (CUS_ID, CUS_FNAME, CUS_LNAME, CUS_EMAIL, CUS_PHONE) VALUES (:1, :2, :3, :4, :5)")
dataload_csv('Payment_Table.csv', "INSERT INTO Payment (PAY_ID, RES_ID, PAY_DATE, PAY_AMOUNT, PAY_STATUS) VALUES (:1, :2, TO_DATE(:3, 'MM/DD/YYYY'), :4, :5)")
import streamlit as st
import oracledb
import pandas as pd
import os

# --- DATABASE SETUP ---
LIB_DIR = "instantclient_23_0"
DB_USER = "SRAGHUNANDAN8117_SCHEMA_QWBJH"
DB_PASS = "JFNP11!GGyAHO60A2W34M57W83YBAZ"
DB_DSN = "db.freesql.com:1521/23ai_34ui2"


@st.cache_resource
def init_db():
    if LIB_DIR:
        try:
            oracledb.init_oracle_client(lib_dir=LIB_DIR)
        except Exception as e:
            st.error(f"Oracle Error: {e}")


init_db()


@st.cache_data
def get_hotel_suggestions():
    file_path = 'Hotel_Table.csv'
    if not os.path.exists(file_path):
        file_path = os.path.join('Tables', 'Hotel_Table.csv')
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return sorted(df['HOTEL_NAME'].dropna().unique().tolist())
        return []
    except:
        return []


def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)


# SIDEBAR
with st.sidebar:
    st.title("Hotel Admin")
    st.markdown("---")
    choice = st.radio("MAIN MENU", ["Dashboard & Reports", "Add Record", "Edit Record", "Delete Record"])

# DASHBOARD SECTION
if choice == "Dashboard & Reports":
    st.header("Hotel Dashboard")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Room Availability",
        "Hotel Search",
        "Financial Timeline",
        "Price Analysis",
        "Contact List",
        "Raw Data"
    ])

    try:
        conn = get_connection()

        # ROOM AVAILABILITY
        with tab1:
            st.subheader("Room Status Filter")
            filter_choice = st.segmented_control(
                "Select status:",
                options=["All", "Vacant", "Booked", "Occupied"],
                default="All"
            )

            base_query = """
                SELECT h.hotel_name, r.room_num, r.room_price, r.room_status 
                FROM rooms r 
                JOIN hotels h ON r.hotel_id = h.hotel_id
            """

            if filter_choice == "All":
                query = base_query
            else:
                query = base_query + f" WHERE r.room_status = '{filter_choice}'"

            df = pd.read_sql(query, conn)

            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Current Filter", filter_choice)
            col_m2.metric("Total Rooms Found", len(df))

            st.dataframe(df, use_container_width=True)

        # HOTEL SEARCH
        with tab2:
            st.subheader("Hotel Directory")
            hotel_names = get_hotel_suggestions()
            search_query = st.selectbox("Search hotel name...", options=hotel_names, index=None,
                                        placeholder="Type or select a hotel name...")
            if search_query:
                df = pd.read_sql("SELECT * FROM hotels WHERE LOWER(hotel_name) LIKE :1", conn,
                                 params=[f"%{search_query.lower()}%"])
                if not df.empty:
                    st.success(f"Found {len(df)} matching hotel(s)")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"Nothing close to '{search_query}' was found.")

        # FINANCIAL TIMELINE
        with tab3:
            st.subheader("Reservations & Associated Costs")
            col1, col2 = st.columns(2)
            start, end = col1.date_input("From Date"), col2.date_input("To Date")
            query = """
                SELECT r.res_id, r.res_date, r.res_status, p.pay_amount, s.serv_type, s.serv_price
                FROM reservations r
                LEFT JOIN payments p ON r.res_id = p.res_id
                LEFT JOIN services s ON r.res_id = s.res_id
                WHERE r.res_date BETWEEN :1 AND :2
            """
            df = pd.read_sql(query, conn, params=[start, end])
            if not df.empty:
                total_res = len(df['RES_ID'].unique())
                st.metric("Total Reservations in Period", total_res)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No reservations found for the selected date range.")

        # PRICE ANALYSIS
        with tab4:
            st.subheader("Price Analysis")
            order = st.segmented_control("Sort results by:", ["Price: Low to High", "Price: High to Low"],
                                         default="Price: Low to High")
            direction = "ASC" if order == "Price: Low to High" else "DESC"

            with st.spinner("Fetching latest price data..."):
                query = f"""
                    SELECT h.hotel_name, r.room_num, r.room_price, h.address 
                    FROM hotels h 
                    JOIN rooms r ON h.hotel_id = r.hotel_id 
                    WHERE r.room_status = 'Vacant' 
                    ORDER BY r.room_price {direction}
                """
                df = pd.read_sql(query, conn)
                st.dataframe(df, use_container_width=True)

        # CONTACT LIST
        with tab5:
            st.subheader("Emergency Contact List")

            sort_selection = st.segmented_control(
                "Sort results alphabetically by:",
                options=["Guest Name", "Hotel Name"],
                default="Guest Name"
            )

            sort_column = '"Guest Name"' if sort_selection == "Guest Name" else 'h.hotel_name'

            query = f"""
                SELECT 
                    c.cus_fname || ' ' || c.cus_lname AS "Guest Name", 
                    h.hotel_name AS "Hotel", 
                    c.cus_phone AS "Phone Number",
                    c.cus_email AS "Email"
                FROM customers c
                JOIN reservations r ON c.cus_id = r.cus_id
                JOIN rooms rm ON r.room_id = rm.room_id
                JOIN hotels h ON rm.hotel_id = h.hotel_id
                WHERE r.res_status = 'Checked-In'
                ORDER BY {sort_column} ASC
            """

            df = pd.read_sql(query, conn)
            st.metric("Active Guests", len(df))

            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No guests are currently Checked-In.")

        # RAW DATA
        with tab6:
            st.subheader("Database Explorer")
            tbl = st.selectbox("Select Table:",
                               ["Hotels", "Customers", "Rooms", "Reservations", "Payments", "Services"])
            df = pd.read_sql(f"SELECT * FROM {tbl.lower()}", conn)
            st.dataframe(df, use_container_width=True)

        conn.close()
    except Exception as e:
        st.error(f"Connection Error: {e}")

# --- OTHER ACTIONS ---
elif choice == "Add Record":
    st.header("Add New Entry")
    st.info("Feature coming soon...")
elif choice == "Edit Record":
    st.header("Update Information")
    st.info("Feature coming soon...")
elif choice == "Delete Record":
    st.header("Delete Information")
    st.info("Feature coming soon...")
DROP TABLE services CASCADE CONSTRAINTS;
DROP TABLE payments CASCADE CONSTRAINTS;
DROP TABLE reservations CASCADE CONSTRAINTS;
DROP TABLE rooms CASCADE CONSTRAINTS;
DROP TABLE customers CASCADE CONSTRAINTS;
DROP TABLE hotels CASCADE CONSTRAINTS;

CREATE TABLE hotels (
    hotel_id    NUMBER PRIMARY KEY,
    hotel_name  VARCHAR2(100),
    address     VARCHAR2(255),
    hotel_phone VARCHAR2(20)
);

CREATE TABLE customers (
    cus_id      NUMBER PRIMARY KEY,
    cus_fname   VARCHAR2(50),
    cus_lname   VARCHAR2(50),
    cus_email   VARCHAR2(100),
    cus_phone   VARCHAR2(20)
);

CREATE TABLE rooms (
    room_id     NUMBER PRIMARY KEY,
    hotel_id    NUMBER REFERENCES hotels(hotel_id),
    room_num    NUMBER,
    room_price  NUMBER(10, 2),
    room_status VARCHAR2(20),
    cancel_risk NUMBER(4, 2)
);

CREATE TABLE reservations (
    res_id      NUMBER PRIMARY KEY,
    cus_id      NUMBER REFERENCES customers(cus_id),
    room_id     NUMBER REFERENCES rooms(room_id),
    res_date    DATE,
    res_status  VARCHAR2(50),
    total_cost  NUMBER(10, 2)
);

CREATE TABLE payments (
    pay_id      NUMBER PRIMARY KEY,
    res_id      NUMBER REFERENCES reservations(res_id),
    pay_date    DATE,
    pay_amount  NUMBER(10, 2),
    pay_status  VARCHAR2(20)
);

CREATE TABLE services (
    serv_phone  VARCHAR2(20),
    res_id      NUMBER REFERENCES reservations(res_id),
    serv_type   VARCHAR2(50),
    serv_price  NUMBER(10, 2)
);
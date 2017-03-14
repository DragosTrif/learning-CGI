CREATE DATABASE IF NOT EXISTS my_store;
USE my_store;
create table cart
(session_id varchar(25) not null,
product_id integer not null,
quantity integer not null);
create table products
(product_id integer primary key auto_increment,
product_name varchar(25) not null,
product_desc varchar(25) not null,
product_price float(10,2) not null);
create table order_products
(order_id varchar(25) not null,
product_id integer not null,
quantity integer not null);
create table orders
(order_id varchar(25) primary key,
name varchar(60) not null,
addr varchar(60) not null,
city varchar(60) not null,
state char(2) not null,
zip char(5) not null,
cc_number varchar(20) not null,
cc_type varchar(4) not null,
cc_exp_month char(2) not null,
cc_exp_year char(4) not null);
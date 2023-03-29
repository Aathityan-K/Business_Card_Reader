import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import sqlite3
import os
import re
import io

mydb = sqlite3.connect("OCR.db")
cursor = mydb.cursor()


st.title("Business Card Extraction using OCR")
uploaded_file = st.file_uploader(label="Upload Your Image", type=("jpg", "png", "jpeg"))
result = []

if uploaded_file is not None:
    bi_image = uploaded_file.read()
    file_name, file_extension = os.path.splitext(uploaded_file.name) if uploaded_file.name else ('', '')
    file_path = 'D:\\temp\\'
    file = os.path.join(file_path, file_name + file_extension)

    if os.path.exists(file):
        os.remove(file)
    with open(file, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if file:
        binary_data = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(binary_data))

        reader = easyocr.Reader(['en'])
        result = reader.readtext(np.array(image))
else:
    st.write("Upload the file")

image = Image.open(uploaded_file) if uploaded_file is not None else None
if image is not None:
    st.image(image)


def card_holder_name(output):
    if len(result) > 0 and len(result[0]) > 1:
        name = [result[0][-2]]
        card_holder = ''.join(name)
        return card_holder


def card_holder_designation(output):
    if len(result) > 0 and len(result[1]) > 1:
        designation = [result[1][-2]]
        holder_designation = ''.join(designation)
        return holder_designation


with st.expander("Details"):
    phone_number = ''
    email_address = ''
    website_url = ''
    area = ''
    city = ''
    state = ''
    pincode = ''
    company_name = ''

    for i in result:
        text = i[-2].strip()

        if re.match(r'\d{3}-\d{3}-\d{4}', text):
            phone_number += text
        elif '@' in text:
            email_address += text
        elif '.com' in text:
            website_url += text
        elif re.match(r'\b\w+\s*\d{6}\b', text) or re.match(r'\+\b\w+\s*\d{6}\b', text):
            m, n = text.split()
            state += m
            pincode += n
        elif re.match(r'\d+\s[a-zA-Z]+\s[a-zA-Z]+\s?,\s?[a-zA-Z]+;', text):
            b, c = text.split(',')
            area += b.strip()
            city += c.strip()
        elif re.match(r'\w', text):
            company_name += text

    Card_holder_name = card_holder_name(result)
    Card_holder_designation = card_holder_designation(result)

    error = 0
    Name = st.text_input('First Name', Card_holder_name)
    Phone = st.text_input('Phone Number', phone_number)
    Designation = st.text_input('Designation', Card_holder_designation)
    if len(Phone) == 0:
        error += 1
        st.error('Invalid Phone number')
    companyname = st.text_input('Company Name', company_name)
    if len(companyname) == 0:
        error += 1
        st.error('Invalid Company Name')
    companymail = st.text_input('Mail ID', email_address)
    if len(companymail) == 0:
        error += 1
        st.error('Invalid Mail')
    companywebsite = st.text_input('Website', website_url)
    if len(companywebsite) == 0:
        error += 1
        st.error('Invalid Website link')

    col1, col2 = st.columns(2)
    with col1:
        Area = st.text_input('Area', area)
        if len(Area) == 0:
            error += 1
            st.error("Enter Area")
        City = st.text_input('City', city)
        if len(City) == 0:
            error += 1
            st.error('Enter City')

    with col2:
        State = st.text_input('State', state)
        if len(State) == 0:
            error += 1
            st.error('Enter State')
        Pincode = st.text_input('Pincode', pincode)
        if len(Pincode) == 0:
            error += 1
            st.error('Enter Pincode')

        address = st.text_area('Company Address', Area + ", " + City + ", " + State + ", " + Pincode, disabled=True)
        st.write(Name)

        if error > 0:
            st.button('Upload to Database', key='btn_scrape', disabled=True)
        else:
            st.button('Upload to Database', key='btn_scrape', disabled=False)

        to_db = False


        def creating_database():
            global to_db
            if to_db:
                return

            to_db = True

            cursor.execute('''CREATE TABLE IF NOT EXISTS Card_Reader(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Image BLOB,
                    Name VARCHAR(250),
                    Phone_Number BIGINT,
                    Designation VARCHAR(50),
                    Company_Name VARCHAR(50),
                    Mail VARCHAR(50),
                    Website VARCHAR(50),
                    Area VARCHAR(30),
                    State VARCHAR(30),
                    City VARCHAR(30),
                    Pincode INT(10)
                    );''')
            #   cursor.execute(sql_table)
            mydb.commit()


        creating_database()

        if st.session_state.get("btn_scrape"):
            try:
                cursor.execute(
                    "INSERT INTO Card_Reader(Image, Name, Phone_Number, Designation, Company_Name, Mail, Website, Area,State,City,Pincode)VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (sqlite3.Binary(bi_image), Card_holder_name, Phone, Card_holder_designation, company_name, companymail,
                     companywebsite, Area, State, City, Pincode))
                st.success('Uploaded data successfully')

            except Exception as e:
                st.error(f"Error: {e}")

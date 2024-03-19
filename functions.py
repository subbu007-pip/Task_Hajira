import easyocr
import re
from PIL import  ImageOps
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError



def get_details_from_image(image):#extracting data from image
    try:
        reader = easyocr.Reader(['en'])
        gray_image = ImageOps.grayscale(image)
        #resize the image to improve OCR accuracy
        resized_image = gray_image.resize((int(image.width * 1.5), int(image.height * 1.5)))
        #convert PIL image to numpy array for OpenCV processing
        image_array = np.array(resized_image)
        #apply thresholding to the image to improve text visibility
        _, thresholded_image = cv2.threshold(image_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #OCR works (Optical Character Recognition)
        result = reader.readtext(thresholded_image)
        text_datas=[]
        text_datas.clear()
        for detection in result:
          text = detection[1]
          text_datas.append(text)
        return text_datas
    except Exception as e:
        st.error(f"Error while processing image: {str(e)}")
   

def get_text_df(text_datas,uploaded_file):
    try:
        #using regular expression extract details
        phone_number_pattern = r'\+\d{1,3}-\d{3}-\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b|\b\d{5}-\d{5}\b|\b\d{10}\b'
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        website_pattern = r'(www\.\w+\.\w+)|(https://www\.\w+\.\w+)|(https?://)?(www\.\S+)'
        address_pattern = r'\d+\s+(.*?)$'
        pincode_pattern = r'\b\d{6}\b|\b\d{3}-\d{3}\b'
        company_index=len(text_datas)-1
        final_data = {'Name':text_datas[0],'Designation':text_datas[1],'Address': 'NA','Pincode': 'NA',
                    'Phone_number': 'NA','email_id': 'NA','Website': 'NA','Company':text_datas[company_index]}
        for details in text_datas:
            address= re.search(address_pattern, details)
            pincode = re.search(pincode_pattern, details)
            phone_number = re.search(phone_number_pattern, details)
            email_id= re.search(email_pattern, details)
            website = re.search(website_pattern, details)
            if address:
                final_data['Address'] = address.group()
            if pincode:
                final_data['Pincode'] = pincode.group()
            if phone_number:
                final_data['Phone_number'] = phone_number.group()
            if email_id:
                final_data['email_id'] = email_id.group()
            if website:
                final_data['Website'] = website.group()
        
        final_df= pd.DataFrame([final_data])
        final_df['image']=uploaded_file
        return final_df,final_data
    except Exception as e:
        st.error(f"Error while texting contents: {str(e)}")

def get_id_details():#getting id details
    try:
        connection1,curs1,engine=get_connections()
        details=[]
        curs1.execute("SELECT id FROM business_cards")
        for record in curs1:
            details.append(record)
        ids_columns=pd.DataFrame(details,columns=['ids'])
        close_connections(curs1,connection1)
        return ids_columns
    except Exception as e:
        st.error(f"Error while getting ids: {str(e)}")
        return None 
    
  
def display_contents(final_data):#display contents
    try:
        st.text(f"Name: {final_data['Name']}")
        st.text(f"Designation: {final_data['Designation']}")
        st.text(f"Address: {final_data['Address']}")
        st.text(f"Pincode: {final_data['Pincode']}")
        st.text(f"Phone Number: {final_data['Phone_number']}")
        st.text(f"Email ID: {final_data['email_id']}")
        st.text(f"Website: {final_data['Website']}")
        st.text(f"Company: {final_data['Company']}")
    except Exception as e:
        st.error(f"Error while Displaying contents: {str(e)}")

def get_updates(detail_df):
    name=st.text_input("Name:",f"{detail_df['Name']}")
    designation=st.text_input("Designation:",f"{detail_df['Designation']}")
    address=st.text_input("Address:",f"{detail_df['Address']}")
    pincode=st.text_input("Pincode:",f"{detail_df['Pincode']}")
    phone_number=st.text_input("Phone Number:",f"{detail_df['Phone_number']}")
    email_id=st.text_input("Email ID:",f"{detail_df['email_id']}")
    web=st.text_input("Website:",f"{detail_df['Website']}")
    company_name=st.text_input("Company:",f"{detail_df['Company']}")
    updated_data =[name,designation,address,pincode,phone_number,email_id,web,company_name]
    return updated_data

def get_connections():#for usage connection functions is created separately
    try:
        connection1 = sqlite3.connect('business_card_data.db')
        curs1 = connection1.cursor()
        engine = create_engine('sqlite:///business_card_data.db',echo=True)
        return connection1,curs1,engine
    except Exception as e:
        st.error(f"Error occured while connecting sql {str(e)}")
def close_connections(curs1,connection1):#close function also created separately
    try:
        curs1.close()
        connection1.close()
    except Exception as e:
        st.error(f"Error occured while closing cursor and connection {str(e)}")


def table_creation_sql():
    try:
        table_creation_query='''CREATE TABLE IF NOT EXISTS business_cards ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, designation TEXT, address TEXT,pincode TEXT, phone_number TEXT, email_id TEXT,
                        website TEXT, company TEXT, image BLOB )'''
        connection1,curs1,engine=get_connections()
        curs1.execute(table_creation_query)
        close_connections(curs1,connection1)
    except Exception as e:
        st.error(f"Error while creating table: {str(e)}")

def insert_to_sql(final_df):
    try:
        connection1,curs1,engine=get_connections()
        final_df.to_sql('business_cards', engine, if_exists='append', index=False)
        st.success("Details inserted successfully!")
        close_connections(curs1,connection1)
    except IntegrityError:
        st.error('Table values already Inserted')

def get_details(id):
    try:
        ids_query=f"SELECT * FROM business_cards Where id={id};"
        connection1,curs1,engine=get_connections()
        details=[]
        curs1.execute(ids_query)
        for record in curs1:
            details.append(record)
        columns_fields = ['id', 'Name', 'Designation', 'Address', 'Pincode', 'Phone_number', 'email_id', 'Website', 'Company', 'image']
        df = pd.DataFrame(details, columns=columns_fields)
        close_connections(curs1,connection1)
        return df
    except Exception as e:
        st.error(f"Error Occured getting Data,the error is {str(e)}")

def update_sql(updated_data,selected_id):
    try:
        update_query=f'''UPDATE business_cards SET name=?, designation=?, address=?, pincode=?, phone_number=?, email_id=?, website=?, company=?
                            WHERE id={selected_id}'''
        values=[updated_data[0], updated_data[1], updated_data[2], updated_data[3],
                        updated_data[4], updated_data[5], updated_data[6], updated_data[7]]
        connection1,curs1,engine=get_connections()
        curs1.execute(update_query,updated_data)
        connection1.commit()
        close_connections(curs1,connection1)
        st.success("Record updated successfully!")
    except Exception as e:
        st.error(f"Error Occured While Updating Data,the error is {str(e)}")

def delete_sql_record(selected_id):
    try:
        delete_query=f"DELETE FROM business_cards WHERE id={int(selected_id)}"
        connection1,curs1,engine=get_connections()
        curs1.execute(delete_query)
        connection1.commit()
        close_connections(curs1,connection1)
        st.success(f"Record with ID {selected_id} deleted successfully!")
    except Exception as e:
        st.error(f"Error Occured While Deleting Data,the error is {str(e)}")

def truncate_sql_record():
    try:
        connection1,curs1,engine=get_connections()
        curs1.execute("DELETE FROM business_cards")
        connection1.commit()
        curs1.execute("VACUUM")
        connection1.commit()
        close_connections(curs1,connection1)
        st.success(f"All Records deleted successfully!")
    except Exception as e:
        st.error(f"Error Occured While Deleting All records,the error is {str(e)}")
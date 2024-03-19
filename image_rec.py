from PIL import Image
from io import BytesIO
import streamlit as st
from functions import *
import numpy as np


st.set_page_config(page_title="Business Card Data Management Application", 
                   page_icon="https://img.icons8.com/external-others-phat-plus/64/external-businesscard-business-management-color-line-others-phat-plus.png", layout="wide")
st.title("Extracting Business Card Management Application")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
tab1, tab2= st.tabs([":card_file_box:   FETCH DETAILS       ", ":file_cabinet:    RETRIEVE DETAILS       "])

with tab1:#page for text extraction and save into sql
  uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
  if uploaded_file is not None:
    file_name = uploaded_file.name
    st.write("filename:", file_name)
    if st.button('Fetch & Save Details'):
      with st.spinner('Please Wait,the data are under processing...'):
        #for reading the file
        uploaded_image_data = uploaded_file.read()
        #here image to binary image to PIL image
        image = Image.open(BytesIO(uploaded_image_data))
        image_array = np.array(image)
        image_bytes = image_array.tobytes()
        result=get_details_from_image(image)
        final_df,final_data=get_text_df(result,uploaded_image_data )
        col1, col2 = st.columns(2)
        with col1:
          st.subheader("Uploaded Image")
          st.image(image, caption='Uploaded Card')
        with col2:
          st.subheader("Extracted Business Card Data")
          st.subheader("Individual Data Fields")
          display_contents(final_data)
        table_creation_sql()
        insert_to_sql(final_df)
        
          
with tab2:#page for data updation,deletion
  st.subheader("Retrieve Data from Database")
  id_value=get_id_details()

  if id_value is not None:
    ids=id_value['ids'].unique()
    selected_id=st.selectbox('Select the id to display details',ids)

    if selected_id:
      detail_df=get_details(selected_id)
      st.markdown("""<style>.custom-column {width: 33.33% !important; /* Set equal width for all columns */
        height: 400px !important; /* Set equal height for all columns */display: inline-block;
        margin: 10px; /* Add margin between columns if needed */}</style>""",unsafe_allow_html=True)
      #inorder to use values here series dataframe is converted to dict
      record_dict = detail_df.to_dict(orient='records')[0]
      image_data=record_dict['image']
      
      col1, col2 ,col3= st.columns(3)
      with col1:
        st.markdown("### Business Card Data")
        st.image(image_data)
        truncate_condition=st.button('Delete')
        if truncate_condition:
          truncate_sql_record()
      
      with col2:
        st.markdown("### Details")
        display_contents(record_dict)
        delete_condition=st.button('Delete ')
        if delete_condition:
          delete_sql_record(selected_id)

      with col3:
        st.markdown("### Update Details")
        updated_data=get_updates(record_dict)
        update_condition=st.button('Update')
        if update_condition:
          if len(updated_data) == 8:
            update_sql(updated_data,selected_id)
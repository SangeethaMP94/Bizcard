# Importing the required libraries
import easyocr
import streamlit as st
from PIL import Image
import os
import PIL
import numpy as np
import psycopg2
import re
import pandas as pd
import webbrowser

#setting page configuration in streamlit
st.set_page_config(page_title='Bizcardx Extraction',page_icon="chart_with_upwards_trend", layout="wide")

def insert_datas(res):
    image_dict = {'Name': [], 'Designation': [], 'Company': [], 'Contact': [],'Email': [], 'Website': [],'Address': [], 'Pincode': []}
    
    #To Extract The Name
    name = res[0]
    image_dict['Name'].append(name)
    
    #To Extract The Designation
    designation = res[1]
    image_dict['Designation'].append(designation)

    con = []
    com = []
    for m in range(2,len(res)):
        #To Extract Contact Numbers
        if res[m].startswith('+') and '-' in res[m]:
            con.extend([res[m]])

        #To Extract EMAIL-Id
        elif "@" in res[m] and ".com" in res[m]:
            sm = res[m].lower()
            image_dict['Email'].append(sm)

        #To Extract website link
        elif 'www' in res[m] or 'WWW' in res[m] or 'wwW' in res[m]:
            sm = res[m].lower()
            image_dict['Website'].append(sm)

        #To Extract Pincode
        elif 'Tamil Nadu' in res[m] or 'TamilNadu' in res[m]:
            image_dict['Pincode'].append(res[m])

        #To Extract The Company Name
        elif re.match(r'^[A-Za-z]',res[m]):
           com.extend(res[m])

        else: 
          #To Extract Address
          t =re.sub(r'[.,;]','',res[m])
          image_dict['Address'].append(t)
    
    image_dict['Contact'].append('&'.join(con))
    image_dict['Company'].append(''.join(com))


      
    df = pd.DataFrame.from_dict(image_dict,orient='index').T
    return df

#Establishing connection to database
mydb = psycopg2.connect(user = 'postgres',host = 'localhost', password= 'Tkkrathna26@' , port = '5432' , database = 'Biz')
mycursor = mydb.cursor()

reader = easyocr.Reader(['en'])

#Creating table in sql
query = """create table if not exists Business_card( 
              id serial PRIMARY KEY,
              name TEXT,
              designation TEXT,
              company TEXT,
              contact VARCHAR,
              email TEXT,
              website TEXT,
              address TEXT,
              pincode TEXT)"""

mycursor.execute(query)
mydb.commit()

#Defining The Menu Bar For Streamlit app
option = st.selectbox(
    'Please select any one',
    ('Home', 'Upload'))

st.write('You selected:', option)  

# Creating Home Section
if option == "Home":

    col1,col2 = st.columns([2,2])
    with col1:
        
        st.title("BISUNESS CARD🖼️")
        url = "https://png.pngtree.com/thumb_back/fh260/back_our/20190623/ourmid/pngtree-black-business-atmosphere-business-card-background-image_239793.jpg"
        st.image(url)
    
    with col2:

         
        st.subheader("Business card extraction is the process of digitizing the information on a physical business card and transferring it to a digital format."
                 " This allows the information to be easily stored, organized, and shared electronically."
                     "There are several methods for extracting information from a business card. One option is to manually enter the information into a digital contact management system, such as Microsoft Outlook or Google Contacts.")

# Creating Upload Section
if option == "Upload":
        
        #Uploading file to streamlit app
        upload_card = st.file_uploader('Upload Here', label_visibility= 'collapsed',type= ['png','jpg','jpeg'])      
                    
        if upload_card is not None:
                ig = Image.open(upload_card)
                st.image(ig)

               # Extracting data from image (Image view)    
                result = reader.readtext(np.array(ig))
                
                res = []
                for i in result:
                        res.append(i[1])
                st.write(res) 
                tx = insert_datas(res)
                st.write(tx)
                
                option2 = st.selectbox(
                'Please select any one',
                 ( 'Extract','Modify','Delete'))
                
                # Creating Extract Section
                if option2 == "Extract":
                    
                    #inserting data into table
                    def insert(tx):
                        for index,i in tx.iterrows():
                            insert_values = "INSERT INTO Business_card (Name, Designation, Company, Contact,Email, Website,Address,Pincode) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                            result_values = (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7])
                            mycursor.execute(insert_values,tuple(result_values))
                            mydb.commit()
                    y = insert(tx)
                    st.markdown(":red[Extract Successfully...!]")

                # Creating Modify Section
                if option2 == "Modify":
                    
                    def modify(tx):

                        col_1, col_2 = st.columns([4, 4])

                        dx = {'Name': [], 'Designation': [], 'Company': [], 'Contact': [],'Email': [], 'Website': [],'Address': [], 'Pincode': []}
                        
                        with col_1:

                            edited_name = st.text_input('Name', tx["Name"][0])
                            dx['Name'].append(edited_name)
                            
                            edited_designation = st.text_input('Designation', tx["Designation"][0])
                            dx['Designation'].append(edited_designation)
                            
                            edited_company = st.text_input('Company', tx["Company"][0])
                            dx['Company'].append(edited_company)
                            
                            edited_contact = st.text_input('Contact', tx["Contact"][0])
                            dx['Contact'].append(edited_contact)
                            
                            
                        
                        with col_2:
                            edited_email = st.text_input('Email', tx["Email"][0])
                            dx['Email'].append(edited_email)
                        
                            edited_website = st.text_input('Website', tx["Website"][0])
                            dx['Website'].append(edited_website)
                            
                            edited_address = st.text_input('Address', tx["Address"][0])
                            dx['Address'].append(edited_address)
                            
                            edited_pincode = st.text_input('Pincode', tx["Pincode"][0])
                            dx['Pincode'].append(edited_pincode)

                        updates = st.button("Update and Preview")
                                      
                        if 'updates':
                            
                            names = []
                            mycursor.execute("select Name from Business_card")
                            x = mycursor.fetchall()
                            for i in x:
                                 y = ','.join(i)
                                 names.append(y)

                            dx2 = pd.DataFrame(dx)
                            st.write(dx2)


                            for index,i in dx2.iterrows():

                                    query2 = """update Business_card set Name = %s, Designation = %s, Company = %s, Contact = %s,Email = %s, Website = %s,Address = %s,Pincode = %s where name  = %s """
                                    values = (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[0])
                                    mycursor.execute(query2,tuple(values))
                                    mydb.commit()

                    d = modify(tx)

                ## Creating Delete Section
                if option2 == 'Delete':
                    del_list = []
                    mycursor.execute("select Name from Business_card")
                    d =  mycursor.fetchall()
                    for i in d:
                        z = ','.join(i)
                        del_list.append(z) 
                         
                    
                    option5 = st.selectbox(
                    'Please select any one name to delete',del_list)

                    mycursor.execute(f"delete from Business_card where name ='{option5}' ")
                    mydb.commit()

import streamlit as st
import sqlite3
import time
from datetime import datetime, timedelta
import base64

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('credentials.db')
    return conn



def check_login(username, password):
    return username == "admin" and password == "1234"


# Function to fetch credentials from the database
def fetch_credentials():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM credentials')
    data = cursor.fetchall()
    conn.close()
    return data

# Function to add a new credential to the database
def add_credential(title, site, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO credentials (title, site, username, password) VALUES (?, ?, ?, ?)',
                   (title, site, username, password))
    conn.commit()
    conn.close()

# Function to update a credential in the database
def update_credential(title, site, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE credentials SET title = ?, username = ?, password = ? WHERE site = ?',
                   (title, username, password, site))
    conn.commit()
    conn.close()

# Function to delete a credential from the database
def delete_credential(site):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM credentials WHERE site = ?', (site,))
    conn.commit()
    conn.close()

# Custom CSS for styling
custom_css = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            .st-emotion-cache-1avcm0n {
                display:none
            }
            
            .st-emotion-cache-1y4p8pa {
                padding: 0rem 1rem 10rem;
            }
                        
            .logo-container {
                text-align: center;
                margin-bottom: 20px;
            }
            .logo-container img {
                width: 250px;
                height: auto;
            }
            .st-emotion-cache-19rxjzo {
                width: 90vw;
                height: 10vh;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
            }

            @media (min-width: 1024px) {
                .st-emotion-cache-19rxjzo {
                    width: 690px;
                    height: 60px;
                    max-width: none;
                    max-height: none;
                }
            }

            @media (max-width: 600px) {
                .st-emotion-cache-19rxjzo {
                    width: 90vw;
                    height: 8vh;
                }
            }
            
            .separator {
                border: 0;
                border-top: 1px solid #ccc;
                margin: 10px 0;
            }

            .cancel-button, .edit-button, .delete-button {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px 2px;
                cursor: pointer;
                border-radius: 5px;
            }

            .cancel-button {
                background-color: #f44336;
            }

            .cancel-button:hover {
                background-color: #d32f2f;
            }

            .edit-button:hover {
                background-color: #45a049;
            }

            .delete-button {
                background-color: #f44336;
            }

            .delete-button:hover {
                background-color: #d32f2f;
            }
            </style>
            """
st.markdown(custom_css, unsafe_allow_html=True)

# Insert logo at the top of the page
st.markdown('<div class="logo-container"><img src="https://nexgeno.in/_next/image?url=%2Flogo.png&w=640&q=75" alt="Company Logo"></div>', unsafe_allow_html=True)

# Function to set a cookie
def set_cookie(key, value, expires_at):
    st.session_state.cookies[key] = {
        "value": value,
        "expires_at": expires_at
    }

# Function to get a cookie
def get_cookie(key):
    cookie = st.session_state.cookies.get(key)
    if cookie and datetime.now() < cookie['expires_at']:
        return cookie['value']
    return None

# Initialize cookies if not present
if 'cookies' not in st.session_state:
    st.session_state.cookies = {}

# Set the initial page and session expiration
if 'page' not in st.session_state:
    st.session_state.page = 'login'
    st.session_state.session_expiration = datetime.now() + timedelta(days=7)

# Check session validity
if datetime.now() > st.session_state.session_expiration:
    st.session_state.page = 'login'
    st.session_state.session_expiration = datetime.now() + timedelta(days=7)
    st.session_state.cookies.clear()  # Clear cookies on session expiration

# Login Page
if st.session_state.page == 'login':
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.page = 'main'
            st.session_state.session_expiration = datetime.now() + timedelta(days=7)
            set_cookie('session', base64.b64encode(f"{username}|{password}".encode()).decode(), st.session_state.session_expiration)
            st.rerun()
        else:
            st.error("Invalid username or password")

# Main Page: Search bar and list of sites
if st.session_state.page == 'main':
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    search_query = st.text_input("Search", key="search_query")
    st.markdown('<hr class="separator">', unsafe_allow_html=True)
    
    credentials = fetch_credentials()
    matching_sites = [site for site in credentials if search_query.lower() in site[1].lower() or search_query.lower() in site[2].lower()]

    if matching_sites:
        for site in matching_sites:
            site_name = site[2]
            title_name = site[1]
            if st.button(f"{title_name}"):
                st.session_state.selected_site = site
                st.session_state.page = 'details'
                st.rerun()
    else:
        if search_query:
            st.write("No matching sites found.")
       
    if st.button("+ Add New Credential"):
        st.session_state.page = 'add'
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# Details Page: Show username and password
if st.session_state.page == 'details':
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    selected_site = st.session_state.selected_site
    st.header(f"{selected_site[1]}")  # Display the title
    
    st.text_input("Username", value=selected_site[3])
    st.text_input("Password", value=selected_site[4], type="password")
    
    st.markdown("**Visit Site:** " + f"[{selected_site[2]}]({selected_site[2]})")

    if st.button("Edit", key="edit_button"):
        st.session_state.page = 'edit'
        st.rerun()

    if st.button("Delete", key="delete_button"):
        delete_credential(selected_site[2])
        st.write("Credential deleted successfully!")
        st.session_state.page = 'main'
        st.rerun()
    
    if st.button("Go back"):
        st.session_state.page = 'main'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


# Add New Credential Page: Form to input new username, password, and site
if st.session_state.page == 'add':
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    with st.form(key='add_form'):
        new_title = st.text_input("Title")
        new_site = st.text_input("URL")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        
        submit_button = st.form_submit_button("Add Credential")
        
    if submit_button:
        if new_title and new_site and new_username and new_password:
            add_credential(new_title, new_site, new_username, new_password)
            st.write("Credential added successfully!")
            st.balloons()  # Call this on a separate line
            time.sleep(1.5)

            st.session_state.page = 'main'
            st.rerun()
        else:
            st.error("Please fill out all fields.")

    st.markdown('</div>', unsafe_allow_html=True)


# Edit Credential Page: Form to edit existing username, password, and site
if st.session_state.page == 'edit':
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    selected_site = st.session_state.selected_site
    
    with st.form(key='edit_form'):
        updated_title = st.text_input("Title", value=selected_site[1])
        updated_username = st.text_input("Username", value=selected_site[3])
        updated_password = st.text_input("Password", type="password", value=selected_site[4])
        
        submit_button = st.form_submit_button("Update Credential")
        
        if submit_button:
            if updated_title and updated_username and updated_password:
                update_credential(updated_title, selected_site[2], updated_username, updated_password)
                st.write("Credential updated successfully!")
                st.session_state.page = 'main'
                st.rerun()
            else:
                st.error("Please fill out all fields.")
    
    st.markdown('</div>', unsafe_allow_html=True)




import streamlit as st
import hashlib
import pickle
import os
from datetime import datetime, timedelta

# File to store user data
USER_DB_FILE = "user_database.pkl"

def init_auth():
    """Initialize the authentication system"""
    # Create session state variables if they don't exist
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_error" not in st.session_state:
        st.session_state.login_error = None
    if "signup_error" not in st.session_state:
        st.session_state.signup_error = None

def load_users():
    """Load user database from file"""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "rb") as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save user database to file"""
    with open(USER_DB_FILE, "wb") as f:
        pickle.dump(users, f)

def hash_password(password):
    """Create a secure hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password, email):
    """
    Register a new user
    
    Args:
        username (str): The username for the new account
        password (str): The password for the new account
        email (str): The email for the new account
        
    Returns:
        bool: True if signup successful, False otherwise
    """
    users = load_users()
    
    # Check if username already exists
    if username in users:
        st.session_state.signup_error = "Username already exists. Please choose another."
        return False
    
    # Check if email already exists
    for user in users.values():
        if user.get("email") == email:
            st.session_state.signup_error = "Email already registered. Please use another email."
            return False
    
    # Create user
    users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    save_users(users)
    return True

def login(username, password):
    """
    Authenticate a user
    
    Args:
        username (str): The username to authenticate
        password (str): The password to authenticate
        
    Returns:
        bool: True if login successful, False otherwise
    """
    users = load_users()
    
    # Check if username exists
    if username not in users:
        st.session_state.login_error = "Invalid username or password"
        return False
    
    # Check if password is correct
    if users[username]["password_hash"] != hash_password(password):
        st.session_state.login_error = "Invalid username or password"
        return False
    
    # Update last login time
    users[username]["last_login"] = datetime.now().isoformat()
    save_users(users)
    
    # Set session state
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.login_error = None
    
    return True

def logout():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None

def render_login_page():
    """Render the login page"""
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submit = st.form_submit_button("Login")
        
        if submit:
            if login(username, password):
                st.rerun()
    
    if st.session_state.login_error:
        st.error(st.session_state.login_error)
    
    st.info("Please enter your username and password to access the chart analysis tools.")

def render_signup_page():
    """Render the signup page"""
    st.markdown("<h2 style='text-align: center;'>Create an Account</h2>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not username or not email or not password:
                st.session_state.signup_error = "All fields are required"
            elif password != password_confirm:
                st.session_state.signup_error = "Passwords do not match"
            elif len(password) < 6:
                st.session_state.signup_error = "Password must be at least 6 characters long"
            elif signup(username, password, email):
                # Automatically log in after signup
                login(username, password)
                st.rerun()
    
    if st.session_state.signup_error:
        st.error(st.session_state.signup_error)
    
    st.info("Create an account to access chart analysis tools. Your data is stored securely.")

def require_auth():
    """
    Check if user is authenticated and redirect to login if not
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not st.session_state.authenticated:
        # Add simple tabs for login/signup instead of query params
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            render_login_page()
            
        with signup_tab:
            render_signup_page()
            
        return False
    
    return True
import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from supabase import create_client, Client

# Page configuration
st.set_page_config(
    page_title="Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase setup
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register new user in Supabase"""
    try:
        # Check if username already exists
        existing = supabase.table('users').select('username').eq('username', username).execute()
        
        if existing.data:
            return False, "Username already exists"
        
        # Insert new user
        data = {
            'username': username,
            'email': email,
            'password': hash_password(password)
        }
        
        supabase.table('users').insert(data).execute()
        return True, "Registration successful!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username, password):
    """Authenticate user with Supabase"""
    try:
        # Query user by username
        response = supabase.table('users').select('password').eq('username', username).execute()
        
        if not response.data:
            return False, "Username not found"
        
        stored_password = response.data[0]['password']
        
        if stored_password == hash_password(password):
            return True, "Login successful!"
        
        return False, "Incorrect password"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_info(username):
    """Get user information from Supabase"""
    try:
        response = supabase.table('users').select('email, created_at').eq('username', username).execute()
        
        if response.data:
            return (response.data[0]['email'], response.data[0]['created_at'])
        return None
        
    except Exception as e:
        st.error(f"Error fetching user info: {str(e)}")
        return None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
    }
    .metric-delta {
        font-size: 0.85rem;
        color: #10b981;
        margin-top: 0.5rem;
    }
    .user-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #666;
        margin: 1.5rem 0 1rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .login-container {
        max-width: 500px;
        margin: 3rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        color: #666;
        font-size: 0.95rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .error-message {
        background: #fee;
        color: #c33;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #c33;
        margin: 1rem 0;
    }
    .success-message {
        background: #efe;
        color: #3c3;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3c3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Charts"

# Generate sample data
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(1000, 5000, len(dates)) + np.linspace(1000, 3000, len(dates)),
        'Profit': np.random.randint(200, 1500, len(dates)) + np.linspace(200, 800, len(dates)),
        'Customers': np.random.randint(50, 300, len(dates)),
        'Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], len(dates)),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'Satisfaction': np.random.uniform(3.5, 5.0, len(dates))
    })
    return df

# Dashboard Pages
def show_charts_page():
    st.markdown('<div class="main-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 2rem;">Overview of key metrics and performance indicators</p>', unsafe_allow_html=True)
    
    df = generate_sample_data()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['Sales'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Total Sales</div>
            <div class="metric-value">${total_sales:,.0f}</div>
            <div class="metric-delta">↑ 12.5% from last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_profit = df['Profit'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💎 Total Profit</div>
            <div class="metric-value">${total_profit:,.0f}</div>
            <div class="metric-delta">↑ 8.3% from last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_customers = df['Customers'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Avg Customers</div>
            <div class="metric-value">{avg_customers:.0f}</div>
            <div class="metric-delta">↑ 5.7% from last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_satisfaction = df['Satisfaction'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⭐ Satisfaction</div>
            <div class="metric-value">{avg_satisfaction:.2f}/5.0</div>
            <div class="metric-delta">↑ 0.3 from last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sales = go.Figure()
        fig_sales.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Sales'],
            mode='lines',
            name='Sales',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        fig_sales.update_layout(
            title='📈 Sales Trend Over Time',
            xaxis_title='Date',
            yaxis_title='Sales ($)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12),
            height=400
        )
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col2:
        category_sales = df.groupby('Category')['Sales'].sum().reset_index()
        fig_pie = px.pie(
            category_sales,
            values='Sales',
            names='Category',
            title='🎯 Sales by Category',
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.4
        )
        fig_pie.update_layout(
            font=dict(family='Inter', size=12),
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)

def show_user_data_page():
    st.markdown('<div class="main-header">👥 Registered Users</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 2rem;">View all registered users in the system</p>', unsafe_allow_html=True)
    
    try:
        # Fetch all users from Supabase
        response = supabase.table('users').select('id, username, email, created_at').execute()
        
        if response.data:
            df_users = pd.DataFrame(response.data)
            
            # Format the created_at column
            if 'created_at' in df_users.columns:
                df_users['created_at'] = pd.to_datetime(df_users['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">👥 Total Users</div>
                    <div class="metric-value">{len(df_users)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Get most recent registration
                latest_user = df_users.iloc[-1]['username'] if len(df_users) > 0 else "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🆕 Latest User</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #667eea; margin-top: 0.5rem;">
                        {latest_user}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📊 Active Session</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #667eea; margin-top: 0.5rem;">
                        {st.session_state.username}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 User Database")
            
            # Display users table
            st.dataframe(
                df_users,
                use_container_width=True,
                height=500,
                hide_index=True
            )
            
            # Download button
            csv = df_users.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Users Data as CSV",
                data=csv,
                file_name='users_data.csv',
                mime='text/csv'
            )
        else:
            st.info("No users found in the database.")
            
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")

def show_update_profile_page():
    st.markdown('<div class="main-header">⚙️ Update Profile</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 2rem;">Update your account information</p>', unsafe_allow_html=True)
    
    # Get current user info
    user_info = get_user_info(st.session_state.username)
    
    if user_info:
        current_email, created_at = user_info
        
        # Display current info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">👤 Current Username</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #667eea; margin-top: 0.5rem;">
                    {st.session_state.username}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📧 Current Email</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #667eea; margin-top: 0.5rem;">
                    {current_email}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Update form
        st.markdown("### 🔄 Update Information")
        
        with st.form("update_form"):
            new_email = st.text_input("New Email", value=current_email, placeholder="Enter new email")
            new_username = st.text_input("New Username", value=st.session_state.username, placeholder="Enter new username")
            
            st.markdown("---")
            st.markdown("#### 🔒 Change Password (Optional)")
            
            current_password = st.text_input("Current Password", type="password", placeholder="Enter current password")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                submit_button = st.form_submit_button("💾 Update Profile", use_container_width=True)
            
            if submit_button:
                try:
                    # Update email and username
                    update_data = {}
                    
                    if new_email != current_email:
                        update_data['email'] = new_email
                    
                    if new_username != st.session_state.username:
                        # Check if new username already exists
                        existing = supabase.table('users').select('username').eq('username', new_username).execute()
                        if existing.data:
                            st.error("❌ Username already exists!")
                            st.stop()
                        update_data['username'] = new_username
                    
                    # Update password if provided
                    if current_password:
                        # Verify current password
                        success, message = login_user(st.session_state.username, current_password)
                        if not success:
                            st.error("❌ Current password is incorrect!")
                            st.stop()
                        
                        if new_password and confirm_password:
                            if new_password != confirm_password:
                                st.error("❌ New passwords do not match!")
                                st.stop()
                            elif len(new_password) < 6:
                                st.error("❌ Password must be at least 6 characters!")
                                st.stop()
                            else:
                                update_data['password'] = hash_password(new_password)
                        elif new_password or confirm_password:
                            st.error("❌ Please fill both new password fields!")
                            st.stop()
                    
                    # Perform update if there are changes
                    if update_data:
                        supabase.table('users').update(update_data).eq('username', st.session_state.username).execute()
                        
                        # Update session state if username changed
                        if 'username' in update_data:
                            st.session_state.username = new_username
                        
                        st.success("✅ Profile updated successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.info("ℹ️ No changes to update.")
                        
                except Exception as e:
                    st.error(f"❌ Error updating profile: {str(e)}")
    else:
        st.error("Could not fetch user information.")

def show_dataset_page():
    st.markdown('<div class="main-header">📁 Dataset Explorer</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 2rem;">View and analyze your data</p>', unsafe_allow_html=True)
    
    df = generate_sample_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Total Records</div>
            <div class="metric-value">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📋 Columns</div>
            <div class="metric-value">{len(df.columns)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Date Range</div>
            <div style="font-size: 0.9rem; font-weight: 600; color: #667eea; margin-top: 0.5rem;">
                {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_category = st.multiselect(
            "Category",
            options=df['Category'].unique(),
            default=df['Category'].unique()
        )
    
    with col2:
        selected_region = st.multiselect(
            "Region",
            options=df['Region'].unique(),
            default=df['Region'].unique()
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(df['Date'].min(), df['Date'].max()),
            min_value=df['Date'].min(),
            max_value=df['Date'].max()
        )
    
    filtered_df = df[
        (df['Category'].isin(selected_category)) &
        (df['Region'].isin(selected_region))
    ]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.Timestamp(date_range[0])) &
            (filtered_df['Date'] <= pd.Timestamp(date_range[1]))
        ]
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Data Table")
    
    st.dataframe(
        filtered_df.style.background_gradient(subset=['Sales', 'Profit'], cmap='RdYlGn'),
        use_container_width=True,
        height=500
    )
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv'
    )

# Main app logic
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; padding: 2rem 0;">🔐</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown('''
            <div class="login-header">
                <div class="login-title">Welcome Back</div>
                <div class="login-subtitle">Enter your credentials to access your account</div>
            </div>
            ''', unsafe_allow_html=True)
            
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("Sign In", key="login_btn"):
                    if login_username and login_password:
                        success, message = login_user(login_username, login_password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">Please fill all fields</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('''
            <div class="login-header">
                <div class="login-title">Create Account</div>
                <div class="login-subtitle">Sign up to get started</div>
            </div>
            ''', unsafe_allow_html=True)
            
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("Sign Up", key="register_btn"):
                    if reg_username and reg_email and reg_password and reg_confirm:
                        if reg_password != reg_confirm:
                            st.markdown('<div class="error-message">Passwords do not match</div>', unsafe_allow_html=True)
                        elif len(reg_password) < 6:
                            st.markdown('<div class="error-message">Password must be at least 6 characters</div>', unsafe_allow_html=True)
                        else:
                            success, message = register_user(reg_username, reg_email, reg_password)
                            if success:
                                st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">Please fill all fields</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown(f"""
        <div class="user-profile">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.25rem;">{st.session_state.username}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Administrator</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        
        if st.button("📊 Analytics Dashboard", key="charts", use_container_width=True):
            st.session_state.current_page = "Charts"
            st.rerun()
        
        if st.button("📁 Dataset Explorer", key="dataset", use_container_width=True):
            st.session_state.current_page = "Dataset"
            st.rerun()
        
        if st.button("👥 Registered Users", key="users_data", use_container_width=True):
            st.session_state.current_page = "Users"
            st.rerun()
        
        if st.button("⚙️ Update Profile", key="update_profile", use_container_width=True):
            st.session_state.current_page = "Update"
            st.rerun()
        
        st.markdown('<div class="section-header">Account</div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.current_page = "Charts"
            st.rerun()
    
    if st.session_state.current_page == "Charts":
        show_charts_page()
    elif st.session_state.current_page == "Dataset":
        show_dataset_page()
    elif st.session_state.current_page == "Users":
        show_user_data_page()
    elif st.session_state.current_page == "Update":
        show_update_profile_page()
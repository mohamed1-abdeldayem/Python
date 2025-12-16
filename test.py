import streamlit as st
import hashlib
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DB_FILE = "users.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register new user in database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        )
        result = c.fetchone()
        conn.close()
        
        if result is None:
            return False, "Username not found"
        
        if result[0] == hash_password(password):
            return True, "Login successful!"
        return False, "Incorrect password"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_info(username):
    """Get user information"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT email, created_at FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result

# Initialize database
init_db()

# Custom CSS (same as before)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .auth-page .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main { background-color: #f8f9fa; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    .auth-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 450px;
        margin: 2rem auto;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .dashboard-header {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .page-title {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .page-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 0.95rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    st.markdown('<div class="dashboard-header"><h1 class="page-title">📊 Analytics Dashboard</h1><p class="page-subtitle">Overview of key metrics and performance indicators</p></div>', unsafe_allow_html=True)
    
    df = generate_sample_data()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['Sales'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #667eea; font-size: 0.9rem; margin: 0;'>💰 Total Sales</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>${total_sales:,.0f}</h2>
            <p style='color: #10b981; font-size: 0.85rem; margin: 0;'>↑ 12.5% from last period</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_profit = df['Profit'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #8b5cf6; font-size: 0.9rem; margin: 0;'>💎 Total Profit</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>${total_profit:,.0f}</h2>
            <p style='color: #10b981; font-size: 0.85rem; margin: 0;'>↑ 8.3% from last period</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_customers = df['Customers'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #ec4899; font-size: 0.9rem; margin: 0;'>👥 Avg Customers</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>{avg_customers:.0f}</h2>
            <p style='color: #10b981; font-size: 0.85rem; margin: 0;'>↑ 5.7% from last period</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_satisfaction = df['Satisfaction'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #f59e0b; font-size: 0.9rem; margin: 0;'>⭐ Satisfaction</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>{avg_satisfaction:.2f}/5.0</h2>
            <p style='color: #10b981; font-size: 0.85rem; margin: 0;'>↑ 0.3 from last period</p>
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

def show_dataset_page():
    st.markdown('<div class="dashboard-header"><h1 class="page-title">📁 Dataset Explorer</h1><p class="page-subtitle">View and analyze your data</p></div>', unsafe_allow_html=True)
    
    df = generate_sample_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #667eea; font-size: 0.9rem; margin: 0;'>📊 Total Records</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>{len(df):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #8b5cf6; font-size: 0.9rem; margin: 0;'>📋 Columns</h3>
            <h2 style='color: #1e293b; font-size: 1.8rem; margin: 0.5rem 0;'>{len(df.columns)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #ec4899; font-size: 0.9rem; margin: 0;'>📅 Date Range</h3>
            <h2 style='color: #1e293b; font-size: 1.1rem; margin: 0.5rem 0;'>{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}</h2>
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
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
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
    st.markdown('<div class="auth-page">', unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin: 2rem 0;'><h1 style='color: white; font-size: 3rem;'>🔐</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2 style="color: #2d3748; margin-bottom: 0.5rem;">Welcome Back</h2><p style="color: #718096;">Enter your credentials to access your account</p></div>', unsafe_allow_html=True)
            
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
                            st.markdown(f'<div class="error-msg">{message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-msg">Please fill all fields</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2 style="color: #2d3748; margin-bottom: 0.5rem;">Create Account</h2><p style="color: #718096;">Sign up to get started</p></div>', unsafe_allow_html=True)
            
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Sign Up", key="register_btn"):
                    if reg_username and reg_email and reg_password and reg_confirm:
                        if reg_password != reg_confirm:
                            st.markdown('<div class="error-msg">Passwords do not match</div>', unsafe_allow_html=True)
                        elif len(reg_password) < 6:
                            st.markdown('<div class="error-msg">Password must be at least 6 characters</div>', unsafe_allow_html=True)
                        else:
                            success, message = register_user(reg_username, reg_email, reg_password)
                            if success:
                                st.markdown(f'<div class="success-msg">{message}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="error-msg">{message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-msg">Please fill all fields</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem 0 1rem 0;'>
            <div style='width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 50%; margin: 0 auto 1rem auto; display: flex; align-items: center; justify-content: center;'>
                <span style='font-size: 2.5rem;'>👤</span>
            </div>
            <h3 style='color: white; margin: 0;'>{st.session_state.username}</h3>
            <p style='color: #94a3b8; font-size: 0.85rem;'>Administrator</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 2px; background: rgba(255,255,255,0.1); margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin: 1rem 0 0.5rem 0;'>Navigation</h4>", unsafe_allow_html=True)
        
        if st.button("📊 Analytics Dashboard", key="charts", use_container_width=True):
            st.session_state.current_page = "Charts"
            st.rerun()
        
        if st.button("📁 Dataset Explorer", key="dataset", use_container_width=True):
            st.session_state.current_page = "Dataset"
            st.rerun()
        
        st.markdown("<div style='height: 2px; background: rgba(255,255,255,0.1); margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin: 1rem 0 0.5rem 0;'>Account</h4>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.current_page = "Charts"
            st.rerun()
    
    if st.session_state.current_page == "Charts":
        show_charts_page()
    else:
        show_dataset_page()
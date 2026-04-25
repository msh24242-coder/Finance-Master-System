import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page & Theme Configuration
st.set_page_config(page_title="SPAR Budget Control", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Segoe UI'; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-weight: bold; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff00; }
    .stDataFrame { border: 1px solid #00ff00; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⬛ SPAR Marketing LPO Control")

# 2. Smart File Loader
def find_data_file():
    path = 'Data'
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        for f in files:
            if 'Sheet1' in f or 'LPO' in f: return os.path.join(path, f)
        if files: return os.path.join(path, files[0])
    return None

file_path = find_data_file()

# 3. Sidebar Control
st.sidebar.header("🕹️ Control Panel")
monthly_budget = st.sidebar.number_input("Monthly Budget (QR):", min_value=0, value=70000)

if not file_path:
    st.error("❌ Data file missing. Please check your 'Data' folder.")
else:
    try:
        # Load Data
        df = pd.read_csv(file_path, skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Clean Data
        df = df[df['company name'].notna()].copy()

        # --- 4. THE REFERENCE NUMBER GENERATOR (Your Formula) ---
        # Formula: NO + "-" + company + LPO + "-" + Quotation + "-" + Finance + Received
        def generate_ref(row):
            no = str(row.get('NO', '')).split('.')[0] # Remove decimals if any
            company = str(row.get('company name', ''))
            lpo = str(row.get('LPO Number', '')).split('.')[0]
            quotation = str(row.get('Qutation numbr', '')).split('.')[0]
            finance = str(row.get('finance', ''))
            received = str(row.get('Receved ', ''))
            
            return f"{no}-{company}{lpo}-{quotation}-{finance}-{received}"

        df['Generated_Ref'] = df.apply(generate_ref, axis=1)

        # 5. Date & Month Handling
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['Month_Year'] = df['date'].dt.strftime('%B %Y').fillna("Other/Pending")
        
        months = df['Month_Year'].unique().tolist()
        selected_month = st.sidebar.selectbox("Select Month:", months)

        # 6. Financial Logic
        malls = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
        for col in malls:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        month_df = df[df['Month_Year'] == selected_month].copy()
        month_df['Total_Spent'] = month_df[[c for c in malls if c in month_df.columns]].sum(axis=1)
        
        spent = month_df['Total_Spent'].sum()
        remaining = monthly_budget - spent
        usage = (spent / monthly_budget * 100) if monthly_budget > 0 else 0

        # --- Display Layout ---
        st.success(f"Linked File: {os.path.basename(file_path)}")

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("BUDGET LIMIT", f"{monthly_budget:,.0f} QR")
        with col2: st.metric("ACTUAL SPENT", f"{spent:,.2f} QR")
        with col3: st.metric("REMAINING", f"{remaining:,.2f} QR")

        st.write(f"### Budget Utilization: {usage:.1f}%")
        st.progress(min(usage/100, 1.0))

        st.divider()

        # Detailed Table with Generated Reference
        st.subheader(f"Detailed LPO Records: {selected_month}")
        display_cols = ['Generated_Ref', 'date', 'Items', 'Total_Spent']
        existing_malls = [m for m in malls if m in month_df.columns]
        
        st.dataframe(month_df[display_cols + existing_malls], use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

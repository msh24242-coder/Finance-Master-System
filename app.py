import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Settings
st.set_page_config(page_title="SPAR Budget Control", layout="wide")

# Styling: SPAR Green Theme & English Language
st.markdown("""
    <style>
    .stApp { background-color: #004d26; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Segoe UI'; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; }
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    section[data-testid="stSidebar"] { background-color: #003d1e; border-right: 1px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🟢 SPAR Marketing Monthly Budget Control")

# 1. Sidebar for Budget & Month Selection
st.sidebar.header("📊 Budget Setup")
monthly_budget = st.sidebar.number_input("Set Monthly Budget (QR):", min_value=0, value=70000)

# File path
file_path = 'Data/LPO DATA 2023 jan Jihad.xlsx - Sheet1.csv'

if not os.path.exists(file_path):
    st.error("❌ Data file missing in 'Data' folder.")
else:
    try:
        # 2. Read Data
        df = pd.read_csv(file_path, skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filter only active LPOs
        df = df[df['LPO Number'].notna()].copy()
        
        # 3. Create the Reference Number (Applying your Excel Formula)
        # Formula: A&"-"&D&C&"-"&E&"-"&F&G
        # A: NO, D: company name, C: LPO Number, E: Qutation numbr, F: finance, G: Receved
        df['Ref_Number'] = (
            df['NO'].astype(str) + "-" + 
            df['company name'].astype(str) + 
            df['LPO Number'].astype(str) + "-" + 
            df['Qutation numbr'].astype(str) + "-" + 
            df['finance'].astype(str) + 
            df['Receved '].astype(str)
        )

        # 4. Handle Dates & Months
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['Month_Year'] = df['date'].dt.strftime('%B %Y')

        # Month Selector
        available_months = df['Month_Year'].dropna().unique().tolist()
        selected_month = st.sidebar.selectbox("Select Tracking Month:", available_months)

        # 5. Financial Calculations for the selected month
        mall_cols = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
        for col in mall_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Filter DF for current month
        month_df = df[df['Month_Year'] == selected_month].copy()
        month_df['Total_Spent'] = month_df[mall_cols].sum(axis=1)
        
        actual_total = month_df['Total_Spent'].sum()
        balance = monthly_budget - actual_total
        utilization = (actual_total / monthly_budget) * 100 if monthly_budget > 0 else 0

        # --- Dashboard Display ---
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Allocated Budget", f"{monthly_budget:,.2f} QR")
        with m2:
            st.metric("Actual Expenses", f"{actual_total:,.2f} QR")
        with m3:
            st.metric("Remaining Balance", f"{balance:,.2f} QR", delta=f"{balance:,.0f}")

        # Budget Progress Bar
        st.subheader(f"Budget Utilization: {selected_month}")
        st.progress(min(utilization/100, 1.0))
        st.write(f"Consumed: **{utilization:.1f}%**")

        st.divider()

        # Charts
        l_col, r_col = st.columns(2)
        with l_col:
            st.subheader("Expenses by Branch")
            branch_totals = month_df[mall_cols].sum().reset_index()
            branch_totals.columns = ['Branch', 'Amount']
            fig_pie = px.pie(branch_totals[branch_totals['Amount']>0], values='Amount', names='Branch', 
                             hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)

        with r_col:
            st.subheader("Top Vendors this Month")
            top_v = month_df.groupby('company name')['Total_Spent'].sum().nlargest(5).reset_index()
            fig_bar = px.bar(top_v, x='company name', y='Total_Spent', color_discrete_sequence=['#00ff00'])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Detailed Table
        st.subheader("LPO Tracker & Reference Numbers")
        # Showing the generated Ref Number clearly in the table
        display_cols = ['Ref_Number', 'date', 'Items', 'Total_Spent'] + mall_cols
        st.dataframe(month_df[display_cols], use_container_width=True)

    except Exception as e:
        st.error(f"Error processing records: {e}")

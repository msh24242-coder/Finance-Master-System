import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. إعدادات الصفحة والواجهة السوداء (Pure Black Theme)
st.set_page_config(page_title="SPAR Black Edition", layout="wide")

st.markdown("""
    <style>
    /* خلفية التطبيق سوداء بالكامل */
    .stApp {
        background-color: #000000;
    }
    
    /* تغيير ألوان النصوص للأبيض */
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* صناديق الإحصائيات (Metrics) */
    [data-testid="stMetricValue"] {
        color: #00ff00 !important; /* أخضر فسفوري للأرقام */
        font-weight: bold;
    }
    
    /* القائمة الجانبية سوداء بحدود خضراء */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #00ff00;
    }

    /* تحسين شكل الجداول لتناسب الخلفية السوداء */
    .stDataFrame {
        border: 1px solid #00ff00;
        border-radius: 5px;
    }
    
    /* أزرار الإدخال */
    .stNumberInput input {
        background-color: #1a1a1a !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⬛ SPAR Marketing LPO Control - Black Edition")

# 2. وظيفة البحث عن الملف وتجهيز البيانات
def find_data():
    folder = 'Data'
    if os.path.exists(folder):
        files = [f for f in os.listdir(folder) if f.endswith('.csv')]
        for f in files:
            if 'Sheet1' in f: return os.path.join(folder, f)
        if files: return os.path.join(folder, files[0])
    return None

file_path = find_data()

# 3. إعدادات الميزانية في القائمة الجانبية
st.sidebar.header("🕹️ Control Panel")
monthly_budget = st.sidebar.number_input("Monthly Budget (QR):", min_value=0, value=70000)

if not file_path:
    st.error("❌ Data file missing. Please check your 'Data' folder.")
else:
    try:
        # قراءة الملف
        df = pd.read_csv(file_path, skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['LPO Number'].notna()].copy()

        # تطبيق معادلة الـ Reference الخاصة بك
        df['Reference_Full'] = (
            df['NO'].astype(str) + "-" + 
            df['company name'].astype(str) + 
            df['LPO Number'].astype(str) + "-" + 
            df['Qutation numbr'].astype(str) + "-" + 
            df['finance'].astype(str) + 
            df['Receved '].astype(str)
        )

        # معالجة الشهور
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['Month_Year'] = df['date'].dt.strftime('%B %Y')
        
        months = df['Month_Year'].dropna().unique().tolist()
        selected_month = st.sidebar.selectbox("Select Month:", months if months else ["No Data"])

        # حساب المصاريف
        malls = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
        for col in malls:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        month_df = df[df['Month_Year'] == selected_month].copy()
        month_df['Total_Spent'] = month_df[malls].sum(axis=1)
        
        spent = month_df['Total_Spent'].sum()
        remaining = monthly_budget - spent
        usage = (spent / monthly_budget * 100) if monthly_budget > 0 else 0

        # --- عرض البيانات ---
        
        # البطاقات العلوية
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("BUDGET LIMIT", f"{monthly_budget:,.0f} QR")
        with m2:
            st.metric("ACTUAL SPENT", f"{spent:,.2f} QR")
        with m3:
            st.metric("REMAINING", f"{remaining:,.2f} QR")

        # بار الميزانية
        st.write(f"### Budget Consumption: {usage:.1f}%")
        st.progress(min(usage/100, 1.0))

        st.divider()

        # الرسوم البيانية (خلفية شفافة لتناسب السواد)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Expenses by Branch")
            b_data = month_df[malls].sum().reset_index()
            b_data.columns = ['Branch', 'Amount']
            fig_p = px.pie(b_data[b_data['Amount']>0], values='Amount', names='Branch', hole=0.6,
                           color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
            st.plotly_chart(fig_p, use_container_width=True)

        with c2:
            st.subheader("Spending Analysis")
            fig_b = px.bar(month_df.groupby('company name')['Total_Spent'].sum().reset_index(), 
                           x='company name', y='Total_Spent', color_discrete_sequence=['#00ff00'])
            fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_b, use_container_width=True)

        # الجدول التفصيلي
        st.subheader(f"Detailed Logs: {selected_month}")
        st.dataframe(month_df[['Reference_Full', 'date', 'Items', 'Total_Spent'] + malls], use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

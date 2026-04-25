import streamlit as st
import pandas as pd
import os

# 1. إعدادات الهوية البصرية (سواد تام وخطوط واضحة)
st.set_page_config(page_title="SPAR Control Panel", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-weight: bold; font-size: 2.5rem; }
    section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1a1a1a; }
    .stDataFrame { border: 1px solid #333; border-radius: 8px; }
    /* إخفاء أي رسائل خطأ افتراضية من ستريم ليت */
    .stException { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. البحث عن البيانات بصمت
def load_data():
    folder = 'Data'
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.csv') and ('Sheet1' in f or 'LPO' in f):
                df = pd.read_csv(os.path.join(folder, f), skiprows=1)
                df.columns = [str(c).strip() for c in df.columns]
                return df
    return None

# 3. واجهة التحكم الجانبية
st.sidebar.title("SYSTEM CONTROL")
budget_input = st.sidebar.number_input("MONTHLY BUDGET (QR)", value=70000)

data = load_data()

if data is None:
    st.title("⬛ SYSTEM STANDBY")
    st.info("Waiting for Data Input... Please ensure CSV is in /Data folder.")
else:
    # معالجة البيانات
    df = data[data['company name'].notna()].copy()
    
    # تطبيق معادلة الرقم المرجعي (Ref Number)
    def make_ref(row):
        no = str(row.get('NO', '')).split('.')[0]
        comp = str(row.get('company name', ''))
        lpo = str(row.get('LPO Number', '')).split('.')[0]
        quot = str(row.get('Qutation numbr', '')).split('.')[0]
        fin = str(row.get('finance', ''))
        recv = str(row.get('Receved ', ''))
        return f"{no}-{comp}{lpo}-{quot}-{fin}-{recv}"

    df['REFERENCE_ID'] = df.apply(make_ref, axis=1)

    # معالجة التاريخ والشهور
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['Month'] = df['date'].dt.strftime('%B %Y').fillna("PENDING")
    
    # اختيار الشهر
    selected_month = st.sidebar.selectbox("SELECT MONTH", df['Month'].unique())
    
    # الحسابات المالية
    malls = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
    for m in malls:
        if m in df.columns: df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0)
    
    month_data = df[df['Month'] == selected_month].copy()
    total_spent = month_data[[c for c in malls if c in month_data.columns]].sum().sum()
    remaining = budget_input - total_spent

    # --- العرض النهائي ---
    st.title(f"SPAR BUDGET TRACKER - {selected_month.upper()}")
    
    # عرض الأرقام الكبيرة فقط
    c1, c2, c3 = st.columns(3)
    c1.metric("TARGET BUDGET", f"{budget_input:,.0f}")
    c2.metric("ACTUAL EXPENSES", f"{total_spent:,.2f}")
    c3.metric("REMAINING BALANCE", f"{remaining:,.2f}")

    st.divider()

    # عرض الجدول التفصيلي (لب الموضوع)
    st.subheader("TRANSACTION LOG & REFERENCE CODES")
    cols_to_display = ['REFERENCE_ID', 'date', 'Items'] + [m for m in malls if m in month_data.columns]
    st.dataframe(month_data[cols_to_display], use_container_width=True, hide_index=True)

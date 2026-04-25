import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="نظام إدارة LPO", layout="wide")

st.title("📊 لوحة تحكم الارتباطات المالية (LPO)")

# التحقق من وجود المجلد والملف
data_path = 'Data/lpo_tracker.csv'

if not os.path.exists(data_path):
    st.error(f"❌ لم يتم العثور على ملف البيانات في المسار: {data_path}")
    st.info("تأكد من أن اسم الملف في GitHub هو lpo_tracker.csv وموجود داخل مجلد Data")
else:
    try:
        # قراءة البيانات
        df = pd.read_csv(data_path)
        df.columns = df.columns.str.strip()
        
        # تحويل الأرقام
        if 'finance' in df.columns:
            df['finance'] = pd.to_numeric(df['finance'], errors='coerce').fillna(0)

            # --- عرض المؤشرات ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي المبالغ", f"{df['finance'].sum():,.2f} QR")
            with col2:
                st.metric("عدد الطلبات", len(df))
            with col3:
                st.metric("الموردين", df['company name'].nunique() if 'company name' in df.columns else 0)

            # --- الرسم البياني ---
            if 'company name' in df.columns:
                st.subheader("📈 توزيع المصاريف")
                fig = px.bar(df, x='company name', y='finance', color='company name')
                st.plotly_chart(fig, use_container_width=True)

            # --- الجدول ---
            st.subheader("📑 جدول البيانات")
            st.dataframe(df)
        else:
            st.warning("⚠️ لم يتم العثور على عمود باسم 'finance' في ملفك.")
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")

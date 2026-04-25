import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="نظام إدارة LPO", layout="wide")

st.title("📊 لوحة تحكم الارتباطات المالية (LPO)")

data_path = 'Data/lpo_tracker.csv'

if not os.path.exists(data_path):
    st.error(f"❌ لم يتم العثور على ملف: {data_path}")
else:
    try:
        # قراءة الملف
        df = pd.read_csv(data_path)
        
        # تنظيف أسماء الأعمدة (حذف المسافات وتحويلها لأحرف صغيرة للبحث)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # البحث عن عمود المالية (سواء كان اسمه finance أو Finance أو finance )
        finance_col = next((c for c in df.columns if 'finance' in c), None)
        company_col = next((c for c in df.columns if 'company' in c), None)

        if finance_col:
            # تحويل البيانات لأرقام
            df[finance_col] = pd.to_numeric(df[finance_col], errors='coerce').fillna(0)

            # --- عرض المؤشرات ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي المبالغ", f"{df[finance_col].sum():,.2f} QR")
            with col2:
                st.metric("عدد الطلبات", len(df))
            with col3:
                vendor_count = df[company_col].nunique() if company_col else 0
                st.metric("عدد الموردين", vendor_count)

            # --- الرسم البياني ---
            if company_col:
                st.subheader("📈 توزيع المصاريف حسب الشركة")
                fig = px.bar(df, x=company_col, y=finance_col, 
                             color=company_col, text_auto='.2s')
                st.plotly_chart(fig, use_container_width=True)

            # --- عرض الجدول الأصلي ---
            st.subheader("📑 جدول البيانات التفصيلي")
            st.dataframe(df, use_container_width=True)
            
        else:
            st.warning("⚠️ لم أجد عموداً يحتوي على كلمة 'finance'. الأعمدة الموجودة في ملفك هي:")
            st.write(list(df.columns))
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")

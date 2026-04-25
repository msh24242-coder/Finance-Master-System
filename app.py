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
        
        # تنظيف أسماء الأعمدة لضمان عدم وجود مسافات
        df.columns = [str(c).strip() for c in df.columns]

        # استخدام الأسماء الحقيقية التي ظهرت في ملفك
        finance_col = 'total_amount'
        company_col = 'vendor_name'
        paid_col = 'paid_amount'
        balance_col = 'balance'

        # تحويل الأعمدة المالية لأرقام
        for col in [finance_col, paid_col, balance_col]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- عرض المؤشرات المالية (Metrics) ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي قيمة الـ LPOs", f"{df[finance_col].sum():,.2f} QR")
        with col2:
            st.metric("المبالغ المدفوعة", f"{df[paid_col].sum():,.2f} QR")
        with col3:
            st.metric("المبالغ المتبقية", f"{df[balance_col].sum():,.2f} QR")
        with col4:
            st.metric("عدد المعاملات", len(df))

        # --- الرسوم البيانية ---
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📈 أعلى 5 موردين من حيث القيمة")
            top_vendors = df.groupby(company_col)[finance_col].sum().nlargest(5).reset_index()
            fig_bar = px.bar(top_vendors, x=company_col, y=finance_col, color=finance_col,
                             labels={finance_col: 'الإجمالي', company_col: 'المورد'})
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("📋 حالة الدفعات")
            if 'status' in df.columns:
                fig_pie = px.pie(df, names='status', title="توزيع حالات الـ LPO")
                st.plotly_chart(fig_pie, use_container_width=True)

        # --- جدول البيانات ---
        st.subheader("📑 كشف البيانات التفصيلي")
        st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")

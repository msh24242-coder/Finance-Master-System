import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="SPAR LPO System", layout="wide")

st.title("📊 نظام عرض بيانات SPAR LPO")

# المسار الدقيق للملف في مجلد Data
file_path = 'Data/LPO DATA 2023 jan Jihad.xlsx - Sheet1.csv'

if not os.path.exists(file_path):
    st.error(f"❌ لم يتم العثور على الملف في المسار المذكور.")
else:
    try:
        # 1. قراءة الملف مع تخطي السطر الأول (العنوان الكبير)
        df = pd.read_csv(file_path, skiprows=1)
        
        # 2. تنظيف أسماء الأعمدة من المسافات
        df.columns = [str(c).strip() for c in df.columns]

        # 3. فلترة البيانات: الاحتفاظ فقط بالأسطر التي تحتوي على رقم LPO حقيقي
        # هذا يمنع ظهور أي معلومات عشوائية من أسفل الملف
        df = df[df['LPO Number'].notna()]
        
        # 4. تحديد أعمدة الفروع (المولات) لتحويلها لأرقام
        mall_cols = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office', 'All Stores', 'Others']
        for col in mall_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. حساب الإجمالي الفعلي (Actual Total) لكل سطر بناءً على توزيع المبالغ في المولات
        df['Total Amount'] = df[mall_cols].sum(axis=1)

        # --- عرض الواجهة ---
        
        # الإحصائيات العلوية
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("إجمالي مبالغ الـ LPOs", f"{df['Total Amount'].sum():,.2f} QR")
        with c2:
            st.metric("عدد الشركات المذكورة", df['company name'].nunique())
        with c3:
            st.metric("عدد العمليات (LPOs)", len(df))

        st.divider()

        # الجداول والرسوم
        tab1, tab2 = st.tabs(["📑 الجدول الكامل من الملف", "📈 تحليل المصاريف"])

        with tab1:
            st.subheader("البيانات كما هي في الملف الأصلي")
            # عرض الأعمدة التي تهمك فقط لسهولة القراءة
            important_cols = ['LPO Number', 'company name', 'date', 'Items', 'Total Amount'] + [c for c in mall_cols if c in df.columns]
            st.dataframe(df[important_cols], use_container_width=True)

        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("توزيع المبالغ على الفروع")
                branch_sums = df[mall_cols].sum().reset_index()
                branch_sums.columns = ['Branch', 'Value']
                branch_sums = branch_sums[branch_sums['Value'] > 0]
                fig = px.pie(branch_sums, values='Value', names='Branch', hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_b:
                st.subheader("أكبر 5 موردين")
                vendor_sums = df.groupby('company name')['Total Amount'].sum().nlargest(5).reset_index()
                fig_v = px.bar(vendor_sums, x='company name', y='Total Amount', color='Total Amount')
                st.plotly_chart(fig_v, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ: {e}")

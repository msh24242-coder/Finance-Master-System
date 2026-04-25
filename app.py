import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="نظام ميزانية SPAR", layout="wide")
st.title("📊 لوحة تحكم ميزانية سبار (SPAR)")

# المسار الدقيق الذي ذكرته
file_path = 'Data/LPO DATA 2023 jan Jihad.csv'

if not os.path.exists(file_path):
    st.error(f"❌ لم يتم العثور على الملف في المسار: {file_path}")
    st.info("تأكد من أن اسم الملف في GitHub مطابق تماماً للاسم أعلاه (بما في ذلك المسافات).")
else:
    try:
        # 1. قراءة الملف مع تخطي السطر الأول (العنوان الرئيسي)
        df = pd.read_csv(file_path, skiprows=1)
        
        # 2. تنظيف أسماء الأعمدة من المسافات
        df.columns = [str(c).strip() for c in df.columns]

        # 3. فلترة البيانات: الاحتفاظ فقط بالأسطر التي تحتوي على رقم LPO حقيقي
        df = df[df['LPO Number'].notna()]
        
        # 4. تحديد أعمدة الفروع (المولات) لتحويلها لأرقام
        mall_cols = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
        for col in mall_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. حساب الإجمالي الفعلي (Actual Total) بناءً على مجموع الفروع
        df['Total Amount'] = df[[c for c in mall_cols if c in df.columns]].sum(axis=1)

        # --- الواجهة الرسومية ---
        st.success(f"✅ تم ربط الملف بنجاح: {os.path.basename(file_path)}")
        
        # صناديق المؤشرات
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("إجمالي المبالغ المصروفة", f"{df['Total Amount'].sum():,.2f} QR")
        with c2:
            st.metric("عدد الموردين", df['company name'].nunique())
        with c3:
            st.metric("عدد الـ LPOs", len(df))

        st.divider()

        # الرسوم البيانية
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("📍 توزيع الميزانية حسب الفرع")
            branch_sums = df[mall_cols].sum().reset_index()
            branch_sums.columns = ['Branch', 'Value']
            branch_sums = branch_sums[branch_sums['Value'] > 0]
            fig_pie = px.pie(branch_sums, values='Value', names='Branch', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.subheader("🏢 أعلى 5 موردين")
            vendor_sums = df.groupby('company name')['Total Amount'].sum().nlargest(5).reset_index()
            fig_bar = px.bar(vendor_sums, x='company name', y='Total Amount', color='Total_Amount' if 'Total_Amount' in vendor_sums else None)
            st.plotly_chart(fig_bar, use_container_width=True)

        # الجدول التفصيلي
        st.subheader("📑 كشف البيانات التفصيلي")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

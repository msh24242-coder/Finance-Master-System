import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="SPAR LPO Analytics", layout="wide")
st.title("📊 لوحة تحكم ميزانية سبار (SPAR)")

# المسار الذي ذكرته
folder_path = 'Data'

# البحث عن الملف داخل مجلد Data
def get_data():
    if not os.path.exists(folder_path):
        return None
    # البحث عن أي ملف ينتهي بـ .csv (لأن GitHub يحول الملفات المرفوعة أحياناً أو نستخدم نسخة الـ CSV)
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if files:
        return os.path.join(folder_path, files[0])
    return None

file_path = get_data()

if not file_path:
    st.error(f"❌ لم يتم العثور على ملف البيانات في مجلد: {folder_path}")
    st.info("تأكد من أن الملف موجود داخل مجلد Data في GitHub وأن صيغته CSV")
else:
    try:
        # قراءة الملف مع تخطي السطر الأول لأنه عنوان "SPAR MARKETING..."
        df = pd.read_csv(file_path, skiprows=1)
        
        # تنظيف أسماء الأعمدة
        df.columns = [str(c).strip() for c in df.columns]

        # تحديد أعمدة الفروع (المولات) لتحويلها لأرقام وجمعها
        malls = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office', 'All Stores', 'Others']
        available_malls = [m for m in malls if m in df.columns]
        
        for m in available_malls:
            df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0)
            
        # حساب الإجمالي لكل سطر (مجموع المولات)
        df['Total_Amount'] = df[available_malls].sum(axis=1)

        # الموردين والـ LPO
        vendor_col = 'company name'
        lpo_col = 'LPO Number'

        # --- صناديق المعلومات ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("إجمالي الميزانية المرصودة", f"{df['Total_Amount'].sum():,.2f} QR")
        with c2:
            st.metric("عدد الموردين", df[vendor_col].nunique() if vendor_col in df.columns else 0)
        with c3:
            st.metric("عدد طلبات LPO", len(df[df[lpo_col].notna()]) if lpo_col in df.columns else len(df))

        st.divider()

        # --- الرسوم البيانية ---
        col_left, col_right = st.columns(2)
        
        with col_left:
            if vendor_col in df.columns:
                st.subheader("🏢 أعلى 10 موردين (قيمة التعاقدات)")
                top_v = df.groupby(vendor_col)['Total_Amount'].sum().nlargest(10).reset_index()
                fig_bar = px.bar(top_v, x=vendor_col, y='Total_Amount', color='Total_Amount', template="plotly_dark")
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("📍 توزيع الميزانية على الفروع")
            branch_totals = df[available_malls].sum().reset_index()
            branch_totals.columns = ['Branch', 'Amount']
            fig_pie = px.pie(branch_totals, values='Amount', names='Branch', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- الجدول ---
        st.subheader("📑 التفاصيل الكاملة للبيانات")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")

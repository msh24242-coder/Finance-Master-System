import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="نظام إدارة SPAR LPO", layout="wide")

st.title("📊 لوحة تحكم ميزانية التسويق (SPAR)")

# مسار الملف الحقيقي
data_path = 'Data/lpo_tracker.csv'

if not os.path.exists(data_path):
    st.error(f"❌ لم يتم العثور على ملف البيانات في: {data_path}")
else:
    try:
        # قراءة الملف مع تخطي السطر الأول (لأن العنوان يبدأ من السطر الثاني في ملفك)
        df = pd.read_csv(data_path, skiprows=1)
        
        # تنظيف أسماء الأعمدة من المسافات
        df.columns = [str(c).strip() for c in df.columns]

        # تعيين الأعمدة بناءً على ملفك الحقيقي
        finance_col = 'finance'
        company_col = 'company name'
        lpo_col = 'LPO Number'
        status_col = 'invoice'

        # تحويل عمود المالية إلى أرقام (مع التعامل مع العملات إذا وجدت)
        df[finance_col] = pd.to_numeric(df[finance_col], errors='coerce').fillna(0)

        # --- صناديق المؤشرات ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الميزانية (LPOs)", f"{df[finance_col].sum():,.2f} QR")
        with col2:
            st.metric("عدد المعاملات", len(df[df[lpo_col].notna()]))
        with col3:
            st.metric("عدد الشركات الموردة", df[company_col].nunique())

        st.divider()

        # --- الرسوم البيانية ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🏢 أعلى 10 شركات من حيث القيمة")
            top_vendors = df.groupby(company_col)[finance_col].sum().nlargest(10).reset_index()
            fig_bar = px.bar(top_vendors, x=company_col, y=finance_col, color=finance_col,
                             labels={finance_col: 'الإجمالي', company_col: 'الشركة'})
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("📍 توزيع المصاريف حسب الفروع")
            # تجميع المبالغ للفروع (Tawar, 03 mall, Bsquare, etc.)
            branches = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
            branch_totals = {}
            for b in branches:
                if b in df.columns:
                    branch_totals[b] = pd.to_numeric(df[b], errors='coerce').sum()
            
            branch_df = pd.DataFrame(list(branch_totals.items()), columns=['Branch', 'Amount'])
            fig_pie = px.pie(branch_df, values='Amount', names='Branch', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- الجدول التفاعلي ---
        st.subheader("📑 كشف البيانات الشامل")
        st.dataframe(df[[lpo_col, company_col, finance_col, status_col, 'date']].dropna(subset=[lpo_col]), use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
        st.info("تأكد من أن الملف مرفوع بشكل صحيح في مجلد Data")

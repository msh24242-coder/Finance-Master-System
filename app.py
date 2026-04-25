import pandas as pd

# تعيين مسار الملف (تأكد أن اسم الملف هنا يطابق ما رفعته في مجلد Data)
FILE_PATH = 'Data/lpo_tracker.csv' 

def run_finance_system():
    try:
        # قراءة الملف
        df = pd.read_csv(FILE_PATH)
        
        # تنظيف أسماء الأعمدة من أي مسافات زائدة
        df.columns = df.columns.str.strip()

        print("--- نظام إدارة الـ LPOs: تم تحميل البيانات بنجاح ---")
        
        # 1. عرض ملخص عام (بناءً على أعمدتك: LPO Number, company name, finance)
        # ملاحظة: سنعتبر عمود 'finance' هو المبلغ الإجمالي للـ LPO
        if 'finance' in df.columns:
            total_finance = pd.to_numeric(df['finance'], errors='coerce').sum()
            print(f"إجمالي قيمة الارتباطات المالية (LPOs): {total_finance}")
        
        # 2. البحث عن الشركات الأكثر تعاملاً
        if 'company name' in df.columns:
            top_vendors = df['company name'].value_counts().head(3)
            print("\n--- أكثر 3 شركات تعاملاً معها ---")
            print(top_vendors)

        # 3. عرض حالة الاستلام (Received) والفواتير (invoice)
        print("\n--- آخر 5 عمليات مسجلة ---")
        columns_to_show = ['LPO Number', 'company name', 'finance', 'invoice', 'Receved']
        # عرض الأعمدة المتاحة فقط لتجنب الأخطاء
        existing_cols = [c for c in columns_to_show if c in df.columns]
        print(df[existing_cols].tail())

    except Exception as e:
        print(f"حدث خطأ: تأكد من رفع الملف بالصيغة الصحيحة. التفاصيل: {e}")

if __name__ == "__main__":
    run_finance_system()

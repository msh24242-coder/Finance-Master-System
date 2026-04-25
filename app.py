import pandas as pd
import os

def run_finance_system():
    # البحث عن أي ملف CSV داخل مجلد Data
    data_dir = 'Data'
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not files:
        print("❌ خطأ: لم يتم العثور على أي ملف CSV في مجلد Data")
        return

    file_path = os.path.join(data_dir, files[0])
    print(f"✅ جاري تحليل ملف: {file_path}")

    try:
        # قراءة الملف مع تجاهل المشاكل البسيطة
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip() # تنظيف الأسماء

        print("\n--- التقرير المالي المباشر ---")
        
        # حساب المبالغ من عمود finance
        if 'finance' in df.columns:
            # تحويل النص لأرقام لضمان الحساب الصحيح
            df['finance_numeric'] = pd.to_numeric(df['finance'], errors='coerce').fillna(0)
            total = df['finance_numeric'].sum()
            print(f"💰 إجمالي الارتباطات المالية: {total}")
        
        # عرض الشركات
        if 'company name' in df.columns:
            print("\n🏢 ملخص الشركات:")
            print(df['company name'].value_counts())

    except Exception as e:
        print(f"❌ حدث خطأ أثناء القراءة: {e}")

if __name__ == "__main__":
    run_finance_system()

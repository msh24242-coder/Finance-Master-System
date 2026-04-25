import pandas as pd

def calculate_finance_report():
    # 1. قراءة بيانات الـ LPOs
    try:
        lpo_df = pd.read_csv('Data/lpo_tracker.csv')
        
        # 2. حساب إجمالي الالتزامات المالية
        total_contracted = lpo_df['Total_Amount'].sum()
        total_paid = lpo_df['Paid_Amount'].sum()
        total_remaining = lpo_df['Balance'].sum()

        print("--- التقرير المالي العام ---")
        print(f"إجمالي مبالغ الـ LPOs: {total_contracted}")
        print(f"إجمالي المبالغ المدفوعة: {total_paid}")
        print(f"إجمالي المبالغ المتبقية بذمتك: {total_remaining}")
        print("---------------------------")

        # 3. فلترة الـ LPOs غير المكتملة
        pending = lpo_df[lpo_df['Status'] != 'Completed']
        print("\n--- طلبات شراء (LPOs) بانتظار السداد ---")
        print(pending[['LPO_ID', 'Vendor_Name', 'Balance']])

    except FileNotFoundError:
        print("خطأ: لم يتم العثور على ملف البيانات. تأكد من وجود Data/lpo_tracker.csv")

# تشغيل التقرير
calculate_finance_report()

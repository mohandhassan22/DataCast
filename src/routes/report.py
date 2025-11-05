from flask import Blueprint, render_template, request, jsonify, send_file
from datetime import datetime
import calendar
import io
import csv
from src.models.employee import Employee
from src.models.branch import Branch
from src.db import db  # changed from src.main to src.db
from src.auth import password_required

# إنشاء Blueprint للتقارير
report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/', methods=['GET','POST'])
@password_required
def get_reports():
    """عرض صفحة التقارير"""
    branches = Branch.query.all()
    return render_template('reports/index.html', branches=branches)

@report_bp.route('/api/active', methods=['GET', 'POST'])
@password_required
def api_get_active_employees():
    """API لاسترجاع الموظفين النشطين"""
    branch_id = request.args.get('branch_id')
    status = request.args.get('status', 'Active')
    
    # بناء الاستعلام
    query = Employee.query
    
    # تطبيق الفلاتر
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    if status:
        query = query.filter(Employee.status == status)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    return jsonify([employee.to_dict() for employee in employees])

@report_bp.route('/api/terminated', methods=['GET'])
@password_required
def api_get_terminated_employees():
    """API لاسترجاع الموظفين المنتهية خدمتهم"""
    branch_id = request.args.get('branch_id')
    month = request.args.get('month')  # بتنسيق YYYY-MM
    
    # بناء الاستعلام
    query = Employee.query.filter(Employee.status == 'Termination')
    
    # تطبيق فلتر الفرع
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    # تطبيق فلتر الشهر (يتم تطبيقه بعد استرجاع البيانات لأنه يتطلب معالجة التاريخ)
    if month:
        try:
            year, month_num = map(int, month.split('-'))
            filtered_employees = []
            
            for employee in employees:
                if employee.resignation_date:
                    if employee.resignation_date.year == year and employee.resignation_date.month == month_num:
                        filtered_employees.append(employee)
            
            employees = filtered_employees
        except (ValueError, AttributeError):
            # في حالة حدوث خطأ في تنسيق الشهر، نتجاهل الفلتر
            pass
    
    return jsonify([employee.to_dict() for employee in employees])

@report_bp.route('/export/active', methods=['GET'])
@password_required
def export_active_employees():
    """تصدير تقرير الموظفين النشطين"""
    branch_id = request.args.get('branch_id')
    status = request.args.get('status', 'Active')
    
    # بناء الاستعلام
    query = Employee.query
    
    # تطبيق الفلاتر
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    if status:
        query = query.filter(Employee.status == status)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    # إنشاء ملف CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # كتابة رأس الجدول
    writer.writerow(['ID', 'الاسم بالعربية', 'الاسم بالإنجليزية', 'الفرع', 'الحالة', 
                    'رقم البطاقة', 'اليوزر', 'البريد الإلكتروني', 'رقم الموبايل', 'تاريخ التعيين'])
    
    # كتابة بيانات الموظفين
    for employee in employees:
        branch_name = 'غير معروف'
        branch = Branch.query.get(employee.branch_id)
        if branch:
            branch_name = branch.name
            
        hire_date = employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else ''
        
        writer.writerow([
            employee.id,
            employee.name_ar,
            employee.name_en,
            branch_name,
            employee.status,
            employee.id_card_number,
            employee.username,
            employee.email,
            employee.mobile_number,
            hire_date
        ])
    
    # إعداد الملف للتنزيل
    output.seek(0)
    
    # تحديد اسم الملف
    status_text = status if status else 'All'
    filename = f"active_employees_{status_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@report_bp.route('/export/terminated', methods=['GET'])
@password_required
def export_terminated_employees():
    """تصدير تقرير الموظفين المنتهية خدمتهم"""
    branch_id = request.args.get('branch_id')
    month = request.args.get('month')  # بتنسيق YYYY-MM
    
    # بناء الاستعلام
    query = Employee.query.filter(Employee.status == 'Termination')
    
    # تطبيق فلتر الفرع
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    # تطبيق فلتر الشهر
    if month:
        try:
            year, month_num = map(int, month.split('-'))
            filtered_employees = []
            
            for employee in employees:
                if employee.resignation_date:
                    if employee.resignation_date.year == year and employee.resignation_date.month == month_num:
                        filtered_employees.append(employee)
            
            employees = filtered_employees
            month_name = calendar.month_name[month_num]
        except (ValueError, AttributeError):
            # في حالة حدوث خطأ في تنسيق الشهر، نتجاهل الفلتر
            month_name = 'All'
    else:
        month_name = 'All'
    
    # إنشاء ملف CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # كتابة رأس الجدول
    writer.writerow(['ID', 'الاسم بالعربية', 'الاسم بالإنجليزية', 'الفرع', 
                    'رقم البطاقة', 'اليوزر', 'البريد الإلكتروني', 'رقم الموبايل', 
                    'تاريخ التعيين', 'تاريخ انتهاء الخدمة'])
    
    # كتابة بيانات الموظفين
    for employee in employees:
        branch_name = 'غير معروف'
        branch = Branch.query.get(employee.branch_id)
        if branch:
            branch_name = branch.name
            
        hire_date = employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else ''
        resignation_date = employee.resignation_date.strftime('%Y-%m-%d') if employee.resignation_date else ''
        
        writer.writerow([
            employee.id,
            employee.name_ar,
            employee.name_en,
            branch_name,
            employee.id_card_number,
            employee.username,
            employee.email,
            employee.mobile_number,
            hire_date,
            resignation_date
        ])
    
    # إعداد الملف للتنزيل
    output.seek(0)
    
    # تحديد اسم الملف
    filename = f"terminated_employees_{month_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

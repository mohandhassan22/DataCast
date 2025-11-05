from flask import Blueprint, request, jsonify, render_template
from src.models.employee import Employee
from src.models.branch import Branch
from src.db import db  # changed from src.main to src.db
from sqlalchemy import or_

# إنشاء Blueprint للبحث
search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/', methods=['GET', 'POST'])
def search_form():
    """عرض نموذج البحث المتقدم"""
    branches = Branch.query.all()
    return render_template('search/index.html', branches=branches)

@search_bp.route('/results', methods=['GET', 'POST'])
def search_results():
    """تنفيذ البحث وعرض النتائج"""
    # استخراج معايير البحث من الطلب
    search_term = request.args.get('search_term', '')
    search_type = request.args.get('search_type', 'name')
    branch_id = request.args.get('branch_id', '')
    status = request.args.get('status', '')
    
    # بناء استعلام البحث
    query = Employee.query
    
    # تطبيق معايير البحث
    if search_term:
        if search_type == 'name':
            query = query.filter(or_(
                Employee.name_ar.like(f'%{search_term}%'),
                Employee.name_en.like(f'%{search_term}%')
            ))
        elif search_type == 'id_card':
            query = query.filter(Employee.id_card_number.like(f'%{search_term}%'))
        elif search_type == 'username':
            query = query.filter(Employee.username.like(f'%{search_term}%'))
    
    # تصفية حسب الفرع إذا تم تحديده
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    
    # تصفية حسب الحالة إذا تم تحديدها
    if status:
        query = query.filter(Employee.status == status)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    # الحصول على معلومات الفروع للعرض
    branches = Branch.query.all()
    branch_dict = {branch.id: branch for branch in branches}
    
    return render_template('search/results.html', 
                          employees=employees, 
                          branches=branches,
                          branch_dict=branch_dict,
                          search_term=search_term,
                          search_type=search_type,
                          selected_branch_id=branch_id,
                          selected_status=status)

@search_bp.route('/api', methods=['GET'])
def api_search():
    """واجهة برمجة التطبيقات للبحث"""
    # استخراج معايير البحث من الطلب
    search_term = request.args.get('search_term', '')
    search_type = request.args.get('search_type', 'name')
    branch_id = request.args.get('branch_id', '')
    status = request.args.get('status', '')
    
    # بناء استعلام البحث
    query = Employee.query
    
    # تطبيق معايير البحث
    if search_term:
        if search_type == 'name':
            query = query.filter(or_(
                Employee.name_ar.like(f'%{search_term}%'),
                Employee.name_en.like(f'%{search_term}%')
            ))
        elif search_type == 'id_card':
            query = query.filter(Employee.id_card_number.like(f'%{search_term}%'))
        elif search_type == 'username':
            query = query.filter(Employee.username.like(f'%{search_term}%'))
    
    # تصفية حسب الفرع إذا تم تحديده
    if branch_id:
        query = query.filter(Employee.branch_id == branch_id)
    
    # تصفية حسب الحالة إذا تم تحديدها
    if status:
        query = query.filter(Employee.status == status)
    
    # تنفيذ الاستعلام
    employees = query.all()
    
    # تحويل النتائج إلى قاموس
    results = []
    for employee in employees:
        branch = Branch.query.get(employee.branch_id)
        employee_data = employee.to_dict()
        employee_data['branch_name'] = branch.name if branch else ''
        employee_data['branch_code'] = branch.code if branch else ''
        results.append(employee_data)
    
    return jsonify(results)

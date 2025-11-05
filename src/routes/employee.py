from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from src.models.employee import Employee
from src.models.branch import Branch
from src.db import db  # changed from src.main to src.db
from src.auth import password_required

# إنشاء Blueprint للموظفين
employee_bp = Blueprint('employee', __name__, url_prefix='/employees')

@employee_bp.route('/', methods=['GET'])
def get_employees():
    """عرض جميع الموظفين"""
    employees = Employee.query.all()
    branches = Branch.query.all()
    return render_template('employees/index.html', employees=employees, branches=branches)

@employee_bp.route('/api/list', methods=['GET'])
def api_get_employees():
    """API لاسترجاع قائمة الموظفين"""
    employees = Employee.query.all()
    return jsonify([employee.to_dict() for employee in employees])

@employee_bp.route('/create', methods=['GET', 'POST'])
@password_required
def create_employee_form():
    """عرض نموذج إضافة موظف جديد"""
    branches = Branch.query.all()
    return render_template('employees/create.html', branches=branches)

@employee_bp.route('/', methods=['GET','POST'])
@password_required
def create_employee():
    """إنشاء موظف جديد"""
    data = request.form
    
    # التحقق من البيانات المطلوبة
    if not data.get('name_ar') or not data.get('name_en') or not data.get('branch_id'):
        return jsonify({'error': 'اسم الموظف بالعربية والإنجليزية والفرع مطلوبة'}), 400
    
    # التحقق من وجود الفرع
    branch = Branch.query.get(data.get('branch_id'))
    if not branch:
        return jsonify({'error': 'الفرع غير موجود'}), 400
    
    # تحويل التواريخ إذا كانت موجودة
    uniform_receipt_date = None
    if data.get('uniform_receipt_date'):
        try:
            uniform_receipt_date = datetime.strptime(data.get('uniform_receipt_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    visa_receipt_date = None
    if data.get('visa_receipt_date'):
        try:
            visa_receipt_date = datetime.strptime(data.get('visa_receipt_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    hire_date = None
    if data.get('hire_date'):
        try:
            hire_date = datetime.strptime(data.get('hire_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    resignation_date = None
    if data.get('resignation_date'):
        try:
            resignation_date = datetime.strptime(data.get('resignation_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # إنشاء موظف جديد
    new_employee = Employee(
        branch_id=data.get('branch_id'),
        name_ar=data.get('name_ar'),
        name_en=data.get('name_en'),
        identification_number=data.get('identification_number'),
        mobile_number=data.get('mobile_number'),
        email=data.get('email'),
        id_card_number=data.get('id_card_number'),
        username=data.get('username'),
        status=data.get('status', 'Training'),
        title=data.get('title', 'Agent'),
        received_shirt=bool(data.get('received_shirt')),
        received_sweater=bool(data.get('received_sweater')),
        received_pants=bool(data.get('received_pants')),
        uniform_receipt_date=uniform_receipt_date,
        received_visa=bool(data.get('received_visa')),
        visa_receipt_date=visa_receipt_date,
        received_demo_line=bool(data.get('received_demo_line')),
        demo_line_number=data.get('demo_line_number'),
        hire_date=hire_date,
        resignation_date=resignation_date
    )
    
    try:
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({'message': 'تم إضافة الموظف بنجاح', 'employee': new_employee.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ أثناء إضافة الموظف: {str(e)}'}), 500

@employee_bp.route('/<int:employee_id>', methods=['GET','POST'])
def get_employee(employee_id):
    """عرض تفاصيل موظف محدد"""
    employee = Employee.query.get_or_404(employee_id)
    branch = Branch.query.get(employee.branch_id) if employee.branch_id else None
    return render_template('employees/show.html', employee=employee, branch=branch)

@employee_bp.route('/api/<int:employee_id>', methods=['GET','POST'])
def api_get_employee(employee_id):
    """API لاسترجاع تفاصيل موظف محدد"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())


# دعم GET و POST على /employees/<id>/edit (لمن يريد معالجة التعديل هنا)
@employee_bp.route('/<int:employee_id>/edit', methods=['GET', 'POST'])
@password_required
def edit_employee_form(employee_id):
    """عرض أو معالجة نموذج تعديل موظف"""
    employee = Employee.query.get_or_404(employee_id)
    branches = Branch.query.all()
    if request.method == 'POST':
        # إعادة استخدام منطق التحديث الموجود
        return update_employee(employee_id)
    return render_template('employees/edit.html', employee=employee, branches=branches)

@employee_bp.route('/<int:employee_id>', methods=['PUT', 'POST'])
@password_required
def update_employee(employee_id):
    """تحديث بيانات موظف"""
    employee = Employee.query.get_or_404(employee_id)
    
    # استخدام form أو json حسب نوع الطلب
    if request.method == 'POST' and request.form.get('_method') == 'PUT':
        data = request.form
    else:
        data = request.json or {}

    # تحديث كل الحقول
    # الفرع
    # معالجة branch_id بشكل آمن
    branch_id = data.get('branch_id')
    if branch_id is not None and branch_id != '':
        branch = Branch.query.get(branch_id)
        if not branch:
            return jsonify({'error': 'الفرع غير موجود'}), 400
        employee.branch_id = int(branch_id)
    # إذا لم يتم إرسال branch_id، لا تغيّر قيمة الموظف الحالية ولا تجعلها None

    # نصوص
    employee.name_ar = data.get('name_ar', employee.name_ar)
    employee.name_en = data.get('name_en', employee.name_en)
    employee.identification_number = data.get('identification_number', employee.identification_number)
    employee.mobile_number = data.get('mobile_number', employee.mobile_number)
    employee.email = data.get('email', employee.email)
    employee.id_card_number = data.get('id_card_number', employee.id_card_number)
    employee.username = data.get('username', employee.username)
    employee.status = data.get('status', employee.status)
    employee.title = data.get('title', employee.title)
    employee.demo_line_number = data.get('demo_line_number', employee.demo_line_number)

    # الحقول المنطقية (checkbox)
    def get_bool(key):
        # إذا كان من form: موجود = True، غير موجود = False
        # إذا كان من json: القيمة مباشرة
        if request.method == 'POST':
            return key in data
        return bool(data.get(key, False))

    employee.received_shirt = get_bool('received_shirt')
    employee.received_sweater = get_bool('received_sweater')
    employee.received_pants = get_bool('received_pants')
    employee.received_visa = get_bool('received_visa')
    employee.received_demo_line = get_bool('received_demo_line')

    # التواريخ
    def parse_date(key):
        val = data.get(key)
        if val:
            try:
                return datetime.strptime(val, '%Y-%m-%d').date()
            except ValueError:
                return None
        return getattr(employee, key)

    employee.uniform_receipt_date = parse_date('uniform_receipt_date')
    employee.visa_receipt_date = parse_date('visa_receipt_date')
    employee.hire_date = parse_date('hire_date')
    employee.resignation_date = parse_date('resignation_date')

    try:
        db.session.commit()
        return jsonify({'message': 'تم تحديث بيانات الموظف بنجاح', 'employee': employee.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ أثناء تحديث بيانات الموظف: {str(e)}'}), 500

@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
@password_required
def delete_employee(employee_id):
    """حذف موظف"""
    employee = Employee.query.get_or_404(employee_id)
    
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'تم حذف الموظف بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ أثناء حذف الموظف: {str(e)}'}), 500

@employee_bp.route('/branch/<int:branch_id>', methods=['GET','POST'])
def get_employees_by_branch(branch_id):
    """عرض الموظفين حسب الفرع"""
    branch = Branch.query.get_or_404(branch_id)
    employees = Employee.query.filter_by(branch_id=branch_id).all()
    return render_template('employees/by_branch.html', branch=branch, employees=employees)

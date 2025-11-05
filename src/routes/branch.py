from flask import Blueprint, request, jsonify, render_template
from src.models.branch import Branch
from src.db import db  # changed from src.main to src.db
from src.auth import password_required

# إنشاء Blueprint للفروع
branch_bp = Blueprint('branch', __name__, url_prefix='/branches')

@branch_bp.route('/', methods=['GET'])
def get_branches():
    """عرض جميع الفروع"""
    branches = Branch.query.all()
    return render_template('branches/index.html', branches=branches)

@branch_bp.route('/api/list', methods=['GET'])
def api_get_branches():
    """API لاسترجاع قائمة الفروع"""
    branches = Branch.query.all()
    return jsonify([branch.to_dict() for branch in branches])

@branch_bp.route('/create', methods=['GET', 'POST'])
@password_required
def create_branch_form():
    """عرض نموذج إنشاء فرع جديد"""
    return render_template('branches/create.html')

@branch_bp.route('/', methods=['POST'])
@password_required
def create_branch():
    """إنشاء فرع جديد"""
    data = request.form
    print('بيانات النموذج المستلمة:', dict(data))  # طباعة البيانات المستلمة
    
    # التحقق من البيانات المطلوبة
    if not data.get('name') or not data.get('code'):
        return jsonify({'error': 'اسم الفرع وكود الفرع مطلوبان'}), 400
    
    # التحقق من عدم تكرار كود الفرع
    existing_branch = Branch.query.filter_by(code=data.get('code')).first()
    if existing_branch:
        return jsonify({'error': 'كود الفرع موجود بالفعل'}), 400
    
    # إنشاء فرع جديد
    new_branch = Branch(
        name=data.get('name'),
        code=data.get('code'),
        phone=data.get('phone'),
        ip_address=data.get('ip_address'),
        regional_manager=data.get('regional_manager'),
        super_name=data.get('super_name'),
        area_name=data.get('area_name'),
        area_email=data.get('area_email'),
        branch_manager=data.get('branch_manager'),
        location_latitude=float(data.get('location_latitude')) if data.get('location_latitude') else None,
        location_longitude=float(data.get('location_longitude')) if data.get('location_longitude') else None,
        location_address=data.get('location_address')
    )
    
    try:
        db.session.add(new_branch)
        db.session.commit()
        return jsonify({'message': 'تم إنشاء الفرع بنجاح', 'branch': new_branch.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print('خطأ أثناء إضافة الفرع:', str(e))  # طباعة نص الخطأ
        return jsonify({'error': f'حدث خطأ أثناء إنشاء الفرع: {str(e)}'}), 500

@branch_bp.route('/<int:branch_id>', methods=['GET'])
def get_branch(branch_id):
    """عرض تفاصيل فرع محدد"""
    branch = Branch.query.get_or_404(branch_id)
    return render_template('branches/show.html', branch=branch)

@branch_bp.route('/api/<int:branch_id>', methods=['GET'])
def api_get_branch(branch_id):
    """API لاسترجاع تفاصيل فرع محدد"""
    branch = Branch.query.get_or_404(branch_id)
    return jsonify(branch.to_dict())

@branch_bp.route('/<int:branch_id>/edit', methods=['GET'])
@password_required
def edit_branch_form(branch_id):
    """عرض نموذج تعديل فرع"""
    branch = Branch.query.get_or_404(branch_id)
    return render_template('branches/edit.html', branch=branch)

@branch_bp.route('/<int:branch_id>', methods=['PUT', 'POST'])
@password_required
def update_branch(branch_id):
    """تحديث بيانات فرع"""
    branch = Branch.query.get_or_404(branch_id)
    
    # استخدام form أو json حسب نوع الطلب
    if request.method == 'POST' and request.form.get('_method') == 'PUT':
        data = request.form
    else:
        data = request.json
    
    # تحديث بيانات الفرع
    if data.get('name'):
        branch.name = data.get('name')
    if data.get('code'):
        # التحقق من عدم تكرار كود الفرع
        existing_branch = Branch.query.filter(Branch.code == data.get('code'), Branch.id != branch_id).first()
        if existing_branch:
            return jsonify({'error': 'كود الفرع موجود بالفعل'}), 400
        branch.code = data.get('code')

    branch.phone = data.get('phone', branch.phone)
    branch.ip_address = data.get('ip_address', branch.ip_address)
    branch.regional_manager = data.get('regional_manager', branch.regional_manager)
    branch.super_name = data.get('super_name', branch.super_name)
    branch.area_name = data.get('area_name', branch.area_name)
    branch.area_email = data.get('area_email', branch.area_email)
    branch.branch_manager = data.get('branch_manager', branch.branch_manager)

    # معالجة الإحداثيات بشكل آمن
    lat = data.get('location_latitude')
    if lat not in [None, '', 'None']:
        try:
            branch.location_latitude = float(lat)
        except ValueError:
            branch.location_latitude = None
    else:
        branch.location_latitude = None

    lon = data.get('location_longitude')
    if lon not in [None, '', 'None']:
        try:
            branch.location_longitude = float(lon)
        except ValueError:
            branch.location_longitude = None
    else:
        branch.location_longitude = None

    branch.location_address = data.get('location_address', branch.location_address)
    
    try:
        db.session.commit()
        return jsonify({'message': 'تم تحديث الفرع بنجاح', 'branch': branch.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ أثناء تحديث الفرع: {str(e)}'}), 500

@branch_bp.route('/<int:branch_id>', methods=['DELETE'])
@password_required
def delete_branch(branch_id):
    """حذف فرع"""
    branch = Branch.query.get_or_404(branch_id)
    
    try:
        db.session.delete(branch)
        db.session.commit()
        return jsonify({'message': 'تم حذف الفرع بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ أثناء حذف الفرع: {str(e)}'}), 500

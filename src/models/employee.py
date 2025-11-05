from datetime import datetime
from src.db import db  # changed from src.main to src.db

class Employee(db.Model):
    """نموذج الموظف في قاعدة البيانات"""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # البيانات الشخصية
    name_ar = db.Column(db.String(255), nullable=False)  # الاسم بالعربية
    name_en = db.Column(db.String(255), nullable=False)  # الاسم بالإنجليزية
    identification_number = db.Column(db.String(50))  # الرقم التعريفي
    mobile_number = db.Column(db.String(50))  # رقم الموبايل
    email = db.Column(db.String(255))  # البريد الإلكتروني
    id_card_number = db.Column(db.String(50))  # رقم البطاقة
    username = db.Column(db.String(100))  # اسم المستخدم
    
    # الحالة والمسمى الوظيفي
    status = db.Column(db.Enum('Active', 'Training', 'Suspend', 'Termination', name='employee_status'), default='Training')
    title = db.Column(db.Enum('Agent', 'Leader', name='employee_title'), default='Agent')
    
    # بيانات الزي
    received_shirt = db.Column(db.Boolean, default=False)  # استلام القميص
    received_sweater = db.Column(db.Boolean, default=False)  # استلام البلوفر
    received_pants = db.Column(db.Boolean, default=False)  # استلام البنطلون
    uniform_receipt_date = db.Column(db.Date)  # تاريخ استلام الزي
    
    # بيانات الفيزا
    received_visa = db.Column(db.Boolean, default=False)  # استلم فيزا
    visa_receipt_date = db.Column(db.Date)  # تاريخ استلام الفيزا
    
    # بيانات خط الديمو
    received_demo_line = db.Column(db.Boolean, default=False)  # استلم خط ديمو
    demo_line_number = db.Column(db.String(50))  # رقم خط الديمو
    
    # تواريخ التعيين والاستقالة
    hire_date = db.Column(db.Date)  # تاريخ التعيين
    resignation_date = db.Column(db.Date)  # تاريخ الاستقالة
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Employee {self.name_en}>'
    
    def to_dict(self):
        """تحويل بيانات الموظف إلى قاموس"""
        return {
            'id': self.id,
            'branch_id': self.branch_id,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'identification_number': self.identification_number,
            'mobile_number': self.mobile_number,
            'email': self.email,
            'id_card_number': self.id_card_number,
            'username': self.username,
            'status': self.status,
            'title': self.title,
            'received_shirt': self.received_shirt,
            'received_sweater': self.received_sweater,
            'received_pants': self.received_pants,
            'uniform_receipt_date': self.uniform_receipt_date.isoformat() if self.uniform_receipt_date else None,
            'received_visa': self.received_visa,
            'visa_receipt_date': self.visa_receipt_date.isoformat() if self.visa_receipt_date else None,
            'received_demo_line': self.received_demo_line,
            'demo_line_number': self.demo_line_number,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'resignation_date': self.resignation_date.isoformat() if self.resignation_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

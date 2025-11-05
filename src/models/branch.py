from datetime import datetime
from src.db import db  # changed from src.main to src.db

class Branch(db.Model):
    """نموذج الفرع في قاعدة البيانات"""
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    regional_manager = db.Column(db.String(255))
    super_name = db.Column(db.String(255))
    area_name = db.Column(db.String(255))
    area_email = db.Column(db.String(255))
    branch_manager = db.Column(db.String(255))
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    location_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع جدول الموظفين (علاقة واحد إلى متعدد)
    employees = db.relationship('Employee', backref='branch', lazy=True)

    def __repr__(self):
        return f'<Branch {self.name}>'
    
    def to_dict(self):
        """تحويل بيانات الفرع إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'phone': self.phone,
            'ip_address': self.ip_address,
            'regional_manager': self.regional_manager,
            'super_name': self.super_name,
            'area_name': self.area_name,
            'area_email': self.area_email,
            'branch_manager': self.branch_manager,
            'location_latitude': self.location_latitude,
            'location_longitude': self.location_longitude,
            'location_address': self.location_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

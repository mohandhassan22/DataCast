from functools import wraps
from flask import session, request, redirect, url_for, render_template, flash

# Password for admin actions
ADMIN_PASSWORD = "Admin123#"

def password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated in session
        if not session.get('authenticated'):
            # If POST request with password, verify it
            if request.method == 'POST' and request.form.get('password'):
                if request.form.get('password') == ADMIN_PASSWORD:
                    session['authenticated'] = True
                    # If there's a next URL, redirect there
                    next_url = request.form.get('next')
                    if next_url:
                        return redirect(next_url)
                    return f(*args, **kwargs)
                else:
                    flash('كلمة المرور غير صحيحة', 'danger')
            
            # Show password prompt
            return render_template('auth/password_prompt.html', next=request.path)
        
        # User is authenticated, proceed
        return f(*args, **kwargs)
    
    return decorated_function

def init_auth(app):
    """Initialize authentication related configurations"""
    # Set secret key for session
    app.secret_key = 'employee_management_system_secret_key'
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    @app.route('/logout')
    def logout():
        """تسجيل الخروج"""
        session.clear()
        return redirect(url_for('index'))

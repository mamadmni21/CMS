from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import numpy as np
import pandas as pd
import os
import random
from jinja2 import TemplateNotFound
from app.models import db, UserDtl, User, CustomerOrderDtl, PurReq, SupplierDtl, PurReportPO, PurReportSup, PurReportBill
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from types import SimpleNamespace
from sqlalchemy import func

print("✅ Loaded routes.py FROM:", __file__)

main = Blueprint('main', __name__)

# Role Tabs Mapping
ROLE_MENU = {
    "1001": ["Developer Monitoring Dashboard", "HR Department", "Project Management", "Product Management",
             "Finance and Accounting", "Purchasing", "Warehouse Management System", "Production Department", "Inventory", "General Affairs",
             "Organization Chart", "Reporting Tools", "Database Settings", "Customer Dashboard", "Meeting Time", "Create Order", "Order History"],
      
    "1011": ["Finance and Accounting Dashboard", "Finance and Accounting Reporting Tools", "Customer Relationship Management", "Meeting Time", "Forcaster AI"],
    "1010": ["HR Dashboard", "HR Reporting Tools", "Employee Management", "Payroll Management", "Meeting Time"],
    "1013": ["Purchasing Dashboard", "Purchasing Reporting Tools", "Purchasing Order Approval", "Create Purchase Order", "Supplier Management", "Purchase Order History", "Purchase Schedule", "Meeting Time"],
    "1014": ["Customer Dashboard", "Customer Order Status", "Customer Profile", "Customer Wallet", "Customer Create Order", "Meeting Time"],
    "1016": ["Production Dashboard", "Production Reporting Tools", "Production Staff Management", "Product Management", "Material Management", "Production Inventory", "Meeting Time"],   
    "1017": ["Supplier Dashboard", "Supply Status", "Supplier Profile", "Supplier Wallet", "Meeting Time"],
    "1018": ["Customer Dashboard", "Customer Order Status", "Customer Profile", "Customer Wallet", "Customer Create Order", "Meeting Time"],
    "1020": ["Warehouse Dashboard", "WH Supply Status", "WH Profile", "WH Stocks", "Meeting Time"],

}

# Icon Mapping for each Menu
MENU_ICONS = {
    "Developer Monitoring Dashboard": "dev_dashboard_icon.png",
    "Monitoring Dashboard": "dashboard",
    "Human Resource Management": "group",
    "Project Management": "project_mgmt_icon.png",
    "Product Management": "product_mgmt_icon.png",
    "Finance and Accounting": "fi_ac_icon.png",
    "Purchasing": "purchasing_icon.png",
    "Production Department": "production_icon.png",
    "Inventory": "inventory_icon.png",
    "General Affairs": "general_affair_icon.png",
    "Organization Chart": "account_tree",
    "Reporting Tools": "reporting_tools_icon.png",
    "Purchasing Reporting Tools": "reporting_tools_icon.png",
    "Database Settings": "storage",
    "Customer Dashboard": "dashboard.png",
    "Create Order": "create_order_icon.png",
    "Create Purchase Order": "create_order_icon.png",
    "Order History": "order_history_icon.png",
    "Purchase Order History": "order_history_icon.png",
    "Order Status": "order_status_icon.png",
    "Order Approval" : "order_status_icon.png",
    "Purchasing Order Approval" : "order_status_icon.png",
    "Customer Order Status": "order_status_icon.png",
    "Customer Profile": "cust_profile_icon.png",
    "Customer Wallet": "cust_wallet_icon.png",
    "Customer Create Order": "create_order_icon.png",
    "Supplier Dashboard": "supervisor_account",
    "Supply Status": "local_shipping",
    "Supplier Profile": "supp_profile_icon.png",
    "Supplier Wallet": "supp_wallet_icon.png",
    "Supplier Management" : "supp_profile_icon.png",
    "User Dashboard": "person",
    "HR Department": "hr_icon.png",
    "HR Dashboard": "hr_dashboard_icon.png",
    "HR Reporting Tools": "reporting_tools_icon.png",
    "Employee Management": "emp_mgmt_icon.png",
    "Payroll Management": "emp_payroll_icon.png",
    "Management Dashboard": "leaderboard",
    "Finance and Accounting Dashboard": "dashboard.png",
    "Finance and Accounting Reporting Tools": "reporting_tools_icon.png",
    "Customer Relationship Management": "crm_icon.png",
    "Purchasing Dashboard": "dashboard.png",
    "Production Dashboard": "build",
    "GA Dashboard": "domain",
    "CRM Dashboard": "people",
    "Purchase Schedule" : "pur_sch_icon.png",
    "Warehouse Management System" : "warehouse_mgmt_sys_icon.png",
    "Meeting Time" : "meeting_online.png",
    "Customer Relationship Management" : "crm_icon.png",
    "Warehouse Dashboard":"dashboard.png",
    "WH Supply Status":"wh_supply_sts_icon.png",
    "WH Profile":"supp_profile_icon.png",
    "WH Stocks":"wh_stock_icon.png",
    "Forcaster AI":"ai_icon.png",
}


TAB_ROUTE_MAP = {
    "Customer Dashboard": "main.customer_dashboard",
    "Customer Profile": "main.customer_profile",
    "Customer Wallet": "main.customer_wallet",
    "Customer Order Status": "main.customer_order_status",
    "Customer Create Order": "main.customer_create_order",
    "Create Order": "main.create_order",
    "Order History": "main.order_history",
    "Order Status": "main.order_status",
    "Supplier Dashboard": "main.supplier_dashboard",
    "Supplier Profile": "main.supplier_profile",
    "Supplier Wallet": "main.supplier_wallet",
    "Supply Status": "main.supply_status",
    "Finance and Accounting": "main.finance_accounting",
    "Finance and Accounting Reporting Tools":"main.accounting_reporting_tools",
    "Finance and Accounting Dashboard" : "main.finance_accounting_dashboard", 
    "HR Dashboard": "main.hr_dashboard",
    "Purchasing Dashboard": "main.purchasing_dashboard",
    "Reporting Tools": "main.reporting_tools",
    "Developer Monitoring Dashboard": "main.developer_monitoring_dashboard",
    "HR Department":"main.hr_department",
    "Payroll Management":"main.payroll_management",
    "Employee Management":"main.employee_management",
    "Purchasing":"main.purchasing", 
    "Purchasing Order Approval":"main.purchasing_order_approval",
    "Purchase Order History":"main.purchase_order_history",
    "Create Purchase Order" : "main.create_purchase_order",
    "Purchase Schedule" : "main.purchase_schedule",
    "Purchasing Reporting Tools":"main.purchasing_report_tools",
    "Supplier Management": "main.supplier_management",
    "HR Reporting Tools": "main.hr_reporting_tools",
    "Warehouse Management System": "main.warehouse_management_system",
    "Meeting Time" : "main.meeting_time",
    "Customer Relationship Management" : "main.customer_relationship_management",
    "Warehouse Dashboard": "main.wh_dashboard",
    "WH Supply Status": "main.wh_supply_status",
    "WH Profile": "main.wh_profile",
    "WH Stocks": "main.wh_stocks",
    "Production Department": "main.production_department",
    "Forcaster AI":"main.forecaster_ai"
    
    # Add more as needed...
}


def get_usr_full_nm_from_session():
    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    if user_dtl:
        session["usr_full_nm"] = user_dtl.usr_full_nm
        return user_dtl.usr_full_nm
    return username or "Unknown User"

@main.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')


@main.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(usr_nm=username).first()
    if user and (user.usr_pass == password or check_password_hash(user.usr_pass, password)):
        session['username'] = user.usr_nm
        session['role_id'] = user.usr_role_id
        session['role_name'] = user.usr_role_nm
        return redirect(url_for('main.dashboard'))

    return render_template('login.html', error='Invalid credentials')


@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    tabs = ROLE_MENU.get(role_id, [])

    usr_full_nm = get_usr_full_nm_from_session()

    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = username
    balance_myr = None
    currency = "MYR"

    if user_dtl:
        session['usr_full_nm'] = user_dtl.usr_full_nm
        usr_full_nm = user_dtl.usr_full_nm

        from app.models import CustomerSavingsDtl
        savings = CustomerSavingsDtl.query.filter_by(
            cust_id=user_dtl.usr_id,
            cust_nm=user_dtl.usr_nm
        ).first()
        if savings:
            balance_myr = savings.saving_blc
            currency = savings.currency or "MYR"

    return render_template(
        'dashboard.html',
        username=username,
        usr_full_nm=usr_full_nm,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        balance_myr=balance_myr,
        currency=currency,
        **{"TAB_ROUTE_MAP": TAB_ROUTE_MAP}  # ✅ add this
    )



@main.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        usr_nm = request.form['usr_nm']

        # Username check
        existing_user = User.query.filter_by(usr_nm=usr_nm).first()
        if existing_user:
            return render_template('user_signup.html', message="⚠️ Username already exists, please choose another.")

        # Determine role
        role_name = request.form['usr_role_nm']
        role_id = "1018" if role_name == "Customer" else "1017"

        # Generate new user ID
        last_user = UserDtl.query.filter(UserDtl.usr_id.like('CUS%')).order_by(UserDtl.usr_id.desc()).first()
        new_usr_id = f"CUS{int(last_user.usr_id.replace('CUS', '')) + 1}" if last_user else "CUS1"

        try:
            # Get form data
            usr_full_nm = request.form['usr_full_nm']
            usr_phone = request.form['usr_phone']
            usr_email = request.form['usr_email']
            usr_nid = request.form['usr_nid']
            usr_add = request.form['usr_add']
            usr_city = request.form['usr_city']
            usr_region = request.form['usr_region']
            usr_country = request.form['usr_country']
            usr_dob = request.form['usr_dob']
            usr_company_nm = request.form['usr_company_nm']
            usr_company_reg_no = request.form['usr_company_reg_no']
            usr_comp_pos_nm = request.form['usr_comp_pos_nm']
            usr_pass = generate_password_hash(request.form['usr_pass'])

            # Insert into usr_dtl
            new_dtl = UserDtl(
                usr_id=new_usr_id,
                usr_nm=usr_nm,
                usr_full_nm=usr_full_nm,
                usr_phone=usr_phone,
                usr_email=usr_email,
                usr_nid=usr_nid,
                usr_add=usr_add,
                usr_city=usr_city,
                usr_region=usr_region,
                usr_country=usr_country,
                usr_dob=usr_dob,
                usr_company_nm=usr_company_nm,
                usr_company_reg_no=usr_company_reg_no,
                usr_comp_pos_nm=usr_comp_pos_nm,
                usr_role_id=role_id,
                usr_role_nm=role_name
            )
            db.session.add(new_dtl)

            # Insert into usr_login (User table)
            new_login = User(
                usr_id=new_usr_id,
                usr_nm=usr_nm,
                usr_pass=usr_pass,
                usr_role_id=role_id,
                usr_role_nm=role_name,
                log_count=0  # 👈 Add this line
            )
            db.session.add(new_login)
            db.session.commit()

            # Auto-login
            session['username'] = usr_nm
            session['role_id'] = role_id
            session['role_name'] = role_name

            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            return render_template('user_signup.html', message=f"❌ Registration failed: {str(e)}")

    return render_template('user_signup.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


@main.route('/test')
def test_template():
    return render_template("login.html")


@main.route("/customer_dashboard")
def customer_dashboard():
    # ───────────────────────────────────────────────
    # 1️⃣  login required
    # ───────────────────────────────────────────────
    if "username" not in session:
        return redirect(url_for("main.home"))

    # ───────────────────────────────────────────────
    # 2️⃣  role‑gate  ➜  allow 1018, 1014, 1001
    # ───────────────────────────────────────────────
    allowed_roles = {"1018", "1014", "1001"}
    role_id = str(session.get("role_id"))

    if role_id not in allowed_roles:
        return redirect(url_for("main.dashboard"))

    username = session["username"]

    # ───────────────────────────────────────────────
    # 3️⃣  try to fetch customer details
    # ───────────────────────────────────────────────
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()

    if user_dtl is None:
        # No row in usr_dtl (typical for developer / admin)
        # → build a lightweight stand‑in with the attrs we need
        user_dtl = SimpleNamespace(
            usr_full_nm=username,  # show the login name
            usr_id="",             # empty so queries using it just return None
            usr_nm=username
        )

    # keep a readable name in the session (optional)
    session.setdefault("usr_full_nm", user_dtl.usr_full_nm)

    # ───────────────────────────────────────────────
    # 4️⃣  current order (may be None)
    # ───────────────────────────────────────────────
    current_order = (
        CustomerOrderDtl.query
        .filter(
            CustomerOrderDtl.cust_id == user_dtl.usr_id,
            CustomerOrderDtl.cust_nm == user_dtl.usr_nm,
            CustomerOrderDtl.last_status != "Confirmed"
        )
        .order_by(CustomerOrderDtl.last_update.desc())
        .first()
        if user_dtl.usr_id else None
    )

    # ───────────────────────────────────────────────
    # 5️⃣  wallet / currency
    # ───────────────────────────────────────────────
    from app.models import CustomerSavingsDtl

    savings   = (CustomerSavingsDtl.query
                 .filter_by(cust_id=user_dtl.usr_id)
                 .first()) if user_dtl.usr_id else None

    currency  = savings.currency if savings else "MYR"

    # ───────────────────────────────────────────────
    # 6️⃣  misc computed fields
    # ───────────────────────────────────────────────
    monthly_payment  = 0
    current_month    = datetime.now().strftime("%B %Y")
    progress_map = {
        "Order created": 20,
        "Paid and preparing": 40,
        "Delivery": 60,
        "Arrived": 80,
        "Confirmed": 100,
    }
    current_progress = (
        progress_map.get(current_order.last_status, 0)
        if current_order else 0
    )

    next_month_date  = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)
    next_month       = next_month_date.strftime("%B %Y")
    next_payment     = 0
    monthly_data     = [120, 80, 100, 150]   # demo numbers

    # ───────────────────────────────────────────────
    # 7️⃣  render
    # ───────────────────────────────────────────────
    return render_template(
        "customer_dashboard.html",
        usr_full_nm      = user_dtl.usr_full_nm,
        current_order    = current_order,
        progress_percent = current_progress,
        currency         = currency,
        monthly_payment  = monthly_payment,
        current_month    = current_month,
        next_month       = next_month,
        next_payment     = next_payment,
        monthly_data     = monthly_data,
    )


@main.route('/customer_order_status')
def customer_order_status():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    if str(session.get('role_id')) != "1018":
        return redirect(url_for('main.dashboard'))

    usr_full_nm = session.get('usr_full_nm', 'Valued Customer')

    return render_template(
        'customer_order_status.html',
        usr_full_nm=usr_full_nm
    )


@main.route('/api/current_order_status')
def current_order_status():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session.get('username')
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    if not user_dtl:
        return jsonify({'error': 'User not found'}), 404

    current_order = CustomerOrderDtl.query.filter(
        CustomerOrderDtl.cust_id == user_dtl.usr_id,
        CustomerOrderDtl.cust_nm == user_dtl.usr_nm,
        CustomerOrderDtl.last_status != "Confirmed"
    ).order_by(CustomerOrderDtl.last_update.desc()).first()

    if not current_order:
        return jsonify({'status': None})

    status = current_order.last_status
    progress_map = {
        'Order created': 20,
        'Paid and preparing': 40,
        'Delivery': 60,
        'Arrived': 80,
        'Confirmed': 100
    }

    return jsonify({
        'status': status,
        'progress': progress_map.get(status, 0),
        'cust_order_id': current_order.cust_order_id,
        'item_id': current_order.cust_order_itm_id,
        'item_name': current_order.cust_order_itm_nm,
        'amount': current_order.order_amount,
        'last_update': current_order.last_update.strftime('%Y-%m-%d %H:%M:%S')
    })



@main.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'profile_pic' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.customer_profile'))

    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('main.customer_profile'))

    # You can add logic here to save the file
    # For now, just simulate success
    flash('Profile picture uploaded successfully!', 'success')
    return redirect(url_for('main.customer_profile'))



@main.route('/customer_profile')
def customer_profile():
    print("DEBUG: /customer_profile route hit")
    print("DEBUG: session contents =", dict(session))

    if 'username' not in session:
        return redirect(url_for('main.home'))

    # if session.get('role_id') != "1018":
    if str(session.get('role_id')) != "1018":

        return redirect(url_for('main.dashboard'))

    username = session.get('username')
    print("DEBUG: looking up user_dtl for username =", username)

    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    print("DEBUG: user_dtl result =", user_dtl)

    if not user_dtl:
        flash("User not found in usr_dtl table", "danger")
        return redirect(url_for('main.dashboard'))

    return render_template(
        'customer_profile.html',
        user=user_dtl,
        usr_full_nm=user_dtl.usr_full_nm
    )




@main.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session['username']
    user = UserDtl.query.filter_by(usr_nm=username).first()
    if not user:
        return redirect(url_for('main.dashboard'))

    # Update fields from form
    user.usr_full_nm = request.form.get('usr_full_nm')
    user.usr_phone = request.form.get('usr_phone')
    user.usr_email = request.form.get('usr_email')
    user.usr_nid = request.form.get('usr_nid')
    user.usr_add = request.form.get('usr_add')
    user.usr_city = request.form.get('usr_city')
    user.usr_region = request.form.get('usr_region')
    user.usr_country = request.form.get('usr_country')
    user.usr_company_nm = request.form.get('usr_company_nm')
    user.usr_company_reg_no = request.form.get('usr_company_reg_no')
    user.usr_comp_pos_nm = request.form.get('usr_comp_pos_nm')

    try:
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile.', 'danger')

    return redirect(url_for('main.customer_profile'))

@main.route('/edit_profile')
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session['username']
    user = UserDtl.query.filter_by(usr_nm=username).first()
    if not user:
        return redirect(url_for('main.dashboard'))

    return render_template('edit_profile.html', user=user)

@main.route('/customer_wallet')
def customer_wallet():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    #if session.get('role_id') != "1018":  # or "1014" if applicable
    if str(session.get('role_id')) != "1018":
        return redirect(url_for('main.dashboard'))
    

    username = session.get('username')
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()

    if not user_dtl:
        return redirect(url_for('main.dashboard'))

    usr_full_nm = user_dtl.usr_full_nm
    usr_id = user_dtl.usr_id

    # ✅ Get balance and currency from customer_savings_dtl
    from app.models import CustomerSavingsDtl
    savings = CustomerSavingsDtl.query.filter_by(cust_id=usr_id).first()
    balance = savings.saving_blc if savings else 0
    currency = savings.currency if savings else "MYR"

    # ✅ Static transaction logs (mocked for now)
    transaction_logs = [
        {'project': 'Project A', 'amount': '120.00', 'date': '2025-06-10'},
        {'project': 'Project B', 'amount': '85.00', 'date': '2025-06-15'},
        {'project': 'Project C', 'amount': '150.00', 'date': '2025-06-20'},
        {'project': 'Project D', 'amount': '90.00', 'date': '2025-07-01'},
    ]

    # Mocked next payment & month
    next_payment = 0
    next_month_date = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)
    next_month = next_month_date.strftime("%B %Y")

    return render_template(
        'customer_wallet.html',
        usr_full_nm=usr_full_nm,
        balance=balance,
        currency=currency,
        next_payment=next_payment,
        next_month=next_month,
        transaction_logs=transaction_logs
    )


@main.route('/customer_topup')
def customer_topup():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    if str(session.get('role_id')) != "1018":
        return redirect(url_for('main.dashboard'))

    return render_template('customer_topup.html')



@main.route('/developer_monitoring_dashboard')
def developer_monitoring_dashboard():
    # ✅ Developers (role_id 1001) only
    if 'username' not in session or str(session.get('role_id')) != "1001":
        return redirect(url_for('main.dashboard'))

    # Get user's display name
    usr_full_nm = get_usr_full_nm_from_session()

    # ---------- quick counts ----------
    users_count     = db.session.execute(db.select(db.func.count()).select_from(UserDtl)).scalar()
    depts_count     = db.session.execute(db.text("SELECT COUNT(*) FROM dept_dtl")).scalar()
    mats_count      = db.session.execute(db.text("SELECT COUNT(*) FROM material_dtl")).scalar()
    orders_count    = db.session.execute(db.text("SELECT COUNT(*) FROM order_dtl")).scalar()
    products_count  = db.session.execute(db.text("SELECT COUNT(*) FROM product_itm_dtl")).scalar()
    projects_count  = db.session.execute(db.text("SELECT COUNT(*) FROM proj_management_dtl")).scalar()

    return render_template(
        "developer_monitoring_dashboard.html",
        usr_full_nm=usr_full_nm,
        users_count=users_count,
        depts_count=depts_count,
        mats_count=mats_count,
        orders_count=orders_count,
        products_count=products_count,
        projects_count=projects_count
    )


@main.route('/warehouse_management_system')
def warehouse_management_system():
    """
    Warehouse Management System landing page.
    Allowed for role_id 1020 (Warehouse staff) and 1001 (admin/dev).
    Displays the Warehouse-specific menu (role 1020).
    """
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1020", "1001"]:
        return redirect(url_for('main.dashboard'))
    
    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    # Warehouse menu → defined in your ROLE_MENU dictionary
    warehouse_menu = ROLE_MENU.get("1020", [])

    return render_template(
        "warehouse_management_system.html",
        username=username,
        usr_full_nm=usr_full_nm,
        menu_items=warehouse_menu,
        menu_icons=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )

@main.route('/wh_dashboard')
def wh_dashboard():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    # ✅ Ensure warehouse staff (1020) inherits admin (1001) menu
    tabs = ROLE_MENU.get(role_id, ROLE_MENU.get("1001", []))

    usr_full_nm = get_usr_full_nm_from_session()

    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = username
    balance_myr = None
    currency = "MYR"

    if user_dtl:
        session['usr_full_nm'] = user_dtl.usr_full_nm
        usr_full_nm = user_dtl.usr_full_nm

        from app.models import CustomerSavingsDtl
        savings = CustomerSavingsDtl.query.filter_by(
            cust_id=user_dtl.usr_id,
            cust_nm=user_dtl.usr_nm
        ).first()
        if savings:
            balance_myr = savings.saving_blc
            currency = savings.currency or "MYR"

    return render_template(
        'warehouse_dashboard.html',
        username=username,
        usr_full_nm=usr_full_nm,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        balance_myr=balance_myr,
        currency=currency,
        **{"TAB_ROUTE_MAP": TAB_ROUTE_MAP}
    )

@main.route('/wh_supply_status')
def wh_supply_status():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    tabs = ROLE_MENU.get(role_id, [])

    usr_full_nm = get_usr_full_nm_from_session()

    return render_template(
        'warehouse_supply_status.html',
        username=username,
        usr_full_nm=usr_full_nm,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )

@main.route('/wh_stocks')
def wh_stocks():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    tabs = ROLE_MENU.get(role_id, [])

    usr_full_nm = get_usr_full_nm_from_session()

    return render_template(
        'warehouse_stocks.html',
        username=username,
        usr_full_nm=usr_full_nm,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )



@main.route('/hr_department')
def hr_department():
    """
    HR Department landing page.
    Allowed for role_id 1010 (HR staff) and 1001 (admin/dev).
    Displays the HR-specific menu (role 1010).
    """
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1010", "1001"]:
        return redirect(url_for('main.dashboard'))
    
    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    hr_menu = ROLE_MENU.get("1010", [])

    return render_template(
        "hr_department.html",
        username=username,
        usr_full_nm=usr_full_nm,
        menu_items=hr_menu,
        menu_icons=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )

from flask import session

@main.route('/hr_reporting_tools', methods=['GET', 'POST'])
def hr_reporting_tools():
    # Example data for Box 1 (menu of reporting tools)
    hr_apps = [
        {"id": "attendance", "icon": "event_note", "title": "Attendance Reports",
         "description": "View staff attendance by department and period."},
        {"id": "performance", "icon": "bar_chart", "title": "Performance Reports",
         "description": "Monitor staff KPIs and evaluation scores."},
        {"id": "payroll", "icon": "payments", "title": "Payroll Reports",
         "description": "Check payroll summaries and problem logs."},
        {"id": "recruitment", "icon": "group_add", "title": "Recruitment Reports",
         "description": "Track hiring status and recruitment pipeline."},
        {"id": "inventory", "icon": "inventory_2", "title": "Inventory Reports",
         "description": "Manage office supplies and asset availability."},
    ]

    # Get selected app from query params (?app=attendance for example)
    selected_app = request.args.get("app", None)

    # Placeholder: Box 2 - form fields depending on the selected app
    forms = {
        "attendance": ["Start Date", "End Date", "Department"],
        "performance": ["Employee ID", "Evaluation Period"],
        "payroll": ["Month", "Year"],
        "recruitment": ["Job Title", "Status"],
        "inventory": ["Category", "Date Range"]
    }

    selected_form = forms.get(selected_app, [])

    # Placeholder: Box 3 - reference table data
    table_data = []
    if selected_app == "attendance":
        table_data = [
            {"Employee": "John Doe", "Date": "2025-08-01", "Status": "Present"},
            {"Employee": "Jane Smith", "Date": "2025-08-01", "Status": "Absent"}
        ]
    elif selected_app == "performance":
        table_data = [
            {"Employee": "John Doe", "Score": "85", "Period": "Q2 2025"},
            {"Employee": "Jane Smith", "Score": "90", "Period": "Q2 2025"}
        ]
    elif selected_app == "payroll":
        table_data = [
            {"Employee": "John Doe", "Month": "July", "Amount": "$2000"},
            {"Employee": "Jane Smith", "Month": "July", "Amount": "$2100"}
        ]
    elif selected_app == "recruitment":
        table_data = [
            {"Candidate": "Alice", "Job": "Developer", "Status": "Interviewed"},
            {"Candidate": "Bob", "Job": "Designer", "Status": "Pending"}
        ]
    elif selected_app == "inventory":
        table_data = [
            {"Item": "Laptop", "Stock": 12, "Category": "IT Assets"},
            {"Item": "Chair", "Stock": 40, "Category": "Furniture"}
        ]

    # Get username from session if logged in
    username = session.get("username", "Guest")

    return render_template(
        "hr_reporting_tools.html",
        hr_apps=hr_apps,
        selected_app=selected_app,
        selected_form=selected_form,
        table_data=table_data,
        username=username
    )



@main.route('/finance_accounting')
def finance_accounting():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1011", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    # Use 1011 menu for both 1011 and 1001 roles
    finance_menu = ROLE_MENU.get("1011", [])

    return render_template(
        "finance_accounting.html",
        username=username,
        usr_full_nm=usr_full_nm,
        menu_items=finance_menu,
        menu_icons=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )


@main.route('/finance_accounting_dashboard')
def finance_accounting_dashboard():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1011", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    return render_template(
        "finance_accounting_dashboard.html",
        username=username,
        usr_full_nm=usr_full_nm,

        # Dummy data for now
        current_year="2025",
        current_month="July 2025",
        total_revenue="5,250,000,000",
        total_expenses="3,980,000,000",
        outstanding_invoices=18,
        paid_invoices=120,
        overdue_invoices=5,
        monthly_profit="1,270,000,000",
        cash_reserves="8,500,000,000"
    )





@main.route('/purchasing')
def purchasing():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    # Use 1013 menu for both 1013 and 1001 roles
    purchasing_menu = ROLE_MENU.get("1013", [])

    return render_template(
        "purchasing.html",  # adjust template name if needed
        username=username,
        usr_full_nm=usr_full_nm,
        menu_items=purchasing_menu,
        menu_icons=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )



@main.route('/purchasing_dashboard')
def purchasing_dashboard():
    """
    Purchasing Dashboard page.
    Role allowed: 1013 (Purchasing), and 1001 (Admin/Dev)
    """
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    return render_template(
        "purchasing_dashboard.html",
        username=username,
        usr_full_nm=usr_full_nm,

        # Dummy sample values for now
        on_going_po=15,
        total_po_requests=42,
        incoming_bills=5,
        current_month="July 2025",
        previous_bills=[{"month": "June", "date": "2025-06-28"}, {"month": "May", "date": "2025-05-26"}],
        declined_po=3,
        total_suppliers=12,
        total_unpaid_bills="2,195,000,000"
    )

@main.route('/purchasing_order_approval', methods=["GET", "POST"])
def purchasing_order_approval():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_id = session.get("user_id")

    # Load all requests
    pur_reqs = PurReq.query.all()

    # Handle POST submission for approve/reject
    if request.method == "POST":
        selected_id = request.form.get("pur_req_id")
        action = request.form.get("action")
        selected_req = PurReq.query.filter_by(pur_req_id=selected_id).first()

        if action in ["approve", "reject"] and selected_req:
            year = datetime.datetime.now().year
            prefix = "APV" if action == "approve" else "RJC"

            last_entry = PurReq.query.filter(PurReq.pur_req_apv_id.like(f"{year}{prefix}%")) \
                                     .order_by(PurReq.pur_req_apv_id.desc()).first()

            next_number = 1
            if last_entry and last_entry.pur_req_apv_id:
                try:
                    last_num = int(last_entry.pur_req_apv_id[-1])
                    next_number = last_num + 1
                except ValueError:
                    pass  # fallback to 1 if ID is malformed

            new_apv_id = f"{year}{prefix}{next_number:03}"

            selected_req.pur_req_sts = "Approved" if action == "approve" else "Rejected"
            selected_req.pur_req_apv_id = new_apv_id
            selected_req.pur_req_apr_usr_id = user_id
            selected_req.pur_req_apr_usr_name = username
            db.session.commit()

            # ✅ redirect to GET with selected ID as query parameter
            return redirect(url_for('main.purchasing_order_approval', selected_id=selected_id))

    # ✅ handle GET request and dropdown selection
    selected_id = request.args.get("selected_id")
    selected_req = PurReq.query.filter_by(pur_req_id=selected_id).first() if selected_id else None

    return render_template(
        "purchasing_order_approval.html",
        pur_reqs=pur_reqs,
        selected_id=selected_id,
        selected_req=selected_req
    )

@main.route('/purchase_order_history', methods=["GET", "POST"])
def purchase_order_history():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_id = session.get("user_id")

    pur_reqs = PurReq.query.all()
    selected_id = request.args.get("selected_id")
    selected_req = None
    history_data = None
    file_error = None

    # ✅ Handle ID selection to populate Box 2 form
    if selected_id:
        selected_req = PurReq.query.filter_by(pur_req_id=selected_id).first()

    # ✅ Handle POST actions (Excel upload or Edit/Confirm button)
    if request.method == "POST":
        if 'excel_file' in request.files:
            # === Excel Upload Logic ===
            uploaded_file = request.files.get("excel_file")
            if uploaded_file and uploaded_file.filename.endswith(".xlsx"):
                try:
                    import pandas as pd
                    df = pd.read_excel(uploaded_file, engine="openpyxl")
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    df.fillna('', inplace=True)
                    history_data = df.to_dict(orient="records")
                except Exception as e:
                    file_error = f"❌ Failed to read Excel file: {str(e)}"
            else:
                file_error = "❌ Please upload a valid .xlsx Excel file."

        elif 'action' in request.form:
            # === Handle Edit/Confirm button in Box 2 ===
            pur_req_id = request.form.get("pur_req_id")
            action = request.form.get("action")
            selected_req = PurReq.query.filter_by(pur_req_id=pur_req_id).first()

            if action == "edit":
                # TODO: Handle edit logic (show editable form or save updated data)
                pass
            elif action == "confirm":
                # TODO: Handle confirm logic
                pass

    return render_template(
        "purchase_order_history.html",
        pur_reqs=pur_reqs,
        selected_id=selected_id,
        selected_req=selected_req,
        history_data=history_data,
        file_error=file_error
    )

@main.route('/supplier_management', methods=["GET", "POST"])
def supplier_management():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_id = session.get("user_id")

    # Existing purchase request logic
    pur_reqs = PurReq.query.all()
    selected_id = request.args.get("selected_id")
    selected_req = PurReq.query.filter_by(pur_req_id=selected_id).first() if selected_id else None

    # New: supplier list for Box 1
    supplier_list = SupplierDtl.query.order_by(SupplierDtl.date_created.desc()).all()

    # New: selected supplier
    selected_spl_id = request.args.get("spl_id")
    selected_supplier = SupplierDtl.query.filter_by(spl_id=selected_spl_id).first() if selected_spl_id else None

    # Tab selection (default to edit)
    active_tab = request.args.get("tab", "edit")

    # Handle Excel or confirm actions
    history_data = None
    file_error = None
    if request.method == "POST":
        if 'excel_file' in request.files:
            uploaded_file = request.files.get("excel_file")
            if uploaded_file and uploaded_file.filename.endswith(".xlsx"):
                try:
                    import pandas as pd
                    df = pd.read_excel(uploaded_file, engine="openpyxl")
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    df.fillna('', inplace=True)
                    history_data = df.to_dict(orient="records")
                except Exception as e:
                    file_error = f"❌ Failed to read Excel file: {str(e)}"
            else:
                file_error = "❌ Please upload a valid .xlsx Excel file."

    return render_template(
        "supplier_management.html",
        pur_reqs=pur_reqs,
        selected_id=selected_id,
        selected_req=selected_req,
        supplier_list=supplier_list,
        selected_supplier=selected_supplier,
        active_tab=active_tab,
        history_data=history_data,
        file_error=file_error
    )

# ─────────────────────────────────────────────
# Purchasing Reporting Tools Routes
# ─────────────────────────────────────────────
@main.route('/purchasing_report_tools', methods=["GET"])
def purchasing_report_tools():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    # ✅ Allow 1001 to see 1013 menu
    role_id = str(session.get("role_id"))
    if role_id not in ["1013", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")

    return render_template("purchasing_report_tools.html", username=username)


# ✅ Dynamic form loader
@main.route("/load_report_form/<report_type>")
def load_report_form(report_type):
    if report_type == "po_report":
        purchase_ids = PurReq.query.with_entities(PurReq.pur_req_id).all()
        pur_req_data = PurReq.query.all()
        return render_template(
            "reports/forms/po_report_form.html",
            purchase_ids=purchase_ids,
            pur_req_data=pur_req_data
        )

    elif report_type == "supplier_report":
        supplier_ids = SupplierDtl.query.with_entities(SupplierDtl.spl_id).all()
        supplier_data = SupplierDtl.query.all()
        return render_template(
            "reports/forms/supplier_report_form.html",
            supplier_ids=supplier_ids,
            supplier_data=supplier_data
        )

    elif report_type == "bills_report":
        bill_ids = PurReportBill.query.with_entities(PurReportBill.rep_bill_id).all()
        bill_data = PurReportBill.query.all()
        return render_template(
            "reports/forms/incoming_bills.html",
            bill_ids=bill_ids,
            bill_data=bill_data
        )
    return "<p>Invalid report type selected.</p>"

# ─────────────────────────────────────────────
# Purchase Schedule Part
# ─────────────────────────────────────────────

@main.route('/purchase_schedule')
def purchase_schedule():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    tabs = ROLE_MENU.get(role_id, [])

    return render_template(
        'purchase_schedule.html',
        username=username,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        **{"TAB_ROUTE_MAP": TAB_ROUTE_MAP}
    )


# ─────────────────────────────────────────────
# DataTables API Endpoints
# ─────────────────────────────────────────────
@main.route("/api/purchase_orders")
def api_purchase_orders():
    data = [
        {
            "pur_req_id": p.pur_req_id,
            "request_date": p.request_date.strftime("%Y-%m-%d") if p.request_date else "",
            "status": p.status
        }
        for p in PurReq.query.all()
    ]
    return jsonify({"data": data})


@main.route("/api/suppliers")
def api_suppliers():
    data = [
        {
            "spl_id": s.spl_id,
            "spl_nm": s.spl_nm,
            "spl_comp_nm": s.spl_comp_nm,
            "spl_position": s.spl_position,
            "date_created": s.date_created.strftime("%Y-%m-%d") if s.date_created else ""
        }
        for s in SupplierDtl.query.all()
    ]
    return jsonify({"data": data})


@main.route("/api/incoming_bills")
def api_incoming_bills():
    data = [
        {
            "bill_id": b.bill_id,
            "supplier_name": b.supplier_name,
            "bill_amount": b.current_bill,
            "currency": getattr(b, "currency", ""),  # Only if PurReportBill has a currency column
            "bill_date": b.expected_payment_date.strftime("%Y-%m-%d") if b.expected_payment_date else "",
            "status": getattr(b, "status", "")  # Optional if your model tracks bill status
        }
        for b in PurReportBill.query.all()
    ]
    return jsonify({"data": data})

# ─────────────────────────────────────────────
# Report Submission Handlers
# ─────────────────────────────────────────────
def generate_unique_id(table_model, id_column, prefix):
    year = datetime.now().strftime("%Y")
    max_id = db.session.query(func.max(getattr(table_model, id_column))).scalar()
    if max_id and max_id.startswith(year + prefix):
        number = int(max_id[-4:]) + 1
    else:
        number = 1
    return f"{year}{prefix}{number:04d}"


@main.route("/submit_po_report", methods=["POST"])
def submit_po_report():
    selected_ids = request.form.getlist("purchase_ids")
    notes = request.form.get("report_notes", "").strip()

    new_id = generate_unique_id(PurReportPO, "rep_po_id", "REPPO")
    ids_padded = (selected_ids + [None] * 5)[:5]

    report = PurReportPO(
        rep_po_id=new_id,
        pur_req_id_1=ids_padded[0],
        pur_req_id_2=ids_padded[1],
        pur_req_id_3=ids_padded[2],
        pur_req_id_4=ids_padded[3],
        pur_req_id_5=ids_padded[4],
        report_notes=notes if notes else None,
        report_date=datetime.now()
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"status": "success", "message": "PO Report generated!", "report_id": new_id})


@main.route("/submit_supplier_report", methods=["POST"])
def submit_supplier_report():
    selected_ids = request.form.getlist("supplier_ids")
    notes = request.form.get("report_notes", "").strip()

    new_id = generate_unique_id(PurReportSup, "rep_sup_id", "REPSUP")
    ids_padded = (selected_ids + [None] * 3)[:3]

    report = PurReportSup(
        rep_sup_id=new_id,
        spl_id_1=ids_padded[0],
        spl_id_2=ids_padded[1],
        spl_id_3=ids_padded[2],
        report_notes=notes if notes else None,
        report_date=datetime.now()
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"status": "success", "message": "Supplier Report generated!", "report_id": new_id})


@main.route("/submit_bills_report", methods=["POST"])
def submit_bills_report():
    selected_ids = request.form.getlist("bill_ids")
    notes = request.form.get("report_notes")

    new_id = generate_unique_id(PurReportBill, "rep_bill_id", "REPBIL")
    ids_padded = (selected_ids + [None] * 4)[:4]

    report = PurReportBill(
        rep_bill_id=new_id,
        bill_id_1=ids_padded[0],
        bill_id_2=ids_padded[1],
        bill_id_3=ids_padded[2],
        bill_id_4=ids_padded[3],
        report_notes=notes,
        report_date=datetime.now()
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"status": "success", "message": "Bills Report generated!", "report_id": new_id})

@main.route('/meeting_time')
def meeting_time():
    if 'username' not in session:
        return redirect(url_for('main.home'))

    username = session.get('username')
    role_id = str(session.get('role_id'))
    role_name = session.get('role_name')
    tabs = ROLE_MENU.get(role_id, [])

    usr_full_nm = get_usr_full_nm_from_session()

    return render_template(
        'meeting_time.html',
        username=username,
        usr_full_nm=usr_full_nm,
        role=role_name,
        role_id=role_id,
        tabs=tabs,
        MENU_ICONS=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )


@main.route('/production_department')
def production_department():
    """
    Production Department landing page.
    Allowed for role_id 1016 (Production staff) and 1001 (admin/dev).
    Displays the Production-specific menu (role 1016).
    """
    if 'username' not in session:
        return redirect(url_for('main.home'))

    role_id = str(session.get("role_id"))
    if role_id not in ["1016", "1001"]:
        return redirect(url_for('main.dashboard'))

    username = session.get("username")
    user_dtl = UserDtl.query.filter_by(usr_nm=username).first()
    usr_full_nm = user_dtl.usr_full_nm if user_dtl else username
    session['usr_full_nm'] = usr_full_nm

    production_menu = ROLE_MENU.get("1016", [])

    return render_template(
        "production_department.html",
        username=username,
        usr_full_nm=usr_full_nm,
        menu_items=production_menu,
        menu_icons=MENU_ICONS,
        TAB_ROUTE_MAP=TAB_ROUTE_MAP
    )

@main.route('/forecaster_ai')
def forecaster_ai():
    return render_template('forecaster_ai.html')

@main.route('/api/forecast/<forecast_type>')
def get_forecast_data(forecast_type):
    # --- Simulate 30 days of data ---
    dates = [datetime.now() - timedelta(days=i) for i in range(30)][::-1]
    data = []

    if forecast_type == "cashflow":
        base = 10000
        trend = np.cumsum(np.random.normal(500, 200, 30)) + base
        data = [{"date": d.strftime("%Y-%m-%d"), "value": float(v)} for d, v in zip(dates, trend)]
        summary = f"📈 Forecasted cash inflow indicates a {round((trend[-1]-trend[0])/trend[0]*100, 2)}% change over 30 days."
    
    elif forecast_type == "delay":
        delays = np.clip(np.random.normal(5, 2, 30), 0, 10)
        data = [{"date": d.strftime("%Y-%m-%d"), "value": float(v)} for d, v in zip(dates, delays)]
        summary = f"⏳ Average payment delay is {np.mean(delays):.1f} days, with peaks around {np.max(delays):.1f} days."

    elif forecast_type == "liquidity":
        summary = (
            "💡 Liquidity Improvement Suggestions:\n"
            "- Increase short-term asset ratio.\n"
            "- Negotiate better payment terms.\n"
            "- Optimize inventory turnover."
        )
        data = []

    elif forecast_type == "stability":
        summary = (
            "🧭 Financial Stability Recommendations:\n"
            "- Diversify revenue streams.\n"
            "- Reduce operational costs by 5%.\n"
            "- Strengthen risk reserves."
        )
        data = []

    else:
        summary = "Invalid forecast type."
        data = []

    return jsonify({"summary": summary, "chart_data": data})

# ---- routes.py (or part of main.py blueprint) ----

@main.route('/hr_dashboard')
def hr_dashboard():
    if 'username' not in session or str(session.get('role_id')) not in ("1010", "1001"):
        return redirect(url_for('main.dashboard'))
    usr_full_nm = get_usr_full_nm_from_session()
    return render_template("hr_dashboard.html", usr_full_nm=usr_full_nm)


@main.route('/employee_management')
def employee_management():
    if 'username' not in session or str(session.get('role_id')) not in ("1010", "1001"):
        return redirect(url_for('main.dashboard'))
    usr_full_nm = get_usr_full_nm_from_session()
    return render_template("employee_management.html", usr_full_nm=usr_full_nm)


@main.route('/payroll_management')
def payroll_management():
    if 'username' not in session or str(session.get('role_id')) not in ("1010", "1001"):
        return redirect(url_for('main.dashboard'))
    usr_full_nm = get_usr_full_nm_from_session()
    return render_template("payroll_management.html", usr_full_nm=usr_full_nm)



@main.route('/accounting_reporting_tools')
def accounting_reporting_tools():
    if 'username' not in session or str(session.get('role_id')) not in ("1010", "1001"):
        return redirect(url_for('main.dashboard'))
    usr_full_nm = get_usr_full_nm_from_session()
    return render_template("payroll_management.html", usr_full_nm=usr_full_nm)




# routes.py  (add near the bottom, after other routes)

# ----------  PLACEHOLDER / STUB DASHBOARDS  ----------
def _simple_stub(page_title):
    return render_template(
        'stub.html',
        page_title=page_title,
        usr_full_nm=session.get('usr_full_nm', 'User'),
        current_year=datetime.now().year
    )



@main.route('/create_purchase_order')
def create_purchase_order():
    return _simple_stub('Create Purchase Order')

@main.route('/reporting_tools')
def reporting_tools():
    return _simple_stub('Reporting Tools')

@main.route('/create_order')
def create_order():
    return _simple_stub('Create Order')

@main.route('/order_history')
def order_history():
    return _simple_stub('Order History')


@main.route('/customer_create_order')
def customer_create_order():
    return _simple_stub('Customer Create Order')


@main.route('/wh_profile')
def wh_profile():
    return _simple_stub('WH Profile')

@main.route('/customer_relationship_management')
def customer_relationship_management():
    return _simple_stub('Customer Relationship Management')    

# …add the rest that appear in TAB_ROUTE_MAP …

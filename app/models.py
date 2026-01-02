from app import db
from datetime import datetime


# ==============================
# USER MODELS
# ==============================

class User(db.Model):
    __tablename__ = 'usr_login'
    usr_nm = db.Column(db.String(50), primary_key=True)
    usr_pass = db.Column(db.String(100))
    usr_role_nm = db.Column(db.String(50))
    usr_role_id = db.Column(db.String(10))
    usr_id = db.Column(db.String(20), unique=True)
    log_count = db.Column(db.Integer, default=0, nullable=False)

class Role(db.Model):
    __tablename__ = 'usr_role'
    usr_role_id = db.Column(db.String(10), primary_key=True)
    usr_role_nm = db.Column(db.String(50))

class UserDtl(db.Model):
    __tablename__ = 'usr_dtl'
    usr_id = db.Column(db.String(20), primary_key=True)
    usr_nm = db.Column(db.String(50))
    usr_full_nm = db.Column(db.String(100))
    usr_phone = db.Column(db.String(20))
    usr_email = db.Column(db.String(30))
    usr_nid = db.Column(db.String(30))
    usr_add = db.Column(db.String(200))
    usr_city = db.Column(db.String(50))
    usr_region = db.Column(db.String(50))
    usr_country = db.Column(db.String(50))
    usr_dob = db.Column(db.Date)
    usr_company_nm = db.Column(db.String(100))
    usr_company_reg_no = db.Column(db.String(100))
    usr_comp_pos_nm = db.Column(db.String(100))
    usr_role_id = db.Column(db.String(10))
    usr_role_nm = db.Column(db.String(50))

# ==============================
# CUSTOMER MODELS
# ==============================

class CustomerSavingsDtl(db.Model):
    __tablename__ = 'customer_savings_dtl'
    cust_id = db.Column(db.String(50), primary_key=True)
    cust_nm = db.Column(db.String(100))
    saving_blc = db.Column(db.Float)
    currency = db.Column(db.String(10))

class CustomerOrderDtl(db.Model):
    __tablename__ = 'customer_order_dtl'
    cust_order_id = db.Column(db.String(50), primary_key=True)
    cust_order_itm_id = db.Column(db.String(50))
    cust_order_itm_nm = db.Column(db.String(100))
    order_amount = db.Column(db.Float)
    cust_id = db.Column(db.String(50))
    cust_nm = db.Column(db.String(100))
    last_status = db.Column(db.String(50))
    last_update = db.Column(db.DateTime)

# ==============================
# PURCHASE MODELS
# ==============================

class PurReq(db.Model):
    __tablename__ = 'pur_req'
    pur_req_id = db.Column(db.String(100), primary_key=True)
    pur_req_usr_name = db.Column(db.String(100))
    pur_req_usr_id = db.Column(db.String(100))
    pur_req_dept = db.Column(db.String(100))
    pur_req_itm_id = db.Column(db.String(100))
    pur_req_itm_name = db.Column(db.String(100))
    pur_req_itm_qty = db.Column(db.Integer)
    pur_req_itm_unit = db.Column(db.String(50))
    pur_req_date = db.Column(db.String(100))
    pur_req_sts = db.Column(db.String(50))
    pur_req_apv_id = db.Column(db.String(100))
    pur_req_apr_usr_id = db.Column(db.String(100))
    pur_req_apr_usr_name = db.Column(db.String(100))

class SupplierDtl(db.Model):
    __tablename__ = 'supplier_dtl'
    spl_id = db.Column(db.String(50), primary_key=True)
    spl_nm = db.Column(db.String(100))
    spl_position = db.Column(db.String(100))
    spl_comp_nm = db.Column(db.String(100))
    spl_comp_reg_no = db.Column(db.String(50))
    comp_address = db.Column(db.String(200))
    date_created = db.Column(db.DateTime)

# ==============================
# REPORT MODELS
# ==============================

class PurReportPO(db.Model):
    __tablename__ = 'pur_report_po'
    rep_po_id = db.Column(db.String(20), primary_key=True)
    pur_req_id_1 = db.Column(db.String(20))
    pur_req_id_2 = db.Column(db.String(20))
    pur_req_id_3 = db.Column(db.String(20))
    pur_req_id_4 = db.Column(db.String(20))
    pur_req_id_5 = db.Column(db.String(20))
    report_notes = db.Column(db.Text)
    report_date = db.Column(db.DateTime)

class PurReportSup(db.Model):
    __tablename__ = 'pur_report_sup'
    rep_sup_id = db.Column(db.String(20), primary_key=True)
    spl_id_1 = db.Column(db.String(20))
    spl_id_2 = db.Column(db.String(20))
    spl_id_3 = db.Column(db.String(20))
    report_notes = db.Column(db.Text)
    report_date = db.Column(db.DateTime)

class PurReportBill(db.Model):
    __tablename__ = 'pur_report_bill'
    rep_bill_id = db.Column(db.String(20), primary_key=True)  # e.g. 2025REPBILL1
    supplier_id = db.Column(db.String(50), nullable=True)
    supplier_nm = db.Column(db.String(255), nullable=True)
    current_months = db.Column(db.String(20), nullable=True)  # e.g. "2025-08"
    current_bill = db.Column(db.Numeric(12, 2), nullable=True)
    expected_payment_date = db.Column(db.Date, nullable=True)
    report_notes = db.Column(db.Text, nullable=True)
    report_date = db.Column(db.Date, default=datetime.utcnow)

    def __init__(self, spl_id=None, spl_nm=None, current_months=None,
                 current_bill=None, expected_payment_date=None, report_notes=None):
        self.rep_bill_id = self.generate_unique_id()
        self.spl_id = spl_id
        self.spl_nm = spl_nm
        self.current_months = current_months
        self.current_bill = current_bill
        self.expected_payment_date = expected_payment_date
        self.report_notes = report_notes
        self.report_date = datetime.utcnow().date()

    @staticmethod
    def generate_unique_id():
        year = datetime.utcnow().year
        prefix = f"{year}REPBILL"
        last_entry = PurReportBill.query.filter(
            PurReportBill.rep_bill_id.like(f"{prefix}%")
        ).order_by(PurReportBill.rep_bill_id.desc()).first()
        last_num = int(last_entry.rep_bill_id.replace(prefix, "")) + 1 if last_entry else 1
        return f"{prefix}{last_num}"




class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    date = db.Column(db.Date)
    status = db.Column(db.String(20))

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    kpi_score = db.Column(db.Integer)

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    salary = db.Column(db.Float)
    month = db.Column(db.String(20))

class Recruitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100))
    stage = db.Column(db.String(50))

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    stock_qty = db.Column(db.Integer)

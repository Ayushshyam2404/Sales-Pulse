from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from datetime import datetime
import base64
import re
import requests  # We use this to talk to SendGrid over HTTP (works on PythonAnywhere free tier)

app = Flask(__name__)

# --- SENDGRID CONFIGURATION ---
# I have inserted your key below. 
# IMPORTANT: You must verify the SENDER_EMAIL in SendGrid Settings -> Sender Authentication
SENDGRID_API_KEY = "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"
SENDER_EMAIL = "orangefalconrev@gmail.com"  # <--- CHANGE THIS to your verified SendGrid sender email

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class ReportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(100), default="Grand Plaza Hotel")
    start_date = db.Column(db.String(20), default="")
    end_date = db.Column(db.String(20), default="")

    visible_revenue = db.Column(db.Boolean, default=True)
    visible_pipeline = db.Column(db.Boolean, default=True)
    visible_activity = db.Column(db.Boolean, default=True)
    visible_insight = db.Column(db.Boolean, default=True)
    visible_source = db.Column(db.Boolean, default=True)
    visible_financials = db.Column(db.Boolean, default=True)
    visible_logs = db.Column(db.Boolean, default=True)
    visible_companies = db.Column(db.Boolean, default=True)

    revenue = db.Column(db.Integer, default=14500)
    rooms_booked = db.Column(db.Integer, default=120)
    past_revenue = db.Column(db.Integer, default=45000)
    past_rooms = db.Column(db.Integer, default=85)
    upcoming_revenue = db.Column(db.Integer, default=78500)
    upcoming_rooms = db.Column(db.Integer, default=120)
    lnr_calls = db.Column(db.Integer, default=42)
    leisure_calls = db.Column(db.Integer, default=18)
    rfps = db.Column(db.Integer, default=5)
    lnrs = db.Column(db.Integer, default=12)
    proposals = db.Column(db.Integer, default=8)
    signed = db.Column(db.Integer, default=2)
    ytd_revenue = db.Column(db.Integer, default=1056992)
    last_year_ytd = db.Column(db.Integer, default=1315108)
    mtd_revenue = db.Column(db.Integer, default=52829)
    last_year_mtd = db.Column(db.Integer, default=69770)
    mtd_forecast = db.Column(db.Integer, default=62247)
    rfps_submitted = db.Column(db.Integer, default=701)
    rfps_consideration = db.Column(db.Integer, default=16)
    sales_rooms = db.Column(db.Integer, default=1500)
    estimated_revenue = db.Column(db.Integer, default=139255)
    
    # --- DIAL CUSTOMIZATION ---
    dial_1_label = db.Column(db.String(100), default="YTD vs Last Year")
    dial_1_value = db.Column(db.Integer, default=0)
    dial_1_max = db.Column(db.Integer, default=0)
    
    dial_2_label = db.Column(db.String(100), default="MTD vs Forecast")
    dial_2_value = db.Column(db.Integer, default=0)
    dial_2_max = db.Column(db.Integer, default=0)
    
    dial_3_label = db.Column(db.String(100), default="RFP Consideration")
    dial_3_value = db.Column(db.Integer, default=0)
    dial_3_max = db.Column(db.Integer, default=0)
    
    # --- CARD TITLES/LABELS ---
    card_financials_title = db.Column(db.String(100), default="Sales & Marketing Financial Report")
    card_revenue_title = db.Column(db.String(100), default="Property Performance")
    card_pipeline_title = db.Column(db.String(100), default="Pipeline Pulse")
    card_activity_title = db.Column(db.String(100), default="Activity: Corporate vs Leisure")
    card_source_title = db.Column(db.String(100), default="Business Source: RFP vs LNR")
    card_logs_title = db.Column(db.String(100), default="Detailed Call Activity Log")
    
    # --- STAT LABELS ---
    label_total_revenue = db.Column(db.String(50), default="Total Revenue")
    label_rooms_booked = db.Column(db.String(50), default="Rooms Booked")
    label_past_revenue = db.Column(db.String(80), default="Past Stayed Revenue from Sales")
    label_past_rooms = db.Column(db.String(30), default="Rooms")
    label_upcoming_revenue = db.Column(db.String(80), default="Upcoming Revenue OTB from Sales")
    label_upcoming_rooms = db.Column(db.String(30), default="Rooms")
    label_active_proposals = db.Column(db.String(50), default="Active Proposals")
    label_signed_contracts = db.Column(db.String(50), default="Signed Contracts")
    label_ytd_rev = db.Column(db.String(50), default="YTD Revenue")
    label_mtd_rev = db.Column(db.String(50), default="MTD Revenue")
    label_est_rev = db.Column(db.String(50), default="Est. Revenue")
    label_sales_rooms = db.Column(db.String(50), default="Sales Rooms")
    label_rfps_sent = db.Column(db.String(50), default="RFPs Sent")
    label_rfp_requests = db.Column(db.String(50), default="RFP Requests")
    label_lnr_contracts = db.Column(db.String(50), default="LNR Contracts")
    label_corp_calls = db.Column(db.String(50), default="Corp")
    label_leisure_calls = db.Column(db.String(50), default="Leisure")
    label_rfps_source = db.Column(db.String(50), default="RFPs")
    label_lnrs_source = db.Column(db.String(50), default="LNRs")
    
    # --- CHART DATA LABELS ---
    chart_activity_title = db.Column(db.String(50), default="Call Volume")
    chart_activity_mix = db.Column(db.String(50), default="Activity Mix")
    chart_source_title = db.Column(db.String(50), default="Source Volume")
    chart_source_mix = db.Column(db.String(50), default="Contract Mix")
    
    # --- COMPANY NAMES (TOP 5) ---
    company_1 = db.Column(db.String(100), default="Marriott International")
    company_2 = db.Column(db.String(100), default="Hilton Hotels")
    company_3 = db.Column(db.String(100), default="IHG Hotels")
    company_4 = db.Column(db.String(100), default="Hyatt Hotels")
    company_5 = db.Column(db.String(100), default="Wyndham Hotels")
    card_companies_title = db.Column(db.String(100), default="Top Companies")
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class CallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(100)) 
    date = db.Column(db.String(50))
    name = db.Column(db.String(100))
    status = db.Column(db.String(100))

with app.app_context():
    db.create_all()
    if not ReportData.query.first():
        today = datetime.now()
        db.session.add(ReportData(start_date=today.strftime('%Y-%m-%d')))
        db.session.commit()

# --- SMART PARSING LOGIC ---
def smart_parse_excel(file_storage):
    try:
        df = pd.read_excel(file_storage, header=None)
        
        # 1. FIND THE HEADER ROW
        header_row_idx = -1
        for r in range(min(10, len(df))): 
            row_values = [str(x).lower() for x in df.iloc[r].tolist()]
            if any("date" in x for x in row_values) and any("name" in x for x in row_values):
                header_row_idx = r
                break
        
        if header_row_idx == -1: return [] 

        # 2. SCAN COLUMNS
        logs = []
        cols = len(df.columns)
        
        for c in range(cols):
            col_header = str(df.iloc[header_row_idx, c]).lower()
            
            if "date" in col_header:
                # Determine Section Title
                title = str(df.iloc[header_row_idx - 1, c]).strip()
                if title == "nan" or title == "":
                    if c > 0: title = str(df.iloc[header_row_idx - 1, c - 1]).strip()
                if title == "nan": title = "General Activity"

                # Find Neighbors
                name_col_idx = -1
                status_col_idx = -1
                
                for offset in range(4): 
                    if c + offset >= cols: break
                    neighbor_header = str(df.iloc[header_row_idx, c + offset]).lower()
                    
                    if "name" in neighbor_header and "group" in neighbor_header: name_col_idx = c + offset
                    elif "name" in neighbor_header and "guest" in neighbor_header: name_col_idx = c + offset
                    elif "name" in neighbor_header and name_col_idx == -1: name_col_idx = c + offset 
                    
                    if "status" in neighbor_header: status_col_idx = c + offset

                # Extract Data
                if name_col_idx != -1:
                    start_data_row = header_row_idx + 1
                    for r in range(start_data_row, len(df)):
                        name_val = df.iloc[r, name_col_idx]
                        if pd.isna(name_val) or str(name_val).strip() == "": continue 
                        
                        date_val = df.iloc[r, c]
                        status_val = df.iloc[r, status_col_idx] if status_col_idx != -1 else ""

                        date_str = str(date_val)
                        if isinstance(date_val, datetime):
                            date_str = date_val.strftime('%m/%d/%y')
                        elif len(date_str) > 10: date_str = date_str[:10]

                        logs.append(CallLog(
                            log_type=title,
                            date=date_str,
                            name=str(name_val),
                            status=str(status_val) if pd.notna(status_val) else ""
                        ))
        return logs

    except Exception as e:
        print(f"Parsing Error: {e}")
        return []

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    record = ReportData.query.first()
    logs = CallLog.query.all()
    
    log_list = [{
        'type': l.log_type, 'date': l.date, 'name': l.name, 'status': l.status
    } for l in logs]

    return jsonify({
        'hotel_name': record.hotel_name,
        'start_date': record.start_date,
        'end_date': record.end_date,
        'visible_revenue': record.visible_revenue,
        'visible_pipeline': record.visible_pipeline,
        'visible_activity': record.visible_activity,
        'visible_insight': record.visible_insight,
        'visible_source': record.visible_source,
        'visible_financials': record.visible_financials,
        'visible_logs': record.visible_logs,
        'visible_companies': record.visible_companies,
        'revenue': record.revenue,
        'rooms': record.rooms_booked,
        'past_revenue': record.past_revenue,
        'past_rooms': record.past_rooms,
        'upcoming_revenue': record.upcoming_revenue,
        'upcoming_rooms': record.upcoming_rooms,
        'lnr_calls': record.lnr_calls,
        'leisure_calls': record.leisure_calls,
        'rfps': record.rfps,
        'lnrs': record.lnrs,
        'proposals': record.proposals,
        'signed': record.signed,
        'ytd_revenue': record.ytd_revenue,
        'last_year_ytd': record.last_year_ytd,
        'mtd_revenue': record.mtd_revenue,
        'last_year_mtd': record.last_year_mtd,
        'mtd_forecast': record.mtd_forecast,
        'rfps_submitted': record.rfps_submitted,
        'rfps_consideration': record.rfps_consideration,
        'sales_rooms': record.sales_rooms,
        'estimated_revenue': record.estimated_revenue,
        'dial_1_label': record.dial_1_label,
        'dial_1_value': record.dial_1_value,
        'dial_1_max': record.dial_1_max,
        'dial_2_label': record.dial_2_label,
        'dial_2_value': record.dial_2_value,
        'dial_2_max': record.dial_2_max,
        'dial_3_label': record.dial_3_label,
        'dial_3_value': record.dial_3_value,
        'dial_3_max': record.dial_3_max,
        'card_financials_title': record.card_financials_title,
        'card_revenue_title': record.card_revenue_title,
        'card_pipeline_title': record.card_pipeline_title,
        'card_activity_title': record.card_activity_title,
        'card_source_title': record.card_source_title,
        'card_logs_title': record.card_logs_title,
        'label_total_revenue': record.label_total_revenue,
        'label_rooms_booked': record.label_rooms_booked,
        'label_past_revenue': record.label_past_revenue,
        'label_past_rooms': record.label_past_rooms,
        'label_upcoming_revenue': record.label_upcoming_revenue,
        'label_upcoming_rooms': record.label_upcoming_rooms,
        'label_active_proposals': record.label_active_proposals,
        'label_signed_contracts': record.label_signed_contracts,
        'label_ytd_rev': record.label_ytd_rev,
        'label_mtd_rev': record.label_mtd_rev,
        'label_est_rev': record.label_est_rev,
        'label_sales_rooms': record.label_sales_rooms,
        'label_rfps_sent': record.label_rfps_sent,
        'label_rfp_requests': record.label_rfp_requests,
        'label_lnr_contracts': record.label_lnr_contracts,
        'label_corp_calls': record.label_corp_calls,
        'label_leisure_calls': record.label_leisure_calls,
        'label_rfps_source': record.label_rfps_source,
        'label_lnrs_source': record.label_lnrs_source,
        'chart_activity_title': record.chart_activity_title,
        'chart_activity_mix': record.chart_activity_mix,
        'chart_source_title': record.chart_source_title,
        'chart_source_mix': record.chart_source_mix,
        'company_1': record.company_1,
        'company_2': record.company_2,
        'company_3': record.company_3,
        'company_4': record.company_4,
        'company_5': record.company_5,
        'card_companies_title': record.card_companies_title,
        'logs': log_list
    })

@app.route('/api/update', methods=['POST'])
def update_data():
    record = ReportData.query.first()
    
    record.hotel_name = request.form.get('hotel_name')
    record.start_date = request.form.get('start_date')
    record.end_date = request.form.get('end_date')
    
    record.visible_revenue = request.form.get('visible_revenue') == 'true'
    record.visible_pipeline = request.form.get('visible_pipeline') == 'true'
    record.visible_activity = request.form.get('visible_activity') == 'true'
    record.visible_insight = request.form.get('visible_insight') == 'true'
    record.visible_source = request.form.get('visible_source') == 'true'
    record.visible_financials = request.form.get('visible_financials') == 'true'
    record.visible_logs = request.form.get('visible_logs') == 'true'
    record.visible_companies = request.form.get('visible_companies') == 'true'

    record.revenue = request.form.get('revenue')
    record.rooms_booked = request.form.get('rooms')
    record.past_revenue = request.form.get('past_revenue')
    record.past_rooms = request.form.get('past_rooms')
    record.upcoming_revenue = request.form.get('upcoming_revenue')
    record.upcoming_rooms = request.form.get('upcoming_rooms')
    record.lnr_calls = request.form.get('lnr_calls')
    record.leisure_calls = request.form.get('leisure_calls')
    record.ytd_revenue = request.form.get('ytd_revenue')
    record.last_year_ytd = request.form.get('last_year_ytd')
    record.mtd_revenue = request.form.get('mtd_revenue')
    record.last_year_mtd = request.form.get('last_year_mtd')
    record.mtd_forecast = request.form.get('mtd_forecast')
    record.rfps_submitted = request.form.get('rfps_submitted')
    record.rfps_consideration = request.form.get('rfps_consideration')
    record.sales_rooms = request.form.get('sales_rooms')
    record.estimated_revenue = request.form.get('estimated_revenue')
    record.dial_1_label = request.form.get('dial_1_label', 'YTD vs Last Year')
    record.dial_1_value = request.form.get('dial_1_value') or 0
    record.dial_1_max = request.form.get('dial_1_max') or 0
    
    record.dial_2_label = request.form.get('dial_2_label', 'MTD vs Forecast')
    record.dial_2_value = request.form.get('dial_2_value') or 0
    record.dial_2_max = request.form.get('dial_2_max') or 0
    
    record.dial_3_label = request.form.get('dial_3_label', 'RFP Consideration')
    record.dial_3_value = request.form.get('dial_3_value') or 0
    record.dial_3_max = request.form.get('dial_3_max') or 0

    # --- CARD TITLES ---
    record.card_financials_title = request.form.get('card_financials_title') or record.card_financials_title
    record.card_revenue_title = request.form.get('card_revenue_title') or record.card_revenue_title
    record.card_pipeline_title = request.form.get('card_pipeline_title') or record.card_pipeline_title
    record.card_activity_title = request.form.get('card_activity_title') or record.card_activity_title
    record.card_source_title = request.form.get('card_source_title') or record.card_source_title
    record.card_logs_title = request.form.get('card_logs_title') or record.card_logs_title
    
    # --- STAT LABELS ---
    record.label_total_revenue = request.form.get('label_total_revenue') or record.label_total_revenue
    record.label_rooms_booked = request.form.get('label_rooms_booked') or record.label_rooms_booked
    record.label_past_revenue = request.form.get('label_past_revenue') or record.label_past_revenue
    record.label_past_rooms = request.form.get('label_past_rooms') or record.label_past_rooms
    record.label_upcoming_revenue = request.form.get('label_upcoming_revenue') or record.label_upcoming_revenue
    record.label_upcoming_rooms = request.form.get('label_upcoming_rooms') or record.label_upcoming_rooms
    record.label_active_proposals = request.form.get('label_active_proposals') or record.label_active_proposals
    record.label_signed_contracts = request.form.get('label_signed_contracts') or record.label_signed_contracts
    record.label_ytd_rev = request.form.get('label_ytd_rev') or record.label_ytd_rev
    record.label_mtd_rev = request.form.get('label_mtd_rev') or record.label_mtd_rev
    record.label_est_rev = request.form.get('label_est_rev') or record.label_est_rev
    record.label_sales_rooms = request.form.get('label_sales_rooms') or record.label_sales_rooms
    record.label_rfps_sent = request.form.get('label_rfps_sent') or record.label_rfps_sent
    record.label_rfp_requests = request.form.get('label_rfp_requests') or record.label_rfp_requests
    record.label_lnr_contracts = request.form.get('label_lnr_contracts') or record.label_lnr_contracts
    record.label_corp_calls = request.form.get('label_corp_calls') or record.label_corp_calls
    record.label_leisure_calls = request.form.get('label_leisure_calls') or record.label_leisure_calls
    record.label_rfps_source = request.form.get('label_rfps_source') or record.label_rfps_source
    record.label_lnrs_source = request.form.get('label_lnrs_source') or record.label_lnrs_source
    
    # --- CHART LABELS ---
    record.chart_activity_title = request.form.get('chart_activity_title') or record.chart_activity_title
    record.chart_activity_mix = request.form.get('chart_activity_mix') or record.chart_activity_mix
    record.chart_source_title = request.form.get('chart_source_title') or record.chart_source_title
    record.chart_source_mix = request.form.get('chart_source_mix') or record.chart_source_mix
    
    # --- COMPANY NAMES ---
    record.company_1 = request.form.get('company_1') or record.company_1
    record.company_2 = request.form.get('company_2') or record.company_2
    record.company_3 = request.form.get('company_3') or record.company_3
    record.company_4 = request.form.get('company_4') or record.company_4
    record.company_5 = request.form.get('company_5') or record.company_5
    record.card_companies_title = request.form.get('card_companies_title') or record.card_companies_title

    # EXCEL PARSING RESTORED
    if 'excel_file' in request.files:
        file = request.files['excel_file']
        if file.filename != '':
            logs = smart_parse_excel(file)
            if logs:
                db.session.query(CallLog).delete()
                db.session.add_all(logs)

    record.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Data updated'})

# --- SENDGRID EMAIL LOGIC (HTTP) ---
@app.route('/api/share', methods=['POST'])
def share_report():
    try:
        data = request.json
        recipient = data.get('email')
        image_data = data.get('image')

        if not recipient or not image_data:
            return jsonify({'success': False, 'message': 'Missing data'}), 400

        # Clean base64 string
        image_data_clean = re.sub('^data:image/.+;base64,', '', image_data)

        # SendGrid API Endpoint (Works on Free Tier)
        url = "https://api.sendgrid.com/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }

        # Construct JSON Payload
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": SENDER_EMAIL},
            "subject": "Orange Falcon Sales Pulse Report",
            "content": [{
                "type": "text/html",
                "value": """
                    <div style="background-color: #000; color: #fff; font-family: sans-serif; padding: 20px;">
                        <h2 style="color: #FF9F0A;">Orange Falcon Sales Pulse Report</h2>
                        <p>Here are the key insights of your property</p>
                        <br>
                        <img src="cid:dashboard_image" style="width: 100%; max-width: 800px; border-radius: 12px; border: 1px solid #333;">
                        <br><br>
                        <p style="color: #888; font-size: 12px;">Orange Falcon (Formerly Known As Orange Technolab LLC) &copy; 2025</p>
                    </div>
                """
            }],
            "attachments": [{
                "content": image_data_clean,
                "type": "image/png",
                "filename": "dashboard.png",
                "disposition": "inline",
                "content_id": "dashboard_image"
            }]
        }

        # Send POST request
        response = requests.post(url, headers=headers, json=payload)

        # Check response
        if response.status_code in [200, 202]:
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        else:
            # Log exact error from SendGrid for debugging
            print(f"SendGrid Error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'message': f"SendGrid Error: {response.text}"}), 500

    except Exception as e:
        print(f"System Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
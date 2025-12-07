from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import re

app = Flask(__name__)

# --- EMAIL CONFIGURATION ---
SMTP_EMAIL = "orangefalconrev@gmail.com"        # <--- PUT YOUR EMAIL HERE
SMTP_PASSWORD = "zccc opry odun gpla"      # <--- PUT YOUR APP PASSWORD HERE
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

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

    revenue = db.Column(db.Integer, default=14500)
    rooms_booked = db.Column(db.Integer, default=120)
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
        'revenue': record.revenue,
        'rooms': record.rooms_booked,
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

    record.revenue = request.form.get('revenue')
    record.rooms_booked = request.form.get('rooms')
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

@app.route('/api/share', methods=['POST'])
def share_report():
    try:
        data = request.json
        recipient = data.get('email')
        image_data = data.get('image')

        if not recipient or not image_data:
            return jsonify({'success': False, 'message': 'Missing data'}), 400

        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        img_bytes = base64.b64decode(image_data)

        msg = MIMEMultipart()
        msg['Subject'] = "Orange Falcon Sales Pulse Report"
        msg['From'] = SMTP_EMAIL
        msg['To'] = recipient

        # EMAIL BODY UPDATE
        html_body = """
        <html>
          <body style="background-color: #000; color: #fff; font-family: sans-serif; padding: 20px;">
            <h2 style="color: #FF9F0A;">Orange Falcon Sales Pulse Report</h2>
            <p>Here are the key insights of your property</p>
            <br>
            <img src="cid:dashboard_image" style="width: 100%; max-width: 800px; border-radius: 12px; border: 1px solid #333;">
            <br><br>
            <p style="color: #888; font-size: 12px;">Orange Falcon (Formerly Known As Orange Technolab LLC) &copy; 2025</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        image = MIMEImage(img_bytes, name="dashboard.png")
        image.add_header('Content-ID', '<dashboard_image>')
        image.add_header('Content-Disposition', 'inline', filename='dashboard.png')
        msg.attach(image)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return jsonify({'success': True, 'message': 'Email sent successfully'})

    except Exception as e:
        print(f"Email Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
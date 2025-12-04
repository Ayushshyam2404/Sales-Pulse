from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class ReportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(100), default="Grand Plaza Hotel")
    
    start_date = db.Column(db.String(20), default="")
    end_date = db.Column(db.String(20), default="")
    
    revenue = db.Column(db.Integer, default=14500)
    rooms_booked = db.Column(db.Integer, default=120)
    
    # Activity Section (Updated to Leisure)
    lnr_calls = db.Column(db.Integer, default=42)
    leisure_calls = db.Column(db.Integer, default=18)
    
    # NEW: Business Source Section
    rfps = db.Column(db.Integer, default=5)
    lnrs = db.Column(db.Integer, default=12)
    
    # Pipeline Section
    proposals = db.Column(db.Integer, default=8)
    signed = db.Column(db.Integer, default=2)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize DB with defaults
with app.app_context():
    db.create_all()
    if not ReportData.query.first():
        today = datetime.now()
        two_weeks_ago = today - timedelta(days=14)
        
        db.session.add(ReportData(
            start_date=two_weeks_ago.strftime('%Y-%m-%d'),
            end_date=today.strftime('%Y-%m-%d')
        ))
        db.session.commit()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    record = ReportData.query.first()
    
    if request.method == 'GET':
        return jsonify({
            'hotel_name': record.hotel_name,
            'start_date': record.start_date,
            'end_date': record.end_date,
            'revenue': record.revenue,
            'rooms': record.rooms_booked,
            'lnr_calls': record.lnr_calls,
            'leisure_calls': record.leisure_calls, # Updated
            'rfps': record.rfps,
            'lnrs': record.lnrs,
            'proposals': record.proposals,
            'signed': record.signed
        })
    
    if request.method == 'POST':
        data = request.json
        record.hotel_name = data.get('hotel_name')
        record.start_date = data.get('start_date')
        record.end_date = data.get('end_date')
        record.revenue = data.get('revenue')
        record.rooms_booked = data.get('rooms')
        
        record.lnr_calls = data.get('lnr_calls')
        record.leisure_calls = data.get('leisure_calls') # Updated
        
        record.rfps = data.get('rfps')
        record.lnrs = data.get('lnrs')
        
        record.proposals = data.get('proposals')
        record.signed = data.get('signed')
        record.last_updated = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Data saved successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
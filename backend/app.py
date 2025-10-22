from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///job_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    dateApplied = db.Column(db.String(50), nullable=False)
    jobUrl = db.Column(db.String(500))
    notes = db.Column(db.Text)
    location = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'status': self.status,
            'dateApplied': self.dateApplied,
            'jobUrl': self.jobUrl or '',
            'notes': self.notes or '',
            'location': self.location or '',
            'salary': self.salary or '',
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/applications', methods=['GET'])
def get_applications():
    applications = Application.query.all()
    return jsonify([app.to_dict() for app in applications])

@app.route('/api/applications', methods=['POST'])
def add_application():
    data = request.json
    
    new_app = Application(
        company=data.get('company'),
        position=data.get('position'),
        status=data.get('status', 'Applied'),
        dateApplied=data.get('dateApplied'),
        jobUrl=data.get('jobUrl', ''),
        notes=data.get('notes', ''),
        location=data.get('location', ''),
        salary=data.get('salary', '')
    )
    
    db.session.add(new_app)
    db.session.commit()
    return jsonify(new_app.to_dict()), 201

@app.route('/api/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    data = request.json
    app = Application.query.get(app_id)
    
    if not app:
        return jsonify({'error': 'Application not found'}), 404
    
    app.company = data.get('company', app.company)
    app.position = data.get('position', app.position)
    app.status = data.get('status', app.status)
    app.dateApplied = data.get('dateApplied', app.dateApplied)
    app.jobUrl = data.get('jobUrl', app.jobUrl)
    app.notes = data.get('notes', app.notes)
    app.location = data.get('location', app.location)
    app.salary = data.get('salary', app.salary)
    app.updatedAt = datetime.utcnow()
    
    db.session.commit()
    return jsonify(app.to_dict())

@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    app = Application.query.get(app_id)
    
    if not app:
        return jsonify({'error': 'Application not found'}), 404
    
    db.session.delete(app)
    db.session.commit()
    return jsonify({'message': 'Application deleted successfully'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = Application.query.count()
    applied = Application.query.filter_by(status='Applied').count()
    interview = Application.query.filter_by(status='Interview').count()
    offer = Application.query.filter_by(status='Offer').count()
    rejected = Application.query.filter_by(status='Rejected').count()
    
    stats = {
        'total': total,
        'applied': applied,
        'interview': interview,
        'offer': offer,
        'rejected': rejected
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
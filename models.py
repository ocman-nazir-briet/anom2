from config import db
from datetime import datetime

class AppType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name




class LogsData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    date_created = db.Column(db.DateTime, default=datetime.now)

    app_type_id = db.Column(db.Integer, db.ForeignKey('app_type.id'), nullable=False)
    app_type = db.relationship('AppType', backref=db.backref('logs_data', lazy=True))

    def __repr__(self):
        return self.id




class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.now)

    rule_id = db.Column(db.Integer, db.ForeignKey('rules.id'))
    rule = db.relationship('Rules', backref=db.backref('alerts', lazy=True))

    def __repr__(self):
        return f"Alert(id={self.id}, severity_type={self.severity_type}, rule_name={self.rule_name})"




class Rules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    severity_type = db.Column(db.String(255))
    risk_score = db.Column(db.Integer)
    rule_name = db.Column(db.String(255), unique=True)
    query_check = db.Column(db.String(255))
    look_back = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now)

    app_type_id = db.Column(db.Integer, db.ForeignKey('app_type.id'))
    app_type = db.relationship('AppType', backref=db.backref('rules', lazy=True))

    def __repr__(self):
        return f"Rule(id={self.id}, severity_type={self.severity_type})"
    
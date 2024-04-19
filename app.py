import os
from flask import Flask, request, jsonify
from models import AppType, LogsData, Rules
from config import app, db
from datetime import datetime
from rules import dropboxRulesTrigger


@app.route("/")
def home():
    return "Hello World"



@app.route("/addRule", methods=['GET', 'POST'])
def addRule():
    if request.method == "POST":
        try:
            data = request.json
            try:
                app_type=data['app_type']
                type = AppType.query.filter_by(name=app_type).first()            
            except:
                return jsonify({'error': 'Invalid AppType.'}), 500
            
            rule_data = Rules(
                severity_type=data['severity_type'], 
                risk_score=data['risk_score'], 
                rule_name=data['rule_name'], 
                app_type=type,
                query_check=data['query_check'],
                look_back=data['look_back']
                )
            
            db.session.add(rule_data)
            db.session.commit()
            return jsonify({'message': 'Rule added successfully.'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'An error occurred while adding data to the Rules table.'}), 500
    else:
        return jsonify({'message': 'Only POST requests are allowed.'}), 405



@app.route("/dropbox", methods=['GET', 'POST'])
def dropbox():
    if request.method == "POST":
        try:
            data = request.json
            type = AppType.query.filter_by(name='dropbox').first()
            
            """
            Here checking for the anomly in ingested logs data, if found then we will save that log in db and generate an alert for it.
            """
            alert = dropboxRulesTrigger(data)
            print("Anomly Found? ",alert)
            if type:
                logs_data = LogsData(
                    data=data, app_type=type, date_created=datetime.now())
                db.session.add(logs_data)
                db.session.commit()
                return jsonify({'message': 'Data added successfully.'}), 200
            else:
                return jsonify({'error': 'AppType with name "dropbox" does not exist.'}), 404

        except Exception as e:
            print(str(e))
            db.session.rollback()
            return jsonify({'error': 'An error occurred while adding data to the LogsData table.'}), 500
    else:
        return jsonify({'message': 'Only POST requests are allowed.'}), 405



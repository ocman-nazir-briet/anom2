import os
from flask import Flask, request, jsonify
from models import AppType, LogsData, Rules
from config import app, db
from datetime import datetime
from rules import rulesTrigger


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



@app.route("/ingest", methods=['GET', 'POST'])
def addData():
    if request.method == "POST":
        try:
            data = request.json
            app_type = request.headers.get('appType')

            type = AppType.query.filter_by(name=app_type).first()
            
            """
            Here checking for the anomly in ingested logs data, if found then we will save that log in db and generate an alert for it.
            """
            alert = rulesTrigger(data, app_type)
            print("Anomly Found? ",alert)
            if type:
                logs_data = LogsData(
                    data=data, app_type=type, date_created=datetime.now())
                db.session.add(logs_data)
                db.session.commit()
                return jsonify({'message': f'{app_type} Log Data added successfully.'}), 200
            else:
                return jsonify({'error': f'AppType with name {app_type} does not exist.'}), 404

        except Exception as e:
            print(str(e))
            db.session.rollback()
            return jsonify({'error': f'An error occurred while adding data to the {app_type} LogsData table.'}), 500
    else:
        return jsonify({'message': 'Only POST requests are allowed.'}), 405


# @app.route("/github", methods=['GET', 'POST'])
# def github():
#     if request.method == "POST":
#         try:
#             data = request.json
#             type = AppType.query.filter_by(name='github').first()
            
#             """
#             Here checking for the anomly in ingested logs data, if found then we will save that log in db and generate an alert for it.
#             """
#             alert = githubRulesTrigger(data)
#             print("Anomly Found? ",alert)
#             if type:
#                 logs_data = LogsData(
#                     data=data, app_type=type, date_created=datetime.now())
#                 db.session.add(logs_data)
#                 db.session.commit()
#                 return jsonify({'message': 'Data added successfully.'}), 200
#             else:
#                 return jsonify({'error': 'AppType with name "github" does not exist.'}), 404

#         except Exception as e:
#             print(str(e))
#             db.session.rollback()
#             return jsonify({'error': 'An error occurred while adding data to the LogsData table.'}), 500
#     else:
#         return jsonify({'message': 'Only POST requests are allowed.'}), 405


# @app.route("/azure", methods=['GET', 'POST'])
# def azure():
#     if request.method == "POST":
#         try:
#             data = request.json
#             app_type = request.headers.get('appType')

#             type = AppType.query.filter_by(name=app_type).first()
            
#             """
#             Here checking for the anomly in ingested logs data, if found then we will save that log in db and generate an alert for it.
#             """
#             alert = rulesTrigger(data, app_type)
#             print("Anomly Found? ",alert)
#             if type:
#                 logs_data = LogsData(
#                     data=data, app_type=type, date_created=datetime.now())
#                 db.session.add(logs_data)
#                 db.session.commit()
#                 return jsonify({'message': 'Data added successfully.'}), 200
#             else:
#                 return jsonify({'error': 'AppType with name does not exist.'}), 404

#         except Exception as e:
#             print(str(e))
#             db.session.rollback()
#             return jsonify({'error': 'An error occurred while adding data to the LogsData table.'}), 500
#     else:
#         return jsonify({'message': 'Only POST requests are allowed.'}), 405



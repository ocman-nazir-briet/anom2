import os
from flask import Flask, request, jsonify
from models import AppType, LogsData, Rules, Alert
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


# list of rules
@app.route("/list-rules", methods=["GET"])
def list_rules():
    # need to add is active
    rules = Rules.query.filter_by(is_active=True).all()

    rules_list = []
    for rule in rules:
        rule_data = {
            'id': rule.id,
            'severity_type': rule.severity_type,
            'risk_score': rule.risk_score,
            'rule_name': rule.rule_name,
            'query_check': rule.query_check,
            'look_back': rule.look_back,
            'date_created': rule.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'app_type_id': rule.app_type_id
        }
        rules_list.append(rule_data)

    return jsonify({"rules": rules_list})


# single rule
@app.route("/rule/<int:rule_id>", methods=["GET"])
def get_rule(rule_id):
    rule = Rules.query.get(rule_id)

    if rule and rule.is_active:
        rule_data = {
            'id': rule.id,
            'severity_type': rule.severity_type,
            'risk_score': rule.risk_score,
            'rule_name': rule.rule_name,
            'query_check': rule.query_check,
            'look_back': rule.look_back,
            'date_created': rule.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'app_type_id': rule.app_type_id
        }

        return jsonify(rule_data), 200
    else:
        return jsonify({'error': 'Rule not found or not active'}), 404


# post api for alert ret of specific app
@app.route("/alerts", methods=["POST"])
def get_alerts_by_app_type():
    request_data = request.get_json()
    app_type_id = request_data.get('app_type_id')

    if app_type_id is None:
        return jsonify({'error': 'app_type_id is required in the request body'}), 400

    alerts = Alert.query.filter_by(app_type_id=app_type_id).all()

    if alerts:
        alert_list = []
        for alert in alerts:
            alert_data = {
                'id': alert.id,
                'data': alert.data,
                'is_active': alert.is_active,
                'date_created': alert.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'rule_id': alert.rule_id
            }
            alert_list.append(alert_data)

        return jsonify({"alerts": alert_list}), 200
    else:
        return jsonify({'error': 'No alerts found for the given app type'}), 404


# post api for log ret of specific app
@app.route("/logs-data", methods=["POST"])
def get_logs_data_by_app_type():
    request_data = request.get_json()
    app_type_id = request_data.get('app_type_id')

    if app_type_id is None:
        return jsonify({'error': 'app_type_id is required in the request body'}), 400

    logs_data = LogsData.query.filter_by(app_type_id=app_type_id).all()

    if logs_data:
        logs_data_list = []
        for log_data in logs_data:
            log_data_dict = {
                'id': log_data.id,
                'data': log_data.data,
                'date_created': log_data.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'app_type_id': log_data.app_type_id
            }
            logs_data_list.append(log_data_dict)

        return jsonify({"logs_data": logs_data_list}), 200
    else:
        return jsonify({'error': 'No logs data found for the given app type'}), 404

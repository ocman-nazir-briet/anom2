from models import Alert, AppType, Rules, LogsData
from utils import generateAlert
from flask_sqlalchemy import SQLAlchemy
from config import app, db
from sqlalchemy import cast, JSON
from sqlalchemy import func
from datetime import datetime, timedelta




# DropBox
def dropboxRulesTrigger(data):
    alert_check = False
    rules = Rules.query.join(AppType).filter(AppType.name == "dropbox").all()

    """
    Here I'm using rules from database
    """
    for rule in rules:
        check = str(rule.query_check)
        hours = rule.look_back
        look_back = datetime.now() - timedelta(hours=hours)

        if check:
            if 'count' in check:
                count = (
                    LogsData.query
                    .filter(func.json_extract_path_text(LogsData.data, 'actor', 'admin', 'email') == data['actor']['admin']['email'])
                    .filter(func.json_extract_path_text(LogsData.data, 'event_type', 'tag') == data['event_type']['tag'])
                    .filter(LogsData.date_created >= look_back)
                    .count()
                )
                data["count"] = count    
            if eval(check):
                alert_check = True
                generateAlert(data, rule.id)

    """
    Returning on the basis of anomly, if found then true and save that log to logsdata and vice versa 
    """
    if alert_check==True:
        return True
    else:
        return False

# GitHub
def githubRulesTrigger(data):
    alert_check = False
    rules = Rules.query.join(AppType).filter(AppType.name == "github").all()

    """
    Here I'm using rules from database
    """
    for rule in rules:
        check = str(rule.query_check)
        if eval(check):
            alert_check = True
            generateAlert(data, rule.id)

    """
    Returning on the basis of anomly, if found then true and save that log to logsdata and vice versa 
    """
    if alert_check==True:
        return True
    else:
        return False

# Azure
def azureRulesTrigger(data):
    alert_check = False
    rules = Rules.query.join(AppType).filter(AppType.name == "azure").all()

    """
    Here I'm using rules from database
    """
    for rule in rules:
        check = str(rule.query_check)
        if eval(check):
            alert_check = True
            generateAlert(data, rule.id)

    """
    Returning on the basis of anomly, if found then true and save that log to logsdata and vice versa 
    """
    if alert_check==True:
        return True
    else:
        return False
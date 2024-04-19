from models import Alert, AppType, Rules, LogsData
from utils import generateAlert
from flask_sqlalchemy import SQLAlchemy
from config import app, db
from sqlalchemy import cast, JSON
from sqlalchemy import func
from datetime import datetime, timedelta





def dropboxRulesTrigger(data):
    alert_check = False
    # rules = Rules.query.filter_by(app_type="dropbox").all()
    rules = Rules.query.join(AppType).filter(AppType.name == "dropbox").all()

    """
    Here I'm using rules from database
    """
    for rule in rules:
        check = str(rule.query_check)
        hours = rule.look_back
        look_back = datetime.now() - timedelta(hours=0)

        if check:
            if 'count' in check:
                count = (
                    LogsData.query
                    .filter(func.json_extract_path_text(LogsData.data, 'actor', 'admin', 'email') == data['actor']['admin']['email'])
                    .filter(func.json_extract_path_text(LogsData.data, 'event_type', 'tag') == data['event_type']['tag'])
                    # .filter(LogsData.date_created >= look_back)
                    .count()
                )
                data["count"] = count    
            if eval(check):
                alert_check = True
                generateAlert(data, rule.id)
        

    """
    Rule 1. Dropbox Admin Sign-in-as Session
    """

    # check = str(data['event_type']['tag'] == 'sign_in_as_session_start' and data['actor']['admin']['team_member_id'] == "dbmid:AADQXRJkgb76NF2a5yGdAwkOV-t_IYp2exg")
    # if eval(check):
    #     alert_check = True
    #     generateAlert("medium", 50, "Dropbox Admin Sign-in-as Session", "dropbox", data)


    """
    Rule 2. Dropbox item shared externally
    """
    # if data['event_type']['tag'] == "shared_content_add_member":
    #     alert_check = True
    #     generateAlert("medium", 50, "Dropbox item shared externally", "dropbox", data)


    """
    Rule 3. Dropbox Linked Team Application Added
    """
    # if data['event_type']['tag'] == "app_link_team" or  data['event_type']['tag'] == "app_link_member":
    #     alert_check = True
    #     generateAlert("low", 10, "Dropbox Linked Team Application Added", "dropbox", data)


    """
    Rule 4. Dropbox Many Deletes
    """
    # if data['event_category']['tag'] == "file_operations" and  data['event_type']['tag'] == "delete":
    #     # previous check missing, will add later
    #     alert_check = True
    #     generateAlert("medium", 50, "Dropbox Many Deletes", "dropbox", data)


    """
    Rule 5. Dropbox Many Downloads
    """
    # if data['event_category']['tag'] == "file_operations" and  data['event_type']['tag'] == "download":
    #     # previous check missing, will add later
    #     alert_check = True
    #     generateAlert("medium", 50, "Dropbox Many Downloads", "dropbox", data)


    """
    Rule 6. Dropbox Ownership Transfer
    """
    # if data['event_category']['tag'] == "dropbox_ownership_transfer":
    #     alert_check = True
    #     generateAlert("high", 70, "Dropbox Ownership Transfer", "dropbox", data)


    """
    Rule 7. Dropbox User Disabled 2FA
    """
    # if data['event_category']['tag'] == "tfa" and data['event_type']['tag'] == "tfa_change_status" and data['p_log_type'] == "Dropbox.TeamEvent":
    #     alert_check = True
    #     generateAlert("high", 70, "Dropbox User Disabled 2FA", "dropbox", data)


    """
    Returning on the basis of anomly, if found then true and save that log to logsdata and vice versa 
    """
    if alert_check==True:
        return True
    else:
        return False



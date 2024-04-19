from config import db
from models import Alert, Rules


def generateAlert(data, rule_id):
    rule = Rules.query.get(rule_id)
    alert = Alert(data=data, is_active=True, rule = rule)
    db.session.add(alert)
    db.session.commit()

def sendAlert():
    pass
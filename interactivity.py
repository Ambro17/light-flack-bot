from flask.blueprints import Blueprint
from flask import request
from slack.web.client import WebClient
import json

bp = Blueprint('interactive', __name__)
roomsbot = 'xoxb-548583362998-891180035635-ZSCbzL8TZYQXAd6VMzRpKMRU'
OviBot = WebClient(roomsbot)


@bp.route("/message_actions", methods=["POST"])
def message_actions():
    print("Handling message action..")
    action = json.loads(request.form["payload"])
    try:
        return handle_action(action)
    except Exception as e:
        print('Something bad happened')
        print(f'{e!r}')
        return '', 200

    return '', 200


def handle_action(action):
    print(f"Action: {action}")

    if action["type"] == "view_submission":
        print('Run plan')

    return '', 200

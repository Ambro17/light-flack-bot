import os
from collections import namedtuple
from dataclasses import dataclass

from flask.blueprints import Blueprint
from flask import request
from slack.web.client import WebClient
import json
from typing import Optional

bp = Blueprint('interactive', __name__)

OviBot = WebClient(os.getenv('BOT_TOKEN'))

PlanConfig = namedtuple('PlanConfig', 'console sensor source post_install')

@dataclass
class PlanConfig:
    '''Class for keeping track of an item in inventory.'''
    console: str
    sensor: str
    source: str
    post_install: str
    branch_source: Optional[str]


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
    if action["type"] == "view_submission":
        print('Username: ', action['user']['username'])
        plan = read_params(action['view']['state']['values'])
        try:
            validate_config(plan)
        except ValueError as e:
            return {
                "response_action": "errors",
                "errors": {
                    "branch": f"{e!s}"
                }
            }
        print(plan)

    print(action)

    return '', 200


def validate_config(plan: PlanConfig) -> None:
    if plan.source == 'branch' and not plan.branch_source:
        raise ValueError('Missing required source branch to install from a branch')


def read_params(form_data) -> PlanConfig:
    console = form_data['console']['console_name']['value']
    sensor = form_data['sensor']['sensor_name']['value']
    branch = form_data['branch']['branch_action'].get('value')
    install_from = form_data['source']['source_action']['selected_option']['value']
    after_install_action = form_data['post_install']['post_install_action']['selected_option']['value']
    return PlanConfig(
        console=console, 
        sensor=sensor, 
        source=install_from, 
        post_install=after_install_action, 
        branch_source=branch
    )
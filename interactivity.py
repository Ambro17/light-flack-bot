import os
import json
from collections import namedtuple
from dataclasses import dataclass

from flask.blueprints import Blueprint
from flask import request
from slack.web.client import WebClient
from typing import Optional

from tasks import async_task, async_func

bp = Blueprint('interactive', __name__)

OviBot = WebClient(os.getenv('BOT_TOKEN'))


@dataclass
class PlanConfig:
    '''Class for keeping track of an item in inventory.'''
    console: str
    sensor: str
    install_source: str
    post_install: str
    branch_source: Optional[str]

    def to_dict(self):
        base = {
            'console': self.console,
            'sensors': self.sensor,
            'environment': self.install_source,
        }
        if self.branch_source:
            base['source'] = f'branch:{self.branch_source}'
        if self.post_install != 'nothing':
            if self.post_install == 'common-setup':
                base['run_common_setup'] = True
            elif self.post_install == 'regression-lite':
                base['deadpool_test_plan'] = 'regression_lite.json'
            elif self.post_install == 'regression-full':
                base['run_regression_testsuite'] = True


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
    response = '', 200
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
        # Fix this, it should return link but answer in less than 3 seconds
        response = run_installation_plan(plan.to_dict(), user_id=action['user']['id'])

    print(action)

    return response


def read_params(form_data) -> PlanConfig:
    console = form_data['console']['console_name']['value']
    sensor = form_data['sensor']['sensor_name']['value']
    branch = form_data['branch']['branch_action'].get('value')
    install_from = form_data['source']['source_action']['selected_option']['value']
    after_install_action = form_data['post_install']['post_install_action']['selected_option']['value']
    return PlanConfig(
        console=console, 
        sensor=sensor, 
        install_source=install_from, 
        post_install=after_install_action, 
        branch_source=branch
    )


def validate_config(plan: PlanConfig) -> None:
    if plan.source == 'branch' and not plan.branch_source:
        raise ValueError('Missing required source branch to install from a branch')


@async_func
def run_installation_plan(plan: dict, user_id, plan_id: str):
    # Notify user of success or failure with new message (respond)
    # interact with onattended
    # Get return value
    try:
        user = get_user(user_id)
        Bamboo = BambooHelper(BAMBOO_SERVER, user.bamboo_token)
        branch_id = Bamboo.get_branch_key(plan_id, user.username.replace('.', '_'))
        plan['ovi_token_secret'] = user.ovi_token
        build_key = Bamboo.run_plan(branch_id, plan)
        build_url = BUILD_URL.format(BAMBOO_SERVER, build_key)
        OviBot.chat_postMessage(channel=user, text=build_url)
    except Exception as e:
        print(repr(e))
        OviBot.chat_postMessage(channel=user, text='Something went wrong.. Try Again')

import time

import requests
from flask import Blueprint, request
from slack import WebClient

from tasks import async_task


main = Blueprint('main', __name__)
roomsbot = '1234'
OviBot = WebClient(roomsbot)


@main.route('/')
@async_task
def index():
    """Serve client-side application."""
    time.sleep(10)
    return 'Hello World'


@main.route('/rate2', methods=('GET', 'POST'))
@async_task
def rate_text():
    """Show slack modal"""
    # Api post to response_url
    data = {'text': 'hola'}
    print(request.form)
    respond(request.form['response_url'], data)
    return '', 200


@main.route('/rate', methods=('GET', 'POST'))
@async_task
def rate_modal():
    """Show slack modal"""
    rate_popup = {
      "type": "modal",
      "title": {
        "type": "plain_text",
        "text": "Onattended",
        "emoji": True
      },
      "submit": {
        "type": "plain_text",
        "text": "Run Plan",
        "emoji": True
      },
      "close": {
        "type": "plain_text",
        "text": "Cancel",
        "emoji": True
      },
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Hi <fakelink.toUser.com|@Ambro>!* How would you like your *RATE* recipe"
          }
        },
        {
          "type": "divider"
        },
        {
          "block_id": "source",
          "type": "input",
          "element": {
            "type": "static_select",
            "placeholder": {
              "type": "plain_text",
              "text": "Choose installation source",
              "emoji": True
            },
            "action_id": "source_action",
            "options": [
              {
                "text": {
                  "text": "Nightly",
                  "type": "plain_text"
                },
                "value": "nightly"
              },
              {
                "text": {
                  "text": "Staging",
                  "type": "plain_text"
                },
                "value": "staging"
              }
            ]
          },
          "label": {
            "type": "plain_text",
            "text": ":gear:  Install from",
            "emoji": True
          }
        },
        {
          "block_id": "post_install",
          "type": "input",
          "element": {
            "type": "static_select",
            "placeholder": {
              "type": "plain_text",
              "text": "What?",
              "emoji": True
            },
            "action_id": "post_install_action",
            "options": [
              {
                "text": {
                  "text": "Run Common Setup",
                  "type": "plain_text"
                },
                "value": "common-setup"
              },
              {
                "text": {
                  "text": "Do Nothing",
                  "type": "plain_text"
                },
                "value": "nothing"
              }
            ]
          },
          "label": {
            "type": "plain_text",
            "text": ":wrench:  After installation do",
            "emoji": True
          }
        },
        {
          "type": "divider"
        },
        {
          "type": "input",
          "block_id": "console",
          "element": {
            "type": "plain_text_input",
            "placeholder": {
              "type": "plain_text",
              "text": "Enter your appliance hostname"
            },
            "action_id": "console_name"
          },
          "label": {
            "type": "plain_text",
            "text": ":computer: Console",
            "emoji": True
          }
        },
        {
          "type": "input",
          "block_id": "sensor",
          "element": {
            "type": "plain_text_input",
            "placeholder": {
              "type": "plain_text",
              "text": "Enter your appliance hostname"
            },
            "action_id": "sensor_name"
          },
          "label": {
            "type": "plain_text",
            "text": ":desktop_computer: Sensor",
            "emoji": True
          }
        }
      ]
    }

    OviBot.views_open(
        trigger_id=request.form['trigger_id'],
        view=rate_popup
    )

    return '', 200


def respond(url, response, status=200):
    """Reply to a given response url"""
    sign(response)
    r = requests.post(url, json=response, timeout=10)
    if r.status_code != 200:
        print('Something went wrong')
    else:
        print('Response sent succesfully for task X.')


def sign(r):
    r.update({
        "attachments": [{
                "footer": "RateBot",
                "footer_icon": 'https://i.imgur.com/xTYLdOb.png',
                "ts": time.time()
            }
        ]
    })

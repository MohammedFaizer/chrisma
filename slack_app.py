import logging
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
load_dotenv()
import os
slack_token = os.getenv("SLACK_TOKEN")
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

logging.basicConfig(level=logging.INFO)

app = App(
    token=slack_token,
    signing_secret=slack_signing_secret,
    token_verification_enabled=False,
)


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Slack command listener
@app.command("/incognito")
def send_anonymous(ack, body, client):
    ack()
    channel_id=body.get("channel_id")
    trigger_id = body.get("trigger_id")
    if trigger_id and channel_id:
        try:
            # Open the modal using the views.open method
            client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": "ask_modal", 
                    "private_metadata": channel_id,  # Set a callback_id
                    "title": {
                        "type": "plain_text",
                        "text": "Chrisma-Chris",
                        "emoji": True
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Submit",
                        "emoji": True
                    },
                    "close": {
                        "type": "plain_text",
                        "text": "Cancel",
                        "emoji": True
                    },
                    "blocks": [
                        {
                            "type": "input",
                            "block_id": "TSK01",
                            "element": {
                                "type": "plain_text_input",
                                "multiline": True,
                                "action_id": "plain_text_input-action"
                            },
                            "label": {
                                "type": "plain_text",
                                "text": "Enter Your Message",
                                "emoji": True
                            }
                        }
                    ]
                }
            )
        except Exception as e:
            logging.error(f"Error opening modal: {e}")
    else:
        logging.error("Trigger ID not found in the request")

# Handle modal submission
@app.view("ask_modal")  # Listen for the specific callback_id "ask_modal"
def handle_modal_submission(ack, body, client):
    ack()  # Acknowledge the submission    
    print(body)
    private_metadata = body['view']['private_metadata']
    user_message = body['view']['state']['values']['TSK01']['plain_text_input-action']['value']
    print(user_message)
    client.chat_postMessage(
                channel=private_metadata, text=user_message
            )
    logging.info("Modal submission received")
   
   


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    flask_app.run(port=3000)

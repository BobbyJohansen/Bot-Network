import os

from flask import Flask, request
from slackclient import SlackClient
from multiprocessing import Queue
from multiprocessing import Lock

from BotManagerExecutor import BotManagerExecutor

# Environment config for authentication with slack
from configuration.config import env
from log.logger import Logger

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]

# Bot Manager communications
managerQ = Queue()
qlock = Lock()

app = Flask(__name__)
logger = Logger().gimme_logger("SlackAuthentication")

# Routes
@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)

@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    bot = {}

    # Retrieve the auth code from the request params
    auth_code = request.args['code']
    # Retrieve the state code passed back from the button originally to identify what button authed us
    bot['state'] = request.args['state']

    # An empty string is a valid token for this request
    sc = SlackClient("")

    # Request the auth tokens from Slack
    auth_response = sc.api_call(
            "oauth.access",
            client_id=client_id,
            client_secret=client_secret,
            code=auth_code
    )
    logger.info(auth_response)

    bot['user_access_token'] = auth_response['access_token']
    bot['bot_access_token'] = auth_response['bot']['bot_access_token']
    bot['team_name'] = auth_response['team_name']
    logger.info(bot['team_name'] + "  /  " + bot['user_access_token'] + "  /  " + bot['bot_access_token'])
    # Send to Bot Manager Executor
    with qlock:
        logger.info("Dispatching bot onto manager executor queue")
        managerQ.put(bot)

    # TODO: make this a redirect to a static success url on the website probably should be configurable
    return "Auth complete!"


def init():
    # load the manager executor on its own thread
    creation_endpoint = env.get('creation_endpoint', '/create')
    managers = env.get('managers', ['http://localhost:5001'])
    executor = BotManagerExecutor("", managerQ, qlock, managers, creation_endpoint)
    executor.init()
    executor.setDaemon(True)
    executor.start()

# pre application initialization code for prod
if not env.get("listener_debug"):
    logger.info("calling init for production")
    init()

# For local debugging to run this in production you will want to do the following:
# flask run --host=0.0.0.0:5002 TODO: make execution script in python that starts the application with the prod flask command
if __name__ == "__main__":
    init()
    port = env.get("listener_port", 5002)
    debug = env.get("listener_debug", False)
    logger.info("Starting SlackAuthentication on port:" + str(port))
    app.run("0.0.0.0", port, debug, use_reloader=False)

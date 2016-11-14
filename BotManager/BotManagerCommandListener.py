"""
This is the listener managing multiple bots. It is fairly stupid and only knows how to spin up bots
(and eventually shut them down). It is stupid so many of them can be spun up for horizontal scaling purposes
It can also be tuned for vertical scaling

Eventually this could just pick up on the database (RETHINK and listen to a live feed) when it hears a new account
being persisted it could just kick off create_bot()
"""
from flask import Flask, request, make_response
from multiprocessing import Queue
from multiprocessing import Lock

from BotManager import BotManager

# Bot Manager communications
from configuration.config import env
from log.logger import Logger

managerQ = Queue()
qlock = Lock()

listener = Flask(__name__)
logger = Logger().gimme_logger("BotManagerCommandListener")
creation_endpoint = env.get('creation_endpoint', '/create')


# Routes
@listener.route(creation_endpoint, methods=["POST"])
def create_bot():
    # Assume failure so that we can retry if something goes bad
    response = make_response('failed to create bot', 500)
    # Validate for security
    # TODO: create a secure token that should be sent if that toekn does not exist then it didnt come from me
    # TODO: username = request.cookies.get('username')

    try:
        logger.info("create endpoint hit attempting to read bot info")
        # Retrieve the auth code from the request params
        bot_info = request.args
        logger.info(bot_info)

        # send via queue to BotManagerExecutor
        with qlock:
            logger.info("Dispatching bot onto manager executor queue")
            managerQ.put(bot_info)

        # Success
        response = make_response('ok', 200)
    except Exception as e:
        logger.error("Something went wrong attempting to dispatch bot to manager")
        logger.error(e)

    return response

@listener.route("/resources", methods=["GET"])
def get_resources():
    # TODO: Get the total number of running bots, the total space for bots
    max_workers = env.get("pool_size", 5)
    return {'max_workers': max_workers, 'running':'idk'}

def init():
    # load the Bot Manager on its own thread
    logger.info("Initialization of command listener called")
    max_workers = env.get("pool_size", 5)
    manager = BotManager("", managerQ, qlock, max_workers)
    manager.init()
    manager.setDaemon(True)
    manager.start()


# pre application initialization code for prod
if not env.get("listener_debug"):
    logger.info("calling init for production")
    init()


# For local debugging to run this in production you will want to do the following:
# flask run --host=0.0.0.0:5001 TODO: make execution script in python that starts the application with the prod flask command
if __name__ == "__main__":
    init()
    # start the rest application
    port = env.get("listener_port", 5001)
    debug = env.get("listener_debug", False)
    logger.info("Starting BotManagerCommandListener on port:" + str(port))
    listener.run("0.0.0.0", port, debug, use_reloader=False)

from flask import Flask
import logging

logging.basicConfig(
    filename="bot.log",
    filemode="w",
    format="%(asctime)s : %(name)s : %(levelname)s : %(message)s"
)

logging.getLogger("exp").setLevel(logging.DEBUG)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.CRITICAL)
app = Flask(__name__)



@app.route("/api")
def home():
    LOGGER.debug("debug")
    LOGGER.info("/api is called")
    return {"/status":"gives status"}
if __name__ == "__main__":
    app.run(host='https://api.telegram.org/')

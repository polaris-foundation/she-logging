from flask import Flask, request

from she_logging import logger

app = Flask(__name__)


@app.route("/")
def read_root() -> dict:
    logger.info("Hello world")
    return {"Hello": "World"}


@app.route("/items/<item_id>")
def read_item(item_id: int) -> dict:
    q = request.args.get("q", "")
    logger.info(f"GET item {item_id} q={q}")
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)

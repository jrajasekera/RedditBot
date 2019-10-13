from flask import Flask, render_template, request
import logging
import tasks
import configparser

app = Flask(__name__)

# debug logging on for dev purposes
logging.basicConfig(level=logging.DEBUG)

# get groupMe bot application uri from config
config = configparser.ConfigParser()
config.read("config.ini")
groupMeAppUrI = config['GroupMe']['URI']

# test method
@app.route("/test")
def test():
    tasks.greet.delay()
    return "Done"

@app.route("/")
def home():
    return render_template("index.html")

# adds a response task to the queue and returns task id
@app.route("/getWebUI")
def get_bot_response_webUI():
    encodedMsg = request.args.get('msg')
    task = tasks.get_bot_response_webUI.delay(encodedMsg)
    return str(task.task_id)

# returns true if the specified task is complete, false if not
@app.route("/getTaskStatus")
def get_task_status():
    task_id = request.args.get('id')
    status = tasks.get_task_status(task_id)
    return str(status)

# returns the result of the specified task
@app.route("/getTaskResult")
def get_task_result():
    task_id = request.args.get('id')
    result = tasks.get_task_result(task_id)
    return result

# cancels specified task
@app.route("/cancelTask")
def cancel_task():
    task_id = request.args.get('id')
    tasks.cancel_task(task_id)
    return 'Task Cancelled'


# adds a response task to the queue and sends the response back to the groupMe bot application when finished
@app.route("/get")
def get_bot_response():
    encodedMsg = request.args.get('msg')
    tasks.get_bot_response.delay(encodedMsg, groupMeAppUrI)
    return ''

if __name__ == "__main__":
    app.run()

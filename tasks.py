import configparser
import celery
from celery.result import AsyncResult
from celery.task.control import revoke
from celery.exceptions import SoftTimeLimitExceeded
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.response_selection import get_random_response
from chatterbot.filters import get_recent_repeated_responses
from chatterbot.comparisons import SynsetDistance
from chatterbot.logic import BestMatch
import urllib.parse
import logging
import requests

# creates instance of chatbot
def createBot(dbName,dbURI):
    return ChatBot("Reddit Bot",
           		storage_adapter = "chatterbot.storage.MongoDatabaseAdapter",
           		database = dbName,
           		database_uri = dbURI,
           		preprocessors=[
                   		'chatterbot.preprocessors.clean_whitespace',
           			    'chatterbot.preprocessors.convert_to_ascii'
           		],
           		filters=[get_recent_repeated_responses],
           		logic_adapters=[
           			{
           			    'import_path': 'ClosestMatch_adapter.ClosestMatch',
                       	'statement_comparison_function': SynsetDistance,
                       	'response_selection_method': get_random_response,
           			    'maximum_similarity_threshold': 0.80
           			    #'excluded_words' : []
           			}
           		],
           		read_only=True,
           	)

#Trains Chatbot with files from data dir
def train(bot):
    trainer = ChatterBotCorpusTrainer(bot)

    #trainer.train(
    #    "chatterbot.corpus.english.conversations",
    #	"chatterbot.corpus.english.greetings",
    #	"chatterbot.corpus.english.health",
    #)

    files = [] # put filenames here

    for file in files:
        fileName = "./data/" + file
        trainer.train(fileName)



# logging turned on for dev purposes
logging.basicConfig(level=logging.DEBUG)

#read setting from config file
config = configparser.ConfigParser()
config.read("config.ini")
mongodbName = config['MongoDB']['Name']
mongodbURI = config['MongoDB']['URI']
redisURI = config['Redis']['URI']


#configure task queue
app = celery.Celery('TaskQueue')
app.conf.update(BROKER_URL=redisURI, CELERY_RESULT_BACKEND=redisURI)

# create bot
english_bot = createBot(mongodbName, mongodbURI)

#train bot
train(english_bot)

#function for testing
@app.task
def greet():
    return "Hello There"

#sends message to groupme bot application for integration with the app
def send_to_groupme(msg, groupMeAppUrI):
    groupmeUrl =  groupMeAppUrI + "/?msg=" + msg
    print("Sending msg = " + msg + " to " + groupMeAppUrI)
    requests.get(url = groupmeUrl)

# gets response for groupme messages
@app.task(time_limit=800)
def get_bot_response(msg, groupMeAppUrI):
    try:
        encodedMsg = msg
        userText = urllib.parse.unquote(encodedMsg)
        botResponse = str(english_bot.get_response(userText))
        encodedBotResponse = urllib.parse.quote(botResponse, safe='')
        send_to_groupme(encodedBotResponse, groupMeAppUrI)
        return True
    except SoftTimeLimitExceeded:
        print("Job has timed out for msg = " + urllib.parse.unquote(encodedMsg))
        return False

# returns bot response for web UI
@app.task(time_limit=800)
def get_bot_response_webUI(msg):
    try:
        encodedMsg = msg
        userText = urllib.parse.unquote(encodedMsg)
        botResponse = str(english_bot.get_response(userText))
        return botResponse
    except SoftTimeLimitExceeded:
        print("Job has timed out for msg = " + urllib.parse.unquote(encodedMsg))
        return "Error Has occurred"

# returns true if specified task is complete, else returns false
def get_task_status(task_id):
    result = AsyncResult(task_id)
    return result.ready()

# returns result of specified task
def get_task_result(task_id):
    result = AsyncResult(task_id)
    return result.get()

# cancels specified task
def cancel_task(task_id):
    revoke(task_id, terminate=True)

# reddit-chatterbot

## What is it?
An implementation of Chatterbot [ChatterBot](https://github.com/gunthercox/ChatterBot) library with a web UI as well as GroupMe integration

Built using [flask-chatterbot](https://github.com/chamkank/flask-chatterbot) as a Chatterbot flask template.

As the data corpus grows for an instance of chatterbot, the performance drops drastically in terms of response time. 
This implementations utilizes [Celery](http://www.celeryproject.org/) as a task queue that allows the bot the handle multiple requests on a larger data corpus. Polling is then used to update the browser page when the bot is done processing the message.  

The bot is trained on comment threads from 30 popular subreddits.
I scraped the top 1000 posts from each of the subreddits below to create the corpus (~400MB).
* PoliticalHumor
* memes
* funny
* books
* BeAmazed
* movies
* pics
* offmychest
* self
* 2meirl4meirl
* changemyview
* meirl
* AskWomen
* RoastMe
* AskMen
* Showerthoughts
* nba
* technology
* philosophy
* history
* midlyinteresting
* worldnews
* todayilearned
* science
* explainlikeimfive
* me_irl
* Music
* sports
* news
* politics

## Application Stack
* Heroku instance with one web dyno and one worker dyno to run web application
* MongoDB instance to store corpus
* Redis instance to use as message broker and task result storage
* GroupMe bot application if you want to integrate with GroupMe

App URIs and credentials can be specified in config.ini

## Try it
The live app below uses hobby dynos, so performance will be slow; it may take 1-15 minutes to get a response from the bot.
Some messages may take more that 15 minutes to process and the bot will tell you to try another message.
### You can play with the application here: [RedditBot](https://trip-troop-chatbot-api-heroku.herokuapp.com/)

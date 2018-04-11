from newsapi import NewsApiClient
import os
import requests
import sendgrid
from sendgrid.helpers.mail import *
import datetime



api = NewsApiClient(api_key=os.environ['API_KEY'])

sourcesDict = {'ABC News': {'id': 'abc-news', 'url': 'http://abcnews.go.com'}, 'Al Jazeera English': {'id': 'al-jazeera-english', 'url': 'http://www.aljazeera.com'}, 'Ars Technica': {'id': 'ars-technica', 'url': 'http://arstechnica.com'}, 'Associated Press': {'id': 'associated-press', 'url': 'https://apnews.com/'}, 'Axios': {'id': 'axios', 'url': 'https://www.axios.com'}, 'Bleacher Report': {'id': 'bleacher-report', 'url': 'http://www.bleacherreport.com'}, 'Bloomberg': {'id': 'bloomberg', 'url': 'http://www.bloomberg.com'}, 'Breitbart News': {'id': 'breitbart-news', 'url': 'http://www.breitbart.com'}, 'Business Insider': {'id': 'business-insider', 'url': 'http://www.businessinsider.com'}, 'Buzzfeed': {'id': 'buzzfeed', 'url': 'https://www.buzzfeed.com'}, 'CBS News': {'id': 'cbs-news', 'url': 'http://www.cbsnews.com'}, 'CNBC': {'id': 'cnbc', 'url': 'http://www.cnbc.com'}, 'CNN': {'id': 'cnn', 'url': 'http://us.cnn.com'}, 'CNN Spanish': {'id': 'cnn-es', 'url': 'http://cnnespanol.cnn.com/'}, 'Crypto Coins News': {'id': 'crypto-coins-news', 'url': 'https://www.ccn.com'}, 'Engadget': {'id': 'engadget', 'url': 'https://www.engadget.com'}, 'Entertainment Weekly': {'id': 'entertainment-weekly', 'url': 'http://www.ew.com'}, 'ESPN': {'id': 'espn', 'url': 'http://espn.go.com'}, 'ESPN Cric Info': {'id': 'espn-cric-info', 'url': 'http://www.espncricinfo.com/'}, 'Fortune': {'id': 'fortune', 'url': 'http://fortune.com'}, 'Fox News': {'id': 'fox-news', 'url': 'http://www.foxnews.com'}, 'Fox Sports': {'id': 'fox-sports', 'url': 'http://www.foxsports.com'}, 'Google News': {'id': 'google-news', 'url': 'https://news.google.com'}, 'Hacker News': {'id': 'hacker-news', 'url': 'https://news.ycombinator.com'}, 'IGN': {'id': 'ign', 'url': 'http://www.ign.com'}, 'Mashable': {'id': 'mashable', 'url': 'http://mashable.com'}, 'Medical News Today': {'id': 'medical-news-today', 'url': 'http://www.medicalnewstoday.com'}, 'MSNBC': {'id': 'msnbc', 'url': 'http://www.msnbc.com'}, 'MTV News': {'id': 'mtv-news', 'url': 'http://www.mtv.com/news'}, 'National Geographic': {'id': 'national-geographic', 'url': 'http://news.nationalgeographic.com'}, 'NBC News': {'id': 'nbc-news', 'url': 'http://www.nbcnews.com'}, 'New Scientist': {'id': 'new-scientist', 'url': 'https://www.newscientist.com/section/news'}, 'Newsweek': {'id': 'newsweek', 'url': 'http://www.newsweek.com'}, 'New York Magazine': {'id': 'new-york-magazine', 'url': 'http://nymag.com'}, 'Next Big Future': {'id': 'next-big-future', 'url': 'https://www.nextbigfuture.com'}, 'NFL News': {'id': 'nfl-news', 'url': 'http://www.nfl.com/news'}, 'NHL News': {'id': 'nhl-news', 'url': 'https://www.nhl.com/news'}, 'Politico': {'id': 'politico', 'url': 'https://www.politico.com'}, 'Polygon': {'id': 'polygon', 'url': 'http://www.polygon.com'}, 'Recode': {'id': 'recode', 'url': 'http://www.recode.net'}, 'Reddit /r/all': {'id': 'reddit-r-all', 'url': 'https://www.reddit.com/r/all'}, 'Reuters': {'id': 'reuters', 'url': 'http://www.reuters.com'}, 'TechCrunch': {'id': 'techcrunch', 'url': 'https://techcrunch.com'}, 'TechRadar': {'id': 'techradar', 'url': 'http://www.techradar.com'}, 'The Hill': {'id': 'the-hill', 'url': 'http://thehill.com'}, 'The Huffington Post': {'id': 'the-huffington-post', 'url': 'http://www.huffingtonpost.com'}, 'The New York Times': {'id': 'the-new-york-times', 'url': 'http://www.nytimes.com'}, 'The Next Web': {'id': 'the-next-web', 'url': 'http://thenextweb.com'}, 'The Verge': {'id': 'the-verge', 'url': 'http://www.theverge.com'}, 'The Wall Street Journal': {'id': 'the-wall-street-journal', 'url': 'http://www.wsj.com'}, 'The Washington Post': {'id': 'the-washington-post', 'url': 'https://www.washingtonpost.com'}, 'Time': {'id': 'time', 'url': 'http://time.com'}, 'USA Today': {'id': 'usa-today', 'url': 'http://www.usatoday.com/news'}, 'Vice News': {'id': 'vice-news', 'url': 'https://news.vice.com'}, 'Wired': {'id': 'wired', 'url': 'https://www.wired.com'}}

MAX_QUESTION = 10

#This is the welcome message for when a user starts the skill without a specific intent.
WELCOME_MESSAGE = ("Welcome to the Real News!  You can ask me for news from various sources"
                   " such as CNN or The Washington Post by saying, 'give me the headlines from the washington post'."
                   "You can also ask me for the headlines across sources by saying, 'give me the headlines'."
                   "You can get a list of sources by saying, 'give me the list of sources'"
                   "  What would you like to do?")

HTML_MSG_1 = '<!doctype html> <html> <head> <meta name="viewport" content="width=device-width"> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> <title>Simple Transactional Email</title> <style> /* ------------------------------------- INLINED WITH htmlemail.io/inline ------------------------------------- */ /* ------------------------------------- RESPONSIVE AND MOBILE FRIENDLY STYLES ------------------------------------- */ @media only screen and (max-width: 620px) { table[class=body] h1 { font-size: 28px !important; margin-bottom: 10px !important; } table[class=body] p, table[class=body] ul, table[class=body] ol, table[class=body] td, table[class=body] span, table[class=body] a { font-size: 16px !important; } table[class=body] .wrapper, table[class=body] .article { padding: 10px !important; } table[class=body] .content { padding: 0 !important; } table[class=body] .container { padding: 0 !important; width: 100% !important; } table[class=body] .main { border-left-width: 0 !important; border-radius: 0 !important; border-right-width: 0 !important; } table[class=body] .btn table { width: 100% !important; } table[class=body] .btn a { width: 100% !important; } table[class=body] .img-responsive { height: auto !important; max-width: 100% !important; width: auto !important; } } /* ------------------------------------- PRESERVE THESE STYLES IN THE HEAD ------------------------------------- */ @media all { .ExternalClass { width: 100%; } .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; } .apple-link a { color: inherit !important; font-family: inherit !important; font-size: inherit !important; font-weight: inherit !important; line-height: inherit !important; text-decoration: none !important; } .btn-primary table td:hover { background-color: #34495e !important; } .btn-primary a:hover { background-color: #34495e !important; border-color: #34495e !important; } } </style> </head> <body class="" style="background-color: #f6f6f6; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;"> <table border="0" cellpadding="0" cellspacing="0" class="body" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background-color: #f6f6f6;"> <tr> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td> <td class="container" style="font-family: sans-serif; font-size: 14px; vertical-align: top; display: block; Margin: 0 auto; max-width: 580px; padding: 10px; width: 580px;"> <div class="content" style="box-sizing: border-box; display: block; Margin: 0 auto; max-width: 580px; padding: 10px;"> <!-- START CENTERED WHITE CONTAINER --> <span class="preheader" style="color: transparent; display: none; height: 0; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; visibility: hidden; width: 0;">Here is your requested news briefing from the Real News skill.</span> <table class="main" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background: #ffffff; border-radius: 3px;"> <!-- START MAIN CONTENT AREA --> <tr> <td class="wrapper" style="font-family: sans-serif; font-size: 14px; vertical-align: top; box-sizing: border-box; padding: 20px;"> <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;"> <tr> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;"> '
HTML_MSG_2 = '</td> </tr> </table> </td> </tr> <!-- END MAIN CONTENT AREA --> </table> <!-- START FOOTER --> <div class="footer" style="clear: both; Margin-top: 10px; text-align: center; width: 100%;"> <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;"> <tr> <td class="content-block" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;"> <span class="apple-link" style="color: #999999; font-size: 12px; text-align: center;">Real News</span> <br> Don\'t like these emails? <a href="https://realnewsapp.github.io/unlink.html" style="text-decoration: underline; color: #999999; font-size: 12px; text-align: center;">Unlink your Amazon account</a>. </td> </tr> <tr> <td class="content-block powered-by" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;"> Powered by <a href="https://newsapi.org" style="color: #999999; font-size: 12px; text-align: center; text-decoration: none;">NewsAPI.org</a>. </td> </tr> </table> </div> <!-- END FOOTER --> <!-- END CENTERED WHITE CONTAINER --> </div> </td> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td> </tr> </table> </body> </html>'



#This is the message a user will hear when they start a quiz.
SKILLTITLE = "Real News"

#This is the message a user will hear when they try to cancel or stop the skill"
#or when they finish a quiz.
EXIT_SKILL_MESSAGE = "Thank you for using Real News! Goodbye!"

#This is the message a user will hear after they ask (and hear) about a specific data element.
# REPROMPT_SPEECH = "Which other source would you like to hear news from?"
REPROMPT_HEADLINE = "Would you like to hear more about this?"
NEXT_HEADLINE = "Would you like to hear the next headline?"
EMAIL_HEADLINE = "Would you like me to email you a link to this article?"
NO_DESCRIPTION = "This article does not have a summary. Would you still like me to email you a link to this article?"

#This is the message a user will hear when they ask Alexa for help in your skill.
HELP_MESSAGE = ("You can say something like, \"Alexa, ask Real to give me the headlines\" to get the headlines. "
                "You can also ask for news from a source by saying, \""
                "Alexa, ask Real News to give me the news from source\". "
                "What would you like to do?")

LOGIN_MESSAGE = "You need to login with Amazon before we can send you an email. Check the Alexa app for more details."

#If you don't want to use cards in your skill, set the USE_CARDS_FLAG to false.
#If you set it to true, you will need an image for each item in your data.
USE_CARDS_FLAG = False

STATE_START = "Start"

STATE = STATE_START


# --------------- entry point -----------------

def lambda_handler(event, context):
    """ App entry point  """
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch()
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'])


# --------------- response handlers -----------------

def on_intent(request, session):
    """ Called on receipt of an Intent  """

    intent = request['intent']
    intent_name = request['intent']['name']

    print("on_intent " + intent_name)
    # get_state(session)

    if 'dialogState' in request:
        #delegate to Alexa until dialog sequence is complete
        if request['dialogState'] == "STARTED" or request['dialogState'] == "IN_PROGRESS":
            return dialog_response("", False)

    # process the intents
    if intent_name == "ListSources":
        return listSources(request)
    elif intent_name == "SourcedNews":
        return sourcedNews(request, intent, session)
    elif intent_name == "Headlines":
        return headlines(session)
    elif intent_name == "Next":
        return skip(session)
    elif intent_name == "Previous":
        return previous(session)
    elif intent_name == "AMAZON.YesIntent":
        if 'headline_index' in session['attributes']:
            if 'dialogStatus' in session['attributes']:
                if session['attributes']['dialogStatus'] == 'readTitle':
                    return read_headline(session)
                elif session['attributes']['dialogStatus'] == 'readDescription':
                    return ask_next_headline(session)
                elif session['attributes']['dialogStatus'] == 'readEmail':
                    session['attributes']['headline_index'] += 1
                    return headlines(session)
            return headlines(session)


    elif intent_name == "AMAZON.NoIntent":
        if 'dialogStatus' in session['attributes']:
            status = session['attributes']['dialogStatus']

            print(session)

            if status == "readEmail":
                return do_stop(session)
            elif status == "readTitle":
                if 'headline_index' in session['attributes']:
                    session['attributes']['headline_index'] += 1
                
                return headlines(session)
            elif status == "readDescription":
                if 'headline_index' in session['attributes']:
                    session['attributes']['headline_index'] += 1
                
                return headlines(session)
                
        else:
            print("headline_index didn't exist")
            # elif session['attributes']['dialogStatus'] == 'email':
            #     return response_plain_text("Would you like me to email you a link to the article?", True)
        return headlines(session)

    elif intent_name == "AMAZON.HelpIntent":
        return do_help()
    elif intent_name == "AMAZON.StopIntent":
        return do_stop(session)
    elif intent_name == "AMAZON.CancelIntent":
        return do_stop(session)
    else:
        print("invalid intent reply with help")
        return do_help()


def listSources(request):
    """ Get the names of all the sources from the dictionary"""
    sourceNames = sourcesDict.keys()

    msg = "Here are the sources: "

    i = 1
    for source in sourceNames:
        if i == 1:
            msg += source
        msg += ", " + source
        i += 1

    msg += "."

    print(msg)

    return response({}, response_plain_text(msg, True))

def skip(session):
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    session['attributes']['headline_index'] += 1
    return headlines(session)

def previous(session):
    print(session)
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    if 'headline_index' in session['attributes']:
        if session['attributes']['headline_index'] != 0:
            session['attributes']['headline_index'] -= 1
    else:
        session['attributes']['headline_index'] = 0

    return headlines(session)


def headlines(session):
    if 'attributes' not in session:
        res = api.get_top_headlines()
        
        articles = res['articles']
        session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
    elif 'articles' not in session['attributes']:
        print("before api request\n")
        res = api.get_top_headlines()
        
        print("after api request\n")
        
        articles = res['articles']
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    print(articles)
    print("\n")

    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    print(msg + "\n\n")

    print(articles[0])
    print("\n")

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        'articlesToEmail': articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def ask_next_headline(session):
    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

        print(articlesToEmail)


    articlesToEmail.append(session['attributes']['headline_index'])

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readEmail",
        "articlesToEmail": articlesToEmail
    }

    if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
        return do_stop()

    alexaMsg = "Okay. Would you like to hear the next headline?"

    return response(attributes, response_plain_text(alexaMsg, False))

def read_headline(session):
    if 'articles' not in session['attributes']:

        res = api.get_top_headlines()
        articles = res['articles']
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    
    if article['description'] is not None:
        msg += article['description']
        msg += " "
        # msg += NEXT_HEADLINE
        msg += EMAIL_HEADLINE
    else:
        msg += NO_DESCRIPTION

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']
    else:
        articlesToEmail.append(session['attributes']['headline_index'])

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readDescription",
        "articlesToEmail": articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def sourcedNews(request, intent, session):

    if 'attributes' not in session or 'articles' not in session['attributes']:

        requestedSource = intent['slots']['source']['value']

        """ Split up and format the requested source """
        formattedSource = ""
        words = requestedSource.split()

        for i in range(len(words)):
            if i == len(words) - 1:
                formattedSource += words[i].lower()
            else:
                formattedSource += words[i].lower() + "-"

        print("formattedSource: " + formattedSource)

        found = False

        for source in sourcesDict.values():
            if source['id'] == formattedSource:
                found = True
                break

        if found == False:
            return response({}, response_plain_text("Sorry. I couldn't find that source.", True))

        res = api.get_top_headlines(sources=formattedSource)
        print(res)
        articles = res['articles']

        session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    print(articles)
    print("\n")

    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    print(msg + "\n\n")

    print(articles[0])
    print("\n")

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        "articlesToEmail": articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def do_stop(session):
    """  stop the app """

    """ check if there are any articles to be emailed """

    print('session in do_stop: ')
    print(session)

    user_email = ""

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

        # Exit w/o email if there's nothing to email
        if not articlesToEmail:
            attributes = {"state":globals()['STATE']}
            return response(attributes, response_plain_text(EXIT_SKILL_MESSAGE, True))

        if 'accessToken' not in session['user']:
            attributes = {"state":globals()['STATE']}
            return response(attributes, response_card_login('Real News - Email Setup', LOGIN_MESSAGE, True))
        else:
            request_data = requests.get("https://api.amazon.com/user/profile?access_token=" + session['user']['accessToken'])
            request_json = request_data.json()
            user_email = request_json['email']

        msg = HTML_MSG_1

        articles = session['attributes']['articles']

        msg += "<div align='center'>"
        msg += "<a href='#' style='text-decoration: none; color: #000000;'>"
        msg += "<h1>Real News</h1><hr />"
        msg += "</a>"
        msg += "</div>"

        for i in range(len(articles)):
            if i in articlesToEmail:

                msg += "<div>"
                msg += "<a href=\"" + articles[i]['url'] + "\">"
                msg += "<h2>" + articles[i]['title'] + "</h2>"
                msg += "</a>"
                msg += "<p>"
                if  articles[i]['description'] is not None:
                    msg += articles[i]['description']
                msg += "</p><br />"
                if articles[i]['source']['name'] in sourcesDict:
                    msg += "<a href=\"" + sourcesDict[articles[i]['source']['name']]['url'] + "\">"
                    msg += articles[i]['source']['name']
                    msg += "</a>"
                else:
                    msg += articles[i]['source']['name']
                msg += "</div>"

                if i != len(articles) - 1:
                    msg += "<hr />"
                
                # msg += "<tr>"

                # msg += "<td>"
                # msg += "<a href=\"" + articles[i]['url'] + "\">"
                # msg += "<img height=\"200\" width=\"200\" src=\"" + articles[i]['urlToImage'] + "\" "
                # msg += "</a>"
                # msg += "</td>"

                # msg += "<td>"
                # msg += "<p>"
                # msg += "<a href=\"" + articles[i]['url'] + "\">"
                # msg += "<h2>" + articles[i]['title'] + "</h2> <br />"
                # msg += "</a>"
                # msg += articles[i]['description'] + "<br /><br />"
                # msg += articles[i]['source']['name'] + "<br />"
                # msg += "</p>"
                # msg += "</td>"

                # msg += "<tr>"


        # msg += "</table></body>"
        # msg += "</html>"

        msg += HTML_MSG_2

        # need to get the user's email to send the mail

        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('EMAIL_SENDER_ADDRESS'))
        to_email = Email(user_email)
        now = datetime.datetime.now()

        subject = "Your Flash Briefing for " + str(now.month) + "/" + str(now.day)
        content = Content("text/html", msg)
        mail = Mail(from_email, subject, to_email, content)
        sendGrid = sg.client.mail.send.post(request_body=mail.get())
        print(sendGrid.status_code)
        print(sendGrid.body)
        print(sendGrid.headers)


    # if 'articlesToEmail' in session['attributes']:
    #     articles = session['attributes']['articles']
    #     for article in articlesToEmail:
    #         print(article)

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(EXIT_SKILL_MESSAGE, True))

def do_help():
    """ return a help response  """

    global STATE
    STATE = STATE_START
    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(HELP_MESSAGE, False))

def on_launch():
    """ called on Launch reply with a welcome message """
 
    return get_welcome_message()

def on_session_ended(request):
    """ called on session end  """
    
    print(request)

    if request['reason']:
        end_reason = request['reason']
        print("on_session_ended reason: " + end_reason)
    else:
        print("on_session_ended")

def get_state(session):
    """ get and set the current state  """

    global STATE
    print(session)
    if 'state' in session['attributes']:
        STATE = session['attributes']['state']
    else:
        STATE = STATE_START

# --------------- response string formatters -----------------
def get_welcome_message():
    """ return a welcome message """

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(WELCOME_MESSAGE, False))

def response_plain_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }


def response_ssml_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_and_prompt(output, endsession, reprompt_text):
    """ create a Ssml response with prompt  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def response_card_login(title, output, endsession):
    """ create a simple json plain text response  """

    return {
        'card': {
            'type': 'LinkAccount',
            'title': title,
            'text': output
        },
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'shouldEndSession': endsession
    }

def response_ssml_cardimage_prompt(title, output, endsession, cardtext, abbreviation, reprompt):
    """ create a simple json plain text response  """

    smallimage = get_smallimage(abbreviation)
    largeimage = get_largeimage(abbreviation)
    return {
        'card': {
            'type': 'Standard',
            'title': title,
            'text': cardtext,
            'image':{
                'smallimageurl':smallimage,
                'largeimageurl':largeimage
            },
        },
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_reprompt(output, endsession, reprompt_text):
    """  create a simple json response with a card  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def dialog_response(attributes, endsession):
    """  create a simple json response with card """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response':{
            'directives': [
                {
                    'type': 'Dialog.Delegate'
                }
            ],
            'shouldEndSession': endsession
        }
    }

def response(attributes, speech_response):
    """ create a simple json response """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speech_response
    }
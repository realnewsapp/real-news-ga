from newsapi import NewsApiClient
import os
import requests
import sendgrid
from sendgrid.helpers.mail import *
from constants import *


api = NewsApiClient(api_key=os.environ['API_KEY'])

# --------------- entry point -----------------

def lambda_handler(event, context):
    """ App entry point  """

    if 'action' in event['queryResult']:
        if event['queryResult']['action'] == "input.welcome":
            return on_launch()
        else:
            return on_intent(event)
    else:
        return on_intent(event)

"""     elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request']) """


# --------------- response handlers -----------------

def on_intent(request):
    """ Called on receipt of an Intent  """

    intent = request['queryResult']['intent']
    intent_name = intent['displayName']

    if "outputContexts" not in request:
        request["outputContexts"] = []

    # process the intents
    if intent_name == "ListSources":
        return listSources(request)
    elif intent_name == "SourcedNews":
        return sourcedNews(request)
    elif intent_name == "Headlines":
        headline_index = 0
        for i in request['queryResult']['outputContexts']:
            if 'parameters' in i:
                if 'headline_index' in i['name'] and 'index' in i['parameters']:
                    headline_index = i['parameters']['index']
        return headlines(request, headline_index)
    elif intent_name == "Next":
        return skip(request)
    elif intent_name == "Previous":
        return previous(request)
    elif intent_name == "AMAZON.YesIntent":
        dialogStatus = None
        for i in request['queryResult']['outputContexts']:
            if 'parameters' in i:
                if 'dialogstatus' in i['name'] and 'status' in i['parameters']:
                    dialogStatus = i['parameters']['status']

        for i in request['queryResult']['outputContexts']:
            if 'parameters' in i:
                if 'headline_index' in i['name'] and 'index' in i['parameters']:
                    if dialogStatus is not None:
                        if dialogStatus == 'readTitle':
                            return read_headline(request)
                        elif dialogStatus == 'readDescription':
                            return ask_next_headline(request)
                        elif dialogStatus == 'readEmail':
                            headline_index = i['parameters']['index']
                            headline_index += 1
                            return headlines(request, headline_index)
                    return headlines(request, 0)
    elif intent_name == "AMAZON.NoIntent" or intent_name == "No":
        headline_index = -1
        dialogStatus = None
        for i in request['queryResult']['outputContexts']:
            if 'parameters' in i:
                if 'headline_index' in i['name'] and 'index' in i['parameters']:
                    headline_index = i['parameters']['index']
                if 'dialogstatus' in i['name'] and 'status' in i['parameters']:
                    dialogStatus = i['parameters']['status']

        if dialogStatus is not None:
            if dialogStatus == "readEmail":
                return do_stop(request)
            elif dialogStatus == "readTitle" or dialogStatus == "readDescription":
                if headline_index != -1:
                    headline_index += 1
                else:
                    headline_index = 0
                
                return headlines(request, headline_index)        
        else:
            print("headline_index didn't exist")

        return headlines(request, headline_index)

    elif intent_name == "AMAZON.HelpIntent":
        return do_help()
    elif intent_name == "AMAZON.StopIntent" or intent_name == "Stop":
        return do_stop(request)
    elif intent_name == "AMAZON.CancelIntent":
        return do_stop(request)
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
            i += 1
            continue
        msg += ", " + source
        i += 1

    msg += "."

    return response_plain_text_ga(msg, True)

def skip(session):
    headline_index = 0
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'headline_index' in i['name']:
                headline_index = i['parameters']['index']

    headline_index += 1
    return headlines(session, headline_index)

def previous(session):
    headline_index = 0
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'headline_index' in i['name']:
                headline_index = i['parameters']['index']
    
    headline_index -= 1
    return headlines(session, headline_index)


def headlines(session, headline_index):
    articlesToEmail = None
    articles = None
    source = None
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'articles' in i['name'] and 'articles' in i['parameters']:
                articles = i['parameters']['articles']
            elif 'toemail' in i['name'] and 'articles' in i['parameters']:
                articlesToEmail = i['parameters']['articles']
            elif 'lastsource' in i['name'] and 'name' in i['parameters']:
                source = i['parameters']['name']

    if articles is None:
        res = api.get_top_headlines()

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))
        
        articles = res['articles']
    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if headline_index >= len(articles):
            return do_stop(session)

    msg = ""
    headline_index = int(headline_index)
    article = articles[headline_index]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        

    if articlesToEmail is None:
        articlesToEmail = []

    # if 'articlesToEmail' in session['attributes']:
    #     articlesToEmail = session['attributes']['articlesToEmail']

    for i in session['queryResult']['outputContexts']:
        if 'headline_index' in i['name']:
            i['parameters'] = {}
            i['parameters']['index'] = headline_index
        elif 'articles' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articles
        elif 'toemail' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articlesToEmail
        elif 'lastsource' in i['name']:
            i['parameters'] = {}
            i['parameters']['name'] = 'none'
        elif 'dialogstatus' in i['name']:
            i['parameters'] = {}
            i['parameters']['status'] = 'readTitle'

    # attributes = [
    #     # "state": globals()['STATE'], 
    #     {
    #         'name': 'articles',
    #         'lifespanCount': 10,
    #         'parameters': {
    #             'articles': articles
    #         }
    #     },
    #     {
    #         'name': 'headline_index',
    #         'lifespanCount': 10,
    #         'parameters': {
    #             'index': headline_index
    #         }
    #     },
    #     {
    #         'name': 'stacktrace',
    #         'lifespanCount': 10,
    #         'parameters': {
    #             'none': 'none'
    #         }
    #     }
    #     # "headline_index": session['queryResult']['outputContexts'][0]['headline_index'],
    #     # "articles": "session['queryResult']['outputContexts'][0]['articles']"
    #     # "dialogStatus": "readTitle",
    #     # 'articlesToEmail': articlesToEmail
    # ]

    return response_plain_context_ga(msg, session['queryResult']['outputContexts'], True)

def ask_next_headline(session):
    headline_index = 0
    articlesToEmail = None
    articles = None
    source = None
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'headline_index' in i['name'] and 'index' in i['parameters']:
                headline_index = i['parameters']['index']
            elif 'articles' in i['name'] and 'articles' in i['parameters']:
                articles = i['parameters']['articles']
            elif 'toemail' in i['name'] and 'articles' in i['parameters']:
                articlesToEmail = i['parameters']['articles']
            elif 'lastsource' in i['name'] and 'name' in i['parameters']:
                source = i['parameters']['name']

    if articlesToEmail is None:
        articlesToEmail = []

    headline_index = int(headline_index)
    articlesToEmail.append(articles[headline_index])

    for i in session['queryResult']['outputContexts']:
        if 'headline_index' in i['name']:
            i['parameters'] = {}
            i['parameters']['index'] = headline_index
        elif 'articles' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articles
        elif 'toemail' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articlesToEmail
        elif 'lastsource' in i['name']:
            i['parameters'] = {}
            i['parameters']['name'] = 'none'
        elif 'dialogstatus' in i['name']:
            i['parameters'] = {}
            i['parameters']['status'] = 'readEmail'

    # attributes = {
    #     "state" : globals()['STATE'], 
    #     "headline_index" : session['attributes']['headline_index'],
    #     "articles" : session['queryResult']['outputContexts'][0]['articles'],
    #     # "dialogStatus": "readEmail",
    #     # "articlesToEmail": articlesToEmail
    # }

    # if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
    #     return do_stop()

    msg = "Okay. Would you like to hear the next headline?"

    return response_plain_context_ga(msg, session['queryResult']['outputContexts'], True)

def read_headline(session):
    headline_index = 0
    articlesToEmail = None
    articles = None
    source = None
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'headline_index' in i['name'] and 'index' in i['parameters']:
                headline_index = i['parameters']['index']
            elif 'articles' in i['name'] and 'articles' in i['parameters']:
                articles = i['parameters']['articles']
            elif 'toemail' in i['name'] and 'articles' in i['parameters']:
                articlesToEmail = i['parameters']['articles']
            elif 'lastsource' in i['name'] and 'name' in i['parameters']:
                source = i['parameters']['name']

    if articles is None:
        res = api.get_top_headlines()

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))

        articles = res['articles']

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if headline_index == len(articles):
            return do_stop(session)
    
    msg = ""
    headline_index = int(headline_index)
    article = articles[headline_index]

    # for article in articles:
    
    if article['description'] is not None:
        msg += article['description']
        msg += " "
        # msg += NEXT_HEADLINE
        msg += EMAIL_HEADLINE
    else:
        msg += NO_DESCRIPTION

    if articlesToEmail is None:
        articlesToEmail.append(articles[headline_index])

    # if 'articlesToEmail' in session['attributes']:
    #     articlesToEmail = session['attributes']['articlesToEmail']
    # else:
    #     articlesToEmail.append(session['attributes']['headline_index'])

    for i in session['queryResult']['outputContexts']:
        if 'headline_index' in i['name']:
            i['parameters'] = {}
            i['parameters']['index'] = headline_index
        elif 'articles' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articles
        elif 'toemail' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articlesToEmail
        elif 'lastsource' in i['name']:
            i['parameters'] = {}
            i['parameters']['name'] = 'none'
        elif 'dialogstatus' in i['name']:
            i['parameters'] = {}
            i['parameters']['status'] = 'readDescription'

    # attributes = {
    #     "state" : globals()['STATE'], 
    #     "headline_index" : session['attributes']['headline_index'],
    #     "articles" : session['attributes']['articles'],
    #     "dialogStatus": "readDescription",
    #     "articlesToEmail": articlesToEmail
    # }

    return response_plain_context_ga(msg, session['queryResult']['outputContexts'], True)

def sourcedNews(session):
    headline_index = 0
    source = None
    articlesToEmail = None
    articles = None
    for i in session['queryResult']['outputContexts']:
        if 'parameters' in i:
            if 'headline_index' in i['name'] and 'index' in i['parameters']:
                headline_index = i['parameters']['index']
            elif 'articles' in i['name'] and 'articles' in i['parameters']:
                articles = i['parameters']['articles']
            elif 'toemail' in i['name'] and 'articles' in i['parameters']:
                articlesToEmail = i['parameters']['articles']
            elif 'lastsource' in i['name'] and 'name' in i['parameters']:
                source = i['parameters']['name']

    requestedSource = session['queryResult']['parameters']['source']

    """ Split up and format the requested source """
    formattedSource = ""
    words = requestedSource.split()

    for i in range(len(words)):
        if i == len(words) - 1:
            formattedSource += words[i].lower()
        else:
            formattedSource += words[i].lower() + "-"

    if articles is None or source != formattedSource:
        found = False

        for source in sourcesDict.values():
            if source['id'] == formattedSource:
                found = True
                break

        if found == False:
            return response_plain_text_ga("Sorry. I couldn't find that source.", True)

        res = api.get_top_headlines(sources=formattedSource)


        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))


        articles = res['articles']
        source = formattedSource
        headline_index = 0

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if headline_index == len(articles):
            return do_stop(session)
        
        headline_index += 1
        headline_index = int(headline_index)
    
    msg = ""
    article = articles[headline_index]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    if articlesToEmail is None:
        articlesToEmail = []

    for i in session['queryResult']['outputContexts']:
        if 'headline_index' in i['name']:
            i['parameters'] = {}
            i['parameters']['index'] = headline_index
        elif 'articles' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articles
        elif 'toemail' in i['name']:
            i['parameters'] = {}
            i['parameters']['articles'] = articlesToEmail
        elif 'lastsource' in i['name']:
            i['parameters'] = {}
            i['parameters']['name'] = source
        elif 'dialogstatus' in i['name']:
            i['parameters'] = {}
            i['parameters']['status'] = 'readTitle'

    # attributes = {
    #     "state": globals()['STATE'], 
    #     "headline_index": session['attributes']['headline_index'],
    #     "articles": session['attributes']['articles'],
    #     "dialogStatus": "readTitle",
    #     "articlesToEmail": articlesToEmail
    # }

    return response_plain_context_ga(msg, session['queryResult']['outputContexts'], True)

def do_stop(session):
    """  stop the app """

    """ check if there are any articles to be emailed """

    articlesToEmail = None
    
    if 'outputContexts' in session['queryResult']:
        for i in session['queryResult']['outputContexts']:
            if 'parameters' in i:
                if 'toemail' in i['name'] and 'articles' in i['parameters']:
                    articlesToEmail = i['parameters']['articles']

    user_email = ""

    if articlesToEmail is not None:

        # Exit w/o email if there's nothing to email
        if not articlesToEmail:
            # attributes = {"state":globals()['STATE']}
            return response_plain_text_ga(EXIT_SKILL_MESSAGE, False)

        if 'accessToken' not in session:
            # attributes = {"state":globals()['STATE']}
            return response_followup_ga(LOGIN_MESSAGE, False)
        else:
            request_data = requests.get("https://api.amazon.com/user/profile?access_token=" + session['user']['accessToken'])
            request_json = request_data.json()
            user_email = request_json['email']

        msg = HTML_MSG_1

        articles = session['attributes']['articles']

        msg += "<div align='center'>"
        msg += "<a href='#' style='text-decoration: none; color: #000000;'>"
        msg += "<br>"
        msg += "<img src='https://realnewsapp.github.io/img/logo.png' style='max-width: 50%; height: auto;' />"
        msg += "<br><br><hr />"
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

        msg += HTML_MSG_2

        """ email logic """
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('EMAIL_SENDER_ADDRESS'))
        to_email = Email(user_email)

        subject = "Your Real News Digest"
        content = Content("text/html", msg)
        mail = Mail(from_email, subject, to_email, content)
        sendGrid = sg.client.mail.send.post(request_body=mail.get())

    # attributes = {"state":globals()['STATE']}
    return response_plain_text_ga(EXIT_SKILL_MESSAGE, False)

def do_help():
    """ return a help response  """

    global STATE
    STATE = STATE_START
    # attributes = {"state":globals()['STATE']}
    return response_plain_text_ga(HELP_MESSAGE, True)

def on_launch():
    """ called on Launch reply with a welcome message """
 
    return get_welcome_message()

def on_session_ended(request):
    """ called on session end  """
    

    if request['reason']:
        end_reason = request['reason']
        print("on_session_ended reason: " + end_reason)
    else:
        print("on_session_ended")

def get_state(session):
    """ get and set the current state  """

    global STATE
    if 'state' in session['attributes']:
        STATE = session['attributes']['state']
    else:
        STATE = STATE_START

# --------------- response string formatters -----------------
def get_welcome_message():
    """ return a welcome message """

    return response_plain_text_ga(WELCOME_MESSAGE, True)

def response_plain_text_ga(output, continuesession):
    """ create a simple json plain text response  """

    return {
        "payload": {
            'google': {
                "expectUserResponse": continuesession,
                "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": output
                        }
                    }
                ]
                }
            }
        }
    }

def response_plain_context_ga(output, attributes, continuesession):
    """ create a simple json plain text response  """

    return {
        "payload": {
            'google': {
                "expectUserResponse": continuesession,
                "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": output
                        }
                    }
                ]
                }
            }
        },
        "outputContexts": attributes
    }

def response_followup_ga(output, continuesession):
    """ create a simple json plain text response  """

    return {
        "payload": {
            'google': {
                "expectUserResponse": continuesession,
                "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": output
                        }
                    }
                ]
                }
            }
        },
        "followupEventInput": {
            "name": "Login",
            "languageCode": "en-US",
        }
    }

def response_ga(attributes, speech_response):
    """ create a simple json response """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speech_response
    }

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
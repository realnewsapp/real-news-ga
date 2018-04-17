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
        msg += "<br><img src='"
        msg += EMAIL_HEADER_IMG
        msg += "' style='max-width: 50%; height: auto;' /><br><br><hr />"
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

        subject = "Your Real News Digest"
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
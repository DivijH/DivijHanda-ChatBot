import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"

#Importing dialogflow for Natural Language Processing
import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = <your_project_id>

#Importing MongoDB for storing and retrieving search history of the user
from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:<password>@cluster0-nuplz.mongodb.net/test?retryWrites=true&w=majority')
db = client.get_database('chatbot_db')
news_records = db.news_records
weather_records = db.weather_records

#GNews is an API for fetching news
from gnewsclient import gnewsclient
client = gnewsclient.NewsClient(max_results=3)

def get_news(parameters):
	#Searching for search parameters
	client.topic = parameters.get('news_type', '')
	client.language = parameters.get('language', '')
	client.location = parameters.get('geo_country', '')
	#If no parameters are specified by the user
	if client.topic == '':
		client.topic = 'Nation'
	if client.language == '':
		client.language = 'english'

	#Storing news search request query in our chatbot database
	news_data = {'news_type':client.topic, 'language':client.language, 'geo_country':client.location}
	if news_records.find_one(news_data) == None:
		news_records.insert_one(news_data)
	return client.get_news()


#Importing requests and json for getting data from Weather API(openweathermap)
import requests, json

def get_weather(parameters):
	api_key = <your_api_key>
	city = parameters.get('geo-city')
	url = 'http://api.openweathermap.org/data/2.5/weather?appid=' + api_key + '&q=' + city
	#Storing data in MongoDB
	weather_data = {'geo-city':city}
	if weather_records.find_one(weather_data) == None:
		weather_records.insert_one(weather_data)
	return requests.get(url).json()


def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result 

def fetch_reply(msg, session_id):
	response = detect_intent_from_text(msg, session_id)
	#Fetching news for our user
	if response.intent.display_name == 'get_news':
		news = get_news(dict(response.parameters))
		news_str = 'Here is your news:'
		for row in news:
			news_str += '\n\n{}\n\n{}\n\n'.format(row['title'], row['link'])
		return news_str
	#Fetching weather data for our user
	elif response.intent.display_name == 'get_weather':
		weather = get_weather(dict(response.parameters))
		if weather['cod']!='404' and weather['cod']!='400':
			temperature = str(round(weather['main']['temp']-273.15, 2)) + ' °C'
			weather_str = 'Weather for ' + weather['name'] + ':\nTemperature: ' + temperature + '\nHumidity: ' + str(weather['main']['humidity']) + '%\nAtmospheric Pressure: ' + str(weather['main']['pressure']) + ' hPa\nDescription: ' + str(weather['weather'][0]['description'])
			return weather_str
		else:
			return 'Please enter a valid city'
	#Case for not understanding the query by user
	else:
		return response.fulfillment_text

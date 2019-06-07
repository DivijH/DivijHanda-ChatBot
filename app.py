from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import fetch_reply
import wikipedia

app = Flask(__name__)

@app.route('/')
def hello():
	return 'This site is working'

@app.route('/sms', methods=['POST'])
def sms_reply():
	#Fetch message
	msg = request.form.get('Body')
	sender = request.form.get('From')
	# Create reply
	resp = MessagingResponse()
	my_message = fetch_reply(msg, sender)
	#Message starting with 'Here is your news:' are from news query
	if my_message[0:18]=='Here is your news:':
		image = 'https://www.thelillahuset.com/wp-content/uploads/2018/11/news.jpg'
		resp.message(my_message).media(image)

	#Message starting with 'Weather for ' are from weather query
	elif my_message[0:12]=='Weather for ':
		city = ''
		for ch in my_message[12:]:
			if ch==':':
				break
			city+=ch
		try:
			image = wikipedia.page(city).images[0]
		except:
			image = 'https://wi-images.condecdn.net/image/doEYpG6Xd87/crop/2040/f/weather.jpg'
		resp.message(my_message).media(image)

	#Case for not understanding the user query
	else:
		resp.message(my_message)
	
	return str(resp)

if __name__ == '__main__':
	app.run()
from dash import Dash, dcc, html, Input, Output, DiskcacheManager, CeleryManager, callback
import RPi.GPIO as GPIO
from gpiozero import LED
import Freenove_DHT as DHT
import bluetooth
import smtplib
import time as time
import imaplib
import email
from email.header import decode_header
import webbrowser
import os

emailadd = ""
password = ""


#GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# GPIO setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

DHTin =  13 # DHT pin

Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 17 # Input Pin
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

isSent = False #check to ony send 1 email


def clean(text):
	# clean text for creating a folder
	return "".join(c if c.isalnum() else "_" for c in text)



#on and off LED Image
ledonImg = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.pngall.com%2Fwp-content%2Fuploads%2F2016%2F03%2FLight-Bulb-PNG-File.png&f=1&nofb=1&ipt=4b6dfaef65c3415b004cf1ace7ec7e574e72761bd0b4a499e421ad558bdb6188&ipo=images"
ledoffImg = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fjooinn.com%2Fimages%2Fisolated-light-bulb-1.jpg&f=1&nofb=1&ipt=f78dfa9fd703b7f469b6fdba546220e119555a0d638393e27a9b653beac80ffe&ipo=images"

fanImg = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ficon-library.com%2Fimages%2Ffan-icon-png%2Ffan-icon-png-2.jpg"




def openMot():
	GPIO.output(Motor1,GPIO.HIGH)
	GPIO.output(Motor2,GPIO.LOW)
	GPIO.output(Motor3,GPIO.HIGH)

def clean(text):
	# clean text for creating a folder
	return "".join(c if c.isalnum() else "_" for c in text)


#sendemail
def send():
	with smtplib.SMTP('outlook.office365.com', 587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()

		smtp.login(emailadd, password)

		subject = 'Temp'
		body = 'Temperature exceeded 24C do you want to turn on fans?'

		msg = f'subject: {subject}\n\n{body}'

		smtp.sendmail(emailadd, emailadd, msg)



app = Dash(__name__)

app.head = [html.Link(rel='stylesheet', href='iotcss.css')]

app.layout = html.Div(children=[
	html.Nav([
		html.H3("Iot Project")
		]),
	html.Div(id="wrapper", children=[
		html.Div(id='user',
			 children=[
				 html.Img(id='pfp', src="#"),
				 html.Ul(id="userPref", children=[
					html.Li("Username"),
					html.Li("Light Treshold"),
					html.Li("Temeraure Treshold"),
					html.Li("Humidity Treshold"),
					html.Li("s")
				 ])
				 ]),
		html.Div(id='ledDiv', children=[
			html.H2("LED"),
			html.Button(children=[
				html.Img(src=ledoffImg, id='btnimg', height='200px')
				], id='submit-val', n_clicks=0)
			]),
		html.Div(id='weatherDiv', children=[
			html.H2("Weather"),
			html.Img(src= fanImg, id='fanimg'),
			html.Div(id='testP'),
			html.Div(id='testP1'),
			html.Div(id='bluetoothDiv'),
			])
		]),#interval that updates the code every 1000ms (1s)
		dcc.Interval(
			id='interv',
			interval=1000,
			n_intervals=0
		)
])



#turn LED on and off whenever the user presses the button on the dashboard
@callback(
	Output('btnimg', 'src'),
	Input('submit-val', 'n_clicks'),
	prevent_initial_call=True
)
def update_output(n_clicks):
	if n_clicks % 2:
		GPIO.output(LED, GPIO.LOW)
		return ledoffImg
	else:
		GPIO.output(LED, GPIO.HIGH)
		return ledonImg
	
	return 0
			
# Change the temperature in real time and send email if it reaches a certain treshold (10*C)
# Read the temperature in real time and send email if it reaches a certain treshold (24*C)
@callback(
	Output('testT', 'children'),
	Input('interv', 'n_intervals'),
	prevent_initial_call=True
 )           
def FanCheck(inVal):

	dht = DHT.DHT(DHTin)
	
	isSent = False
	
	counts = 0 # Measurement counts
	while(True):
		counts += 1
		for i in range(0,15):
			chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
			if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
				break
			time.sleep(0.1)
		print("Temperature : %.2f \n"%(dht.temperature))
		if(dht.temperature >= 24 and isSent == False):
			isSent = True # only send 1 email
			send()
			return 0
		return dht.temperature


# Read the humidity in real time
@callback(
	Output('testH', 'children'),
	Input('interv', 'n_intervals'),
	prevent_initial_call=True
 )           
def humidityCheck(inVal):

	dht = DHT.DHT(DHTin)
	
	counts = 0 # Measurement counts
	while(True):
		counts += 1
		for i in range(0,15):
			chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
			if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
				break
			time.sleep(0.1)
		print("Humidity : %.2f\n"%(dht.humidity))
		return dht.humidity

'''
@callback(
	Output('bluetoothDiv', 'children'),
	Input('interv', 'n_intervals'),
	prevent_initial_call=True
 )           
def scan(n):

	devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)

	number_of_devices = len(devices)
	return f'{number_of_devices} devices found'     
'''

# every second, check if the email was sent
# if yes read the email
# else set isSent to True and send an email
@callback(
	Output('testP1', 'children'),
	Input('interv', 'n_intervals'),
	prevent_initial_call=True
 )      
def check(default):
	global isSent

	imap_server = "outlook.office365.com" # email server
	# create an IMAP4 class with SSL 
	imap = imaplib.IMAP4_SSL(imap_server)
	# authenticate
	imap.login(emailadd, password)

	status, messages = imap.select("INBOX")
	# number of top emails to fetch
	N = 1
	# total number of emails
	messages = int(messages[0])  

	if(isSent is True):
		for i in range(messages, messages-N, -1):
	# fetch the email message by ID
			res, msg = imap.fetch(str(i), "(RFC822)")
			for response in msg:
				if isinstance(response, tuple):
			# parse a bytes email into a message object
					msg = email.message_from_bytes(response[1])
			# decode the email subject
					subject, encoding = decode_header(msg["Subject"])[0]
					if isinstance(subject, bytes):
				# if it's a bytes, decode to str
						subject = subject.decode(encoding)
			# decode email sender
					From, encoding = decode_header(msg.get("From"))[0]
					if isinstance(From, bytes):
						From = From.decode(encoding)
			# if the email message is multipart
					if msg.is_multipart():
				# iterate over email parts
						for part in msg.walk():
					# extract content type of email
							content_type = part.get_content_type()
							content_disposition = str(part.get("Content-Disposition"))
							try:
						# get the email body
								body = part.get_payload(decode=True).decode()
								print(body)
							except:
								pass
							if content_type == "text/plain" and "attachment" not in content_disposition:
						# print text/plain emails and skip attachments
								print(body)
								if("yes" in body):
									print("balls2")
									isSent = False 
									openMot()
							#code here
					else:
				# extract content type of email
						content_type = msg.get_content_type()
				# get the email body
						body = msg.get_payload(decode=True).decode()
						if content_type == "text/plain":
					# print only text email parts
							print(body)
							if("yes" in body):
								print("balls")
								isSent = False 
								openMot()
						#code here
# close the connection and logout
	imap.close()
	imap.logout()

if __name__ == '__main__':
	app.run(debug=True)




   
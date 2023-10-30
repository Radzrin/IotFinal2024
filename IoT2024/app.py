from dash import Dash, html, dcc, Input, Output, callback, DiskcacheManager, CeleryManager
import plotly.graph_objects as go
import dash_daq as daq
import dash_bootstrap_components as dbc
import RPi.GPIO as GPIO
from gpiozero import LED
import Freenove_DHT as DHT
import DHT11 as DHT11
# import bluetooth
import smtplib
import time as time
import imaplib
import email
from email.header import decode_header
import webbrowser
import os

emailadd = "iotproject2024@outlook.com"
password = "Project4iot2024"

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED = 12
GPIO.setup(LED, GPIO.OUT)

DHTPin = 13 
dht = DHT.DHT(DHTPin) 

# Motor Setup
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

def openMot():
	GPIO.output(Motor1,GPIO.HIGH)
	GPIO.output(Motor2,GPIO.LOW)
	GPIO.output(Motor3,GPIO.HIGH)

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

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(dbc.NavbarBrand("IoT - Dashboard", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    style={"textDecoration": "none"},
                )
            ],
        ),
        color="#393646",
        dark=True,
    ),
    
    
    # Top Div
    html.Div(children=[
        html.H1("User", "header"),
        html.Div(children=[
            html.Img(src="assets/userIcon.png", id="userIcon"),
        ])
    ],id='topDiv'),
    html.Div(children=[
        html.Div(children=[
            html.H1("Temperature and Humidity", "header"),
            html.Div(children=[
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        color={"gradient":True,"ranges":{"blue":[-10,-24],"green":[-24,24],"red":[24,40]}},
                        id='temp-gauge',
                        label="Temperature",
                        value=0,
                        min=-10,
                        max=40,
                        units="°C",
                        size=150,
                        theme="dark"
                    ),
                ], id="temp-gaugeDiv"),
				html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        color={"gradient":True,"ranges":{"blue":[-20,-24],"green":[-24,24],"red":[24,40]}},
                        id='hum-gauge',
                        label="Humidity",
                        value=0,
                        min=-20,
                        max=100,
                        units="°C",
                        size=150
                    ),
                ], id="hum-gaugeDiv"),
				html.P("Does it Work?"),
                html.Div(id='testP1'),
            ], className="gaugeContainer"),
            
        ],id='temp-humDiv'),

        # Fan Div
        html.Div(children=[
            html.H1("Fan", "header"),
            html.Div(children=[
                html.Img(style={'width': '200px', 'height': '200px'}, src="assets/fan.png", className="rotate-image", id="rotate-image"),
            ], id="fanDiv"),
            daq.ToggleSwitch(id='toggle-switch')
        ], id="div1"),
	html.Div(id='testP'),
        
        # Light Div
        html.Div(children=[
            html.H1("Light", "header"),
            html.Div([
                html.Img(id='image-display'),
            ], id="lightDiv"),
            daq.ToggleSwitch(id='image-toggle')
        ], id="div2"),
    ], className="widgetContainer"),
	# Testing

	# html.Div(id='testT'),
	
    dcc.Interval(
        id='intervalDiv',
        interval=1000,
        n_intervals=0
    )

])
    
#Turn LED on and off whenever the user presses the button on the dashboard
@app.callback(Output('image-display', 'src'),
    Input('image-toggle', 'value'))
    
def update_image(toggle_value):
    lightOn = 'assets/lightOn.png'
    lightOff = 'assets/lightOff.png'
    
    if toggle_value:
        GPIO.output(LED, GPIO.HIGH)
        return lightOn
    else:
        GPIO.output(LED, GPIO.LOW) 
        return lightOff


# Change the temperature in real time and send email if it reaches a certain treshold (10*C)
# Read the temperature in real time and send email if it reaches a certain treshold (24*C)
@app.callback(Output('temp-gauge', 'value'),
    Input('intervalDiv', 'n_intervals'),
    prevent_initial_call=True
)

def FanCheck(inVal):
    global isSent
    for i in range(0,15):
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            break
        time.sleep(0.1)
    print("Temperature : %.2f\n"%(dht.temperature))
	
    if(dht.temperature >= 24 and isSent == False):
        isSent = True # only send 1 email
        send()
        return 0
    return dht.temperature


# Read the humidity in real time
@app.callback(Output('hum-gauge', 'value'),
    Input('intervalDiv', 'n_intervals'),
    prevent_initial_call=True
 )      
     
def humidityCheck(inVal):
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

# TODO: At the moment, the fan is only being turned on by a toggle switch. Change when email is received.
# every second, check if the email was sent
# if yes read the email
# else set isSent to True and send an email
@app.callback(
    Output('rotate-image', 'className'),
    Input('toggle-switch', 'value')
)

def update_image_rotation(toggle_value):
    if toggle_value:
        return "rotate-image"
    else:
        return ""

# every second, check if the email was sent
# if yes read the email
# else set isSent to True and send an email
@app.callback(Output('testP1', 'children'),
    Input('intervalDiv', 'n_intervals'),
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
	isSent = True

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
									print("lmao it works")
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
							print(body + "bod")
							if("yes" in body):
								print("balls")
								isSent = False 
								openMot()
						#code here
# close the connection and logout
	imap.close()
	imap.logout()

check(1)


if __name__ == '__main__':
    app.run_server(debug=True)

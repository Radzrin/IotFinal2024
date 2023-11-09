from dash import Dash, html, dcc, Input, Output, callback, DiskcacheManager, CeleryManager
import plotly.graph_objects as go
import dash_daq as daq
import dash_bootstrap_components as dbc
import RPi.GPIO as GPIO
from gpiozero import LED
import Freenove_DHT as DHT
import DHT11 as DHT11
# import bluetooth
import time, datetime
import webbrowser
import os, ssl, smtplib
from email.message import EmailMessage
import email, imaplib
from email.header import Header, decode_header
import paho.mqtt.client as mqttClient
import dash_mqtt

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LED Setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

# DHT11 Setup
#DHTPin = 13
DHTPin = 17
dht = DHT.DHT(DHTPin)

# Motor Setup
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 4
#Motor3 = 17 # Input Pin
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

def clean(text):
	# clean text for creating a folder
	return "".join(c if c.isalnum() else "_" for c in text)

def openMot():
	GPIO.output(Motor1,GPIO.HIGH)
	GPIO.output(Motor2,GPIO.LOW)
	GPIO.output(Motor3,GPIO.HIGH)
	
def closeMot():
	GPIO.output(Motor1,GPIO.LOW)
	GPIO.output(Motor2,GPIO.HIGH)
	GPIO.output(Motor3,GPIO.LOW)

fanON = "rotate-image"
fanOFF = ""
isSent = False
curr_temperature = 0
led_on_time = datetime.datetime.now()
email_status = ""
email_sender = 'galenkomaxym@gmail.com'
email_password = 'wgdc hsdp jdlj xgld'
email_receiver = 'galenkomaxym@gmail.com'

broker_address= "192.168.0.167"  #Broker address
port = 1884   


def sendTempEmail():
    subject = 'Your preferred temperature'
    body = '''
    Temperature exceeded 24°C do you want to turn on fans?
    '''
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
        
def sendLightEmail():
    global email_status
    email_status = "Email has been sent."
    subject = 'Light is ON'
    body = '''
    The Light is ON at {led_on_time.strftime("%H:%M")} time.
    '''
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)

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
        ]),
        html.Div(children=[
            html.P("User ID: 1232320", id="uid"),
            html.P("User Preferred Temperature: 24°C"),
            html.P("User Name : Name123")
            html.P("Light Intensity Email Status: {email_status}")
        ], id="userContent")
    ],id='topDiv'),
    
    # Temperature and Humidity Header
    html.Div(children=[
        html.Div(children=[
            html.H1("Temperature and Humidity", "header"),
            html.Div(children=[
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        id='temp-gauge',
                        label="Temperature",
                        value=0,
                        min=0,
                        max=40,
                        units="°C",
                        size=150,
                        theme="dark"
                    ),
                ], id="temp-gaugeDiv"),
				html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        id='hum-gauge',
                        label="Humidity",
                        value=0,
                        min=0,
                        max=150,
                        units="°C",
                        size=150
                    ),
                ], id="hum-gaugeDiv"),
            ], className="gaugeContainer"),
            
        ],id='temp-humDiv'),

        # Fan Div
        html.Div(children=[
            html.H1("Fan", "header"),
            html.Div(children=[
                html.Img(style={'width': '200px', 'height': '200px'}, src="assets/fan.png", className="", id="rotate-image"),
            ], id="fanDiv")
        ], id="div1"),
        
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


# Change the humidity and temperature in real time and send email if it reaches a certain threshold (10*C)
# Read the humidity and temperature in real time and send email if it reaches a certain threshold (24*C)
@app.callback(
    Output('temp-gauge', 'value'),
    Output('hum-gauge', 'value'),
    Input('intervalDiv', 'n_intervals'),
    prevent_initial_call=True
)

def HumTempGauges(inVal):
    global isSent
    global curr_temperature
    for i in range(0,15):
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            break
        time.sleep(0.1)
    
    curr_temperature = dht.temperature
	
    #Check if fan must be turned on
    if(dht.temperature >= 24 and isSent == False):
        isSent = True # only send 1 email
        sendTempEmail()
        return 0
        
    return dht.temperature, dht.humidity

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

@app.callback(
    Output('rotate-image', 'className'),
    Input('intervalDiv', 'n_intervals'),
    prevent_initial_call=True
)
def check(toggle_value):
    global isSent
    global led_on_time
    
    led_on_time = datetime.datetime.now()
    
    if(curr_temperature < 24):
        closeMot()
        return fanOFF
    else:
        # IMAP settings
        imap_server = 'imap.gmail.com'  # Replace with your IMAP server (e.g., imap.gmail.com)
        username = 'galenkomaxym@gmail.com'  # Your email address
        password = 'wgdc hsdp jdlj xgld'  # Your email password

        # Subject to search for
        subject_to_search = 'Your preferred temperature'

        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)

        # Select the mailbox you want to search (e.g., 'INBOX')
        mailbox = 'INBOX'
        mail.select(mailbox)

        # Search for emails with the specified subject
        search_criteria = f'SUBJECT "{subject_to_search}"'
        result, data = mail.search(None, search_criteria)

        if result == 'OK':
            email_ids = data[0].split()
            if email_ids:
                latest_email_id = email_ids[-1]  # Get the latest email ID
                # Fetch the latest email
                result, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                if result == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')

                    # Extract and print the email body
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode()
                            if('yes' in body.lower()):
                                openMot() # start motor
                                return fanON
        # Close the mailbox and logout
        mail.close()
        mail.logout()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("IoTlab/ESP")
    client.subscribe("/esp8266/data")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqttClient.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect_async(broker_address, 1884, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()
  
if __name__ == '__main__':
    app.run_server(debug=True)
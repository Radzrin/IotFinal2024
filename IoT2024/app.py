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
from photoResistor import PhotoResistor
import threading

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LED Setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

# Photoresistor
resistor = PhotoResistor()
lightIntensity = 0

# DHT11 Setup
DHTPin = 13 
dht = DHT.DHT(DHTPin) 

# Motor Setup
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 17 # Input Pin
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
emailLightCount = 0
email_sender = 'galenkomaxym@gmail.com'
email_password = 'wgdc hsdp jdlj xgld'
email_receiver = 'galenkomaxym@gmail.com'

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
    global emailLightCount
    emailLightCount = 1
    email_status = "Email has been sent."
    subject = 'Light is ON'
    body = '''
    The Light is ON at '''+ str(led_on_time.strftime("%H:%M")) +'''.'''
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
            html.P("User ID: 204834"),
            html.P("User Prefered Temperature: 24°C"),
            html.P("User Name : Name123"),
            html.P(id="lightEmailStatus")
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
                        max=100,
                        units="%",
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
            dcc.Slider(
                        0,1000, 
                        marks=None,
                        disabled=True,
                        tooltip={"placement": "bottom", "always_visible": True},
                        id="intensityValue"
                    )
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

#Update Light Intensity
@app.callback(Output('intensityValue', 'value'),
    Input('intervalDiv', 'n_intervals'))
    
def update_lightIntensity(toggle_value):
    lightIntensity = int(resistor.lightValue)
    
    return lightIntensity
    
#Turn LED on and off whenever the user presses the button on the dashboard
@app.callback(Output('image-display', 'src'),
            Output('lightEmailStatus', 'children'),
            Input('intervalDiv', 'n_intervals'))
    
def update_image(toggle_value):
    lightOn = 'assets/lightOn.png'
    lightOff = 'assets/lightOff.png'
    lightIntensity = int(resistor.lightValue)
    global emailLightCount
    
    if int(lightIntensity) < 400:
        if(emailLightCount == 0):
            sendLightEmail()
            emailLightCount = 1
        GPIO.output(LED, GPIO.HIGH)
        return lightOn, "Light Intensity Email Status: Sent"
    else:
        GPIO.output(LED, GPIO.LOW) 
        emailLightCount = 0
        return lightOff, "Light Intensity Email Status: Not Sent"


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

# TODO: At the moment, the fan is only being turned on by a toggle switch. Change when email is received.
# every second, check if the email was sent
# if yes read the email
# else set isSent to True and send an email
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

if __name__ == '__main__':
    threading.Thread(target=resistor.run).start()
    app.run_server(debug=True)
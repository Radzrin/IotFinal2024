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

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LED Setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

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

def clean(text):
	# clean text for creating a folder
	return "".join(c if c.isalnum() else "_" for c in text)

fanON = "rotate-image"
fanOFF = ""


# Send Email
emailadd = "iotproject1testing@outlook.com"
password = "Testingiotproject1"
emailCount = 0
isSent = False #check to ony send 1 email

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
        ]),
        html.Div(children=[
            html.P("User ID: 204834"),
            html.P("User Prefered Temperature: 24°C"),
            html.P("User Name : Name123")
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
    isSent = False
    for i in range(0,15):
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            break
        time.sleep(0.1)
    print("Temperature : %.2f\n"%(dht.temperature))
    print("Humidity : %.2f\n"%(dht.humidity))
	
    #Check if fan must be turned on
    if(dht.temperature >= 24 and isSent == False):
        isSent = True # only send 1 email
        emailCount = 1
        send()
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

    imap_server = "outlook.office365.com"  # email server
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
    emailCount = 1
    for i in range(messages, messages - N, -1):
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
                            if "yes" in body:
                                isSent = False
                                openMot() # start motor
                                print("fan is on")
                                return fanON  # Return "rotate-image" when "yes" is found
                            else:
                                # extract content type of email
                                content_type = msg.get_content_type()
                                # get the email body
                                body = msg.get_payload(decode=True).decode()
                                if content_type == "text/plain":
                                    # print only text email parts
                                    print(body + "bod")
                                    if("yes" in body):
                                        isSent = False
                                        openMot() # start motor
                                        print("fan is on")
                                        return fanON
        print("fan is off")  
        # if needed close motor here                          
        return fanOFF
    else:
        print("fan is off")  
        # if needed close motor here  
        return fanOFF
    # Close the connection and logout
    imap.close()
    imap.logout()

check(1)


if __name__ == '__main__':
    app.run_server(debug=True)

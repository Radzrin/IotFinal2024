import time, datetime, webbrowser, os, ssl, smtplib, email, imaplib, threading, sqlite3, secrets
from dash import Dash, html, dcc, Input, Output, callback, DiskcacheManager, CeleryManager
import plotly.graph_objects as go
import dash_daq as daq
import dash_bootstrap_components as dbc
import RPi.GPIO as GPIO
from gpiozero import LED
import Freenove_DHT as DHT
import DHT11 as DHT11
from bluepy.btle import Scanner
from email.message import EmailMessage
from email.header import Header, decode_header
from photoResistor import PhotoResistor

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LED Setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

# Photoresistor
resistor = PhotoResistor()
lightIntensity = 0

# RFID
rfid_codes = []
user_info = []
id = ""
temp_th = 0
light_th = 0
username = ""
curr_user = ""
userEmail = ""
userEmailCount = 0


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

# Creating and populating the database
con = sqlite3.connect("iotuserinfo.db")
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS user")

cur.execute("CREATE TABLE user(RFID_tag, username, email, temp_threshold, light_treshhold)")

cur.execute("""
    INSERT INTO user VALUES
        (' 36 1f 56 91', 'Chris', 'kiko65@outlook.com', 24, 200),
        (' 76 47 50 91', 'Maxym', 'maxymgalenko@gmail.com', 23, 300)
""")

users = cur.execute("SELECT * FROM user").fetchall()

for user in users:
    user_info.append(user);

con.commit()

#----------------------------------------

# Motor Setup
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

# Email Setup
fanON = "rotate-image"
fanOFF = ""
isSentTempEmail = False
isSentLightEmail = False
curr_temperature = 0
led_on_time = datetime.datetime.now()
email_status = ""
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

def sendUserEmail():
    global username
    subject = 'New User'
    body = '''
    User '''+ str(username) +'''has entered at''' + str(led_on_time.strftime("%H:%M"))+ '''.'''
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
            html.P("User ID: 204834", id="user_id"),
            html.P("User Prefered Temperature: 24°C", id="temp_t"),
            html.P("User Name : Name123", id="username"),
            html.P(id="email"),
            html.P(id="light_t"),
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
    html.Button('Submit', id='btebtn', n_clicks=0),
    html.Div(id="bluetoothDiv"),
    html.Div(id='container-button-basic', children='Enter a value and press submit'),
	# html.Div(id='testT'),
	
    dcc.Interval(
        id='intervalDiv',
        interval=1000,
        n_intervals=0
    )

])

# Display User Info, if not register user
@app.callback(Output('user_id', 'children'),
                Output('username', 'children'),
                Output('email', 'children'),
                Output('temp_t', 'children'),
                Output('light_t', 'children'),
    Input('intervalDiv', 'n_intervals'))
     
def update_User(toggle_value):
    global id
    global temp_th
    global light_th
    global user_info
    global username
    global temp_th
    global rfid_codes
    global curr_user
    global userEmail
    global userEmailCount

    rfid_code = str(resistor.rfidValue) 
   # rfid_code = ' 36 1f 56 91' # to test, remove when done and uncomment above
    
    for user in user_info:
        if rfid_code in user[0]:
            # Send Email if not sent yet
            if(userEmailCount == 0):
                # sendUserEmail()
                userEmailCount = 1
            
            # Display Current User's Information
            curr_user = str(user[0])
            id = "User ID:" + str(curr_user)
            temp_string = "User Preferred Temperature: " + str(user[3]) + "°C"
            light_string = "User Preferred Light Intensity: " + str(user[3])
            temp_th = int(user[3])
            light_th = int(user[3])
            username = "Username: " + str(user[1])
            email = "Email: " + str(user[2])


            return id, username, email, temp_string, light_string    
        else: 
            # Return Not Valid if the User is not in the system
            return "User ID: Not Valid", "Username: Not Valid","Email: Not Valid", "User Preferred Temperature: Not Valid", "User Preferred Light Intensity: Not Valid"

#Update Light Intensity
@app.callback(Output('intensityValue', 'value'),
    Input('intervalDiv', 'n_intervals'))
    
def update_lightIntensity(toggle_value):
    lightIntensity = int(resistor.lightValue)
    #update_User(toggle_value)
    
    return lightIntensity

#Update Light Intensity
@app.callback(Output('bluetoothDiv', 'children'),
    Input('btebtn', 'n_clicks'),
    prevent_initial_call=True)
    
def update_bte(toggle_value):
    print("please wait")
    scanner = Scanner()
    devices = scanner.scan(10.0)
    countBT = 0
 
    for device in devices:
        if (device.rssi > -100 and device.rssi < -75):
            countBT  += 1
                       
    return countBT  

    
#Turn LED on and off whenever the user presses the button on the dashboard
@app.callback(Output('image-display', 'src'),
            Output('lightEmailStatus', 'children'),
            Input('intervalDiv', 'n_intervals'))
    
def update_image(toggle_value):
    lightOn = 'assets/lightOn.png'
    lightOff = 'assets/lightOff.png'
    lightIntensity = int(resistor.lightValue)
    global isSentLightEmail
    global light_th
    
    if int(lightIntensity) < light_th:
        if(isSentLightEmail == False):
            sentLightEmail()
            isSentLightEmail = True
        GPIO.output(LED, GPIO.HIGH)
        return lightOn, "Light Intensity Email Status: Sent"
    else:
        GPIO.output(LED, GPIO.LOW)
        isSentLightEmail = False
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
    global temp_th
    global isSentTempEmail
    global curr_temperature
    for i in range(0,15):
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            break
        time.sleep(0.1)
    
    curr_temperature = dht.temperature
    
    #Check if fan must be turned on
    if(dht.temperature >= temp_th and isSentTempEmail == False):
        isSentTempEmail = True # only send 1 email
        sendTempEmail()
        return 0
        
    return dht.temperature, dht.humidity

# Checks if the email was answered with a yes to tun on the fan
@app.callback(
    Output('rotate-image', 'className'),
    Input('intervalDiv', 'n_intervals'),
    prevent_initial_call=True
)
def check(toggle_value):
    global isSentTempEmail
    global led_on_time
    global temp_th
    
    led_on_time = datetime.datetime.now()
    
    if(curr_temperature < temp_th):
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
from dash import Dash, html, dcc, Input, Output, callback, DiskcacheManager, CeleryManager
import plotly.graph_objects as go
import dash_daq as daq
import dash_bootstrap_components as dbc
import Freenove_DHT as DHT
import time
import RPi.GPIO as GPIO
from gpiozero import LED

# GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# GPIO setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

# DHT setup
DHTin=13

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
                        color={"gradient":True,"ranges":{"blue":[-40,-24],"green":[-24,24],"red":[24,40]}},
                        id='temp-gauge',
                        label="Temperature",
                        value=0,
                        min=-40,
                        max=40,
                        units="°C",
                        size=150,
                        theme="dark"
                    ),
                ], id="temp-gaugeDiv"),
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        color={"gradient":True,"ranges":{"blue":[-40,-24],"green":[-24,24],"red":[24,40]}, "value": "black"},
                        id='hum-gauge',
                        label="Humidity",
                        value=0,
                        min=-40,
                        max=40,
                        units="°C",
                        size=150
                    ),
                ], id="hum-gaugeDiv"),
            ], className="gaugeContainer"),
            dcc.Interval(
                id='intervalDiv',
                interval=1000,
                n_intervals=0
            )
            
        ],id='temp-humDiv'),

        # Fan Div
        html.Div(children=[
            html.H1("Fan", "header"),
            html.Div(children=[
                html.Img(style={'width': '200px', 'height': '200px'}, src="assets/fan.png", className="rotate-image", id="rotate-image"),
            ], id="fanDiv"),
            daq.ToggleSwitch(id='toggle-switch')
        ], id="div1"),
        
        # Light Div
        html.Div(children=[
            html.H1("Light", "header"),
            html.Div([
                html.Img(id='image-display'),
            ], id="lightDiv"),
            daq.ToggleSwitch(id='image-toggle')
        ], id="div2"),
    ], className="widgetContainer")
])
    
# Turn Light ON and OFF
@app.callback(Output('image-display', 'src'),
    Input('image-toggle', 'value'))
    
def update_image(toggle_value):
    lightOn = 'assets/lightOn.png'
    lightOff = 'assets/lightOff.png'
    
    if toggle_value:
        # GPIO.output(LED, GPIO.HIGH)
        return lightOn
    else:
        # GPIO.output(LED, GPIO.LOW) 
        return lightOff

# TODO: At the moment, the fan is only being turned on by a toggle switch. Change when email is received.
# TODO: Test the gauge 
@app.callback(
    Output('rotate-image', 'className'),
    Input('toggle-switch', 'value')
)

def update_image_rotation(toggle_value):
    if toggle_value:
        return "rotate-image"
    else:
        return ""

@app.callback(Output('temp-gauge', 'value'),
    Input('intervalDiv', 'n_intervals'),
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
            return 0
        return dht.temperature
    
    '''
    TODO
    make a boolean value called isSent
    change the value to false
    if temp > 10 and isSent = false send email
    set isSent to true
    if inVal 
    '''


# Read Humidity from DHT11 and output to the gauge
# TODO: Test the gauge
@app.callback(Output('hum-gauge', 'value'),
    Input('intervalDiv', 'n_intervals'),
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


if __name__ == '__main__':
    app.run_server(debug=True)

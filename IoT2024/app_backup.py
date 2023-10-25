from dash import Dash, dcc, html, Input, Output, DiskcacheManager, CeleryManager, callback
import RPi.GPIO as GPIO
from gpiozero import LED
import Freenove_DHT as DHT
import time


#GPIO WARNING OFF (ignore this part)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# GPIO setup
LED = 12
GPIO.setup(LED, GPIO.OUT)

DHTin=13


#on and off LED Image
ledonImg = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.pngall.com%2Fwp-content%2Fuploads%2F2016%2F03%2FLight-Bulb-PNG-File.png&f=1&nofb=1&ipt=4b6dfaef65c3415b004cf1ace7ec7e574e72761bd0b4a499e421ad558bdb6188&ipo=images"
ledoffImg = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fjooinn.com%2Fimages%2Fisolated-light-bulb-1.jpg&f=1&nofb=1&ipt=f78dfa9fd703b7f469b6fdba546220e119555a0d638393e27a9b653beac80ffe&ipo=images"


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
            html.Img(src='', id='fanimg'),
            html.Div(id='testT'),
            html.Div(id='testH'),
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

if __name__ == '__main__':
    app.run(debug=True)
from dash import Dash, dcc, html, Input, Output, DiskcacheManager, CeleryManager, callback
import RPi.GPIO as GPIO
from gpiozero import LED

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED = 12
GPIO.setup(LED, GPIO.OUT)



app = Dash(__name__)

app.head = [html.Link(rel='stylesheet', href='iotcss.css')]

app.layout = html.Div(children=[
    html.Nav(
        html.H3("Iot Project")
        ),
    html.Div(id="wrapper", children=[
        html.Div(id='user',
             children=[
                 html.Img(id='pfp', src="#"),
                 ]),
        html.Div(id='ledDiv', children=[
            html.H2("LED"),
            html.Button(children=[
                html.Img(src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fjooinn.com%2Fimages%2Fisolated-light-bulb-1.jpg&f=1&nofb=1&ipt=f78dfa9fd703b7f469b6fdba546220e119555a0d638393e27a9b653beac80ffe&ipo=images", id='btnimg', height='200px')
                ], id='submit-val', n_clicks=0)
            ]),
        html.Div(id='weatherDiv', children=[
            html.H2("Weather")
            ])
        ])
])





@callback(
    Output('btnimg', 'src'),
    Input('submit-val', 'n_clicks'),
    prevent_initial_call=True
)
def update_output(n_clicks):
    if n_clicks % 2:
       GPIO.output(LED, GPIO.LOW)
       return "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fjooinn.com%2Fimages%2Fisolated-light-bulb-1.jpg&f=1&nofb=1&ipt=f78dfa9fd703b7f469b6fdba546220e119555a0d638393e27a9b653beac80ffe&ipo=images"
    else:
       GPIO.output(LED, GPIO.HIGH)
       return"https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.pngall.com%2Fwp-content%2Fuploads%2F2016%2F03%2FLight-Bulb-PNG-File.png&f=1&nofb=1&ipt=4b6dfaef65c3415b004cf1ace7ec7e574e72761bd0b4a499e421ad558bdb6188&ipo=images"
    
    return 0
            
    

if __name__ == '__main__':
    app.run(debug=True)
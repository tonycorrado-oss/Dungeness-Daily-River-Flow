# @title
import requests
import datetime
import pytz
import time
from IPython.display import display, HTML, clear_output

# --- CONFIGURATION ---
# USGS Gauge #12048000 (Dungeness River near Sequim, WA)
GAUGE_ID = "12048000"
URL = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={GAUGE_ID}&parameterCd=00060,00065"

# --- LOGIC DEFINITIONS ---
def get_flow_status(flow):
    """
    Determines status, colors, and text based on flow value (CFS).
    Returns a dictionary of styling and text properties.
    """
    status = {
        "bg_color": "white",
        "text": "Unknown Flow",
        "blink": False,
        "range_min": 0,
        "range_max": 100
    }

    if 0 <= flow <= 62.5:
        status = {
            "bg_color": "#FF0000",
            "text": "Extremely Low- Salmon Endangered",
            "blink": True,
            "range_min": 0,
            "range_max": 62.5
        }
    elif 62.5 < flow <= 120:
        status = {
            "bg_color": "#FFBF00",
            "text": "Critically Low- Withdrawals Reduced",
            "blink": False,
            "range_min": 62.5,
            "range_max": 120
        }
    elif 120 < flow <= 238:
        status = {
            "bg_color": "#CC9900",  # Changed to Dark Yellow
            "text": "Low Flow - Conserve Water",
            "blink": False,
            "range_min": 120,
            "range_max": 238
        }
    elif 238 < flow <= 582:
        status = {
            "bg_color": "#0099FF",
            "text": "Adequate Flow",
            "blink": False,
            "range_min": 238,
            "range_max": 582
        }
    elif 582 < flow <= 2700:
        status = {
            "bg_color": "#800080",
            "text": "High Flow",
            "blink": False,
            "range_min": 582,
            "range_max": 2700
        }
    elif 2700 < flow <= 4275:
        status = {
            "bg_color": "#FFBF00",
            "text": "Flood Alert",
            "blink": False,
            "range_min": 2700,
            "range_max": 4275
        }
    elif 4275 < flow <= 6200:
        status = {
            "bg_color": "#FF0000",
            "text": "Minor to Moderate Flood -Take Precautions",
            "blink": False,
            "range_min": 4275,
            "range_max": 6200
        }
    elif flow > 6200:
        status = {
            "bg_color": "#8B0000",
            "text": "Extreme Flooding – Evacuation May Be Necessary",
            "blink": True,
            "range_min": 6200,
            "range_max": 99999
        }

    return status

def fetch_data():
    try:
        response = requests.get(URL)
        data = response.json()
        time_series = data['value']['timeSeries'][0]
        values = time_series['values'][0]['value']
        latest_reading = values[-1]

        flow_val = float(latest_reading['value'])
        timestamp_str = latest_reading['dateTime']

        dt = datetime.datetime.fromisoformat(timestamp_str)
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')

        return flow_val, formatted_time
    except Exception as e:
        return None, str(e)

def generate_html(flow, timestamp, gauge_id):
    status = get_flow_status(flow)

    blink_keyframes = ""
    blink_animation = ""

    if status['blink']:
        blink_keyframes = f"""
        @keyframes blinker {{
            0% {{ background-color: {status['bg_color']}; opacity: 1; }}
            50% {{ background-color: #333333; opacity: 1; }}
            100% {{ background-color: {status['bg_color']}; opacity: 1; }}
        }}
        """
        blink_animation = "animation: blinker 2s linear infinite;"

    category_defs = [
        (0, 62.5, "#FF0000"),
        (62.5, 120, "#FFBF00"),
        (120, 238, "#CC9900"),  # Changed to Dark Yellow
        (238, 582, "#0099FF"),
        (582, 2700, "#800080"),
        (2700, 4275, "#FFBF00"),
        (4275, 6200, "#FF0000"),
        (6200, 7000, "#8B0000")
    ]

    total_scale = 7000
    bar_html_segments = ""

    for start, end, color in category_defs:
        segment_width = end - start
        width_pct = (segment_width / total_scale) * 100
        bar_html_segments += f'<div style="width: {width_pct}%; background-color: {color}; height: 100%; float: left; border-right: 1px solid white; box-sizing: border-box;"></div>'

    total_marker_pos = min((flow / total_scale) * 100, 100)
    range_span = status['range_max'] - status['range_min']

    if status['range_min'] == 6200:
        display_max = max(7000, flow * 1.1)
        range_span = display_max - 6200
        range_max_label = f"{int(display_max)}"
    else:
        range_max_label = f"{status['range_max']}"

    if range_span == 0: range_span = 1

    current_marker_pos = ((flow - status['range_min']) / range_span) * 100
    current_marker_pos = max(0, min(current_marker_pos, 100))

    html_content = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        {blink_keyframes}

        .app-wrapper {{
            width: 100%;
            height: 700px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Roboto', sans-serif;
            color: white;
            text-shadow: 1px 1px 2px black;
        }}

        .app-container {{
            width: 100%;
            height: 100%;
            background-color: {status['bg_color']};
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            {blink_animation}
        }}

        .main-text {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; text-align: center; }}
        .flow-val {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .meta-info {{ font-size: 11px; margin-bottom: 2px; }}

        .graph-container {{
            width: 90%;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        .bar-border {{
            border: 2px solid white;
            height: 40px;
            width: 100%;
            position: relative;
            background-color: #333;
            overflow: hidden;
        }}

        .triangle-marker {{
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 15px solid white;
            position: absolute;
            bottom: 0px;
            transform: translateX(-50%);
            z-index: 20;
        }}

        .axis-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            margin-top: 5px;
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px black;
        }}
    </style>

    <div class="app-wrapper">
        <div class="app-container">
            <div class="main-text">{status['text']}</div>
            <div class="flow-val">Current Flow: {flow} CFS</div>
            <div class="meta-info">Last Updated: {timestamp}</div>
            <div class="meta-info">USGS Gauge: {gauge_id}</div>

            <hr style="width: 50%; border-color: white; opacity: 0.5; margin: 20px 0;">

            <div class="graph-container">
                <div style="text-align: center; margin-bottom: 5px; font-weight: bold;">Categories of Total River Flow</div>
                <div class="bar-border">
                    {bar_html_segments}
                    <div class="triangle-marker" style="left: {total_marker_pos}%;"></div>
                </div>
            </div>

            <div class="graph-container">
                <div style="text-align: center; margin-bottom: 5px; font-weight: bold;">Categories of Current River Flow</div>
                <div class="bar-border" style="background-color: {status['bg_color']};">
                    <div class="triangle-marker" style="left: {current_marker_pos}%;"></div>
                </div>
                <div class="axis-labels">
                    <span>{status['range_min']} CFS</span>
                    <span>{range_max_label} CFS</span>
                </div>
            </div>

        </div>
    </div>
    """
    return html_content

# --- MAIN LOOP (60-SECOND RENEWAL) ---
print("Starting Dungeness River Monitor...")

try:
    while True:
        flow, timestamp = fetch_data()

        if flow is not None:
            clear_output(wait=True)
            display(HTML(generate_html(flow, timestamp, GAUGE_ID)))
            time.sleep(60)  # Renew every 60 seconds
        else:
            print(f"Error fetching data: {timestamp}")
            time.sleep(10)  # Quick retry if API fails

except KeyboardInterrupt:
    print("Monitor stopped.")

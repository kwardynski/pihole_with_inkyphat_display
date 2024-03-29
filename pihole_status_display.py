#!/usr/bin/env python3
from datetime import datetime
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw

import dotenv
import os
import requests


# Returns the system time at which script was called
# Format: "HH:MM:SS - dd/mm/yyyy"
def get_update_time():
    update_time = datetime.now()
    update_time_str = update_time.strftime("%H:%M:%S - %d/%m/%Y")
    return update_time_str


# Returns stats from pihole web API as a dict containing:
#   unique clients, dns queries, ads blocked, block percentage
# Returns status = "DOWN" if unable to connect/query the API
def get_pihole_stats(pihole_ip, api_token):
    api_path = f"http://{pihole_ip}/admin/api.php?summary&auth={api_token}"
    pihole_stats = dict()
    query_fields = ["unique_clients", "dns_queries_today",
                    "ads_blocked_today", "ads_percentage_today"]

    try:
        api_raw = requests.get(api_path, verify=False, timeout=5).json()
        pihole_stats["status"] = "Connected"
        for field in query_fields:
            pihole_stats[field] = api_raw[field]
    except:
        pihole_stats["status"] = "DOWN"
        for field in query_fields:
            pihole_stats[field] = "-----"
    return pihole_stats


# Generates and renders the stats image for the InkyPHAT screen
def display_info(update_time, hostname, ip_address, pihole_stats):

    # Initialize InkyPHAT instance
    inky_display = auto()

    # Base drawing "variables"
    fonts_path = f"{os.path.dirname(os.path.realpath(__file__))}/fonts"
    dw = inky_display.WIDTH
    dh = inky_display.HEIGHT
    border_perc = 0.125
    info_font = ImageFont.truetype(f"{fonts_path}/SFMono-Regular.otf", 10)
    info_x_offset = 0.01
    stats_font = ImageFont.truetype(f"{fonts_path}/SFMono-Bold.otf", 13)
    stats_x_offset = 0.02
    stats_loc = 0.1385
    stats_step = 0.1875
    if pihole_stats["status"] == "Connected":
        stats_color = inky_display.BLACK
    else:
        stats_color = inky_display.RED

    # Initialize blank canvas with black border
    inky_display.set_border(inky_display.BLACK)
    image = Image.new("P", (dw, dh))
    draw = ImageDraw.Draw(image)

    # Draw top "border" - display hostname and IP address
    draw.rectangle((0, 0, dw, (border_perc)*dh),
                   fill=inky_display.BLACK, outline=inky_display.BLACK)
    draw.text((info_x_offset*dw, 0.0075*dh),
              f'{hostname}:{ip_address}', inky_display.WHITE, font=info_font)

    # Draw bottom "border" - display last update time
    draw.rectangle((0, (1-border_perc)*dh, dw, dh),
                   fill=inky_display.BLACK, outline=inky_display.BLACK)
    draw.text((info_x_offset*dw, 0.895*dh),
              f"Updated: {update_time}", inky_display.WHITE, font=info_font)

    # Display Stats
    draw.text((stats_x_offset*dw, stats_loc*dh),
              f'Status: {pihole_stats["status"]}', stats_color, font=stats_font)
    draw.text((stats_x_offset*dw, (stats_loc+stats_step)*dh),
              f'Clients: {pihole_stats["unique_clients"]}', stats_color, font=stats_font)
    draw.text((stats_x_offset*dw, (stats_loc+2*stats_step)*dh),
              f'Queries (24 hrs): {pihole_stats["dns_queries_today"]}', stats_color, font=stats_font)
    draw.text((stats_x_offset*dw, (stats_loc+3*stats_step)*dh),
              f'Blocked: {pihole_stats["ads_blocked_today"]} ({pihole_stats["ads_percentage_today"]}%)', stats_color, font=stats_font)

    inky_display.set_image(image)
    inky_display.show()


if __name__ == "__main__":
    dotenv.load_dotenv()
    api_token = os.getenv("API_TOKEN")
    hostname = os.getenv("HOSTNAME")
    ip_address = os.getenv("IP_ADDR")
    update_time = get_update_time()
    pihole_stats = get_pihole_stats(ip_address, api_token)
    display_info(update_time, hostname, ip_address, pihole_stats)

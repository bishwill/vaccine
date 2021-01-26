from luma.core.render import canvas
from PIL import Image, ImageDraw
from PIL.ImageFont import truetype
from luma.oled.device import ssd1322
from luma.core.interface.serial import spi
from requests import get
from datetime import datetime
from math import floor
from time import sleep
from os import path
data = {}
time_font = path.dirname(path.realpath(__file__)) + '/time.ttf'
text_font = path.dirname(path.realpath(__file__)) + '/time.ttf'
size = 45

def get_data():
    global cum_vaccinated
    global daily_vaccines
    global time_of_update
    global data
    r = get('https://coronavirus.data.gov.uk/api/v1/data?filters=areaType=overview&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newPeopleVaccinatedFirstDoseByPublishDate%22:%22newPeopleVaccinatedFirstDoseByPublishDate%22,%22newPeopleVaccinatedSecondDoseByPublishDate%22:%22newPeopleVaccinatedSecondDoseByPublishDate%22,%22cumPeopleVaccinatedFirstDoseByPublishDate%22:%22cumPeopleVaccinatedFirstDoseByPublishDate%22,%22cumPeopleVaccinatedSecondDoseByPublishDate%22:%22cumPeopleVaccinatedSecondDoseByPublishDate%22%7D&format=json')
    latest_data = r.json()['data'][0]
    if latest_data != data:
        cum_vaccinated = latest_data['cumPeopleVaccinatedFirstDoseByPublishDate'] + latest_data['cumPeopleVaccinatedSecondDoseByPublishDate']
        daily_vaccines = latest_data['newPeopleVaccinatedFirstDoseByPublishDate'] + latest_data['newPeopleVaccinatedSecondDoseByPublishDate']
        time_of_update = datetime.now().strftime("%H:%M:%S")
        data = latest_data

def predictor(cum_vaccinated, daily_vaccines):
    time = datetime.now().strftime("%H:%M:%S")
    time_diff = ((60*60*int(time[0:2])) + (60*int(time[3:5])) + (int(time[6:8]))) - ((60*60*int(time_of_update[0:2])) + (60*int(time_of_update[3:5])) + (int(time_of_update[6:8])))
    ratio = time_diff / 86400
    num = floor(cum_vaccinated + ratio * daily_vaccines)
    return (f"{num:,}")

def display():
    im = Image.new('RGB', (256, 64))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), predictor(cum_vaccinated, daily_vaccines), fill = 'yellow', font = truetype(time_font, size))
    draw.text((0, 48), 'Vaccine doses administered for COVID-19 in the UK', fill = 'yellow', font = truetype(text_font, 12))
    with canvas(device, background = im) as draw:
        pass

get_data()
serial = spi(port=0, device=0)
device = ssd1322(serial, rotate = 2)


while True:
    sleep(1)
    display()
    if datetime.now().strftime("%M") == '00':
        get_data()
        sleep(60)

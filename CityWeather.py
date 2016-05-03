import pyowm
import sys

APIKEY = '9481fc3a18e6247d653e1caa71b923c1'
CITY_DICT = {'New York': 5128581}
owm = pyowm.OWM(APIKEY)

def get_weather(city):
	response = {}
	if city in CITY_DICT:
		observation = owm.weather_at_id(CITY_DICT[city])
		weather = observation.get_weather()
		response['status'] = str(weather.get_detailed_status())
		response['wind speed'] = str(weather.get_wind()['speed'])
		response['humidity'] = str(weather.get_humidity())
		response['temperature'] = weather.get_temperature('celsius')
		return response

	else:
		print 'City not available'
		return None

def main(cityName):
	get_weather(cityName)

if __name__ == "__main__":
	try:
		main('New York')
	except Exception as e:
		print e
		sys.exit(-1)

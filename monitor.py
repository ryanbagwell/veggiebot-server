from lib.garden import Garden
import datetime

garden = Garden()

""" Read the moisture level """
moisture = garden.read_mcp3008(channel_num=0)

""" Get the existing data """
data = garden.get_data()

""" Append the new reading """
data.append({
    'time': datetime.datetime.utcnow().isoformat(),
    'moistureLevel': moisture,
    })

""" Limit our data sample to 100 """
if len(data) > 100:
    data = data[-100:]

""" Save the data """
garden.save_data(data)




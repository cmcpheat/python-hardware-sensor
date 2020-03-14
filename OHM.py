# ------ References
# http://openhardwaremonitor.org/wordpress/wp-content/uploads/2011/04/OpenHardwareMonitor-WMI.pdf
# https://docs.python.org/2/library/socket.html
# https://wiki.python.org/moin/TcpCommunication#Client

import wmi

debug = False

# OHM class for retreiving hardware/sensor data
class OHM:
    # initiliases OHM application
    def __init__(self):
        self.hwmon = wmi.WMI(namespace="root\OpenHardwareMonitor")

    # when "Temperature" button is pressed on Client
    def get_core_temps(self):
        data = {} # create empty list
        sensors_temp = self.hwmon.Sensor(["Name", "Parent", "Value", "Identifier", "SensorType", "Max"],
                                        SensorType="Temperature") # sensor protocols for OHM

        for temperature in sensors_temp:

            if (temperature.Identifier.find("ram") == -1) and (temperature.Identifier.find("hdd") == -1) \
                    and (temperature.Name.find("Package") == -1):

                data['type'] = "cpu temperature" # sensor protocols for OHM
                data[temperature.name] = temperature.value
        # returns CPU temperature data to server
        return data

    # when "Load" button is pressed on Client
    def get_core_loads(self):
        data = {}
        sensors_load = self.hwmon.Sensor(SensorType="Load") # sensor protocols for OHM

        for load in sensors_load:
            if (load.Identifier.find("ram") == -1) and (load.Identifier.find("hdd") == -1) and (
                    load.Name.find("Total") == -1):

                data['type'] = "cpu load" # sensor protocols for OHM
                data[load.name] = load.value
        # returns CPU load time data to server
        return data

    # when "Power" button is pressed on Client
    def get_core_powers(self):
        data = {}
        sensors_power = self.hwmon.Sensor(SensorType="Power") # sensor protocols for OHM

        for power in sensors_power:
            if (power.Identifier.find("ram") == -1) and (power.Identifier.find("hdd") == -1) and (
                    power.Name.find("Total") == -1):

                data['type'] = "cpu powers" # sensor protocols for OHM
                data[power.name] = power.value
        # returns cpu powers data to server
        return data

    # when "Clock Speed" button is pressed on Client
    def get_clock_speeds(self):
        data = {}
        sensors_speed = self.hwmon.Sensor(SensorType="Clock") # sensor protocols for OHM

        for speed in sensors_speed:
            if (speed.Identifier.find("ram") == -1) and (speed.Identifier.find("hdd") == -1) and (
                    speed.Name.find("Total") == -1):

                data['type'] = "clock speeds" # sensor protocols for OHM
                data[speed.name] = speed.value
        # returns clock speed data to server
        return data


if __name__ == '__main__':

    my_ohm = OHM()
    core_temps = my_ohm.get_core_temps()
    print(core_temps)
    core_loads = my_ohm.get_core_loads()
    print(core_loads)
    cpu_powers = my_ohm.get_core_powers()
    print(cpu_powers)
    clock_speeds = my_ohm.get_clock_speeds()
    print(clock_speeds)

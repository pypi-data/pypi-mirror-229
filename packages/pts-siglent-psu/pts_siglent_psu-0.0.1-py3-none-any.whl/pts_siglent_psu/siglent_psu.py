import time
import pyvisa
import os
import logging


class SiglentSpdPSU:
    """
    ``Base class for the Siglent SPD3303X PSU``
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        self.psu = None
        self.connection_string = connection_string
        self.resource_manager = None

    def open_connection(self):
        """
        ``Opens a TCP/IP connection to connect to the Siglent SPD3303X PSU`` \n
        """
        self.resource_manager = pyvisa.ResourceManager('@py')
        self.connection_string = os.getenv("PSU_CONNECTION_STRING", default='TCPIP0::192.168.123.200::5025::SOCKET')
        try:
            logging.info(f": Opening PSU Resource at {self.connection_string}")
            self.psu = self.resource_manager.open_resource(self.connection_string)
            self.psu.read_termination = '\n'
            self.psu.write_termination = '\n'
        except Exception as e:
            raise Exception(f": ERROR {e}: Could not open Resource")

    def close_connection(self):
        """
        ``Closes the TCP/IP connection to the Siglent SPD3303X PSU`` \n
        """
        self.resource_manager.close()

    def id_number(self):
        """
        ``This function returns the identification number for the Siglent SPD3303X PSU`` \n
        :return: `str` : Instrument ID
        """
        id_num = self.psu.query('*IDN?')
        logging.info(f": ID number of PSU: {id_num}")
        return str(id_num)

    def system_status(self):
        """
        ``This function queries the current working state of the Siglent SPD3303X PSU
        NOTE: The return info is hexadecimal format, but the actual state is binary,
        so you must change the return info into a binary`` \n
        :return: `str` : Instrument ID
        """
        sys_status = self.psu.query('SYSTem:STATus?')
        logging.info(f": System Status of PSU: {sys_status}")
        return str(sys_status)

    def system_version(self):
        """
        ``This function queries the software version of the Siglent SPD3303X PSU`` \n
        :return: `str` : Instrument ID
        """
        sys_version = self.psu.query('*IDN?')
        logging.info(f": System Version of PSU: {sys_version}")
        return str(sys_version)

    def set_ip_address(self, ip_addr):
        """
        ``This function sets the IP address for the Siglent SPD3303X PSU`` \n
        :param ip_addr: `str` : IP address for the instrument; e.g. IPaddr 10.11.13.214 \n
        """
        self.psu.write(f'IPaddr {ip_addr}')
        logging.info(f": IP address set to: {ip_addr}")

    def check_ip_address(self):
        """
        ``This function returns the IP address for the Siglent SPD3303X PSU`` \n
        :return: `str` : IP Address
        """
        ip = self.psu.query('IPaddr?')
        logging.info(f": IP address of PSU is: {ip}")
        return str(ip)

    def set_subnet_mask(self, subnet_mask):
        """
        ``This function sets the Subnet mask for the Siglent SPD3303X PSU`` \n
        :param subnet_mask: `str` : Subnet mask for the instrument; e.g. MASKadd 255.255.255.0 \n
        """
        self.psu.write(f'MASKaddr {subnet_mask}')
        logging.info(f": Subnet mask set to: {subnet_mask}")

    def check_subnet_mask(self):
        """
        ``This function queries the subnet mask for the Siglent SPD3303X PSU`` \n
        :return: `str` : Subnet Mask
        """
        subnet_mask = self.psu.query('MASKaddr?')
        logging.info(f": Subnet mask of PSU is: {subnet_mask}")
        return str(subnet_mask)

    def set_gateway(self, gateway):
        """
        ``This function assigns a gateway for the Siglent SPD3303X PSU`` \n
        :param gateway: `str` : Gateway for the instrument; e.g., GATEaddr 10.11.13.1  \n
        """
        self.psu.write(f'GATEaddr {gateway}')
        logging.info(f": Gateway set to: {gateway}")

    def check_gateway(self):
        """
        ``This function returns the IP address for the Siglent SPD3303X PSU`` \n
        :return: `str` : Gateway address
        """
        gateway = self.psu.query('GATEaddr?')
        logging.info(f": Gateway of PSU is: {gateway}")
        return str(gateway)

    def check_channel(self):
        """
        This function checks the current operating channel
        :return: `str` : Channel number
        """
        channel_selection = self.psu.query(f'INST?')
        logging.info(f": Channel {channel_selection} is selected.")
        return str(channel_selection)

    def channel_selection(self, channel):
        """
        ``This function selects the output channel`` \n
        :param channel: `str` : Selected output channel out of 2 (CH1, Ch2) \n
        :return: `bool` : True or False
        """
        self.psu.write(f'INST {channel}')
        channel_selection = self.psu.query(f'INST?')
        if channel_selection == channel:
            logging.info(f": Channel {channel} is selected.")
            return True
        else:
            logging.info(f": ERROR: Failed to select channel {channel} ")
            return False

    def set_channel_output(self, channel, output):
        """
        ``This function turns on/off the specified channel output for the Siglent SPD3303X PSU.
        Command format: OUTPut {CH1|CH2|CH3},{ON|OFF} ; e.g.: OUTPut CH1,ON`` \n
        :param output: `str` :  Output out of ON or OFF \n
        :param channel: `str` : Output channel out of 2 (CH1, CH2) \n
        :return: `bool` : True or False or raises Error
        """
        sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
        if sys_err == '+0, No error':
            try:
                self.psu.write(f'OUTPut {channel},{output}')
                time.sleep(1)
                sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
                time.sleep(1)
                if sys_err == '+0, No error':
                    logging.info(f": Output {channel} Set to : {output} \n")
                    return True
                else:
                    logging.error(f"ERROR: Could not set {channel} to {output}")
                    return False
            except Exception as e:
                raise Exception(f"ERROR: Failed to set output channel due to error: {e}")

    def set_operation_mode(self, oper):
        """
        ``This function selects channel operation mode for the Siglent SPD3303X PSU.
        Parameters {0|1|2} mean independent, series and parallel respectively.
        Command format: OUTPut:TRACK {0|1|2} ; e.g.: OUTPut:TRACK 0`` \n
        :param oper: `int` :  Operation mode out of 0|1|2 -> {Independent|Series|Parallel} \n
        :return: `bool` : True or False or raises Error
        """
        modes = ['Independent', 'Series', 'Parallel']
        sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
        if sys_err == '+0, No error':
            try:
                self.psu.write(f'OUTPut:TRACK {oper}')
                time.sleep(1)
                sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
                if sys_err == '+0, No error':
                    logging.info(f": Operation mode Set to : {modes[oper]} \n")
                    return True
                else:
                    logging.error(f"ERROR: Could not set to {modes[oper]}")
                    return False
            except Exception as e:
                raise Exception(f"ERROR: Failed to set operation mode due to error: {e}")

    def set_voltage(self, channel, volt_in):
        """
        ``This function sets the output voltage for the Siglent SPD3303X PSU`` \n
        :param volt_in: `int` : Voltage in the range of 0-1200 Volts \n
        :param channel: `str` : Output channel out of 2 (CH1, CH2) \n
        :return: `bool` : True or raises Error
        """
        sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
        if sys_err == '+0, No error':
            try:
                if self.channel_selection(channel):
                    self.psu.write(f'{channel}:VOLT {volt_in}')
                    time.sleep(2)
                    voltage = self.psu.query(f'{channel}:VOLT?')
                    time.sleep(1)
                    if voltage is not None:
                        logging.info(f": Output Voltage Set to : {voltage} Volts")
                        return True
                    else:
                        logging.error(f"ERROR: Could not set voltage")
                        return False
            except Exception as e:
                raise Exception(f"FAIL: to set Voltage : {e}")

    def measure_voltage(self, channel):
        """
        ``This function returns the output voltage of a channel`` \n
        :param channel: `str` : Selected output channel out of 2 (CH1, CH2) \n
        :returns: - `float` : Output Voltage in Volts \n
                  - `str` : System Error code
        """
        if self.psu.query(f'SYST:ERR?') == '+0, No error':
            if self.channel_selection(channel):
                get_volt = self.psu.query(f'MEAS:VOLT? {channel}')
                logging.info(f": Output Voltage: {get_volt} V on channel: {channel}")
                return float(get_volt)
        else:
            logging.info(f": System Errors: {self.psu.query(f'SYST:ERR?')}")
            return str(self.psu.query(f'SYST:ERR?'))

    def set_current(self, channel, curr_in):
        """
        ``This function selects a channel and sets the current for the Siglent SPD3303X PSU.
        Note: Works only when the PSU is in the Constant Current (CC) mode and the desired channel is ON`` \n
        :param curr_in: `int` : Current in the range of 0-2 Amps \n
        :param channel: `str` : Output channel out of 2 (CH1, CH2) \n
        :returns: `bool` : True or raises Error
        """
        sys_err = str(self.psu.query(f'SYST:ERR?', delay=1))
        if sys_err == '+0, No error':
            try:
                if self.channel_selection(channel):
                    self.psu.write(f'{channel}:CURR {curr_in}')
                    current = self.psu.query(f'{channel}:CURR?')
                    if current is not None:
                        logging.info(f": Output Current Set to : {current} Amps")
                        return True
                    else:
                        logging.error(f"FAIL: Could not set Current")
                        return False
            except Exception as e:
                raise Exception(f"ERROR: {e}")

    def measure_current(self, channel):
        """
        ``This function queries the current of a selected channel.
        Note: Works only when the PSU is in the Constant Current (CC) mode and the desired channel is ON`` \n
        :param channel: `str` Selected output channel out of 2 (CH1, CH2) \n
        :returns: - `float` : Output current in Amps \n
                  - `str` : System Error code
        """
        if self.psu.query(f'SYST:ERR?') == '+0, No error':
            if self.channel_selection(channel):
                get_curr = self.psu.query(f'MEASure:CURRent? {channel}')
                logging.info(f": Output current: {get_curr} A on channel: {channel}")
                return float(get_curr)
        else:
            logging.info(f": System Errors: {self.psu.query(f'SYST:ERR?')}")
            return str(self.psu.query(f'SYST:ERR?'))

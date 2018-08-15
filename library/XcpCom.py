import can
import logging
import sqlite3
from can.interfaces.vector import VectorBus
import struct
import re
import matplotlib.pyplot as plt
import numpy
import time


class XcpCommunicator:

    def __init__(self, channel):
        conn = sqlite3.connect('main.db')
        self.c = conn.cursor()
        self.xcp_tx_id = 0xE927F8

        # configure logging settings
        logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

        '''Open connection with Vector hardware, configure channel'''
        can.rc['interface'] = 'vector'
        can.rc['channel'] = 0
        can.rc['bitrate'] = 500000

        self.bus = VectorBus(channel=[channel], app_name='CANoe')

    def check_xcp_response(self):
        # slave to master:
        xcp_rx_id = 0x1CE9F827
        # read response
        # NOTE: add more sophisticated XCP error reporting using error array
        for recvd_msg in self.bus:
            if recvd_msg.arbitration_id == xcp_rx_id:
                return recvd_msg

    def write_xcp(self, message):
        self.bus.send(message)
        response_message = self.check_xcp_response()
        command = hex(message.data[0])

        if response_message.data[0] == 0xFF:
            # response indicates command succesful
            logging.debug('Command: {} Response: Success'.format(command))
        elif response_message.data[0] == 0xFE:
            # response indicates error, report error
            error_code = response_message.data[1]
            self.c.execute("SELECT * FROM error_array WHERE error_code=?", (error_code,))
            error_info = self.c.fetchone()
            if error_info is not None:
                logging.debug('Command: {} Response: {} {}'.format(command, error_info[1], error_info[2].strip()))
            else:
                logging.debug('Command: {} Response: {}'.format(hex(message.data[0]), hex(response_message.data[1])))
        else:
            pass

    def send_connect(self):
        xcp_connect = can.Message(arbitration_id=self.xcp_tx_id, dlc=8, extended_id=True, data=[0xFF, 0, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_connect)

    def xcp_stop(self):
        xcp_stop_daq = can.Message(arbitration_id=self.xcp_tx_id, dlc=8, extended_id=True, data=[0xFE, 0, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_stop_daq)

    def setup_daq(self, address):
        xcp_tx_id = 0xE927F8

        self.send_connect()

        # This command clears all DAQ lists
        xcp_free_daq = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=[0xD6, 0, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_free_daq)

        # allocate daq lists
        daq_count = 1
        alloc_daq_array = struct.pack('<Bxhxxxx', 0xD5, daq_count)
        xcp_alloc_daq = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=alloc_daq_array)
        self.write_xcp(xcp_alloc_daq)

        # allocate and assign ODT
        daq_list_number = 0
        odt_count = 1
        alloc_odt_array = struct.pack('<BxhBxxx', 0xD4, daq_list_number, odt_count)
        xcp_alloc_odt = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=alloc_odt_array)
        self.write_xcp(xcp_alloc_odt)

        # allocate entries and assign to specific ODT in DAQ list
        odt_number = 0
        number_of_entries = 1
        alloc_odt__entry_array = struct.pack('<BxhBBxx', 0xD3, daq_list_number, odt_number, number_of_entries)
        xcp_alloc_odt_entry = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=alloc_odt__entry_array)
        self.write_xcp(xcp_alloc_odt_entry)

        # configure DAQ lists
        # initializes the DAQ list pointer for a subsequent operation with WRITE_DAQ or READ_DAQ.
        xcp_set_daq_ptr = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=[0xE2, 0, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_set_daq_ptr)

        # en_PscActivationState, SLONG length = 4, address = 0x20080CC
        bit_offset = 0xFF  # normal data element
        element_size = 4
        address_extension = 0

        write_daq_data = struct.pack('<BBBBi', 0xE1, bit_offset, element_size, address_extension, address)
        xcp_write_daq = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=write_daq_data)
        self.write_xcp(xcp_write_daq)

        xcp_set_daq_list_mode = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True,
                                            data=[0xE0, 0, 0, 0, 1, 0, 2, 0])
        self.write_xcp(xcp_set_daq_list_mode)

        xcp_start_stop_daq_list = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True,
                                              data=[0xDE, 2, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_start_stop_daq_list)

        xcp_start_daq = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=[0xDD, 1, 0, 0, 0, 0, 0, 0])
        self.write_xcp(xcp_start_daq)

    def graph_response(self, time_delay):
        for i in range(time_delay):
            recvd_msg = self.check_xcp_response()
            y = struct.unpack('<xIxxx', recvd_msg.data)
            #y = (y[0] / 100000)
            # plt.scatter(i, y, '-')
            # plt.pause(.05)
            print(y)
            time.sleep(1)


def main():
    test_address = 0x2048468
    XCP = XcpCommunicator(0)
    XCP.setup_daq(test_address)
    XCP.graph_response(10)
    XCP.xcp_stop()


if __name__ == '__main__':
    main()

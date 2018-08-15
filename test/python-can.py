import can
import cantools
import time
import logging
import struct
from can.interfaces.vector import VectorBus



# configure logging settings
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

# load CAN dbc file
db = cantools.db.load_file(r'C:\data\Tools\CANOE\VECU_PtoPanel\dbc\VECU__FCAN.dbc')

def connect_bus(channel, filters=None):
    '''Open connect with Vector hardware, configure channel'''
    can.rc['interface'] = 'vector'
    can.rc['channel'] = 0
    can.rc['bitrate'] = 500000

    bus = VectorBus(channel=[channel], can_filters=filters, app_name='CANoe')
    logging.debug('Bus object created for ' + bus.channel_info)
    return bus

def send_xcp(bus):
    xcp_id = 0xE927F8
    data_array = [0xFF, 0, 0, 0, 0, 0, 0]
    connect = can.Message(arbitration_id=xcp_id, extended_id=True, data=data_array, dlc=8)
    bus.send(connect)

def test_pto(bus):
    f_can = connect_bus(0)
    pto_msg = db.get_message_by_name('PTO_BBM1_07')

    # create baseline data
    d = {}
    for signal in pto_msg.signals:
        d[signal.name] = 0

    # set enable signal true
    d['SPN980_EngPGoveEnaSwi'] = 0
    pto_data = pto_msg.encode(d)

    print('start broadcast of ' + str(hex(pto_msg.frame_id)))

    msg = can.Message(arbitration_id=pto_msg.frame_id, dlc=8, extended_id=True, data=pto_data)
    task = bus.send_periodic(msg, pto_msg.cycle_time/1000)

    for i in range(5):
        time.sleep(1)

        d['SPN980_EngPGoveEnaSwi'] = 1
        pto_data = pto_msg.encode(d)
        msg.data = pto_data
        task.modify_data(msg)
        time.sleep(1)

        d['SPN980_EngPGoveEnaSwi'] = 0
        pto_data = pto_msg.encode(d)
        msg.data = pto_data
        task.modify_data(msg)
        time.sleep(1)

def xcp_test():
    # connect to can2
    vcan2 = connect_bus(0)
    xcp_tx_id = 0xE927F8
    xcp_rx_id = 0x1CE9F827

    notifier = can.Notifier(vcan2, [can.Printer()])


    # create master to slave message
    xcp_message = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True, data=[0xFF, 0, 0, 0, 0, 0, 0, 0])


def pack_address():
    address = 0x20080CC

    array = struct.pack('<ih', address, 0)

    print(array)



bus = connect_bus(1)
test_pto(bus)


# for i in range(10):
#     new_msg = bus.recv()
#     new_msg_id = hex(new_msg.arbitration_id)
#     dbc_msg = db.get_message_by_frame_id(int(new_msg_id, 16))
#     logging.debug(dbc_msg.name + ' ' + str(new_msg.timestamp))



















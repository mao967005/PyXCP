import can
from can.interfaces.vector import VectorBus
import time
import threading
import logging

# configure logging settings
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')


class DoCan:
    def __init__(self, channel):
        """Open connection with Vector hardware on selected channel,
        channel is 0 based"""
        xcp_rx_id = 0x1CE9F827
        can_filters = [{"can_id": 0x1CE9F827, "can_mask": 0x0, "extended": True}]
        self.bus = VectorBus(channel=[channel], app_name='CANoe', can_filters=can_filters)

        # can_filters = [{"can_id": xcp_rx_id, "can_mask": 0xFFFFFFFF, "extended": True}]
        # self.bus.set_filters(can_filters)

        # self.reader = can.BufferedReader()
        self.notifier = can.Notifier(self.bus, [can.BufferedReader()])

    def connect(self):
        xcp_tx_id = 0xE927F8
        xcp_connect = can.Message(arbitration_id=xcp_tx_id, dlc=8, extended_id=True,
                                  data=[0xFF, 0, 0, 0, 0, 0, 0, 0])
        self.bus.send(xcp_connect)

    def print_latest(self):
        msg = self.notifier.listeners[0].get_message()
        print('from latest {}'.format(msg))

    def cyclic_thread(self, ID):
        my_lock = threading.Lock()
        pto_data = [0]
        pto_msg = can.Message(arbitration_id=ID, dlc=1, extended_id=True, data=pto_data)
        task = can.broadcastmanager.ThreadBasedCyclicSendTask(self.bus, my_lock, pto_msg, .01)
        task.start()
        return task

    @staticmethod
    def modify(thread):
        pto_data = [1]
        pto_msg = can.Message(arbitration_id=0x18fef0fe, dlc=1, extended_id=True, data=pto_data)
        thread.modify_data(pto_msg)


def main():
    init_can = DoCan(0)
    # init_can.connect()
    # time.sleep(.5)
    # init_can.print_latest()

    pto_thread = init_can.cyclic_thread(0x18fef0fe)
    time.sleep(5)
    init_can.modify(pto_thread)
    time.sleep(5)

    # for message in init_can.bus:
    #     print(message)

if __name__ == '__main__':
    main()

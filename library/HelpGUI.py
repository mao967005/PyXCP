import can
import cantools
import webbrowser
import sqlite3
import os
import threading
from can.interfaces.vector import VectorBus


class AssistGUI:
    def __init__(self):
        self.db = cantools.db.load_file('can_database.dbc')

        # connect to sqlite db, used for backbone of tool
        self.conn = sqlite3.connect('main.db')
        self.c = self.conn.cursor()

    @staticmethod
    def open_documentation():
        webbrowser.open_new('.\\doc\\help.pdf')

    def start_pto_trans(self, state):
        pto_msg = self.db.get_message_by_name('PTO')
        # create baseline data
        d = {}
        for signal in pto_msg.signals:
            d[signal.name] = 0

        print('Start broadcast of {}'.format(hex(pto_msg.frame_id)))
        msg = can.Message(arbitration_id=pto_msg.frame_id, dlc=pto_msg.length, extended_id=True, data=pto_data)

        print(state)
        # bus = VectorBus(channel=[0], app_name='CANoe')
        # bus.send_periodic(msg, pto_msg.cycle_time*.001, 10)


        # set enable signal true
        d['EnableSwitch'] = 0
        pto_data = pto_msg.encode(d)

    def parse_a2l(self, file_name):
        """This method parses a .A2L file into a db for later use"""

        main_list = []
        measurement_list = []

        # remove existing table
        try:
            self.c.execute('DROP TABLE measurements')
        except:
            pass

        #self.c.execute('DROP TABLE characteristics')

        # create measurement table
        self.c.execute('''CREATE TABLE measurements (name
                text, data_type text, memory_address int
                  )''')

        # self.c.execute('''CREATE TABLE characteristics (name
        #         text, data_type text, memory_address int
        #           )''')

        # loop through a2l and build database of names and addresses
        with open(file_name) as f:
            for line in f:
                if '/begin MEASUREMENT' in line:
                    [*place_holder, label] = line.split()
                    measurement_list.append(label)
                elif '/* data type */' in line:
                    data_type, *place_holder = line.split()
                elif 'ECU_ADDRESS' in line:
                    place_holder, address = line.split()
                    main_list.append([label, data_type, address])

        self.c.executemany('INSERT INTO measurements VALUES (?,?,?)', main_list)
        self.conn.commit()
        #
        # self.c.execute("SELECT * FROM measurements WHERE error_code=?", (error_code,))
        # measurement_list = self.c.fetchone()
        return measurement_list

    def find_address_from_name(self, name):
        self.c.execute("SELECT * FROM measurements WHERE name=?", (name,))
        result = self.c.fetchone()
        return result

    @staticmethod
    def test_class():
        test = AssistGUI()
        test.parse_file('ASAM.A2L')
        result = test.find_address_from_name('en_ScsaEscRemSetSwCommandSetIncr')
        print(result)


def main():
    obj = AssistGUI()
    obj.test_class()

if __name__ == '__main__':
    main()

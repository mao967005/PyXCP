import cantools

db = cantools.db.load_file(r'C:\data\Tools\CANOE\VECU_PtoPanel\dbc\VECU__FCAN.dbc')


message = db.get_message_by_name('PTO_BBM_27')

data = message.encode({'SPN187_PoweTakeofSeSpee': 50})

print(data)
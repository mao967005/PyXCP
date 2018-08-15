import sqlite3

def create_db():
    file = open('xcp_error_matrix.csv')
    c.execute('''CREATE TABLE error_array (error_code
            int, name text, description text
              )''')
    main_list = []
    for line in file:
        code, name, desc = line.split(',')
        main_list.append([int(code, 16), name, desc])
    c.executemany('INSERT INTO error_array VALUES (?,?,?)', main_list)
    conn.commit()

conn = sqlite3.connect('xcp_error.db')
c = conn.cursor()

create_db()


# error_code = hex(0x2a)
#
#
# c.execute("SELECT * FROM error_array WHERE error_code=?", (error_code,))
# data = c.fetchone()
# print(data)

conn.close()

import sys
from datetime import datetime
from net_operations.lib.funcs import generate_from_template
from net_operations.lib.classes.NetOperations import NetOperations


def hw_report_gen(report_func, template):

    if sys.argv[1]:
        ip = sys.argv[1]
    else:
        ip = input('Введите IP-адрес устройства: ')
    vendor = "huawei"

    conn = NetOperations(ip, vendor)
    try:
        conn.establish_connection()
        report_dic = report_func(conn)
        report_str = generate_from_template(template, report_dic)
        time = str(datetime.now()).replace(' ', '_').replace(':', '.')
        filename = f'{time}_{ip}.md'
        with open(filename, 'w') as dst:
            dst.write(report_str)
        print(f'Report for {ip} saved as {filename}.')
    except Exception as error:
        print('Something gone wrong.')
        print(f'Error is "{error}"')

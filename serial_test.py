import serial
import sys
from time import sleep


class ButtonIDs(object):
    PWR = b'0\n'
    UP = b'1\n'
    DWN = b'2\n'


SER = serial.Serial(port='/dev/cu.usbserial-AH05IQM1', baudrate=9600)
MIN_TEMP = 65
MAX_TEMP = 85
CUR_TEMP = 75
DEG = u'\N{DEGREE SIGN}'


RESPONSE_MAP = {
    'd': ButtonIDs.DWN,
    'down': ButtonIDs.DWN,
    'dwn': ButtonIDs.DWN,
    '-': ButtonIDs.DWN,
    'u': ButtonIDs.UP,
    'up': ButtonIDs.UP,
    '+': ButtonIDs.UP,
    'power': ButtonIDs.PWR,
    'pwr': ButtonIDs.PWR,
}

SPECIAL_OPS = {
    'max': MAX_TEMP,
    'min': MIN_TEMP,
}


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        loop()
    else:
        process_response(args[0])

    sys.exit(0)


def setup():
    global CUR_TEMP

    for _ in range(4):
        click(ButtonIDs.DWN)

    CUR_TEMP = 65 # Set to lowest temp


def loop():
    setup()
    response = ''
    quit_terms = ('q', 'quit')

    while response.lower() not in quit_terms:
        print('\nCurrent Temp: {}{}F'.format(CUR_TEMP, DEG))
        response = input('Command: ')
        if response.lower() not in quit_terms:
            process_response(response)


def reset():
    set_temp(MAX_TEMP)
    set_temp(MIN_TEMP)


def process_response(response):
    arg = response.lower()

    if arg.isnumeric():
        reset()
        set_temp(int(arg))
        return
    if arg in SPECIAL_OPS.keys():
        set_temp(SPECIAL_OPS[arg])
        return
    
    op = RESPONSE_MAP.get(arg, lambda: '')
    if can_execute(op):
        click(op)
        update_temp(response)
    else:
        print('\nInvalid command.')


def set_temp(temp):
    corrected_temp = int(temp / 5) * 5

    while CUR_TEMP > corrected_temp and can_dec():
        click(ButtonIDs.DWN)
        update_temp('-')
    while CUR_TEMP < corrected_temp and can_inc():
        click(ButtonIDs.UP)
        update_temp('+')



def can_dec(op=ButtonIDs.DWN):
    return op == ButtonIDs.DWN and CUR_TEMP > MIN_TEMP


def can_inc(op=ButtonIDs.UP):
    return op == ButtonIDs.UP and CUR_TEMP < MAX_TEMP


def can_execute(op):
    return can_dec(op) or can_inc(op)


def update_temp(response):
    global CUR_TEMP

    arg = response.lower()
    op = RESPONSE_MAP[arg]

    if can_dec(op):
        CUR_TEMP -= 5
    if can_inc(op):
        CUR_TEMP += 5


def click(btn_id):
    SER.write(btn_id)
    sleep(0.2)


if __name__ == '__main__':
    main()
import threading
import time


def pri(thread):
    while True:
        print("[ INFO ] Hello ", thread)
        time.sleep(1)


t1 = threading.Thread(target=pri, args=('t1',))
t1.start()
t1 = threading.Thread(target=pri, args=('t2',))
t1.start()

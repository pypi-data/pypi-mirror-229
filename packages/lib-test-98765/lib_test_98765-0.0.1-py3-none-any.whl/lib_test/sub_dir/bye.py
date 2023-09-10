import time

class Bye:
    def run(self):
        my_str = 'Bye'
        for char in my_str:
            print(char, end=' ')
            time.sleep(1)
        print('')
import time

class Hello:
    def __init__(self):
        pass

    def run(self):
        my_str = 'hello'
        for char in my_str:
            print(char, end=' ')
            time.sleep(1)
        print('')
#それぞれの操作にどれだけ時間がかかるか計測する

from time import  monotonic,sleep

def timer():
    start=monotonic()

    def inner(message):
        print(f'{message}:{monotonic()-start:.2f}')

    return inner


if __name__=='__main__':
    t=timer()
    t('hello world')
    sleep(3)
    t('hello world2')
    sleep(2)
    t('hello world3')
    
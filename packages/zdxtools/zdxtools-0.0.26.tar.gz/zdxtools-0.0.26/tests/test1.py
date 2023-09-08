from pypi_update.src.zdxtools.dx_tools import decorator
from pypi_update.src.zdxtools.dx_tools import spider_tools
import time


class a :
    @decorator.ExceptionD
    def test(self):
        data = {
            'a':1,
            '222':'2',
            'getsig':'213123',
        }
        int(data)
    def test1(self):

        print(spider_tools.return_header(choice='Chrome'))


if __name__ == '__main__':
    b = a()
    b.test1()
import signal


class Terminator:
    def __init__(self):
        signal.signal(signal.SIGINT, self.__do_exit)
        signal.signal(signal.SIGTERM, self.__do_exit)

        self.__exit = False

    @property
    def exit(self) -> bool:
        return self.__exit

    def __do_exit(self):
        self.__exit = True

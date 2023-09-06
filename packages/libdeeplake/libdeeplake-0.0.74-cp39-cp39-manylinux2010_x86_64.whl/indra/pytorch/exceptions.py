class UpcastExceptionWrapper(Exception):
    def __init__(self, message: str = "", index: int = 0, offset: int = 0):
        self.message = message
        self._index = index
        self._offset = offset

    def __str__(self) -> str:
        return f"UpcastExceptionWrapper {self.message} index {self.index} offset {self.offset}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value


class TransformExceptionWrapper(Exception):
    def __init__(self, message: str = "", index: int = 0, offset: int = 0):
        self.message = message
        self._index = index
        self._offset = offset

    def __str__(self) -> str:
        return f"TransformExceptionWrapper {self.message} index {self.index} offset {self.offset}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value


class CollateExceptionWrapper(Exception):
    def __init__(self, message: str = "", index: int = 0, offset: int = 0):
        self.message = message
        self._index = index
        self._offset = offset

    def __str__(self) -> str:
        return f"CollateExceptionWrapper {self.message} index {self.index} offset {self.offset}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value


class StopChildProcess:
    pass

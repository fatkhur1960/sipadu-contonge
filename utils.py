from PyQt5.QtCore import QRunnable, pyqtSignal, QObject

from bridge import BridgeApi


class UploadThread(QRunnable):
    data_uploaded = pyqtSignal(object)
    data_uploading = pyqtSignal(object)

    def __init__(self, target, *args):
        super().__init__()
        self.target = target
        self.args = args

    def run(self):
        self.target(*self.args)


class UploadWorker(QObject):
    data_uploaded = pyqtSignal(object)
    data_uploading = pyqtSignal(object)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, api: BridgeApi, data):
        super().__init__()
        self.data = data
        self.api = api

    def run(self):
        for i, d in enumerate(self.data):
            self.data_uploading.emit((i, "#c8b900", "UPLOADING"))
            res = self.api.upload(d)
            if res:
                self.data_uploaded.emit((i, "#087f23", "UPLOADED"))
            else:
                self.data_uploaded.emit((i, "#ba000d", "FAILED"))
            self.progress.emit((i + 1)/len(self.data)*100)

        self.finished.emit()


class ParserWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, file_path, parser, table):
        super().__init__()
        self.file_path = file_path
        self.parser = parser
        self.table = table

    def run(self):
        self.parser.parse_file(self.file_path, self.table)
        self.finished.emit()


class LoginWorker(QObject):
    login_finished = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, api, username, password, ty):
        super().__init__()
        self.api = api
        self.username = username
        self.password = password
        self.ty = ty

    def run(self):
        result = self.api.login(self.username, self.password, self.ty)
        self.login_finished.emit(result)
        self.finished.emit()

import os
import stat
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject

from app.utils.bridge import BridgeApi
from app.utils.photo_cropper import PhotoCropper
from app.utils.table_headers import EXCEL_HEADERS


class UploadThread(QRunnable):
    data_uploaded = pyqtSignal(object)
    data_uploading = pyqtSignal(object)

    def __init__(self, target, *args):
        super().__init__()
        self.target = target
        self.args = args

    def run(self):
        self.target(*self.args)


class ImportExcelWorker(QObject):
    finished = pyqtSignal()
    data_loaded = pyqtSignal(object)
    data_load_failed = pyqtSignal(str)
    data_length_loaded = pyqtSignal(int)
    progress = pyqtSignal(int)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        import pandas as pd
        import json

        dataframe = pd.read_excel(self.file_path)
        df = dataframe[dataframe['Makesta'] == 'sudah'] 
        # verify excel file columns header
        imported_headers = list(df.columns)
        imported_headers[21] = "Cbp/Kpp"
        if imported_headers != EXCEL_HEADERS:
            self.data_load_failed.emit("Format file excel tidak valid")
            return
        
        df.fillna("", inplace=True)
        df = df.astype(str)
        result = df.to_json(orient="table")
        parsed = json.loads(result)
        data = [list([x for x in i.values()][1:]) for i in parsed['data']]

        data_length = len(data)
        self.data_length_loaded.emit(data_length)

        for r, rows in enumerate(data):
            self.data_loaded.emit((r, rows))
            self.progress.emit((r + 1)/data_length*100)
            
        self.finished.emit()


class ImportPhotoWorker(QObject):
    finished = pyqtSignal()
    photo_cropped = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self, payloads, photos_dir, crop):
        super().__init__()
        self.payloads = payloads
        self.photos_dir = photos_dir
        self.crop = crop

    def run(self):
        cropper = PhotoCropper()
        cropped_dir = os.path.join(self.photos_dir, 'cropped')
        obj = os.scandir(self.photos_dir)
        files = []

        isExist = os.path.exists(cropped_dir)
        if not isExist:
            os.makedirs(cropped_dir)
            st = os.stat(cropped_dir)
            os.chmod(cropped_dir, st.st_mode | stat.S_IREAD | stat.S_IWRITE)

        for entry in obj:
            if entry.is_file() and entry.name.lower().endswith('.jpg'):
                files.append(entry.name)

        task_count = len(files) + len(self.payloads)

        if self.crop:
            for i, filename in enumerate(files):
                cropper.crop_photo((self.photos_dir, filename), cropped_dir)
                self.progress.emit((i + 1)/task_count*100)

            for i, data in enumerate(self.payloads):
                file_photo = os.path.join(
                    cropped_dir, 'cropped_{}.jpg'.format(data['nik']))
                if os.path.exists(file_photo):
                    self.photo_cropped.emit((i, file_photo))

                self.progress.emit((i + len(files) + 1)/task_count*100)
        else:
            for i, data in enumerate(self.payloads):
                file_photo = os.path.join(
                    self.photos_dir, '{}.jpg'.format(data['nik']))
                if os.path.exists(file_photo):
                    self.photo_cropped.emit((i, file_photo))

                self.progress.emit((i + 1)/(task_count-len(files))*100)

        self.finished.emit()


class UploadWorker(QObject):
    data_uploaded = pyqtSignal(object)
    data_uploading = pyqtSignal(object)
    data_not_uploaded = pyqtSignal(object)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, api: BridgeApi, data):
        super().__init__()
        self.data = data
        self.api = api

    def run(self):
        data_count = len(self.data)
        for i, d in enumerate(self.data):
            if d['status'] in ['UPLOADED', 'UPLOADING']:
                self.data_uploaded.emit((i, "#087f23", "SKIPPED"))
                self.progress.emit((i + 1)/data_count*100)
                continue

            self.data_uploading.emit((i, "#c8b900", "UPLOADING"))
            uploaded, skipped = self.api.upload(d)
            if uploaded and not skipped:
                self.data_uploaded.emit((i, "#087f23", "UPLOADED"))
            elif uploaded and skipped:
                self.data_uploaded.emit((i, "#f57f17", "EXIST"))
            else:
                self.data_not_uploaded.emit((i, "#b71c1c", "FAILED"))
            self.progress.emit((i + 1)/data_count*100)

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

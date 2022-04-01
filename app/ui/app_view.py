import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor

from app.utils.bridge import BridgeApi
from app.utils.photo_cropper import PhotoCropper
from app.utils.table_util import TableUtil
from app.utils.table_headers import TABLE_HEADERS
from app.utils.utils import ImportPhotoWorker, LoginWorker, UploadWorker


class AppView(QWidget):
    def __init__(self):
        super().__init__()
        self.bridge = BridgeApi()
        self.tableUtil = TableUtil()
        self.cropper = PhotoCropper()

        self.title = 'Sipadu Contonge'
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        self.payloads = []

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerWindow()

        self.createLoginForm()
        self.createInfoForm()
        self.createTable()

        self.formWidget2.setDisabled(True)

        self.layout = QVBoxLayout()

        hLayout = QHBoxLayout()
        # hLayout.setColumnMinimumWidth(2, 100)
        hLayout.addWidget(self.formWidget, 1)
        hLayout.addWidget(self.formWidget2, 1)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.pbar.setVisible(False)

        self.addRowBtn = QPushButton("Tambahkan Row", self)
        self.addRowBtn.setGeometry(30, 40, 200, 25)
        self.addRowBtn.clicked.connect(self.addTableRow)

        self.removeRowBtn = QPushButton("Hapus Row", self)
        self.removeRowBtn.setGeometry(30, 40, 200, 25)
        self.removeRowBtn.clicked.connect(self.removeTableRow)
        self.removeRowBtn.setStyleSheet("background-color: red")

        self.btnUpload = QPushButton('Upload Anggota', self)
        self.btnUpload.setVisible(False)
        self.btnUpload.setStyleSheet("background-color: #006978")
        self.btnUpload.clicked.connect(self.uploadAnggota)

        self.groupBtn = QHBoxLayout()
        self.groupBtn.addWidget(self.addRowBtn)
        self.groupBtn.addWidget(self.removeRowBtn)
        self.groupBtn.addWidget(self.btnUpload)
        # self.addRowBtn.setVisible(False)

        self.addRowBtn.setDisabled(True)
        self.removeRowBtn.setDisabled(True)
        self.tableWidget.setDisabled(True)

        footer = QLabel(self)
        footer.setOpenExternalLinks(True)
        footer.setText(
            "Sipadu Contonge v1.1.0 - Made with <i style='color: red;'>❤️</i> by <a href='https://instagram.com/fatkhur.py'>@fatkhur.py</a>")

        self.layout.addLayout(hLayout)
        self.layout.addLayout(self.groupBtn)
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.pbar)
        self.layout.addWidget(footer)
        self.setLayout(self.layout)

        self.checkSeason()
        self.show()

    def checkSeason(self):
        self.bridge.load_cookies()
        if self.bridge.authorized:
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.org.setEnabled(False)
            self.loginBtn.setText("Log Out")
            self.loginBtn.setStyleSheet("background-color: red")
            self.loginBtn.clicked.disconnect(self.onLogin)
            self.loginBtn.clicked.connect(self.logout)
            self.doAfterLogin()
            self.loginBtn.setDisabled(False)
            self.formWidget2.setDisabled(False)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createLoginForm(self):
        self.formWidget = QGroupBox("Login Info")
        form = QVBoxLayout()
        self.formWidget.setBaseSize(200, 200)
        self.formWidget.setLayout(form)
        form.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.username = QLineEdit(self)
        usernameLabel = QLabel("Username", self)
        usernameLabel.setBuddy(self.username)
        self.username.resize(100, 40)
        usernameLabel.move(33, 20)
        form.addWidget(usernameLabel)
        form.addWidget(self.username)

        self.password = QLineEdit(self)
        passwordLabel = QLabel("Password", self)
        passwordLabel.setBuddy(self.password)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.move(20, 20)
        self.password.resize(280, 40)
        form.addWidget(passwordLabel)
        form.addWidget(self.password)

        self.org = QComboBox(self)
        orgLabel = QLabel("Tipe", self)
        orgLabel.setBuddy(self.org)
        self.org.addItems(['IPNU', 'IPPNU'])
        # org.move(20, 20)
        form.addWidget(orgLabel)
        form.addWidget(self.org)

        self.loginBtn = QPushButton('Masuk', self)
        self.loginBtn.move(20, 80)
        self.loginBtn.setStyleSheet("background-color: #006978")
        form.addWidget(self.loginBtn)
        self.loginBtn.clicked.connect(self.onLogin)

    def createInfoForm(self):
        self.formWidget2 = QGroupBox("Kepengurusan")
        form = QVBoxLayout()
        self.formWidget2.setBaseSize(200, 200)
        self.formWidget2.setLayout(form)
        form.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.pac = QComboBox(self)
        pacLabel = QLabel("Anak Cabang", self)
        pacLabel.move(0, 0)
        pacLabel.setBuddy(self.pac)
        self.pac.move(10, 10)
        form.addWidget(pacLabel)
        form.addWidget(self.pac)

        self.rk = QComboBox(self)
        rkLabel = QLabel("Ranting/Komisariat", self)
        rkLabel.setBuddy(self.rk)
        self.rk.move(20, 20)
        form.addWidget(rkLabel)
        form.addWidget(self.rk)

        self.file = QPushButton('Import File Excel', self)
        self.file.move(20, 80)
        self.file.setStyleSheet("background-color: #004ba0")
        fileLabel = QLabel("Data Anggota", self)
        fileLabel.setBuddy(self.file)
        form.addWidget(fileLabel)
        form.addWidget(self.file)
        self.file.clicked.connect(self.selectFile)

        self.setDisabledGroupCmb(True)

        self.importPFolderBtn = QPushButton("Import Foto", self)
        self.importPFolderBtn.setGeometry(30, 40, 200, 25)
        self.importPFolderBtn.clicked.connect(self.importPFolder)
        self.importPFolderBtn.setStyleSheet("background-color: #006978")
        self.importPFolderBtn.setVisible(False)
        form.addWidget(self.importPFolderBtn)

        self.enableCrop = QCheckBox("Crop Foto Otomatis", self)
        self.enableCrop.setChecked(True)
        self.enableCrop.setHidden(True)
        form.addWidget(self.enableCrop)

    # Create table
    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(len(TABLE_HEADERS))
        self.tableWidget.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)

    def selectFile(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Data Anggota", "", "Excel Files (*.xlsx)")
        if self.file_path:
            self.tableWidget.clearContents()
            self.formWidget2.setDisabled(True)
            self.tableUtil.parseFile(self.file_path, self.tableWidget)
            self.formWidget2.setDisabled(False)
            self.btnUpload.setVisible(True)
            self.fillTableData()

    def fillTableData(self):
        for r in range(self.tableWidget.rowCount()):
            pac = self.tableWidget.cellWidget(r, 1)
            rk = self.tableWidget.cellWidget(r, 2)
            pac.addItem('-- Pilih Anak Cabang --')
            pac.addItems([p['name'] for p in self.bridge.pacs])
            pac.currentIndexChanged.connect(
                lambda idx, rk=rk:
                    self.fillTableRkItems(idx, rk)
            )

            if len(self.bridge.pacs) == 1:
                pac.setDisabled(True)
                rk.addItems(
                    [x['name'] for x in self.bridge.p_rks if x['id_pac'] == self.bridge.pacs[0]['id']])
            else:
                rk.setDisabled(True)

        self.populateData()
        self.setDisabledGroupCmb(False)
        self.btnUpload.setVisible(True)
        self.importPFolderBtn.setVisible(True)
        self.enableCrop.setHidden(False)

    def importPFolder(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        photos_folder = QFileDialog.getExistingDirectory(
            self, "Pilih Folder Berisi Foto Anggota")
        if photos_folder:
            self.pbar.setVisible(True)
            self.formWidget2.setDisabled(True)
            self.setDisabledGroupBtn(True)

            self.thread = QThread()
            self.worker = ImportPhotoWorker(
                self.payloads, photos_folder, self.enableCrop.isChecked())
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.progress.connect(self.setUploadProgress)
            self.worker.photo_cropped.connect(self.fillAnggotaPhoto)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(lambda: self.pbar.setVisible(False))
            self.thread.finished.connect(lambda: self.pbar.setValue(0))
            self.thread.finished.connect(
                lambda: self.formWidget2.setDisabled(False))
            self.thread.finished.connect(
                lambda: self.showMessage("Foto berhasil diimport"))
            self.thread.finished.connect(
                lambda: self.setDisabledGroupBtn(False))
            self.thread.finished.connect(self.populateData)
            self.thread.start()

    def onLogin(self):
        self.loginBtn.setDisabled(True)
        username = self.username.text()
        password = self.password.text()
        if self.org.currentText() == 'IPPNU':
            ty = 0
        else:
            ty = 1

        self.thread = QThread()
        self.worker = LoginWorker(self.bridge, username, password, ty)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.login_finished.connect(self.onLoginFinished)

        self.thread.start()

    def onLoginFinished(self, result):
        msg = QMessageBox()
        status, msg_text = result

        if status:
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.org.setEnabled(False)
            self.loginBtn.setText("Log Out")
            self.loginBtn.setStyleSheet("background-color: red")
            self.loginBtn.clicked.disconnect(self.onLogin)
            self.loginBtn.clicked.connect(self.logout)
            self.doAfterLogin()
            self.loginBtn.setDisabled(False)
        else:
            self.loginBtn.setDisabled(False)

        self.formWidget2.setDisabled(not status)

        msg.setText(msg_text)
        msg.exec_()

    def doAfterLogin(self):
        # set Pac Values
        self.addRowBtn.setDisabled(False)
        self.removeRowBtn.setDisabled(False)
        self.tableWidget.setDisabled(False)
        self.pac.addItem("-- Pilih Anak Cabang --")
        for p in self.bridge.pacs:
            self.pac.addItem(p['name'])

        if len(self.bridge.pacs) == 1:
            self.pac.setCurrentIndex(1)
            self.pac.setEnabled(True)
            self.rk.setEnabled(True)

            # set Ranting/Komisariat Values
            for rk in self.bridge.p_rks:
                self.rk.addItem(rk['name'])
        else:
            self.pac.activated.connect(self.updateRkItems)
            self.rk.setEnabled(False)

    def logout(self):
        self.pac.clear()
        self.rk.clear()
        self.addRowBtn.setDisabled(True)
        self.removeRowBtn.setDisabled(True)
        self.tableWidget.setDisabled(True)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.username.setEnabled(True)
        self.password.setEnabled(True)
        self.org.setEnabled(True)
        self.loginBtn.setText("Masuk")
        self.loginBtn.setStyleSheet("background-color: #006978")
        self.loginBtn.clicked.disconnect(self.logout)
        self.loginBtn.clicked.connect(self.onLogin)
        self.formWidget2.setDisabled(True)
        self.btnUpload.setVisible(False)
        self.bridge.logout()

    def setDisabledGroupBtn(self, state: bool):
        self.btnUpload.setDisabled(state)
        self.addRowBtn.setDisabled(state)
        self.removeRowBtn.setDisabled(state)
        self.loginBtn.setDisabled(state)

    def setDisabledGroupCmb(self, state):
        self.pac.setDisabled(state)
        self.rk.setDisabled(state)

    def populateData(self):
        self.payloads.clear()
        for r in range(self.tableWidget.rowCount()):
            items = {}
            ac = self.tableWidget.cellWidget(r, 1)
            rk = self.tableWidget.cellWidget(r, 2)

            if ac.currentIndex() == 0:
                ac.setStyleSheet('QComboBox{background-color: red}')
                self.btnUpload.setDisabled(True)
            else:
                ac.setStyleSheet('')
                self.btnUpload.setDisabled(False)

            if rk.currentText() == "" or rk.currentIndex() == 0:
                rk.setStyleSheet('QComboBox{background-color: red}')
                self.btnUpload.setDisabled(True)
            else:
                rk.setStyleSheet('')
                self.btnUpload.setDisabled(False)

            srk = rk.currentText()
            items["status"] = self.tableWidget.item(r, 0).text()
            items["nik"] = self.tableWidget.item(r, 3).text()
            items["nama"] = self.tableWidget.item(r, 4).text()
            items["tempat_lahir"] = self.tableWidget.item(r, 5).text()
            items["tanggal_lahir"] = self.tableWidget.cellWidget(
                r, 6).date().toString("yyyy-MM-dd")
            items["email"] = self.tableWidget.item(r, 7).text()
            items["alamat_lengkap"] = self.tableWidget.item(r, 8).text()
            items["aktif_kepengurusan"] = self.tableWidget.cellWidget(
                r, 9).currentText()
            items["jabatan"] = self.tableWidget.cellWidget(r, 10).currentText()
            items["pelatihan_formal"] = self.tableWidget.cellWidget(
                r, 11).currentText().lower()
            items["makesta"] = self.tableWidget.cellWidget(
                r, 12).currentText().lower()
            items["penyelenggara_makesta"] = self.tableWidget.item(
                r, 13).text()
            items["tempat_makesta"] = self.tableWidget.item(r, 14).text()
            items["waktu_makesta"] = self.tableWidget.cellWidget(
                r, 15).date().toString("yyyy-MM-dd")
            items["lakmud"] = self.tableWidget.cellWidget(
                r, 16).currentText().lower()
            items["penyelenggara_lakmud"] = self.tableWidget.item(r, 17).text()
            items["tempat_lakmud"] = self.tableWidget.item(r, 18).text()
            if items["lakmud"] == "sudah":
                items["waktu_lakmud"] = self.tableWidget.cellWidget(
                    r, 19).date().toString("yyyy-MM-dd")

            items["lakut"] = self.tableWidget.cellWidget(
                r, 20).currentText().lower()
            items["penyelenggara_lakut"] = self.tableWidget.item(r, 21).text()
            items["tempat_lakut"] = self.tableWidget.item(r, 22).text()
            if items["lakut"] == "sudah":
                items["waktu_lakut"] = self.tableWidget.cellWidget(
                    r, 23).date().toString("yyyy-MM-dd")

            items["status_cbp"] = self.tableWidget.cellWidget(
                r, 24).currentText().lower()
            items["nama_ayah"] = self.tableWidget.item(r, 25).text()
            items["nama_ibu"] = self.tableWidget.item(r, 26).text()
            items["pendidikan_terakhir"] = self.tableWidget.cellWidget(
                r, 27).currentText()
            items["pendidikan_sd"] = self.tableWidget.item(r, 28).text()
            items["pendidikan_smp"] = self.tableWidget.item(r, 29).text()
            items["pendidikan_sma"] = self.tableWidget.item(r, 30).text()
            items["pendidikan_pt"] = self.tableWidget.item(r, 31).text()
            items["pendidikan_nonformal"] = self.tableWidget.item(r, 32).text()
            items["no_hp"] = self.tableWidget.item(r, 33).text()
            items["fb"] = self.tableWidget.item(r, 34).text()
            items["ig"] = self.tableWidget.item(r, 35).text()
            items["twitter"] = self.tableWidget.item(r, 36).text()
            items["foto"] = self.tableWidget.item(r, 37).text()

            for rks in self.bridge.p_rks:
                if rks['name'].lower() == srk.lower():
                    items["id_pimpinan_ac"] = str(rks['id_pac'])
                    items["id_pimpinan_rk"] = str(rks['id'])
                    break

            self.payloads.append(items)

    def fillAnggotaPhoto(self, result):
        row, file_photo = result
        self.tableWidget.item(row, 37).setText(file_photo)

    def uploadAnggota(self):
        self.populateData()
        if len(self.payloads) == 0:
            self.showMessage("Tidak ada anggota untuk diupload!")
            return

        self.formWidget2.setDisabled(True)
        self.pbar.setVisible(True)
        self.setDisabledGroupBtn(True)

        self.thread = QThread()
        self.worker = UploadWorker(self.bridge, self.payloads)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.setUploadProgress)
        self.worker.data_uploading.connect(self.onAnggotaUploading)
        self.worker.data_uploaded.connect(self.onAnggotaUploaded)
        self.worker.data_not_uploaded.connect(self.onAnggotaNotUploaded)
        self.thread.finished.connect(
            lambda: self.formWidget2.setDisabled(False))
        self.thread.finished.connect(lambda: self.pbar.setVisible(False))
        self.thread.finished.connect(lambda: self.pbar.setValue(0))
        self.thread.finished.connect(
            lambda: self.showMessage("Anggota berhasil diupload"))
        self.thread.finished.connect(lambda: self.setDisabledGroupBtn(False))
        self.thread.start()

    def showMessage(self, msgText):
        msg = QMessageBox()
        msg.setText(msgText)
        msg.exec_()

    def onAnggotaUploaded(self, result):
        i, color, text = result
        target = self.tableWidget.item(i, 0)
        target.setBackground(QColor(color))
        target.setText(text)
        # time.sleep(0.8)
        # self.payloads.pop(i)
        # self.tableWidget.removeRow(i)

    def onAnggotaNotUploaded(self, result):
        i, color, text = result
        target = self.tableWidget.item(i, 0)
        target.setBackground(QColor(color))
        target.setText(text)

    def onAnggotaUploading(self, result):
        i, color, text = result
        target = self.tableWidget.item(i, 0)
        target.setBackground(QColor(color))
        target.setText(text)

    def setUploadProgress(self, value):
        self.pbar.setValue(value)

    def updateRkItems(self):
        index = self.pac.currentIndex()

        if index > 0:
            pac = self.bridge.pacs[index - 1]
            self.current_rks = [
                x for x in self.bridge.p_rks if x['id_pac'] == pac['id']]
            self.rk.clear()
            self.rk.addItem('-- Pilih Ranting/Komisariat --')
            self.rk.setEnabled(True)
            self.rk.currentIndexChanged.connect(self.updateTableRkItems)
            for rk in self.current_rks:
                self.rk.addItem(rk['name'])
        elif index == 0:
            self.rk.setDisabled(True)

        for r in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(r, 1).setCurrentIndex(index)

    def updateTableRkItems(self, rk_idx):
        for r in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(r, 2).setCurrentIndex(rk_idx)
        self.populateData()

    def fillTableRkItems(self, idx, rk):
        self.populateData()
        rk.currentIndexChanged.connect(lambda: self.populateData())
        rk.setDisabled(idx == 0)
        rk.clear()
        p = self.bridge.pacs[idx - 1]
        rk.addItem('-- Pilih Ranting/Komisariat --')
        rk.addItems(
            [x['name'] for x in self.bridge.p_rks if x['id_pac'] == p['id']])

    def fillTablePacItems(self, r):
        pac = self.tableWidget.cellWidget(r, 1)
        rk = self.tableWidget.cellWidget(r, 2)
        pac.addItem('-- Pilih Anak Cabang --')
        pac.addItems([p['name'] for p in self.bridge.pacs])
        pac.currentIndexChanged.connect(
            lambda idx, rk=rk:
                self.fillTableRkItems(idx, rk)
        )

        if len(self.bridge.pacs) == 1:
            pac.setDisabled(True)
            rk.addItems(
                [x['name'] for x in self.bridge.p_rks if x['id_pac'] == self.bridge.pacs[0]['id']])
        else:
            rk.setDisabled(True)

    def addTableRow(self):
        r = self.tableUtil.addEmptyRow(self.tableWidget)
        self.fillTablePacItems(r)
        self.btnUpload.setVisible(True)

    def removeTableRow(self):
        self.tableUtil.removeRow(self.tableWidget)

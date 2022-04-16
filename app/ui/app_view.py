from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor

from app.utils.bridge import BridgeApi
from app.utils.photo_cropper import PhotoCropper
from app.utils.table_util import TableUtil
from app.utils.table_headers import TABLE_HEADERS
from app.utils.workers import ImportExcelWorker, ImportPhotoWorker, LoginWorker, UploadWorker
import env


class AppView(QWidget):
    def __init__(self):
        super().__init__()
        self.bridge = BridgeApi()
        self.tableUtil = TableUtil()
        self.cropper = PhotoCropper()

        self.title = 'Sipadu Contonge'
        if env.app_debug:
            self.title = '[Debug] Sipadu Contonge'

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
        self.pbar.setFixedHeight(25)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.pbar.setVisible(False)
        self.pbar.setTextVisible(True)

        self.addRowBtn = QPushButton("Tambahkan Row", self)
        self.addRowBtn.setGeometry(30, 40, 200, 25)
        self.addRowBtn.clicked.connect(self.addTableRow)

        self.removeRowBtn = QPushButton("Hapus Row", self)
        self.removeRowBtn.setGeometry(30, 40, 200, 25)
        self.removeRowBtn.clicked.connect(self.removeTableRow)
        self.removeRowBtn.setProperty('class', 'danger-btn')

        self.uploadBtn = QPushButton('Upload Anggota', self)
        self.uploadBtn.setVisible(False)
        self.uploadBtn.setProperty('class', 'primary-btn')
        self.uploadBtn.clicked.connect(self.uploadAnggota)

        self.groupBtn = QHBoxLayout()
        # self.groupBtn.addWidget(self.addRowBtn)
        # self.groupBtn.addWidget(self.removeRowBtn)
        self.groupBtn.addWidget(self.uploadBtn)
        # self.addRowBtn.setVisible(False)

        self.addRowBtn.setDisabled(True)
        self.removeRowBtn.setDisabled(True)
        self.tableWidget.setDisabled(True)

        footer = QLabel(self)
        footer.setOpenExternalLinks(True)
        footer.setText(
            f"""Sipadu Contonge v{env.version} - Made with <span style='color: red;'>❤️</span> by <a href='https://instagram.com/fatkhur.py'>@fatkhur.py</a>
             | Download Template Excel <a href='https://github.com/fatkhur1960/sipadu-contonge/raw/master/template/IPNU-Anggota-Nama_PAC-Nama_Ranting_Komsat.xlsx'>IPNU</a> dan <a href='https://github.com/fatkhur1960/sipadu-contonge/raw/master/template/IPPNU-Anggota-Nama_PAC-Nama_Ranting_Komsat.xlsx'>IPPNU</a>""")

        self.layout.addLayout(hLayout)
        self.layout.addLayout(self.groupBtn)
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.pbar)
        self.layout.addWidget(footer)
        self.setLayout(self.layout)

        if env.app_debug:
            self.checkSeason()

        self.show()

    def checkSeason(self):
        self.bridge.load_cookies()
        if self.bridge.authorized:
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.org.setEnabled(False)
            self.loginBtn.setVisible(False)
            self.logoutBtn.setVisible(True)
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

        self.loginBtn = QPushButton('Login', self)
        self.loginBtn.move(20, 80)
        self.loginBtn.setProperty('class', 'primary-btn')
        form.addWidget(self.loginBtn)
        self.loginBtn.clicked.connect(self.onLogin)

        self.logoutBtn = QPushButton('Logout', self)
        self.logoutBtn.move(20, 80)
        self.logoutBtn.setProperty('class', 'danger-btn')
        self.logoutBtn.setVisible(False)
        form.addWidget(self.logoutBtn)
        self.logoutBtn.clicked.connect(self.logout)

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
        self.file.setProperty('class', 'secondary-btn')
        fileLabel = QLabel("Data Anggota", self)
        fileLabel.setBuddy(self.file)
        form.addWidget(fileLabel)
        form.addWidget(self.file)
        self.file.clicked.connect(self.selectFile)

        self.setDisabledGroupCmb(True)

        self.importPFolderBtn = QPushButton("Import Foto", self)
        self.importPFolderBtn.setGeometry(30, 40, 200, 25)
        self.importPFolderBtn.clicked.connect(self.importPFolder)
        self.importPFolderBtn.setProperty('class', 'primary-btn')
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
        # self.tableWidget.setColumnHidden(38, True)
        for i in range(1, 38):
            self.tableWidget.setColumnWidth(i, 150)

    def selectFile(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Data Anggota", "", "Excel Files (*.xlsx)")
        if self.file_path:
            self.pbar.setVisible(True)
            self.tableWidget.clearContents()
            self.formWidget2.setDisabled(True)

            self.thread = QThread()
            self.worker = ImportExcelWorker(self.file_path)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)

            self.worker.progress.connect(self.setUploadProgress)
            self.worker.data_length_loaded.connect(
                lambda rowCount: self.tableWidget.setRowCount(rowCount))
            self.worker.data_loaded.connect(lambda data: self.tableUtil.fillRow(
                data, self.tableWidget, self.fillTablePacItems))
            self.worker.data_load_failed.connect(self.importExcelFailed)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.importExcelFinished)
            self.thread.start()

    def importExcelFinished(self):
        self.pbar.setVisible(False)
        self.pbar.setValue(0)
        self.formWidget2.setDisabled(False)
        self.populateData()
        self.setDisabledGroupCmb(False)
        self.uploadBtn.setVisible(True)
        self.importPFolderBtn.setVisible(True)
        self.enableCrop.setVisible(True)

    def importExcelFailed(self, message):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.formWidget2.setDisabled(False)
        self.pbar.setVisible(False)
        self.showMessage(message)

    def importPFolder(self):
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
        self.username.setEnabled(False)
        self.password.setEnabled(False)
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
        status, msg_text = result

        if status:
            self.org.setEnabled(False)
            self.loginBtn.setVisible(False)
            self.logoutBtn.setVisible(True)
            self.doAfterLogin()
        else:
            self.username.setEnabled(True)
            self.password.setEnabled(True)

        self.loginBtn.setDisabled(False)
        self.formWidget2.setDisabled(not status)

        self.showMessage(msg_text)

    def doAfterLogin(self):
        # set Pac Values
        self.addRowBtn.setDisabled(False)
        self.removeRowBtn.setDisabled(False)
        self.tableWidget.setDisabled(False)
        if len(self.bridge.pacs) > 1:
            self.pac.addItem("-- Pilih Anak Cabang --")

        for p in self.bridge.pacs:
            self.pac.addItem(p['name'])

        if len(self.bridge.pacs) == 1:
            # self.pac.setCurrentIndex(1)
            self.pac.setDisabled(True)
            self.rk.setEnabled(True)

            # set Ranting/Komisariat Values
            self.rk.currentIndexChanged.connect(self.updateTableRkItems)
            self.rk.addItem("-- Pilih Ranting/Komisariat --")
            for rk in self.bridge.p_rks:
                self.rk.addItem(rk['name'])
        else:
            self.rk.currentIndexChanged.connect(self.updateTableRkItems)
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
        self.logoutBtn.setVisible(False)
        self.loginBtn.setVisible(True)
        self.formWidget2.setDisabled(True)
        self.uploadBtn.setVisible(False)
        self.bridge.logout()

    def setDisabledGroupBtn(self, state: bool):
        self.uploadBtn.setDisabled(state)
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

            if ac.currentIndex() == 0 and len(self.bridge.pacs) > 1:
                ac.setStyleSheet(
                    'QComboBox{background-color: #ff8a80; color: #ffffff; border-color: #b71c1c;}')
                self.uploadBtn.setDisabled(True)
            else:
                ac.setStyleSheet('')
                self.uploadBtn.setDisabled(False)

            if rk.currentText() == "" or rk.currentIndex() == 0:
                rk.setStyleSheet(
                    'QComboBox{background-color: #ff8a80; color: #ffffff; border-color: #b71c1c;}')
                self.uploadBtn.setDisabled(True)
            else:
                rk.setStyleSheet('')
                self.uploadBtn.setDisabled(False)

            srk = rk.currentText()
            items["status"] = self.tableWidget.cellWidget(r, 0).text()
            items["nik"] = self.tableWidget.item(r, 3).text()
            items["nama"] = self.tableWidget.item(r, 4).text().upper()
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
            if items["makesta"] == "sudah":
                items["waktu_makesta"] = self.tableWidget.cellWidget(r, 15).date().toString("yyyy-MM-dd")
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
            
            phoneNum = self.tableWidget.item(r, 33)
            phoneNumVal = phoneNum.text()
            if phoneNumVal.endswith('.0'):
                phoneNumVal = '0' + phoneNumVal.replace('.0', '')
                phoneNum.setText(phoneNumVal)
            items["no_hp"] = phoneNumVal
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
            lambda: self.showMessage("Anggota selesai diupload"))
        self.thread.finished.connect(lambda: self.setDisabledGroupBtn(False))
        self.thread.start()

    def showMessage(self, msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Info")
        msg.setText(msgText)
        msg.exec_()

    def onAnggotaUploaded(self, result):
        i, color, text = result
        target = self.tableWidget.cellWidget(i, 0)
        target.setStyleSheet(f"color: {color}")
        target.setText(text)

    def onAnggotaNotUploaded(self, result):
        i, color, text = result
        target = self.tableWidget.cellWidget(i, 0)
        target.setStyleSheet(f"color: {color}")
        target.setText(text)

    def onAnggotaUploading(self, result):
        i, color, text = result
        self.tableWidget.selectRow(i)
        target = self.tableWidget.cellWidget(i, 0)
        target.setStyleSheet(f"color: {color}")
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
        rk.clear()
        rk.currentIndexChanged.connect(lambda: self.populateData())
        p = self.bridge.pacs[idx - 1]
        rk.addItem('-- Pilih Ranting/Komisariat --')
        rk.addItems(
            [x['name'] for x in self.bridge.p_rks if x['id_pac'] == p['id']])
        rk.setDisabled(False)
        self.populateData()

    def fillTablePacItems(self, r):
        pac = self.tableWidget.cellWidget(r, 1)
        rk = self.tableWidget.cellWidget(r, 2)
        if len(self.bridge.pacs) > 1:
            pac.addItem('-- Pilih Anak Cabang --')
        pac.addItems([p['name'] for p in self.bridge.pacs])
        pac.currentIndexChanged.connect(
            lambda idx, rk=rk:
                self.fillTableRkItems(idx, rk)
        )

        if len(self.bridge.pacs) == 1:
            pac.setDisabled(True)
            rk.addItem('-- Pilih Ranting/Komisariat --')
            rk.currentIndexChanged.connect(self.populateData)
            rk.addItems(
                [x['name'] for x in self.bridge.p_rks if x['id_pac'] == self.bridge.pacs[0]['id']])
        else:
            rk.setDisabled(True)

    def addTableRow(self):
        r = self.tableUtil.addEmptyRow(self.tableWidget)
        self.fillTablePacItems(r)
        self.uploadBtn.setVisible(True)
        self.populateData()

    def removeTableRow(self):
        self.tableUtil.removeRow(self.tableWidget)

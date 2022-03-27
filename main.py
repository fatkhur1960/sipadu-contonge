import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor, QIcon

from bridge import BridgeApi
from parse_excel import ExcelParser
from table_headers import TABLE_HEADERS
from utils import LoginWorker, UploadWorker


# Main Window
class App(QWidget):
    def __init__(self, api: BridgeApi):
        super().__init__()
        self.api = api

        self.parser = ExcelParser()
        self.title = 'Sipadu Contonge'
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        self.payloads = []

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        self.createLoginForm()
        self.createInfoForm()
        self.create_table()

        self.formWidget2.setDisabled(True)

        self.layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        # h_layout.setColumnMinimumWidth(2, 100)
        h_layout.addWidget(self.formWidget, 1)
        h_layout.addWidget(self.formWidget2, 1)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.pbar.setVisible(False)

        self.addRowBtn = QPushButton("Tambahkan Row", self)
        self.addRowBtn.setGeometry(30, 40, 200, 25)
        self.addRowBtn.clicked.connect(self.add_table_row)

        self.removeRowBtn = QPushButton("Hapus Row", self)
        self.removeRowBtn.setGeometry(30, 40, 200, 25)
        self.removeRowBtn.clicked.connect(self.remove_table_row)
        self.removeRowBtn.setStyleSheet("background-color: red")

        self.groupBtn = QHBoxLayout()
        self.groupBtn.addWidget(self.addRowBtn)
        self.groupBtn.addWidget(self.removeRowBtn)
        # self.addRowBtn.setVisible(False)

        self.addRowBtn.setDisabled(True)
        self.removeRowBtn.setDisabled(True)
        self.tableWidget.setDisabled(True)
        
        footer = QLabel(self)
        footer.setOpenExternalLinks(True)
        footer.setText("Sipadu Contonge v1.0.0 - Made with <i style='color: red;'>❤️</i> by <a href='https://instagram.com/fatkhur.py'>@fatkhur.py</a>")

        self.layout.addLayout(h_layout)
        self.layout.addLayout(self.groupBtn)
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.pbar)
        self.layout.addWidget(footer)
        self.setLayout(self.layout)

        self.check_session()

        # Show window
        self.show()

    def check_session(self):
        self.api.load_cookies()
        if self.api.authorized:
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.org.setEnabled(False)
            self.login_button.setText("Log Out")
            self.login_button.setStyleSheet("background-color: red")
            self.login_button.clicked.disconnect(self.on_login)
            self.login_button.clicked.connect(self.logout)
            self.do_after_login()
            self.login_button.setDisabled(False)
            self.formWidget2.setDisabled(False)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createLoginForm(self):
        self.formWidget = QGroupBox("Login Info")
        form = QVBoxLayout()
        # self.formWidget.setDisabled(True)
        self.formWidget.setBaseSize(200, 200)
        self.formWidget.setLayout(form)

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

        self.login_button = QPushButton('Masuk', self)
        self.login_button.move(20, 80)
        self.login_button.setStyleSheet("background-color: #006978")
        form.addWidget(self.login_button)
        self.login_button.clicked.connect(self.on_login)

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

        self.file = QPushButton('Pilih File', self)
        self.file.move(20, 80)
        self.file.setStyleSheet("background-color: #004ba0")
        fileLabel = QLabel("Data Anggota", self)
        fileLabel.setBuddy(self.file)
        form.addWidget(fileLabel)
        form.addWidget(self.file)
        self.file.clicked.connect(self.select_file)

        self.btnUpload = QPushButton('Upload Anggota', self)
        self.btnUpload.setVisible(False)
        self.btnUpload.setStyleSheet("background-color: #006978")
        form.addWidget(self.btnUpload)
        self.btnUpload.clicked.connect(self.upload_anggota)

    # Create table
    def create_table(self):
        self.tableWidget = QTableWidget()
        # self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(len(TABLE_HEADERS))
        self.tableWidget.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        # self.tableWidget.setColumnHidden(0, True)
        # Table will fit the screen horizontally

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Data Anggota", "", "Excel Files (*.xlsx)", options=options)
        if self.file_path:
            self.tableWidget.clearContents()
            self.formWidget2.setDisabled(True)
            self.parser.parse_file(
                self.file_path, self.tableWidget)
            self.formWidget2.setDisabled(False)
            self.btnUpload.setVisible(True)
            self.fill_table_comboboxes()

    def fill_table_comboboxes(self):
        for r in range(self.tableWidget.rowCount()):
            pac = self.tableWidget.cellWidget(r, 1)
            rk = self.tableWidget.cellWidget(r, 2)
            pac.addItem('-- Pilih Anak Cabang --')
            pac.addItems([p['name'] for p in self.api.pacs])
            pac.currentIndexChanged.connect(
                lambda idx, rk=rk:
                    self.fill_rk_table(idx, rk)
            )

            if len(self.api.pacs) == 1:
                pac.setDisabled(True)
                rk.addItems(
                    [x['name'] for x in self.api.p_rks if x['id_pac'] == self.api.pacs[0]['id']])
            else:
                rk.setDisabled(True)

    def on_login(self):
        self.login_button.setDisabled(True)
        username = self.username.text()
        password = self.password.text()
        if self.org.currentText() == 'IPPNU':
            ty = 0
        else:
            ty = 1

        self.thread = QThread()
        self.worker = LoginWorker(self.api, username, password, ty)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.login_finished.connect(self.on_login_finished)

        self.thread.start()

    def on_login_finished(self, result):
        msg = QMessageBox()
        status, msg_text = result

        if status:
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.org.setEnabled(False)
            self.login_button.setText("Log Out")
            self.login_button.setStyleSheet("background-color: red")
            self.login_button.clicked.disconnect(self.on_login)
            self.login_button.clicked.connect(self.logout)
            self.do_after_login()
            self.login_button.setDisabled(False)
        else:
            self.login_button.setDisabled(False)

        self.formWidget2.setDisabled(not status)

        msg.setText(msg_text)
        msg.exec_()

    def do_after_login(self):
        # set Pac Values
        self.addRowBtn.setDisabled(False)
        self.removeRowBtn.setDisabled(False)
        self.tableWidget.setDisabled(False)
        self.pac.addItem("-- Pilih Anak Cabang --")
        for p in self.api.pacs:
            self.pac.addItem(p['name'])

        if len(self.api.pacs) == 1:
            self.pac.setCurrentIndex(1)
            self.pac.setEnabled(True)
            self.rk.setEnabled(True)

            # set Ranting/Komisariat Values
            for rk in self.api.p_rks:
                self.rk.addItem(rk['name'])
        else:
            self.pac.activated.connect(self.change_rk_items)
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
        self.login_button.setText("Masuk")
        self.login_button.setStyleSheet("background-color: #006978")
        self.login_button.clicked.disconnect(self.logout)
        self.login_button.clicked.connect(self.on_login)
        self.formWidget2.setDisabled(True)
        self.btnUpload.setVisible(False)
        self.api.logout()

    def populate_data(self):
        self.payloads.clear()
        for r in range(self.tableWidget.rowCount()):
            items = {}
            srk = self.tableWidget.cellWidget(r, 2).currentText()
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

            if self.tableWidget.item(r, 37).text() != "":
                items["foto"] = self.tableWidget.item(r, 37).text()

            for rks in self.api.p_rks:
                if rks['name'].lower() == srk.lower():
                    items["id_pimpinan_ac"] = str(rks['id_pac'])
                    items["id_pimpinan_rk"] = str(rks['id'])
                    break

            self.payloads.append(items)

    def upload_anggota(self):
        # is_pac = self.pac.currentText()
        # is_rk = self.rk.currentText()

        self.populate_data()

        if len(self.payloads) == 0:
            msg = QMessageBox()
            msg.setText("Tidak ada anggota untuk diupload!")
            msg.exec_()
            return

        # rk_idx = self.rk.currentIndex()
        # rk = self.current_rks[rk_idx-1]

        self.formWidget2.setDisabled(True)
        self.pbar.setVisible(True)

        self.thread = QThread()
        self.worker = UploadWorker(self.api, self.payloads)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.data_uploading.connect(self.on_data_uploading)
        self.worker.data_uploaded.connect(self.on_data_uploaded)
        self.thread.finished.connect(
            lambda: self.formWidget2.setDisabled(False))
        self.thread.finished.connect(lambda: self.pbar.setVisible(False))
        self.thread.finished.connect(lambda: self.pbar.setValue(0))
        self.thread.finished.connect(lambda: self.upload_finished)
        self.thread.start()

    def upload_finished(self):
        msg = QMessageBox()
        msg.setText("Anggota berhasil diupload")
        msg.exec_()

    def on_data_uploaded(self, result):
        i, color, text = result
        target = self.tableWidget.item(i, 0)
        target.setBackground(QColor(color))
        target.setText(text)

    def on_data_uploading(self, result):
        i, color, text = result
        target = self.tableWidget.item(i, 0)
        target.setBackground(QColor(color))
        target.setText(text)

    def report_progress(self, value):
        self.pbar.setValue(value)

    def change_rk_items(self):
        index = self.pac.currentIndex()

        if index > 0:
            pac = self.api.pacs[index - 1]
            self.current_rks = [
                x for x in self.api.p_rks if x['id_pac'] == pac['id']]
            self.rk.clear()
            self.rk.addItem('-- Pilih Ranting/Komisariat --')
            self.rk.setEnabled(True)
            self.rk.currentIndexChanged.connect(self.change_rk_col)
            for rk in self.current_rks:
                self.rk.addItem(rk['name'])
        elif index == 0:
            self.rk.setDisabled(True)

        for r in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(r, 1).setCurrentIndex(index)

    def change_rk_col(self,  rk_idx):
        for r in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(r, 2).setCurrentIndex(rk_idx)

    def fill_rk_table(self, idx, rk):
        rk.setDisabled(idx == 0)
        rk.clear()
        p = self.api.pacs[idx - 1]
        rk.addItem('-- Pilih Ranting/Komisariat --')
        rk.addItems(
            [x['name'] for x in self.api.p_rks if x['id_pac'] == p['id']])

    # def fill_comboboxes(self):
    #     for r in range(self.tableWidget.rowCount()):
    #         self.add_pac_data(r)

    def add_table_row(self):
        r = self.parser.add_empty_row(self.tableWidget)
        self.add_table_pac_data(r)
        self.btnUpload.setVisible(True)

    def remove_table_row(self):
        r = self.tableWidget.currentRow()
        self.tableWidget.removeRow(r)

    def add_table_pac_data(self, r):
        pac = self.tableWidget.cellWidget(r, 1)
        rk = self.tableWidget.cellWidget(r, 2)
        pac.addItem('-- Pilih Anak Cabang --')
        pac.addItems([p['name'] for p in self.api.pacs])
        pac.currentIndexChanged.connect(
            lambda idx, rk=rk:
                self.fill_rk_table(idx, rk)
        )

        if len(self.api.pacs) == 1:
            pac.setDisabled(True)
            rk.addItems(
                [x['name'] for x in self.api.p_rks if x['id_pac'] == self.api.pacs[0]['id']])
        else:
            rk.setDisabled(True)


try:
    from ctypes import windll
    myappid = 'org.pelajarnuwsb.contonge'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == '__main__':
    basedir = os.path.dirname(__file__)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon(os.path.join(basedir, 'icon.ico')))
    ex = App(BridgeApi())
    sys.exit(app.exec())

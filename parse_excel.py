import pandas as pd
import json
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QDateEdit, QFileDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from datetime import datetime


class ExcelParser:
    def add_empty_row(self, table: QTableWidget) -> int:
        r = table.rowCount()
        table.setRowCount(r + 1)

        st = QTableWidgetItem("WAITING")
        st.setFlags(Qt.ItemFlag.ItemIsEnabled)
        table.setItem(r, 0, st)
        table.item(r, 0).setBackground(QColor("#C5C5C5"))
        table.setCellWidget(r, 1, QComboBox())
        table.setCellWidget(r, 2, QComboBox())

        for c in range(3, 6):
            table.setItem(r, c, QTableWidgetItem(""))

        dp = QDateEdit(calendarPopup=True)
        dp.setDisplayFormat("dd MMM yyyy")
        table.setCellWidget(r, 6, dp)

        for c in range(7, 9):
            table.setItem(r, c, QTableWidgetItem(""))

        kp = QComboBox()
        kp.addItems(['Anggota', 'PR', 'PK', 'PAC',
                    'PKPT', 'PC', 'PW', 'PP'])
        table.setCellWidget(r, 9, kp)

        jb = QComboBox()
        jb.addItem('Anggota')
        jb.addItem('Ketua')
        jb.addItem('Wakil Ketua')
        jb.addItem('Sekretaris')
        jb.addItem('Wakil Sekretaris')
        jb.addItem('Bendahara')
        jb.addItem('Wakil Bendahara')
        jb.addItem('Departemen Organisasi')
        jb.addItem('Departemen Kaderisasi')
        jb.addItem('Departemen Jaringan Sekolah dan Pesantren')
        jb.addItem('Departemen Dakwah')
        jb.addItem('Departemen Seni Budaya dan Olahraga')
        jb.addItem('Departemen Jaringan Komunikasi dan Informatika')
        jb.addItem('Lembaga Corp Brigade Pembangunan')
        jb.addItem('Lembaga Ekonomi Koperasi dan Kewirausahaan')
        jb.addItem('Lembaga Pers dan Penerbitan')
        jb.addItem('Lembaga Anti Narkoba')
        jb.addItem('Lembaga Komunikasi Perguruan Tinggi')
        jb.addItem('Lembaga Advokasi dan Kebijakan Publik')
        jb.addItem('Badan Student Research Center')
        jb.addItem('Badan Student Crisis Center')
        table.setCellWidget(r, 10, jb)

        pf = QComboBox()
        pf.addItems(['makesta', 'lakmud', 'lakut'])
        table.setCellWidget(r, 11, pf)

        for c in [12, 16, 20]:
            op = QComboBox()
            op.addItems(['sudah', 'belum'])
            op.setCurrentIndex(1)
            table.setCellWidget(r, c, op)

        for c in [13, 14, 15, 17, 18, 19, 21, 22, 23, 25, 26]:
            table.setItem(r, c, QTableWidgetItem(""))

        op = QComboBox()
        op.addItems(['ya', 'tidak'])
        op.setCurrentIndex(1)
        table.setCellWidget(r, 24, op)

        pnd = QComboBox()
        pnd.addItem('Tidak Ada')
        pnd.addItem('SD/Sederajat')
        pnd.addItem('SMP/Sederajat')
        pnd.addItem('SMA/Sederajat')
        pnd.addItem('D1')
        pnd.addItem('D2')
        pnd.addItem('D3')
        pnd.addItem('S1')
        pnd.addItem('S2')
        pnd.addItem('S3')
        table.setCellWidget(r, 27, pnd)

        for c in [13, 14, 17, 18, 19, 21, 22, 25, 26]:
            table.setItem(r, c, QTableWidgetItem(""))

        for c in [15, 19, 23]:
            dp = QDateEdit(calendarPopup=True)
            dp.setDisplayFormat("dd MMM yyyy")
            table.setCellWidget(r, c, dp)

        for c in range(28, 37):
            table.setItem(r, c, QTableWidgetItem(""))

        st = QTableWidgetItem("")
        st.setFlags(Qt.ItemFlag.ItemIsEnabled)
        table.setItem(r, 37, st)
        table.setColumnWidth(37, 250)
        
        fileBtn = QPushButton("Pilih Foto", table)
        fileBtn.clicked.connect(
            lambda r=r, table=table: self.select_file(r, table))
        table.setCellWidget(r, 38, fileBtn)

        return r

    def parse_file(self, file_path: str, table: QTableWidget,):
        df = pd.read_excel(file_path)
        df.fillna("", inplace=True)
        df = df.astype(str)
        result = df.to_json(orient="table")
        parsed = json.loads(result)
        data = [list([x for x in i.values()][1:]) for i in parsed['data']]

        table.setRowCount(len(data))

        for r, rows in enumerate(data):
            st = QTableWidgetItem("WAITING")
            st.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(r, 0, st)
            table.item(r, 0).setBackground(QColor("#C5C5C5"))
            table.setCellWidget(r, 1, QComboBox())
            table.setCellWidget(r, 2, QComboBox())

            st = QTableWidgetItem("")
            st.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(r, 37, st)
            
            fileBtn = QPushButton("Pilih Foto", table)
            fileBtn.clicked.connect(
                lambda r=r, table=table: self.select_file(r, table))
            table.setCellWidget(r, 38, fileBtn)

            for c, value in enumerate(rows):
                is_date, output = self.extract_date(value)
                if is_date or c == 20:
                    dp = QDateEdit(calendarPopup=True)
                    if isinstance(output, (datetime)):
                        dp.setDate(output.date())
                    dp.setDisplayFormat("dd MMM yyyy")
                    table.setCellWidget(r, c+3, dp)
                elif c == 6:
                    kp = QComboBox()
                    kp.addItems(['Anggota', 'PR', 'PK', 'PAC',
                                'PKPT', 'PC', 'PW', 'PP'])
                    kp.setCurrentText(value)
                    table.setCellWidget(r, c+3, kp)
                elif c == 7:
                    jb = QComboBox()
                    jb.addItem('Anggota')
                    jb.addItem('Ketua')
                    jb.addItem('Wakil Ketua')
                    jb.addItem('Sekretaris')
                    jb.addItem('Wakil Sekretaris')
                    jb.addItem('Bendahara')
                    jb.addItem('Wakil Bendahara')
                    jb.addItem('Departemen Organisasi')
                    jb.addItem('Departemen Kaderisasi')
                    jb.addItem('Departemen Jaringan Sekolah dan Pesantren')
                    jb.addItem('Departemen Dakwah')
                    jb.addItem('Departemen Seni Budaya dan Olahraga')
                    jb.addItem(
                        'Departemen Jaringan Komunikasi dan Informatika')
                    jb.addItem('Lembaga Corp Brigade Pembangunan')
                    jb.addItem('Lembaga Ekonomi Koperasi dan Kewirausahaan')
                    jb.addItem('Lembaga Pers dan Penerbitan')
                    jb.addItem('Lembaga Anti Narkoba')
                    jb.addItem('Lembaga Komunikasi Perguruan Tinggi')
                    jb.addItem('Lembaga Advokasi dan Kebijakan Publik')
                    jb.addItem('Badan Student Research Center')
                    jb.addItem('Badan Student Crisis Center')
                    jb.setCurrentText(value)
                    table.setCellWidget(r, c+3, jb)
                elif c == 8:
                    pf = QComboBox()
                    pf.addItems(['makesta', 'lakmud', 'lakut'])
                    pf.setCurrentText(value)
                    table.setCellWidget(r, c+3, pf)
                elif c in [9, 13, 17]:
                    op = QComboBox()
                    op.addItems(['sudah', 'belum'])
                    op.setCurrentText(value)
                    table.setCellWidget(r, c+3, op)
                elif c == 21:
                    op = QComboBox()
                    op.addItems(['ya', 'tidak'])
                    op.setCurrentText(value)
                    table.setCellWidget(r, c+3, op)
                elif c == 24:
                    pnd = QComboBox()
                    pnd.addItem('Tidak Ada')
                    pnd.addItem('SD/Sederajat')
                    pnd.addItem('SMP/Sederajat')
                    pnd.addItem('SMA/Sederajat')
                    pnd.addItem('D1')
                    pnd.addItem('D2')
                    pnd.addItem('D3')
                    pnd.addItem('S1')
                    pnd.addItem('S2')
                    pnd.addItem('S3')
                    pnd.setCurrentText(value)
                    table.setCellWidget(r, c+3, pnd)
                else:
                    table.setItem(r, c+3, QTableWidgetItem(value))

    def extract_date(self, input):
        try:
            return True, datetime.strptime(input, '%Y-%m-%d')
        except:
            return False, input

    def select_file(self, r, table):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_path, _ = QFileDialog.getOpenFileName(
            table, "Pilih Foto Anggota", "", "Image File (*.jpg)", options=options)

        if self.file_path:
            table.item(r, 37).setText(self.file_path)

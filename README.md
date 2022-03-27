# SIPADU CONTONGE
------------------
Sipadu Contonge merupakan sebuah alat untuk mempermudah para pengurus PC/PAC IPNU IPPNU untuk mengupload data anggota di website https://sipadu.or.id.

### Cara Menjalankan
1. Download `Sipadu_Contonge-Installer` di [sini](https://github.com/fatkhur1960/sipadu-contonge/releases/)
2. Buka file `Sipadu_Contonge-Installer`, Klik Install. Lalu ikuti prosesnya sampai selesai
3. Setelah proses instalasi selesai selanjutnya masukkan `username` dan `password`. Pastikan username dan password yang dimasukkan sudah benar, lalu klik tombol `Masuk`
4. Lalu pilih file excel yang sudah siap untuk diupload. Untuk template file excelnya bisa di download [IPNU](https://github.com/fatkhur1960/sipadu-contonge/raw/master/template/IPNU-Anggota-Nama_PAC-Nama_Ranting_Komsat.xlsx) dan [IPPNU](https://github.com/fatkhur1960/sipadu-contonge/raw/master/template/IPPNU-Anggota-Nama_PAC-Nama_Ranting_Komsat.xlsx). Pastikan untuk penamaan file, sesuaikan dengan format yang sudah tertera. `Contoh: IPNU-Anggota-Garung-Topengan.xlsx atau IPPNU-Anggota-Garung-Topengan.xlsx`
5. *IMPORTANT!!!* Setelah berhasil mengimport data anggota dari file excel, selanjutnya sesuaikan untuk Pimpinan Anak Cabang dan Ranting/Komisariatnya. Sesuai dengan nama file yang diimport.
6. _(Opsional)_ Bagi data anggota ranting yang sudah ada fotonya bisa dipilih satu-persatu sesuai nama anggota.
7. Terakhir, tekan tombol `Upload Anggota` sambil membaca _Basmalah_ biar tidak ada kendala waktu proses uploadnya :v.

### Untuk Proses Development
#### Bagi yang ingin berkonstribusi dalam pengembangan Sipadu Contonge, bisa menjalankan perintah sebagai berikut:
1. Pertama pastikan dulu Rekan/Rekanita menginstall Python di komputer:
    - *Linux*
    ```bash
    $ sudo apt update
    $ sudo apt install software-properties-common
    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt install python3.9 git
    ```
    - *MacOs*
    ```bash
    $ brew install python git
    ```

    - *Windows*<br/>
        - Untuk pengguna Windows bisa mengikuti tutorial di [sini](https://phoenixnap.com/kb/how-to-install-python-3-windows)
        - Untuk install git bisa mengikuti tutorial di [sini](https://www.petanikode.com/git-install/)<br/><br/>

2. Buka Terminal/Command Prompt, lalu:
```bash
$ git clone https://github.com/fatkhur1960/sipadu-contonge.git && cd sipadu-contonge
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
3. Menjalankan program:
```bash
$ python3 main.py
```

4. Build Program
```
$ make prepare && make app-build
```

### Credit by
- PC IPNU IPPNU Wonosobo [@pcipnuippnuwonosobo](https://instagram.com/pcipnuippnuwonosobo/)
- Fatkhur [@fatkhur.py](https://instagram.com/fatkhur.py)
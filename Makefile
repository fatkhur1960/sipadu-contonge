.PHONY: prepare
default: prepare

prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "SipaduContonge" main.py --noconfirm

win-prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico;." --add-data="data/haarcascade_frontalface_default.xml;data" --add-data="style/app.qss;style" -n "SipaduContonge" main.py --noconfirm

app-debug:
	pyinstaller --console --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "SipaduContonge" main.py --noconfirm

app-onefile:
	pyinstaller --onefile --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "SipaduContonge" main.py --noconfirm

app-build:
	pyinstaller "SipaduContonge.spec" --noconfirm

build-win: win-prepare app-build


clean:
	rm -rf dist
	rm -rf build
	rm "SipaduContonge.spec"

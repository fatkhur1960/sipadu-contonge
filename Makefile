.PHONY: prepare
default: prepare

prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "Sipadu Contonge" main.py --noconfirm

app-debug:
	pyinstaller --console --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "Sipadu Contonge" main.py --noconfirm

app-onefile:
	pyinstaller --onefile --icon=icon.ico --add-data="icon.ico:." --add-data="data/haarcascade_frontalface_default.xml:data" --add-data="style/app.qss:style" -n "Sipadu Contonge" main.py --noconfirm

app-build:
	pyinstaller "Sipadu Contonge.spec" --noconfirm


clean:
	rm -rf dist
	rm -rf build
	rm "Sipadu Contonge.spec"

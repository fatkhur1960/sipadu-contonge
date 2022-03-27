.PHONY: prepare
default: prepare

prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico:." -n "Sipadu Contonge" main.py --noconfirm

build-app:
	pyinstaller main.spec --noconfirm


clean:
	rm -rf dist
	rm -rf build
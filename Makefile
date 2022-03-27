.PHONY: prepare
default: prepare

prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico:." main.py

build:
	pyinstaller main.spec


clean:
	rm -rf dist
	rm -rf build
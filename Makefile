.PHONY: prepare
default: prepare

prepare:
	pyinstaller --windowed --icon=icon.ico --add-data="icon.ico:." -n "Sipadu Contonge" main.py --noconfirm

app-build:
	pyinstaller "Sipadu Contonge.spec" --noconfirm


clean:
	rm -rf dist
	rm -rf build
	rm "Sipadu Contonge.spec"
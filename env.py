import os


basedir = os.path.dirname(__file__)
cookie_filepath = os.path.join(basedir, "cookies.pickle")

app_debug = False
login_url = "https://sipadu.or.id/home/login"
add_anggota_url = "https://sipadu.or.id/user/inanggota"
test_url = "http://192.168.0.112:3000/inanggota"
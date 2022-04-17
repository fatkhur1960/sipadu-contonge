import os


basedir = os.path.dirname(__file__)
cookie_filepath = os.path.join(basedir, "cookies.pickle")

version = "1.2.1"
app_debug = False
login_url = "https://sipadu.or.id/home/login"
add_anggota_url = "https://sipadu.or.id/user/inanggota"
test_url = "http://localhost:3000/user/inanggota"
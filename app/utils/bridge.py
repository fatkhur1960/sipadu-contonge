import traceback
import requests
import warnings
import pickle
import os
from lxml import html
from datetime import datetime
import env

warnings.filterwarnings('ignore')

login_url = "https://sipadu.or.id/home/login"
add_anggota_url = "https://sipadu.or.id/user/inanggota"


class BridgeApi:
    def __init__(self):
        self.pacs = []
        self.p_rks = []
        self.authorized = False
        self._req = requests.session()
        self.ty = 1

    def load_cookies(self):
        if not os.path.exists(env.cookie_filepath):
            return

        with open(env.cookie_filepath, 'rb') as f:
            cookies = pickle.load(f)
            self._req.cookies.update(cookies)

        expires = None
        for cookie in self._req.cookies:
            if cookie.name == 'ci_session':
                expires = datetime.fromtimestamp(cookie.expires)

        self.authorized = expires >= datetime.now()
        if self.authorized:
            self.after_login()

    def save_cookies(self):
        with open(env.cookie_filepath, 'wb') as f:
            pickle.dump(self._req.cookies, f)

    def login(self, username: str, password: str, ty: int):
        resp = self._req.post(
            login_url,
            data={
                "username": username,
                "password": password,
                "kategori_user": ty
            },
            verify=False,
        )

        self.ty = ty

        tree = html.fromstring(resp.text)
        title = str(tree.xpath('//title/text()')[0]).strip()

        if title != 'OPERATOR | SIPADU':
            return (False, 'Username/Password salah!')

        self.after_login()
        return (True, 'Login Berhasil')

    def logout(self):
        self.authorized = False
        self.pacs.clear()
        self.p_rks.clear()
        self._req.close()
        if os.path.exists(env.cookie_filepath):
            os.remove(env.cookie_filepath)

    def merge(self, list1, list2):
        merged_list = tuple(zip(list1, list2))
        return merged_list

    def after_login(self):
        # self.save_cookies()
        result = self._req.get(
            add_anggota_url, verify=False)

        tree = html.fromstring(result.text)
        self.form = tree.xpath("//form[@id='quickForm']")[0]

        # inputs = self.form.xpath("//input")
        selects = self.form.xpath("//select")
        # fields = self.form.fields
        id_pc = None
        id_pac = None
        pacs = []
        p_rks = []
        for s in selects:
            if s.name == 'id_pimpinan':
                id_pc = s.value

            if s.name == 'id_pimpinan_ac':
                id_pac = s.value

                labels = s.xpath("option[@class='{}']/text()".format(id_pc))
                values = s.xpath("option[@class='{}']/@value".format(id_pc))

                for l, v in self.merge(labels, values):
                    name = str(l).strip()
                    pacs.append(
                        {'id': int(v), 'id_pc': int(id_pc), 'name': name})

            for p in pacs:
                id_pac = str(p['id'])
                if s.name == 'id_pimpinan_rk':
                    labels = s.xpath(
                        "option[@class='{}']/text()".format(id_pac))
                    values = s.xpath(
                        "option[@class='{}']/@value".format(id_pac))

                    for l, v in self.merge(labels, values):
                        name = str(l).strip()
                        p_rks.append(
                            {'id': int(v), 'id_pac': p['id'], 'name': name})

        self.pacs = pacs
        self.p_rks = p_rks

    def upload(self, data):
        try:
            if self.form.action:
                url = self.form.action
            else:
                url = self.form.base_url

            # url = "http://localhost:3000/inanggota"

            payload = {}
            for k, v in data.items():
                if k != "status":
                    self.form.fields[k] = v

            for k, v in self.form.form_values():
                payload[k] = v

            if data['foto'] != '' or data['foto'] != None and os.path.exists(data['foto']):
                with open(data['foto'], "rb") as foto:
                    result = self._req.post(
                        url, data=payload, verify=False, files={'foto': foto})
            else:
                result = self._req.post(url, data=payload, verify=False)

            print('Upload Result:', result.status_code)

            return result.status_code == 200
        except Exception as e:
            err = ''.join(traceback.format_exception(None, e, e.__traceback__))
            print('Got Error:', err)
            return False

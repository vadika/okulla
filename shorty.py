import string
from math import floor
from urllib.parse import urlparse

from flask import request, render_template, redirect, Blueprint

str_encode = str.encode
from string import ascii_lowercase
from string import ascii_uppercase
import base64
from redis import Redis

rdb = Redis()

host: str = "s/"


def toBase62(num: int, b: int = 62) -> str:
    if b <= 0 or b > 62:
        return 0
    base: str = string.digits + ascii_lowercase + ascii_uppercase
    r: int = num % b
    res: str = base[r]
    q: int = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num: str, b: int = 62) -> int:
    base: str = string.digits + ascii_lowercase + ascii_uppercase
    limit: int = len(num)
    res: int = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res


shorty_home = Blueprint('shorty_home', __name__, template_folder='templates')


@shorty_home.route('/s', methods=['GET', 'POST'])
def s_home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        print("urlparse - " + str(urlparse(original_url).scheme, "utf-8"))
        if urlparse(original_url).scheme:
            url = original_url
        else:
            url = b'http://' + original_url
        urlid = rdb.lpush("shorty", base64.urlsafe_b64encode(url))
        print("url=" + str(url, 'utf-8') + " short url id=" + str(urlid))
        encoded_string = toBase62(urlid)
        return render_template('shorty.html', short_url=host + encoded_string)
    return render_template('shorty.html')


def make_shorty(url_to_short: str) -> str:
    original_url: str = url_to_short
    url: str
    print("*urlparse - " + urlparse(original_url).scheme)
    if urlparse(original_url).scheme:
        url = original_url
    else:
        url = 'http://' + original_url
    urlid: int = rdb.lpush("shorty", base64.urlsafe_b64encode(url.encode()))
    print("*url=" + url + " short url id={}", urlid)
    encoded_string: str = toBase62(urlid)
    return host + encoded_string


shorty_url = Blueprint('shorty_url', __name__, template_folder='templates')


@shorty_url.route('/s/<short_url>')
def s_url(short_url):
    decoded = toBase10(short_url)
    url = host  # fallback if no URL is found
    print("di = " + str(decoded))
    try:
        short = rdb.lindex("shorty", rdb.llen("shorty") - decoded)
        if short is not None:
            url = base64.urlsafe_b64decode(short)
            print("rurl is " + str(url, "utf-8"))
    except Exception as e:
        print(e)
    return redirect(url)

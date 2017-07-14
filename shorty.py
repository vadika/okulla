from flask import Flask, request, render_template, redirect, Blueprint
from math import floor
import string
from urllib.parse import urlparse
str_encode = str.encode
from string import ascii_lowercase
from string import ascii_uppercase
import base64
from redis import Redis

rdb = Redis()

host = "s/"

def toBase62(num, b=62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + ascii_lowercase + ascii_uppercase
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=62):
    base = string.digits + ascii_lowercase + ascii_uppercase
    limit = len(num)
    res = 0
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


def make_shorty(url_to_short):
    original_url = url_to_short
    print("*urlparse - " + str(urlparse(original_url).scheme, "utf-8"))
    if urlparse(original_url).scheme:
        url = original_url
    else:
        url = b'http://' + original_url
    urlid = rdb.lpush("shorty", base64.urlsafe_b64encode(url))
    print("*url=" + str(url, 'utf-8') + " short url id=" + str(urlid))
    encoded_string = toBase62(urlid)
    return (host + encoded_string)



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

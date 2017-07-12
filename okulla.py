from flask import Flask, make_response, render_template, request, redirect, session
from flask_session import Session
from OP_RETURN import *
import pdfkit
import uuid
import hashlib
import base64


testnet = True
STORE = '/home/vadikas/PycharmProjects/okulla/store/'

def trans(key):
    return str(hashlib.md5(key).digest())


app = Flask(__name__)

# Check Configuration section for more details
SESSION_TYPE = 'redis'
app.config.from_object(__name__)

Session(app)

@app.route('/')
def main():
    return render_template("main.html")


@app.route('/url')
def url():
    return render_template("url.html")


@app.route('/notarize', methods=['POST'])
def notarize():
    url = request.form['url']
    if not url:
        return redirect("/url")

    print("url=", url)

    try:
        pdffile = pdfkit.from_url(url, False)
    except:
        return redirect("/url")

    filename = str(uuid.uuid4())
    session['fname'] = filename
    session['url'] = url
    session['md5'] = trans(pdffile)

    f = open(STORE + filename + '.pdf', "wb")
    f.write(pdffile)
    f.close()

    return render_template("notarize.html", pdf_name=filename)


@app.route("/publish", methods=['POST'])
def publish():
    # data = "SETERE http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456-34568 Petr Ivanov АА"

    sign = request.form['signature']
    btc_addr = request.form['btc-addr']
    if not sign:
        return redirect("/url")

    txthash = str(base64.b64encode(str(session['md5']).encode()))
    data = "SETERE " + \
           ' ' + session['url'] + \
           ' ' + txthash + \
           ' ' + sign + \
           ' ' + "http://hole.0xd8.org/check/" \
           + session['fname']

    print(data)
    data = data.encode("utf-8").decode("utf-8")

    result = OP_RETURN_store(data, testnet)

    if 'error' in result:
        return ('Error: ' + result['error'])
    else:
        return ("TxIDs:<br>" + "<br>".join(result['txids']) + "<br><br>Ref: " + result[
            'ref'] + "<br><br>Wait a few seconds then check on: http://" +
                ('testnet.' if testnet else '') + 'coinsecrets.org/' +
                '<br><iframe id="iframepdf style="overflow:hidden;height:100%;width:100%" height="100%" width="100%" src="/pdf"></iframe>')


@app.route("/pdf/<uuid:post_id>")
# @app.route('/docs/<id>')
def get_pdf(post_id):
    f = open(STORE + str(post_id) + '.pdf', "rb")
    binary_pdf = f.read()
    f.close()

    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'yourfilename'
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

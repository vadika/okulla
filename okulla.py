import base64
import uuid
import hashlib
import pdfkit
from flask import Flask, make_response, render_template, request, redirect, session
from flask_session import Session

from OP_RETURN import OP_RETURN_store
from shorty import shorty_url, shorty_home, make_shorty

testnet: bool = True
STORE: str = '/home/ubuntu/PycharmProjects/okulla/store/'


def trans(key: str) -> str:
    return str(hashlib.md5(key).digest())


app = Flask(__name__)
app.register_blueprint(shorty_home)
app.register_blueprint(shorty_url)

# Check Configuration section for more details
SESSION_TYPE: str = 'redis'
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
    purl: str = request.form['url']

    if not purl:
        return redirect("/url")

    print("purl=", purl)
    pdffile: bytes = pdfkit.from_url(purl, False)
    try:
        pdffile: bytes = pdfkit.from_url(purl, False)
        # print(pdffile)
    except:
        return redirect("/url")

    filename = str(uuid.uuid4())
    session['fname'] = filename
    session['url'] = purl
    session['md5'] = trans(pdffile)

    f = open(STORE + filename + '.pdf', "wb")
    f.write(pdffile)
    f.close()

    return render_template("notarize.html", pdf_name=filename)


@app.route("/publish", methods=['POST'])
def publish():
    """ data = "SETERE http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456-34568 Petr Ivanov АА"  """

    sign = request.form['signature']
    btc_addr = request.form['btc-addr']
    if not sign:
        return redirect("/url")

    # txthash = base64.b64encode(bytes(session['md5'].encode()))
    txthash = str(base64.b64encode(str(session['md5']).encode()), 'utf-8')

    print("txthash " + txthash)
    print("make_shorty " + make_shorty("http://hole.0xd8.org/check/" + session['fname']))
    data = "SETERE " + \
           ' ' + make_shorty(session['url'] +
                             ' ' + txthash +
                             ' ' + sign +
                             ' ' + make_shorty("http://hole.0xd8.org/check/" + session['fname']))

    print(data)
    data = data.encode("utf-8").decode("utf-8")

    result = OP_RETURN_store(data, testnet)

    if 'error' in result:
        return 'Error: ' + result['error']
    else:
        return render_template("complete.html", url=session['url'], txids=result['txids'], ref=result['ref'],
                               fname=session['fname'], coinbase=('testnet.' if testnet else '') + 'coinsecrets.org/')
        # ("TxIDs:<br>" + "<br>".join(result['txids']) + "<br><br>Ref: " + result[
        # 'ref'] + "<br><br>Wait a few seconds then check on: http://" +
        #     ('testnet.' if testnet else '') + 'coinsecrets.org/' )


@app.route("/check/<uuid:post_id>")
def check(post_id):
    return redirect("pdf/" + str(post_id))


@app.route("/pdf/<uuid:post_id>")
# @app.route('/docs/<id>')
def get_pdf(post_id: str) -> str:
    f = open(STORE + str(post_id) + '.pdf', "rb")
    binary_pdf = f.read()
    f.close()

    response = make_response(binary_pdf)  #
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'yourfilename'
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

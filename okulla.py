from flask import Flask, make_response, render_template, request, redirect
from OP_RETURN import *
import pdfkit
import uuid
import hashlib



testnet = True


def trans(key):
    return hashlib.md5(key.encode("utf-8")).digest()


app = Flask(__name__)

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

    filename = str(uuid.uuid4()

    f = open('store/' + filename + '.pdf', "wb")
    f.write(pdffile)
    f.close()

    return render_template("notarize.html")


@app.route("/publish", methods=['POST'])
def publish():
    # data = "SETERE http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456-34568 Petr Ivanov АА"
    data = str("SETERE  http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456")
    result = OP_RETURN_store(data, testnet)

    if 'error' in result:
        return ('Error: ' + result['error'])
    else:
        return ("TxIDs:<br>" + "<br>".join(result['txids']) + "<br><br>Ref: " + result[
            'ref'] + "<br><br>Wait a few seconds then check on: http://" +
                ('testnet.' if testnet else '') + 'coinsecrets.org/' +
                '<br><iframe id="iframepdf style="overflow:hidden;height:100%;width:100%" height="100%" width="100%" src="/pdf"></iframe>')


@app.route("/pdf")
# @app.route('/docs/<id>')
def get_pdf(id=None):
    #    if id is not None:
    #    binary_pdf = get_binary_pdf_data_from_database(id=id)
    f = open('/tmp/out.pdf', "rb")
    binary_pdf = f.read()
    f.close()
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'yourfilename'
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

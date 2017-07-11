from flask import Flask, make_response
from OP_RETURN import *
import pdfkit



testnet = True

app = Flask(__name__)

@app.route('/')
def mmmain():
    pdffile = pdfkit.from_url('http://spb.media/text/teoriya-igr', False)

    f = open('/tmp/out.pdf', "wb")
    f.write(pdffile)
    f.close()

    # data = "SETERE http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456-34568 Petr Ivanov АА"
    data = 'SETERE  http://spb.media/text/teoriya-igr http://hole.0xd8.org/check/123456'
    result = OP_RETURN_store(data, testnet)

    if 'error' in result:
        return ('Error: ' + result['error'])
    else:
        return ("TxIDs:<br>" + "<br>".join(result['txids']) + "<br><br>Ref: " + result[
            'ref'] + "<br><br>Wait a few seconds then check on: http://" +
                ('testnet.' if testnet else '') + 'coinsecrets.org/' +
                '<br><iframe id="iframepdf width=800" src="/pdf"></iframe>')


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

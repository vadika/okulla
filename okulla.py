from flask import Flask
from OP_RETURN import *

testnet = True

app = Flask(__name__)


@app.route('/')
def mmmain():

    data="SETERE Однажды в студеную зимнюю пору"
    result = OP_RETURN_store(data, testnet)

    if 'error' in result:
        return ('Error: ' + result['error'])
    else:
        return("TxIDs:<br>" + "<br>".join(result['txids']) + "<br><br>Ref: " + result[
            'ref'] + "<br><br>Wait a few seconds then check on: http://" +
              ('testnet.' if testnet else '') + 'coinsecrets.org/')



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

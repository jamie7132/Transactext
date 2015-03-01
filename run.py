from flask import Flask, request, redirect
import twilio.twiml
from dwolla import oauth, accounts, transactions, constants
from parse_rest.connection import register
from parse_rest.datatypes import Object
from parse_rest.user import User

register('SEZAS4U2ITXk2ET9aIxEnZIH8HkuRfj4IYIDSvnA', 'cf87OLoFdAbeFPBRT6ZFwtVDqak8S9rVfJlnXEGX',master_key='V6WiPiLHBF56SuOHwEV0BkC2MSqJpF8gaFG32Jn0')
app = Flask(__name__)

class MarketItem(Object):
    pass
 
@app.route("/", methods=['GET', 'POST'])
def main():
    """Respond to incoming calls with a simple text message."""

    #print accounts.basic('832-515-2241')
    #print request.values
    body = request.values['Body']
    tokens = body.split()

    user = request.values['From']
    u = None

    resp = twilio.twiml.Response()
    
    if len(User.Query.filter(username=str(user))) == 0:
        u = User.signup(str(user), "")
    else:
        u = User.login(str(user), "")
    if len(tokens) == 1:
        if body.lower() == 'register':
            oauth_token = oauth.genauthurl('http://localhost:5000/return')
            print oauth_token
            resp.message(str(oauth_token))
        elif body.lower().startswith('sell'):
            #item = MarketItem(name='wheat',forSale=True, price=15, owner='Bob')
            #item.save()
            bobSet = MarketItem.Query.filter(owner='Bob')
            for i in bobSet:
                print i.name
                print i.price
    else: 
        resp.message("Invalid request - text 'help' for a list of option")
    """
    elif len(tokens) == 2:
        if body.lower().startswith('pay'):
            num_to = request.values['To']
            num_from = request.values['From']
            print request.values
            resp.message("Paying $" + str(tokens[1]))
        elif body.lower().startswith('request'):
            resp.message("Request $" + str(tokens[1]))
        else:
            resp.message("Invalid demand - Message did not start with 'PAY' or 'REQUEST'")
    """
        #resp.message("Invalid demand - Message must be of format: 'PAY'/'REQUEST' AMOUNT")
    
    return str(resp)

@app.route("/return", methods=['GET'])
def oauth_return():
    code = request.args.get('code') #error check later

    token = oauth.get(code, 'http://localhost:5000/return')

    print token

    constants.access_token = token['access_token']

    return str(accounts.balance())
 
if __name__ == "__main__":
    app.run(debug=True)

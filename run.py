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

def matchmaker():
    buy = MarketItem.Query.filter(forSale=False)
    for it in buy:
        matches = MarketItem.Query.filter(forSale=True, item=str(it.item), price=float(it.price))
        for match in matches:
            u = User.Query.filter(objectId=it.ownerId)[0]
            if match.quantity > it.quantity and match.price*it.quantity <= u.balance:
                match.quantity -= it.quantity
                match.save()
                u.balance -= it.quantity*match.price
                u.save()
                it.delete()
            elif match.quantity == it.quantity and match.price*it.quantity <= User.Query.filter(objectId=it.ownerId)[0].balance:
                u.balance -= it.quantity*match.price
                u.save()
                match.delete()
                it.delete()

    """
        matches = MarketItem.Query.filter(forSale=True, item=str(it.item))
        match_best = {'item': None, 'price': None}
        for match in matches:
            match_best['item'] = match.item
            if match.quantity >= it.quantity and match.price*it.quantity <= User.Query.filter(objectId=it.ownerId)[0].balance:
                print str(match.item) + " " + str(match.price)
                match_best['item'] = match.item
                if match_best['price'] == None or match_best['price'] > match.price:
                    match_best['price'] = match.price
    print match_best
    """ 
@app.route("/", methods=['GET', 'POST'])
def main():
    """Respond to incoming calls with a simple text message."""

    #print accounts.basic('832-515-2241')
    #print request.values
    body = request.values['Body']
    tokens = body.split()

    user = str(request.values['From'])[1:]
    u = None

    resp = twilio.twiml.Response()
    
    if len(User.Query.filter(username=str(user))) == 0:
        u = User.signup(str(user), "", phone=str(user))
    else:
        u = User.login(str(user), "")
    
    if body.lower() == 'register':
        oauth_token = oauth.genauthurl('http://localhost:5000/return?user=' + str(u.username))
        resp.message(str(oauth_token))
    elif body.lower().startswith('sell'):
        item = MarketItem(ownerId=u.objectId, forSale=True, item=str(tokens[2]), quantity=float(tokens[1]), price=float(tokens[4]))
        item.save()
        matchmaker()
    elif body.lower().startswith("buy"):
        order = MarketItem(ownerId=u.objectId, forSale=False, item=str(tokens[2]), quantity=float(tokens[1]), price=float(tokens[4]))
        order.save()
        matchmaker()
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
    user_id = request.args.get('user')

    token = oauth.get(code, 'http://localhost:5000/return?user=' + str(user_id))
    constants.access_token = token['access_token']
  
    u = User.Query.filter(username=str(user_id))[0] 
    u.dwollaAuth = constants.access_token
    u.balance = accounts.balance()
    u.save()

    return ""
  
if __name__ == "__main__":
    app.run(debug=True)

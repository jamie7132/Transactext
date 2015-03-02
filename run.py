from flask import Flask, request, redirect
import twilio.twiml
from dwolla import oauth, accounts, transactions, constants
from dwolla import DwollaClientApp, DwollaUser
from parse_rest.connection import register
from parse_rest.datatypes import Object
from parse_rest.user import User

register('SEZAS4U2ITXk2ET9aIxEnZIH8HkuRfj4IYIDSvnA', 'cf87OLoFdAbeFPBRT6ZFwtVDqak8S9rVfJlnXEGX',master_key='V6WiPiLHBF56SuOHwEV0BkC2MSqJpF8gaFG32Jn0')
app = Flask(__name__)

# Instantiate a new Dwolla client
Dwolla = DwollaClientApp("P/LZrllLoo1ebneqK1EXfS9JzgAQnncvOrZXOOIS3T3+o7YvhT", "s3WSCkaAMu9VZYzSDznfbdVaZFef0/GU+AIUV1I+29TVr/+0j+")

class MarketItem(Object):
    pass

#need to do consolidation later
def matchmaker():
    buy = MarketItem.Query.filter(forSale=False)
    for it in buy:
        matches = MarketItem.Query.filter(forSale=True, item=str(it.item), price=float(it.price))
        u = User.Query.filter(objectId=it.ownerId)[0]
        for match in matches:
            if match.ownerId != it.ownerId and match.quantity > it.quantity and match.price*it.quantity <= u.balance:
                buyer = User.Query.filter(objectId=str(it.ownerId))[0]
                seller = User.Query.filter(objectId=str(match.ownerId))[0]
                seller_id = seller.dwollaId
                transactions.send(str(seller_id), float(it.quantity*match.price), False, str(buyer.dwollaAuth), str(buyer.pin))

                match.quantity -= it.quantity
                match.save()
                u.balance -= it.quantity*match.price
                u.save()
                seller.balance += it.quantity*match.price
                seller.save()
                it.delete()

                print transaction
            elif match.ownerId != it.ownerId and match.quantity == it.quantity and match.price*it.quantity <= User.Query.filter(objectId=it.ownerId)[0].balance:
                buyer = User.Query.filter(objectId=str(it.ownerId))[0]
                seller = User.Query.filter(objectId=str(match.ownerId))[0]
                seller_id = seller.dwollaId
                transactions.send(str(seller_id), float(it.quantity*match.price), False, str(buyer.dwollaAuth), str(buyer.pin))

                u.balance -= it.quantity*match.price
                u.save()
                seller.balance += it.quantity*match.price
                seller.save()
                match.delete()
                it.delete()

                print transaction

@app.route("/", methods=['GET', 'POST'])
def main():
    """Respond to incoming calls with a simple text message."""

    body = request.values['Body']
    tokens = body.split()

    user = str(request.values['From'])[1:]
    u = None

    resp = twilio.twiml.Response()
    
    if len(User.Query.filter(username=str(user))) == 0:
        u = User.signup(str(user), "", phone=str(user))
    else:
        u = User.login(str(user), "")
        constants.access_token = str(u.dwollaAuth)
        constants.pin = str(u.pin)

    if body.lower().startswith('register'):
        u.dwollaId = str(tokens[1])
        u.pin = str(tokens[2])
        constants.pin = str(u.pin)
        u.save()
        oauth_token = oauth.genauthurl('http://localhost:5000/return?user=' + str(u.username))
        resp.message(str(oauth_token))
    elif body.lower() == "balance":
        resp.message("Your balance is $" + str("%.2f" % round(accounts.balance(), 2)))
    elif body.lower().startswith('sell'):
        item = MarketItem(ownerId=u.objectId, forSale=True, item=str(tokens[2]), quantity=float(tokens[1]), price=float(tokens[4]))
        item.save()
        matchmaker()
    elif body.lower().startswith("buy"):
        order = MarketItem(ownerId=u.objectId, forSale=False, item=str(tokens[2]), quantity=float(tokens[1]), price=float(tokens[4]))
        order.save()
        matchmaker()
    elif body.lower().startswith("list"):
        orders = MarketItem.Query.all().order_by('item')
        msg = ""
        for order in orders:
            if order.forSale:
                msg += "For Sale: " + str(order.quantity) + " " + str(order.item) + " for $" + str("%.2f" % round(order.price, 2)) + "\n"
            else:
                msg += "Seeking: " + str(order.quantity) + " " + str(order.item) + " for $" + str("%.2f" % round(order.price, 2)) + "\n"
        resp.message(str(msg))
    else:
        resp.message("Invalid request - text 'help' for a list of option")
   
    print resp
    
    return str(resp)

@app.route("/return", methods=['GET'])
def oauth_return():
    code = request.args.get('code') #error check later
    user_id = request.args.get('user')

    token = oauth.get(code, 'http://localhost:5000/return?user=' + str(user_id))
    constants.access_token = str(token['access_token'])
  
    u = User.Query.filter(username=str(user_id))[0] 
    u.dwollaAuth = str(token['access_token'])
    u.balance = float(accounts.balance())
    u.save()

    return ""
  
if __name__ == "__main__":
    app.run(debug=True)

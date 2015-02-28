from flask import Flask, request, redirect
import twilio.twiml
 
app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    #print request.values
    body = request.values['Body']
    tokens = body.split()

    resp = twilio.twiml.Response()
    
    if len(tokens) == 2:
        if body.lower().startswith('pay'):
            resp.message("Paying $" + str(tokens[1]))
        elif body.lower().startswith('request'):
            resp.message("Request $" + str(tokens[1]))
        else:
            resp.message("Invalid demand - Message did not start with 'PAY' or 'REQUEST'")
    else:
        resp.message("Invalid demand - Message must be of format: 'PAY'/'REQUEST' AMOUNT")
    
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)

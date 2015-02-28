import requests

from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

from flask import Flask, request, redirect
import twilio.twiml

 
app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
 
    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)

#above this line is the twilio stuff and below is the heroku

# Create your views here.

def index(request):
    return hello_monkey()
    #return HttpResponse('Hello from Python!')
"""
def index(request):
    r = requests.get('http://httpbin.org/status/418')
    print r.text
    return HttpResponse('<pre>' + r.text + '</pre>')
"""
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})



from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC6860bff4a7236ba642e62764cd65b314"
auth_token  = "bfd4cb1141419f5d24a4d492d629537c"
client = TwilioRestClient(account_sid, auth_token)
 
message = client.messages.create(body="Jenny please?! I love you <3",
    to="+18325152241",    # Replace with your phone number
    from_="+17603133276") # Replace with your Twilio number
print message.sid

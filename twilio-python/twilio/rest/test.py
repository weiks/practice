from twilio.rest import TwilioRestClient

account_sid = "AC3e783a500263a689cc4c417ccc79ad26" # Your Account SID from www.twilio.com/console
auth_token  = "ecf74a6c2cf79ac2cf57b3601eece109"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+6504693457",    # Replace with your phone number
    from_="+9179333551") # Replace with your Twilio number

print(message.sid)

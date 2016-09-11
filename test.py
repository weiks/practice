from twilio.rest import TwilioRestClient

account_sid = "AC3e783a500263a689cc4c417ccc79ad26" # Your Account SID from www.twilio.com/console
auth_token  = "ecf74a6c2cf79ac2cf57b3601eece109"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

from time import gmtime, strftime

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("mesg", help="please incude the message to be texted")
args = parser.parse_args()


message = client.messages.create(body="Go {} at {}".format(args.mesg, strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())),
    to="+16504693457",    # Replace with your phone number
    from_="+19179333551") # Replace with your Twilio number

print(message.body)
print(message.sid)

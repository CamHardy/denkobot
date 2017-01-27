import os
import argparse 
import time
from slackclient import SlackClient

# denkobot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "make me a sandwich"

# instantiate Slack & Twilo clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
	# Receives commands directed at the bot and determines if they
	# are valid commands. If so, then acts on the commands. If not,
	# returns back what it needs for clarification.

	response = "What the heck did you just say to me?"
	if command.startswith(EXAMPLE_COMMAND):
		response = "Haha no."
	slack_client.api_call("chat.postMessage", channel = channel, text = response, as_user = True)

def parse_slack_output(slack_rtm_output):
	# The Slack Real Time Messaging API is an events firehose.
	# this parsing function returns None unless a message is
	# directed at denkobot, based on the ID.

	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and AT_BOT in output['text']:
				# return text after the @ mention, whitespace removed
				return output['text'].split(AT_BOT)[1].strip().lower(), \
					output['channel']
	return None, None

def usermode():
	if slack_client.rtm_connect():
		print("you are denkobot, you can do anything")
		channels = slack_client.api_call("channels.list")
		print("Availabel channels:")
		for c in channels['channels']:
			print(c['name'] + " (" + c['id'] + ")")
		choice = raw_input("Choose a channel: ")
		while True:
			response = raw_input("Speak: ")
			slack_client.api_call("chat.postMessage", channel = choice, text = response, as_user = True)
			
	else:
		print("Connection failed. Invalid Slack token or bot ID? Maybe you're stupid? Haha yeah probably that.")


def botmode():
	READ_WEBSOCKET_DELAY = 0.5 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("denkobot is alive, each moment a new nightmare.")
		while True:
			command, channel = parse_slack_output(slack_client.rtm_read())
			if command and channel:
				handle_command(command, channel)
				print("Successfully handled command '" + command + "' in channel " + channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID? Maybe you're stupid? Haha yeah probably that.")

def main(args):
	if args.mode == 1:
		usermode()
	else:
		botmode()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Set bot mode.")
	parser.add_argument("-u", "--user", dest = "mode", action = "store_const", const = 1, default = 0)
	args = parser.parse_args()
	main(args)
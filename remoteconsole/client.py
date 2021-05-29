
import json
import urllib
import urllib.request

import remoteconsole.client_input


def send_request(server_address, request_data):
	ip, port = server_address
	console_url = 'http://{}:{}'.format(ip, port)
	request_body = json.dumps(request_data).encode('utf-8')
	request = urllib.request.Request(
		console_url,
		data=request_body,
		headers={'Content-Type': 'application/json'}
	)

	response = urllib.request.urlopen(request)
	response_code = response.getcode()
	response_body = response.read().decode('utf-8')
	response_data = json.loads(response_body)

	if request_data['type'] == 'run':
		handler_output = response_data.get('handler_output')
		if handler_output:
			print(handler_output, end='')
	return response_data

def run_once(server_address, input, more):
	if more:
		s = input('... ')
	else:
		s = input('>>> ')
	request_data = {
		'type': 'run',
		'line': s
	}
	response_data = send_request(server_address, request_data)
	more = response_data.get('more', False)
	return more

def run_repl(server_address):
	input = remoteconsole.client_input.setup(send_request, server_address)

	more = False
	while True:
		try:
			more = run_once(server_address, input, more)
		except KeyboardInterrupt:
			print('KeyboardInterrupt')

def parse_address():
	import sys
	argn = len(sys.argv)
	ip = '127.0.0.1'
	port = 9000
	if argn >= 2:
		ip = sys.argv[1]
	if argn >= 3:
		port = int(sys.argv[2])

	server_address = (ip, port)
	return server_address

def main():
	server_address = parse_address()
	run_repl(server_address)

if __name__ == '__main__':
	main()

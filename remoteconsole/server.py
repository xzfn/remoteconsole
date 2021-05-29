
import io
import json
import queue
import http.server
import socketserver
import threading
import traceback
import time
import code

import remoteconsole.util
import remoteconsole.completion


class HTTPConsoleRequestHandler(http.server.BaseHTTPRequestHandler):
	def do_POST(self):
		console_server = self.server.get_console_server()

		content_type = self.headers.get('Content-Type')
		content_length = int(self.headers.get('Content-Length'))

		request_body = self.rfile.read(content_length).decode('utf-8')
		request_data = json.loads(request_body)
		console_server._server_thread_put_request(request_data)
		# blocking wait for response
		response_data = console_server._server_thread_get_response()
		response_body = json.dumps(response_data).encode('utf-8')

		self.send_response(http.HTTPStatus.OK)
		self.send_header('Content-Type', 'application/json')
		self.end_headers()
		self.wfile.write(response_body)

	def log_message(self, format, *args):
		# silence log
		return

class ConsoleTCPServer(socketserver.TCPServer):
	timeout = 0.0

	def __init__(self, server_address, RequestHandlerClass, console_server):
		super(ConsoleTCPServer, self).__init__(server_address, RequestHandlerClass)
		self._console_server = console_server

	def get_console_server(self):
		return self._console_server


class ConsoleRequestHandler:
	def pre_handle(self, request):
		pass

	def handle(self, request):
		return {}

	def post_handle(self, request, response):
		pass


class ConsoleServer:
	def __init__(self, server_address):
		self.server_address = server_address
		self.request_handler = ConsoleRequestHandler()

		self.request_queue = queue.Queue()
		self.response_queue = queue.Queue()
		self.http_server = ConsoleTCPServer(server_address, HTTPConsoleRequestHandler, self)
		self.http_server_thread = threading.Thread(target=self._server_thread_run)
		self.http_server_thread.start()

	def set_request_handler(self, request_handler):
		self.request_handler = request_handler

	def service(self):
		while True:
			try:
				request = self.request_queue.get_nowait()
			except queue.Empty:
				break

			try:
				self.request_handler.pre_handle(request)
				aux_output = io.StringIO()
				with remoteconsole.util.ScopeTee(aux_output):
					response = {}
					try:
						response = self.request_handler.handle(request)
					except Exception as e:
						print('Error request_handler:')
						traceback.print_exc()

				handler_output = aux_output.getvalue()
				response['handler_output'] = handler_output
				self.request_handler.post_handle(request, response)
			except Exception:
				print('Internal ERROR:')
				traceback.print_exc()
			except SystemExit:
				print('Raised SystemExit')
				self.response_queue.put(response)
				raise

			self.response_queue.put(response)

	def shutdown(self):
		print('console server shutdown ...')
		self.http_server.shutdown()
		self.http_server_thread.join()
		print('console server shutdown done')

	def _server_thread_put_request(self, request):
		self.request_queue.put(request)

	def _server_thread_get_response(self):
		return self.response_queue.get()

	def _server_thread_run(self):
		self.http_server.serve_forever()


class PythonCodeHandler:
	def __init__(self, env):
		self.console_env = env
		self.code_console = code.InteractiveConsole(env)
		self.more = False

	def pre_handle(self, request):
		if request['type'] == 'run':
			if self.more:
				print('... ', end='')
			else:
				print('>>> ', end='')
			print(request['line'])

	def handle(self, request):
		line = request['line']
		request_type = request['type']
		if request_type == 'run':
			more = self.code_console.push(line)
			response = {'more': more}
		elif request_type == 'complete':
			response = {
				'matches': remoteconsole.completion.complete(self.console_env, line)
			}
		return response

	def post_handle(self, request, response):
		self.more = response.get('more', False)


def main(server_address):
	console_server = ConsoleServer(server_address)

	code_console = PythonCodeHandler({})
	console_server.set_request_handler(code_console)

	try:
		while True:
			console_server.service()
			time.sleep(0.1)
	except Exception as e:
		print('Error service:')
		traceback.print_exc()
	finally:
		console_server.shutdown()

if __name__ == '__main__':
	import sys
	argn = len(sys.argv)
	IP = '127.0.0.1'
	PORT = 9000
	if argn >= 2:
		IP = sys.argv[1]
	if argn >= 3:
		PORT = int(sys.argv[2])
	print('RemoteConsoleServer listening at', (IP, PORT))
	main((IP, PORT))
	print('exit')

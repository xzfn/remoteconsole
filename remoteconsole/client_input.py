

AUTO_SPLIT_LINES = True


_has_readline = False
try:
	import readline
	_has_readline = True
except ModuleNotFoundError:
	pass

_has_prompt_toolkit = False
try:
	import prompt_toolkit
	import prompt_toolkit.completion
	_has_prompt_toolkit = True
except ModuleNotFoundError:
	pass


if _has_readline:
	class ReadlineCompleter:
		def __init__(self, send_request, server_address):
			self.send_request = send_request
			self.server_address = server_address

		def complete(self, text, state):
			if not text.strip():
				if state == 0:
					readline.insert_text('\t')
					readline.redisplay()
					return ''
				else:
					return None

			if state == 0:
				self.matches = request_completion(self.send_request, self.server_address, text)

			try:
				return self.matches[state]
			except IndexError:
				return None

if _has_prompt_toolkit:
	class PromptToolkitCompleter(prompt_toolkit.completion.Completer):
		def __init__(self, send_request, server_address):
			super().__init__()
			self.send_request = send_request
			self.server_address = server_address

		def get_completions(self, document, complete_event):
			text = document.text_before_cursor
			matches = request_completion(self.send_request, self.server_address, text)
			for match in matches:
				yield prompt_toolkit.completion.Completion(match, -len(text))


def request_completion(send_request, server_address, text):
	request_data = {
		'type': 'complete',
		'line': text,
	}
	response_data = send_request(server_address, request_data)
	return response_data.get('matches', [])

def setup(send_request, server_address):
	if _has_readline:
		readline.parse_and_bind('tab: complete')
		readline.set_completer(ReadlineCompleter(send_request, server_address).complete)
		input_func = input
	elif _has_prompt_toolkit:
		session = prompt_toolkit.PromptSession(
			complete_while_typing=False,
			complete_style=prompt_toolkit.shortcuts.CompleteStyle.READLINE_LIKE,
			completer=PromptToolkitCompleter(send_request, server_address)
		)
		input_func = session.prompt
	else:
		input_func = input

	if AUTO_SPLIT_LINES:
		return SplitLinesInputWrapper(input_func).input
	else:
		return input_func

class SplitLinesInputWrapper:
	"""Split lines from input. Treat one-time multiple-line input as multiple one-line input."""
	def __init__(self, raw_input):
		self.raw_input = raw_input
		self.cached_lines = []

	def input(self, prompt=None):
		if not self.cached_lines:
			raw_str = self.raw_input(prompt)
			if '\n' not in raw_str:
				return raw_str
			self.cached_lines = raw_str.split('\n')
		return self.cached_lines.pop(0)

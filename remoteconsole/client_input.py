
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
		return input
	elif _has_prompt_toolkit:
		session = prompt_toolkit.PromptSession(
			complete_while_typing=False,
			complete_style=prompt_toolkit.shortcuts.CompleteStyle.READLINE_LIKE,
			completer=PromptToolkitCompleter(send_request, server_address)
		)
		return session.prompt
	else:
		return input

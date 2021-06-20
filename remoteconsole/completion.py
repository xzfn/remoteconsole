import sys
import re
import rlcompleter


# from IPython/core/completer
if sys.platform == 'win32':
    DELIMS = ' \t\n`!@#$^&*()=+[{]}|;\'",<>?'
else:
    DELIMS = ' \t\n`!@#$^&*()=+[{]}\\|;:\'",<>?'
GREEDY_DELIMS = ' =\r\n'
def build_delims_re(delims):
	expr = '[' + ''.join('\\'+ c for c in delims) + ']'
	return re.compile(expr)
DELIMS_RE = build_delims_re(DELIMS)
GREEDY_DELIMS_RE = build_delims_re(GREEDY_DELIMS)

def complete(namespace, line, greedy=True):
	text = DELIMS_RE.split(line)[-1]
	before_text = line[:len(line) - len(text)]
	completer = rlcompleter.Completer(namespace)
	final_matches = []
	matches = []
	if '.' in text:
		matches.extend(completer.attr_matches(text))
	else:
		matches.extend(completer.global_matches(text))
	if matches:
		final_matches = [before_text + match for match in matches]
	elif greedy:
		greedy_text = GREEDY_DELIMS_RE.split(line)[-1]
		if '.' in greedy_text and text != greedy_text:
			greedy_before_text = line[:len(line) - len(greedy_text)]
			greedy_matches = _greedy_attr_matches(completer, greedy_text)
			final_matches = [greedy_before_text + match for match in greedy_matches]
		if not final_matches:
			# try use entire line, no delimiter
			more_greedy_text = line
			if '.' in more_greedy_text and text != more_greedy_text and greedy_text != more_greedy_text:
				final_matches = _greedy_attr_matches(completer, more_greedy_text)

	return final_matches

def _greedy_attr_matches(completer, text):
	# slight modify from rlcompleter.py attr_matches
	dot_pos = text.rfind('.')
	expr, attr = text[:dot_pos], text[dot_pos+1:]
	try:
		thisobject = eval(expr, completer.namespace)
	except Exception:
		return []

	# get the content of the object, except __builtins__
	words = set(dir(thisobject))
	words.discard("__builtins__")

	if hasattr(thisobject, '__class__'):
		words.add('__class__')
		words.update(rlcompleter.get_class_members(thisobject.__class__))
	matches = []
	n = len(attr)
	if attr == '':
		noprefix = '_'
	elif attr == '_':
		noprefix = '__'
	else:
		noprefix = None
	while True:
		for word in words:
			if (word[:n] == attr and
				not (noprefix and word[:n+1] == noprefix)):
				match = "%s.%s" % (expr, word)
				try:
					val = getattr(thisobject, word)
				except Exception:
					pass  # Include even if attribute not set
				else:
					match = completer._callable_postfix(val, match)
				matches.append(match)
		if matches or not noprefix:
			break
		if noprefix == '_':
			noprefix = '__'
		else:
			noprefix = None
	matches.sort()
	return matches

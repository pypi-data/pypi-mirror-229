import itertools
from termcolor import colored

def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)] * n
	return (filter(None, params) for params in itertools.zip_longest(fillvalue=fillvalue, *args))


def output(match):
	if match:
		msg = 'Match Found \n \n'
		msg += 'Audio ID: %s \n'
		msg += 'Audio Hash: %s \n'
		msg += 'Offset: %d \n'
		msg += 'Offset Seconds : %d secs \n'
		msg += 'Confidence: %d'

		print("#" * 40)
		print(colored(msg, 'green') % (
			match.audio.id,
			match.audio.hash_id,
			match.offset,
			match.offset_seconds,
			match.confidence
		))
		print("#" * 40)
	else:
		msg = ' ** No matches found'
		print(colored(msg, 'red'))
import logging
from typing import Any


class MultiLineFormatter(logging.Formatter):
	"""Multi-line formatter."""
	def get_header_length(self, record):
		"""Get the header length of a given record."""
		return len(super().format(logging.LogRecord(
			name=record.name,
			level=record.levelno,
			pathname=record.pathname,
			lineno=record.lineno,
			msg='', args=(), exc_info=None
		)))

	def format(self, record):
		"""Format a record with added indentation."""
		indent = ' ' * self.get_header_length(record)
		head, *trailing = super().format(record).splitlines(True)
		return head + "".join(indent + line for line in trailing)

def setupLogging(level = logging.ERROR, fmt: str = "%(levelname)s: %(message)s") -> None:
	handler = logging.StreamHandler()
	handler.setFormatter(MultiLineFormatter(
		fmt=fmt,
		datefmt="%H:%M:%S",
	))
	logging.basicConfig(
		level=level,
		handlers=[handler],
		force=True,
	)
	if level == logging.DEBUG:
		requests_log = logging.getLogger("urllib3")
		requests_log.setLevel(logging.DEBUG)
		requests_log.propagate = True
		import http.client
		http.client.HTTPConnection.debuglevel = 1

def ml(*args: str) -> str:
	return "\n".join(str(a) for a in args)

def debugml(base: str, *args: tuple[str, Any]) -> None:
	strs = [base]
	vals = list[Any]()
	for arg in args:
		s, v = arg
		strs.append(s)
		vals.append(v)
	logging.debug("\n".join(strs), *vals)

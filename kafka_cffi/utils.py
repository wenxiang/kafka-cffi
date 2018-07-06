import six

from .errors import ConfigurationError


def ensure_bytes(s):
	if isinstance(s, six.binary_type):
		return s
	elif isinstance(s, six.text_type):
		return s.encode("utf8")
	else:
		raise ConfigurationError("argument must be a string / bytes")

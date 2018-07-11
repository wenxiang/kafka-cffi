import six


def ensure_bytes(s):
	if isinstance(s, six.binary_type):
		return s
	elif isinstance(s, six.text_type):
		return s.encode("utf8")
	else:
		raise TypeError("argument must be a string / bytes")


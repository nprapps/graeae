def get_art_root_url(url):
    """
    extract common bits of an art url
    """
    filename, extension = url.rsplit('.', 1)
    fileroot = filename.rsplit('_', 1).pop(0)
    return '{0}.{1}'.format(fileroot, extension)

def get_seamus_id_from_url(url):
	"""
	gets seamus ID from URL
	"""
	if url.startswith('http://www.npr.org') or url.startswith('http://npr.org'):
		url_parts = url.split('/')
		id = url_parts[-2]
		if id.isdigit():
			return id
	
	return None
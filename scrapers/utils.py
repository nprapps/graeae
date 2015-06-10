def get_art_root_url(url):
    """
    extract common bits of an art url
    """
    filename, extension = url.rsplit('.', 1)
    fileroot = filename.rsplit('_', 1).pop(0)
    return '{0}.{1}'.format(fileroot, extension)

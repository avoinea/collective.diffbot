""" Caching
"""
def cacheJsonKey(method, self, *args, **kwargs):
    """ Generate unique cache id
    """
    return (
        self.context.absolute_url(1),
        getattr(self, '__name__', ''),
        self.request.form.get('url', '')
    )

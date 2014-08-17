class Analytics(object):
    """
    Simple containing object for the anaytics ID to be passed into the jinja2 template
    """

    def __init__(self, id):
        """
        :param str id: The google analytics ID
        """
        self.id = id

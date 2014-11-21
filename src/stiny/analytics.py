class Analytics(object):
    """
    Simple containing object for the anaytics ID to be passed into the jinja2 template
    """

    def __init__(self, analytics_id):
        """
        :param str analytics_id: The google analytics ID
        """
        self.analytics_id = analytics_id


class GraphException(BaseException):
    def __init__(self, message, *args, **kwargs):
        super(GraphException, self).__init__(*args, **kwargs)
        self.message = message

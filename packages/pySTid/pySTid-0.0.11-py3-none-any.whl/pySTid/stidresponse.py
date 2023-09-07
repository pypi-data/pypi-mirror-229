class STidAPI_response:
    def __init__(self, success: bool, status_code: int, content):
        self.success = success
        self.status_code = status_code
        self.content = content

    def __bool__(self):
        return self.success

    def __str__(self):
        return str(self.content)
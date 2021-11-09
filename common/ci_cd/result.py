

class Result:
    """ Standard data structure for storing CI/CD Quality results. """

    def __init__(self, name, success, details=None):
        """ Simple data structure for a quality result. """
        self.name = name
        self.success = success
        self.details = {} if details is None else details

    def to_dict(self):
        return dict(
            name=self.name,
            success=self.success,
            details=self.details,
        )

    def to_name_as_key_dict(self):
        data = self.to_dict()
        return {data.pop('name'): data}

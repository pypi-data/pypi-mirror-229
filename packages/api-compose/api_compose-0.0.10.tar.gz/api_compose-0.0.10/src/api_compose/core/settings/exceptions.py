

class IncludeExcludeBothSetException(Exception):
    def __str__(self):
        return 'Cannot both include and exclude models at the same time'


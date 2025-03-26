class FileValidationError(Exception):
    def __init__(self, file_name):
        self.file_name = file_name

    def __str__(self):
        return f"File {self.file_name} failed validation"


class ElementError(FileValidationError):
    def __init__(self, message, line_num):
        self.message = message
        self.line_num = line_num
        super().__init__(message)

    def __str__(self):
        return f"{self.message} at line {self.line_num}"


class XMLAttributeError(FileValidationError):
    def __init__(self, message, line_num):
        self.message = message
        self.line_num = line_num
        super().__init__(message)

    def __str__(self):
        return f"{self.message} at line {self.line_num}"

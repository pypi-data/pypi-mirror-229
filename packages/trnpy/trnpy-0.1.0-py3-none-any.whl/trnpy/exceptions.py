from typing import Optional


class DuplicateLibraryError(Exception):
    """Raised when a library file has already been loaded."""


class SimulationError(Exception):
    """Raised when a simulation reports a fatal error."""


class SimulationNotInitializedError(Exception):
    """Raised when a simulation has not been initialized.

    This error occurs when functions that control or access
    a simulation are called before it has been initialized.
    """


class TrnsysError(Exception):
    """Represents an error raised by TRNSYS."""

    def __init__(self, error_code: int, message: Optional[str] = None):
        super().__init__(
            message if message else f"An unknown TRNSYS error ({error_code}) occurred."
        )
        self.error_code = error_code


class TrnsysSetDirectoriesError(TrnsysError):
    def __init__(self, error_code: int):
        messages = {
            1: "root directory string is too long",
            2: "root directory does not exist",
            3: "exe directory string is too long",
            4: "exe directory does not exist",
            5: "user lib directory string is too long",
            6: "user lib directory does not exist",
        }
        super().__init__(error_code, messages.get(error_code))


class TrnsysLoadInputFileError(TrnsysError):
    def __init__(self, error_code: int):
        messages = {
            1: "input file does not exist",
            2: "directories not set",
            3: "list file cannot be opened for writing",
            4: "input file cannot be opened for reading",
        }
        super().__init__(error_code, messages.get(error_code))


class TrnsysStepForwardError(TrnsysError):
    def __init__(self, error_code: int):
        messages = {
            1: "simulation has reached its final time",
        }
        super().__init__(error_code, messages.get(error_code))


class TrnsysGetOutputValueError(TrnsysError):
    def __init__(self, error_code: int):
        messages = {
            1: "unit is not present in the deck",
            2: "output number is not valid for this unit",
        }
        super().__init__(error_code, messages.get(error_code))


class TrnsysSetInputValueError(TrnsysError):
    def __init__(self, error_code: int):
        messages = {
            1: "unit is not present in the deck",
            2: "input number is not valid for this unit",
        }
        super().__init__(error_code, messages.get(error_code))

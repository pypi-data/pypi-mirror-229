"""Code related to running TRNSYS simulations."""

from __future__ import annotations

from pathlib import Path
from typing import List, Union

from ..exceptions import (
    SimulationNotInitializedError,
    TrnsysGetOutputValueError,
    TrnsysLoadInputFileError,
    TrnsysSetDirectoriesError,
    TrnsysSetInputValueError,
    TrnsysStepForwardError,
)
from .lib import LoadedTrnsysLib, TrnsysDirectories, TrnsysLib


class Simulation:
    """Represents a single TRNSYS simulation."""

    @classmethod
    def new(
        cls,
        trnsys_lib: Union[str, Path],
        type_lib_files: List[Union[str, Path]],
        input_file: Union[str, Path],
    ) -> "Simulation":
        """Create a new TRNSYS simulation.

        The directory containing the compiled TRNSYS library (`trnsys.dll`
        for Windows, `libtrnsys.so` for Linux) must also contain the required
        TRNSYS resource files (`Units.lab`, `Descrips.dat`, etc.).

        Usage example:
            trnsys_lib = "path/to/trnsys.dll"
            type_lib_files = ["path/to/types.dll", "path/to/user_type.dll"]
            input_file = "path/to/example.dck"
            sim = Simulation.new(trnsys_lib, type_lib_files, input_file)
            done = False
            while not done:
                done = sim.step_forward()
                value = sim.get_output_value(unit=7, output_number=1)
                print(f"Current value for output 1 of unit 7 is {value}")

        Args:
            trnsys_lib: Path to the compiled TRNSYS library.
            type_lib_files: List of paths to libraries containing Type subroutines.
            input_file: Path to the simulation's input (deck) file.

        Raises:
            FileNotFoundError: If the TRNSYS library or input file does not exist.
            DuplicateLibraryError: The `trnsys_lib` file is already in use.
            OSError: An error occurred loading `trnsys_lib`.
            TrnsysSetDirectoriesError
            TrnsysLoadInputFileError
        """
        trnsys_lib = Path(trnsys_lib)
        trnsys_lib_dir = trnsys_lib.parent  # use the lib's directory for all paths
        return cls(
            LoadedTrnsysLib(trnsys_lib),
            [Path(x) for x in type_lib_files],
            TrnsysDirectories(
                root=trnsys_lib_dir,
                exe=trnsys_lib_dir,
                user_lib=trnsys_lib_dir,
            ),
            Path(input_file),
        )

    def __init__(
        self,
        lib: TrnsysLib,
        type_lib_files: List[Path],
        dirs: TrnsysDirectories,
        input_file: Path,
    ):
        """Initialize a Simulation object."""
        error_code = lib.set_directories(dirs)
        if error_code:
            raise TrnsysSetDirectoriesError(error_code)

        error_code = lib.load_input_file(input_file, type_lib_files)
        if error_code:
            raise TrnsysLoadInputFileError(error_code)

        self.lib = lib
        self.dirs = dirs
        self.input_file = input_file

    def step_forward(self, steps: int = 1) -> bool:
        """Step the simulation forward.

        It is not possible to step a simulation beyond its final time.  Fewer
        steps than the requested number will be taken if `steps` is greater
        than the number of steps remaining in the simulation.

        Args:
            steps (int, optional): The number of steps to take.  Defaults to 1.

        Returns:
            - True if final time has been reached as a result of stepping forward.
            - False if more steps can be taken.

        Raises:
            ValueError: If `steps` is less than 1.
            TrnsysStepForwardError
        """
        if steps < 1:
            raise ValueError("Number of steps cannot be less than 1.")

        (done, error_code) = self.lib.step_forward(steps)
        if error_code:
            raise TrnsysStepForwardError(error_code)

        return done

    def get_current_time(self) -> float:
        """Return the current time of the simulation.

        Returns:
            float: The current simulation time.

        Raises:
            SimulationNotInitializedError
        """
        (value, error_code) = self.lib.get_current_time()
        if error_code:
            raise SimulationNotInitializedError

        return value

    def get_output_value(self, *, unit: int, output_number: int) -> float:
        """Return the current output value of a unit.

        Args:
            unit (int): The unit of interest.
            output_number (int): The output of interest.

        Returns:
            float: The current output value.

        Raises:
            TrnsysGetOutputValueError
        """
        (value, error_code) = self.lib.get_output_value(unit, output_number)
        if error_code:
            raise TrnsysGetOutputValueError(error_code)

        return value

    def set_input_value(self, *, unit: int, input_number: int, value: float) -> None:
        """Set an input value for a unit.

        Args:
            unit (int): The unit of interest.
            input_number (int): The input of interest.
            value (float): The input is set to this value.

        Raises:
            TrnsysSetInputValueError
        """
        error_code = self.lib.set_input_value(unit, input_number, value)
        if error_code:
            raise TrnsysSetInputValueError(error_code)

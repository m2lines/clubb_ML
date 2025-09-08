import xarray as xr
import numpy as np
import argparse
import re
from pathlib import Path
from numpy.typing import NDArray

NAME_DTYPE = {
    "thvm": np.float64,
    "thlm": np.float64,
    "rtm": np.float64,
    "em": np.float64,
    "exner": np.float64,
    "p_in_Pa": np.float64,
    "thv_ds": np.float64,
    "Lscale": np.float64,
    "Lscale_up": np.float64,
    "Lscale_down": np.float64,
    "mu": np.float64,
    "lmin": np.float64,
    "saturation_formula": np.int32,
    "l_implemented": np.bool,
}

INT_REGEX = re.compile(r"\s*[0-9]+\s*")

# Not a true comma-seperated list of real numbers
# Assumes Fortran E-formating
FLOAT_LIST = re.compile(r"(\s*[0-9]+\.[0-9]*E[+-][0-9]+,?\s*)+")


def parse_grid_info(path: Path | str) -> dict[str, int | NDArray]:
    """Load the data from the file with grid metadata.

    The grid metadata file is a list of lines that follow a pattern:
     <name> = <int> | <comma-sep-list-of-floats>

    Note
    ----
    We are lazy when reading the list of floats and we assume they were printed
    with the Fortran's E-edit descriptor.
    """
    with open(path, "r") as f:
        grid_lines = f.readlines()

    def process_line(line):
        key, value = line.split("=")
        if INT_REGEX.fullmatch(value):
            return key.strip(), int(value)
        elif FLOAT_LIST.fullmatch(value):
            return key.strip(), np.fromstring(value, sep=",")
        else:
            raise ValueError(f"Could not convert pair {key}: {value}")

    return dict(map(process_line, grid_lines))


def load_to_numpy(data_dir: Path, var: str, dtype: np.dtype) -> NDArray:
    """Loads a CSV for a variable from the output directory"""
    path = data_dir / f"{var}.csv"
    data = np.genfromtxt(path, delimiter=",", dtype=dtype, autostrip=True)
    return data


def main(data_dir: str | Path, output_file: str | Path) -> None:
    data_dir = Path(data_dir)

    if not data_dir.is_dir():
        raise ValueError(f"Data directory {data_dir} is not a directory")
    elif not data_dir.exists():
        raise ValueError(f"Data directory {data_dir} does not exist")

    grid_dict = parse_grid_info(data_dir / "grid_file")
    arguments_dict = {
        var: load_to_numpy(data_dir, var, dtype) for var, dtype in NAME_DTYPE.items()
    }

    xr.Dataset(
        data_vars={
            # Inputs
            "thvm": (["samples", "zt"], arguments_dict["thvm"]),
            "thlm": (["samples", "zt"], arguments_dict["thlm"]),
            "rtm": (["samples", "zt"], arguments_dict["rtm"]),
            "em": (["samples", "zm"], arguments_dict["em"]),
            "exner": (["samples", "zt"], arguments_dict["exner"]),
            "p_in_Pa": (["samples", "zt"], arguments_dict["p_in_Pa"]),
            "thv_ds": (["samples", "zt"], arguments_dict["thv_ds"]),
            "mu": (["samples"], arguments_dict["mu"]),
            "lmin": (["samples"], arguments_dict["lmin"]),
            "saturation_formula": (["samples"], arguments_dict["saturation_formula"]),
            "l_implemented": (["samples"], arguments_dict["l_implemented"]),
            # Outputs
            "Lscale": (["samples", "zt"], arguments_dict["Lscale"]),
            "Lscale_up": (["samples", "zt"], arguments_dict["Lscale_up"]),
            "Lscale_down": (["samples", "zt"], arguments_dict["Lscale_down"]),
            # Dependent grid parameters
            "invrs_dzm": (["zm"], grid_dict["invrs_dzm"]),
            "invrs_dzt": (["zt"], grid_dict["invrs_dzt"]),
        },
        coords={
            "zt": grid_dict["zt"],
            "zm": grid_dict["zm"],
        },
        attrs={k: v for k, v in grid_dict.items() if np.isscalar(v)},
    ).to_netcdf(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Collects the single column 'compute_mixing_length' function
        patameters into a NetCDF file.
        """
    )
    parser.add_argument(
        "data_dir", type=Path, help="Path to the directory with the data"
    )
    parser.add_argument("output", type=Path, help="Output path for the NetCDF file")
    args = parser.parse_args()
    main(args.data_dir, args.output)

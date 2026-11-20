"""
generate static/favicon.svg: a spectrum analyser screen with a noise floor and one carrier.
two separate steps. the signal is simulated with numpy, the svg is drawn from its levels
and knows nothing about how they were made. needs numpy, the site build itself does not.
usage: python make_favicon.py [out.svg]
"""

import sys
from pathlib import Path

import numpy as np

# signal
N_BINS = 13  # points of the trace, one corner of the polyline each
CARRIER_BIN = 6  # the middle bin
CARRIER_DB = 16.5  # carrier level above the mean noise power
N_AVERAGES = 8  # sweeps averaged, fewer give a rougher floor
SEED = 44238  # fixed, so the icon can be regenerated; change it for another noise floor

# drawing, all lengths are in the svg's own units
OUTPUT = Path(__file__).parent.parent / "static" / "favicon.svg"
VIEW_BOX = "1.5 1.5 29 29"
FRAME = {"x": 3, "y": 3, "width": 26, "height": 26, "rx": 3.2}
FRAME_WIDTH = 2.9
TRACE_WIDTH = 2
TRACE_LEFT = 7  # where the trace starts and ends, inside the frame
TRACE_RIGHT = 25
FLOOR_Y = 23.5  # y of 0 dB, the mean noise floor
UNITS_PER_DB = 1.0  # screen units per dB, the carrier sets the height
MARGIN = 1.5  # the trace must stay this far inside the frame

# black on light themes, white on dark ones
STYLE = (
    "@media (prefers-color-scheme: dark) "
    '{ [stroke="#000"] { stroke: #fff; } [fill="#000"] { fill: #fff; } }'
)


# step 1: the signal

def noise_power(rng: np.random.Generator, n_bins: int, n_averages: int) -> np.ndarray:
    """linear noise power per bin, averaged over several sweeps, mean power is 1"""
    shape = (n_averages, n_bins)
    # complex gaussian noise, so its power is exponentially distributed
    real = rng.normal(size=shape)
    imag = rng.normal(size=shape)
    power = (real**2 + imag**2) / 2
    return power.mean(axis=0)


def add_carrier(power: np.ndarray, bin_index: int, carrier_db: float) -> np.ndarray:
    """add a carrier of the given level to one bin"""
    if not 0 <= bin_index < len(power):
        raise ValueError(f"carrier bin {bin_index} is outside the {len(power)} bins")
    with_carrier = power.copy()
    with_carrier[bin_index] += 10 ** (carrier_db / 10)
    return with_carrier


def to_db(power: np.ndarray) -> np.ndarray:
    """convert linear power to dB, 0 dB is the mean noise power"""
    return 10 * np.log10(power)


def simulate_levels() -> np.ndarray:
    """trace levels in dB, one per bin, from low to high frequency"""
    rng = np.random.default_rng(SEED)
    power = noise_power(rng, N_BINS, N_AVERAGES)
    power = add_carrier(power, CARRIER_BIN, CARRIER_DB)
    return to_db(power)


# step 2: the svg

def to_points(level_db: np.ndarray) -> list[tuple[float, float]]:
    """map the levels to x and y in the svg, y points down"""
    xs = np.linspace(TRACE_LEFT, TRACE_RIGHT, len(level_db))
    ys = FLOOR_Y - level_db * UNITS_PER_DB
    return list(zip(xs.tolist(), ys.tolist()))


def check_inside_frame(points: list[tuple[float, float]]) -> None:
    """raise if the trace would touch the frame"""
    top = FRAME["y"] + FRAME_WIDTH / 2 + MARGIN
    bottom = FRAME["y"] + FRAME["height"] - FRAME_WIDTH / 2 - MARGIN
    for _, y in points:
        if not top <= y <= bottom:
            raise ValueError(f"y = {y:.1f} is outside {top:.1f} ... {bottom:.1f}, lower the carrier or the noise")


def number(value: float) -> str:
    """shortest text for a coordinate, rounded to 0.1"""
    return f"{value:.1f}".removesuffix(".0")


def path_data(points: list[tuple[float, float]]) -> str:
    """svg path through all points"""
    parts = [f"{number(x)} {number(y)}" for x, y in points]
    return "M" + "L".join(parts)


def stroke_attributes(width: float) -> str:
    return f'stroke="#000" stroke-linecap="round" stroke-linejoin="round" fill="none" stroke-width="{width}"'


def build_svg(points: list[tuple[float, float]]) -> str:
    """the whole icon as text"""
    frame = " ".join(f'{name}="{value}"' for name, value in FRAME.items())
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEW_BOX}">'
        f"<style>{STYLE}</style>"
        f"<rect {frame} {stroke_attributes(FRAME_WIDTH)}/>"
        f'<path d="{path_data(points)}" {stroke_attributes(TRACE_WIDTH)}/>'
        "</svg>\n"
    )


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT
    points = to_points(simulate_levels())
    check_inside_frame(points)
    output.write_text(build_svg(points))
    print(f"wrote {output}")

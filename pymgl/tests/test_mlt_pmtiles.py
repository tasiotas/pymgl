import json
import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pymgl import Map


DEFAULT_MLT_FIXTURE = Path("/Volumes/PrettyMapsDatasets/Planetiler/bc_low.pmtiles")


def _bc_style(path: Path) -> str:
    return json.dumps(
        {
            "version": 8,
            "sources": {
                "bc": {
                    "type": "vector",
                    "url": f"pmtiles://{path.resolve().as_uri()}",
                }
            },
            "layers": [
                {
                    "id": "background",
                    "type": "background",
                    "paint": {"background-color": "#dcecf3"},
                },
                {
                    "id": "global-land",
                    "type": "fill",
                    "source": "bc",
                    "source-layer": "global_land",
                    "paint": {"fill-color": "#e6dfc8"},
                },
                {
                    "id": "land",
                    "type": "fill",
                    "source": "bc",
                    "source-layer": "land",
                    "paint": {"fill-color": "#d8d0b4"},
                },
                {
                    "id": "water",
                    "type": "fill",
                    "source": "bc",
                    "source-layer": "water_polygons",
                    "paint": {"fill-color": "#8fc9df"},
                },
                {
                    "id": "roads",
                    "type": "line",
                    "source": "bc",
                    "source-layer": "highways",
                    "paint": {
                        "line-color": "#d46a4c",
                        "line-width": ["interpolate", ["linear"], ["zoom"], 5, 0.5, 12, 2.5],
                    },
                },
                {
                    "id": "railways",
                    "type": "line",
                    "source": "bc",
                    "source-layer": "railways",
                    "paint": {"line-color": "#555555", "line-width": 1},
                },
            ],
        }
    )


def test_local_pmtiles_mlt_render():
    path = Path(os.environ.get("PYMGL_MLT_PMTILES", DEFAULT_MLT_FIXTURE))
    if not path.is_file():
        pytest.skip("set PYMGL_MLT_PMTILES to an MLT-encoded PMTiles archive")

    image_data = Map(
        _bc_style(path),
        width=512,
        height=512,
        longitude=-122.5464115,
        latitude=50.1031155,
        zoom=7,
    ).renderPNG()

    assert image_data.startswith(b"\x89PNG\r\n\x1a\n")
    image = Image.open(BytesIO(image_data)).convert("RGBA")
    assert image.size == (512, 512)
    assert len(image.getcolors(maxcolors=512 * 512)) > 100

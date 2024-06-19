from unittest.mock import patch

import pytest

from ophyd_async.core import DeviceCollector, StaticDirectoryProvider
from ophyd_async.sim import demo


@pytest.fixture
async def writer(tmp_path) -> demo.SimPatternDetectorWriter:
    async with DeviceCollector(mock=True):
        driver = demo.PatternGenerator()
    directory = StaticDirectoryProvider(tmp_path)

    return demo.SimPatternDetectorWriter(driver, directory)


async def test_correct_descriptor_doc_after_open(writer: demo.SimPatternDetectorWriter):
    with patch("ophyd_async.core._signal.wait_for_value", return_value=None):
        descriptor = await writer.open()

    assert descriptor == {
        "_entry_data_data": {
            "source": "soft:///entry/data/data",
            "shape": (1, 240, 320),
            "dtype": "array",
            "external": "STREAM:",
        },
        "_entry_sum": {
            "source": "soft:///entry/sum",
            "shape": (1,),
            "dtype": "array",
            "external": "STREAM:",
        },
    }

    await writer.close()


async def test_collect_stream_docs(writer: demo.SimPatternDetectorWriter):
    await writer.open()
    [item async for item in writer.collect_stream_docs(1)]
    assert writer.pattern_generator._handle_for_h5_file

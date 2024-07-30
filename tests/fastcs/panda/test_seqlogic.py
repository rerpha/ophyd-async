import asyncio

import pytest

from ophyd_async.core import DEFAULT_TIMEOUT, DeviceCollector
from ophyd_async.core._mock_signal_utils import set_mock_value
from ophyd_async.epics.pvi import fill_pvi_entries
from ophyd_async.fastcs.panda import CommonPandaBlocks
from ophyd_async.fastcs.panda._trigger import PosTrigSeqInfo, PosTrigSeqLogic


@pytest.fixture
async def mock_panda():
    class Panda(CommonPandaBlocks):
        def __init__(self, prefix: str, name: str = ""):
            self._prefix = prefix
            super().__init__(name)

        async def connect(self, mock: bool = False, timeout: float = DEFAULT_TIMEOUT):
            await fill_pvi_entries(
                self, self._prefix + "PVI", timeout=timeout, mock=mock
            )
            await super().connect(mock=mock, timeout=timeout)

    async with DeviceCollector(mock=True):
        mock_panda = Panda("PANDAQSRV:", "mock_panda")

    assert mock_panda.name == "mock_panda"
    return mock_panda


async def test_populate_seq_table(mock_panda):
    async def set_active(value: bool):
        await asyncio.sleep(0.1)
        set_mock_value(mock_panda.seq[1].active, value)

    trigger_logic = PosTrigSeqLogic(mock_panda.seq[1])
    info = PosTrigSeqInfo(prescale_as_us=1)
    await trigger_logic.prepare(info)
    # await asyncio.gather(trigger_logic.kickoff(), set_active(True))
    # await asyncio.gather(trigger_logic.complete(), set_active(False))

from typing import List

from .........Internal.Core import Core
from .........Internal.CommandsGroup import CommandsGroup
from .........Internal import Conversions
from .........Internal.Types import DataType
from .........Internal.ArgSingleList import ArgSingleList
from .........Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PlSubframeCls:
	"""PlSubframe commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plSubframe", core, parent)

	def set(self, cell_name: str, symbols: List[int]) -> None:
		"""SCPI: [CONFigure]:SIGNaling:LTE:CELL:UESCheduling:LAA:RBURst:PLSubframe \n
		Snippet: driver.configure.signaling.lte.cell.ueScheduling.laa.rburst.plSubframe.set(cell_name = '1', symbols = [1, 2, 3]) \n
		No command help available \n
			:param cell_name: No help available
			:param symbols: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle.as_open_list('symbols', symbols, DataType.IntegerList, None))
		self._core.io.write(f'CONFigure:SIGNaling:LTE:CELL:UESCheduling:LAA:RBURst:PLSubframe {param}'.rstrip())

	def get(self, cell_name: str) -> List[int]:
		"""SCPI: [CONFigure]:SIGNaling:LTE:CELL:UESCheduling:LAA:RBURst:PLSubframe \n
		Snippet: value: List[int] = driver.configure.signaling.lte.cell.ueScheduling.laa.rburst.plSubframe.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: symbols: No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_bin_or_ascii_int_list(f'CONFigure:SIGNaling:LTE:CELL:UESCheduling:LAA:RBURst:PLSubframe? {param}')
		return response

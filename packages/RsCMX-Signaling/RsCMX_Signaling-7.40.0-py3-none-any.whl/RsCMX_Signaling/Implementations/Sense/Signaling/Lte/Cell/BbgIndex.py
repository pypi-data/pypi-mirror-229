from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BbgIndexCls:
	"""BbgIndex commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bbgIndex", core, parent)

	def get(self, cell_name: str) -> int:
		"""SCPI: SENSe:SIGNaling:LTE:CELL:BBGindex \n
		Snippet: value: int = driver.sense.signaling.lte.cell.bbgIndex.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: bb_group_index: No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_str(f'SENSe:SIGNaling:LTE:CELL:BBGindex? {param}')
		return Conversions.str_to_int(response)

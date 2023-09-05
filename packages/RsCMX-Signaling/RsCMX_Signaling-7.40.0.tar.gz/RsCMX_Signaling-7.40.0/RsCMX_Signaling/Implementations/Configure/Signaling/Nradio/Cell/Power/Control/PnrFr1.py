from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........Internal.Types import DataType
from ........Internal.ArgSingleList import ArgSingleList
from ........Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PnrFr1Cls:
	"""PnrFr1 commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pnrFr1", core, parent)

	def set(self, cell_name: str, power: float or bool) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:POWer:CONTrol:PNRFr1 \n
		Snippet: driver.configure.signaling.nradio.cell.power.control.pnrFr1.set(cell_name = '1', power = 1.0) \n
		No command help available \n
			:param cell_name: No help available
			:param power: (float or boolean) No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('power', power, DataType.FloatExt))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PNRFr1 {param}'.rstrip())

	def get(self, cell_name: str) -> float or bool:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:POWer:CONTrol:PNRFr1 \n
		Snippet: value: float or bool = driver.configure.signaling.nradio.cell.power.control.pnrFr1.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: power: (float or boolean) No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_str(f'CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PNRFr1? {param}')
		return Conversions.str_to_float_or_bool(response)

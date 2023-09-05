from ..........Internal.Core import Core
from ..........Internal.CommandsGroup import CommandsGroup
from ..........Internal import Conversions
from ..........Internal.Types import DataType
from ..........Internal.ArgSingleList import ArgSingleList
from ..........Internal.ArgSingle import ArgSingle
from .......... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DirectionCls:
	"""Direction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def set(self, cell_name: str, direction: enums.TpcDirection) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:RPTolerance:DIRection \n
		Snippet: driver.configure.signaling.nradio.cell.power.control.tpControl.rpTolerance.direction.set(cell_name = '1', direction = enums.TpcDirection.ALTernating) \n
		No command help available \n
			:param cell_name: No help available
			:param direction: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('direction', direction, DataType.Enum, enums.TpcDirection))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:RPTolerance:DIRection {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self, cell_name: str) -> enums.TpcDirection:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:RPTolerance:DIRection \n
		Snippet: value: enums.TpcDirection = driver.configure.signaling.nradio.cell.power.control.tpControl.rpTolerance.direction.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: direction: No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_str(f'CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:RPTolerance:DIRection? {param}')
		return Conversions.str_to_scalar_enum(response, enums.TpcDirection)

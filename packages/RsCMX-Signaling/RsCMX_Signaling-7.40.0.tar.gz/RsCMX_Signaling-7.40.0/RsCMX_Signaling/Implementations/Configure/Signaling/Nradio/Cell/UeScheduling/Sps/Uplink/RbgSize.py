from .........Internal.Core import Core
from .........Internal.CommandsGroup import CommandsGroup
from .........Internal import Conversions
from .........Internal.Types import DataType
from .........Internal.ArgSingleList import ArgSingleList
from .........Internal.ArgSingle import ArgSingle
from ......... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RbgSizeCls:
	"""RbgSize commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rbgSize", core, parent)

	def set(self, cell_name: str, rgb_size: enums.RgbSize) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:UESCheduling:SPS:UL:RBGSize \n
		Snippet: driver.configure.signaling.nradio.cell.ueScheduling.sps.uplink.rbgSize.set(cell_name = '1', rgb_size = enums.RgbSize.CON1) \n
		No command help available \n
			:param cell_name: No help available
			:param rgb_size: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('rgb_size', rgb_size, DataType.Enum, enums.RgbSize))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:UESCheduling:SPS:UL:RBGSize {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self, cell_name: str) -> enums.RgbSize:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:UESCheduling:SPS:UL:RBGSize \n
		Snippet: value: enums.RgbSize = driver.configure.signaling.nradio.cell.ueScheduling.sps.uplink.rbgSize.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: rgb_size: No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_str(f'CONFigure:SIGNaling:NRADio:CELL:UESCheduling:SPS:UL:RBGSize? {param}')
		return Conversions.str_to_scalar_enum(response, enums.RgbSize)

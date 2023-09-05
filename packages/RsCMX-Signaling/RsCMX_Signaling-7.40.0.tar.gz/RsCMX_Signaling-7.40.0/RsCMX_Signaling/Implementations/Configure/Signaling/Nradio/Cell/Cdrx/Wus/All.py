from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........Internal.Types import DataType
from ........Internal.StructBase import StructBase
from ........Internal.ArgStruct import ArgStruct
from ........Internal.ArgSingleList import ArgSingleList
from ........Internal.ArgSingle import ArgSingle
from ........ import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AllCls:
	"""All commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("all", core, parent)

	def set(self, cell_name: str, enable: bool, mode: enums.WusMode = None, ratio_on_off: float = None) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:CDRX:WUS:ALL \n
		Snippet: driver.configure.signaling.nradio.cell.cdrx.wus.all.set(cell_name = '1', enable = False, mode = enums.WusMode.RATio, ratio_on_off = 1.0) \n
		No command help available \n
			:param cell_name: No help available
			:param enable: No help available
			:param mode: No help available
			:param ratio_on_off: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('enable', enable, DataType.Boolean), ArgSingle('mode', mode, DataType.Enum, enums.WusMode, is_optional=True), ArgSingle('ratio_on_off', ratio_on_off, DataType.Float, None, is_optional=True))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:CDRX:WUS:ALL {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Enable: bool: No parameter help available
			- Mode: enums.WusMode: No parameter help available
			- Ratio_On_Off: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_bool('Enable'),
			ArgStruct.scalar_enum('Mode', enums.WusMode),
			ArgStruct.scalar_float('Ratio_On_Off')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Enable: bool = None
			self.Mode: enums.WusMode = None
			self.Ratio_On_Off: float = None

	def get(self, cell_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:CDRX:WUS:ALL \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.cdrx.wus.all.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:CDRX:WUS:ALL? {param}', self.__class__.GetStruct())

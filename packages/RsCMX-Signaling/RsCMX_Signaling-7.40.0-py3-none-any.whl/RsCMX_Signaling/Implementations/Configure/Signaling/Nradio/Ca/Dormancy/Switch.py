from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from .......Internal.Types import DataType
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from .......Internal.ArgSingleList import ArgSingleList
from .......Internal.ArgSingle import ArgSingle
from ....... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SwitchCls:
	"""Switch commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("switch", core, parent)

	def set(self, cell_group_name: str, dormant: bool, indication_mode: enums.IndicationMode) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CA:DORMancy:SWITch \n
		Snippet: driver.configure.signaling.nradio.ca.dormancy.switch.set(cell_group_name = '1', dormant = False, indication_mode = enums.IndicationMode.AUTO) \n
		No command help available \n
			:param cell_group_name: No help available
			:param dormant: No help available
			:param indication_mode: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_group_name', cell_group_name, DataType.String), ArgSingle('dormant', dormant, DataType.Boolean), ArgSingle('indication_mode', indication_mode, DataType.Enum, enums.IndicationMode))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CA:DORMancy:SWITch {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Dormant: bool: No parameter help available
			- Indication_Mode: enums.IndicationMode: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_bool('Dormant'),
			ArgStruct.scalar_enum('Indication_Mode', enums.IndicationMode)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Dormant: bool = None
			self.Indication_Mode: enums.IndicationMode = None

	def get(self, cell_group_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CA:DORMancy:SWITch \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.ca.dormancy.switch.get(cell_group_name = '1') \n
		No command help available \n
			:param cell_group_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_group_name)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CA:DORMancy:SWITch? {param}', self.__class__.GetStruct())

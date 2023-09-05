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

	def set(self, cell_name: str, enable: bool, follow_mode: enums.ModeBfollow = None, beam_lock_mode: enums.Mode = None, index: int = None) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BEAM:FOLLowing:ALL \n
		Snippet: driver.configure.signaling.nradio.cell.beam.following.all.set(cell_name = '1', enable = False, follow_mode = enums.ModeBfollow.AUTO, beam_lock_mode = enums.Mode.BINDex, index = 1) \n
		No command help available \n
			:param cell_name: No help available
			:param enable: No help available
			:param follow_mode: No help available
			:param beam_lock_mode: No help available
			:param index: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('enable', enable, DataType.Boolean), ArgSingle('follow_mode', follow_mode, DataType.Enum, enums.ModeBfollow, is_optional=True), ArgSingle('beam_lock_mode', beam_lock_mode, DataType.Enum, enums.Mode, is_optional=True), ArgSingle('index', index, DataType.Integer, None, is_optional=True))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:BEAM:FOLLowing:ALL {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Enable: bool: No parameter help available
			- Follow_Mode: enums.ModeBfollow: No parameter help available
			- Beam_Lock_Mode: enums.Mode: No parameter help available
			- Index: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_bool('Enable'),
			ArgStruct.scalar_enum('Follow_Mode', enums.ModeBfollow),
			ArgStruct.scalar_enum('Beam_Lock_Mode', enums.Mode),
			ArgStruct.scalar_int('Index')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Enable: bool = None
			self.Follow_Mode: enums.ModeBfollow = None
			self.Beam_Lock_Mode: enums.Mode = None
			self.Index: int = None

	def get(self, cell_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BEAM:FOLLowing:ALL \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.beam.following.all.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:BEAM:FOLLowing:ALL? {param}', self.__class__.GetStruct())

from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from .......Internal.Types import DataType
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from .......Internal.ArgSingleList import ArgSingleList
from .......Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DltShiftCls:
	"""DltShift commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dltShift", core, parent)

	def set(self, cell_name: str, delta: int) -> None:
		"""SCPI: [CONFigure]:SIGNaling:LTE:CELL:TIMing:DLTShift \n
		Snippet: driver.configure.signaling.lte.cell.timing.dltShift.set(cell_name = '1', delta = 1) \n
		No command help available \n
			:param cell_name: No help available
			:param delta: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('delta', delta, DataType.Integer))
		self._core.io.write(f'CONFigure:SIGNaling:LTE:CELL:TIMing:DLTShift {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Delta: int: No parameter help available
			- Total: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Delta'),
			ArgStruct.scalar_int('Total')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Delta: int = None
			self.Total: int = None

	def get(self, cell_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:LTE:CELL:TIMing:DLTShift \n
		Snippet: value: GetStruct = driver.configure.signaling.lte.cell.timing.dltShift.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:LTE:CELL:TIMing:DLTShift? {param}', self.__class__.GetStruct())

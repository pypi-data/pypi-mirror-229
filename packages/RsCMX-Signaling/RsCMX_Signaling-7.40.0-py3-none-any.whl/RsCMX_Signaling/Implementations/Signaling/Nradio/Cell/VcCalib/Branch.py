from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BranchCls:
	"""Branch commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("branch", core, parent)

	# noinspection PyTypeChecker
	class FetchStruct(StructBase):
		"""Response structure. Fields: \n
			- Branch_1: float: No parameter help available
			- Branch_2: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_float('Branch_1'),
			ArgStruct.scalar_float('Branch_2')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Branch_1: float = None
			self.Branch_2: float = None

	def fetch(self, cell_name: str) -> FetchStruct:
		"""SCPI: FETCh:SIGNaling:NRADio:CELL:VCCalib:BRANch \n
		Snippet: value: FetchStruct = driver.signaling.nradio.cell.vcCalib.branch.fetch(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: structure: for return value, see the help for FetchStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		return self._core.io.query_struct(f'FETCh:SIGNaling:NRADio:CELL:VCCalib:BRANch? {param}', self.__class__.FetchStruct())

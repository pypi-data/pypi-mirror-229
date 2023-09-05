from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.Types import DataType
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct
from ......Internal.ArgSingleList import ArgSingleList
from ......Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdsCls:
	"""Thresholds commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("thresholds", core, parent)

	def set(self, cell_name: str, ncell_name: str, threshold_low: float, threshold_high: float) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:NCELl:THResholds \n
		Snippet: driver.configure.signaling.nradio.ncell.thresholds.set(cell_name = '1', ncell_name = '1', threshold_low = 1.0, threshold_high = 1.0) \n
		No command help available \n
			:param cell_name: No help available
			:param ncell_name: No help available
			:param threshold_low: No help available
			:param threshold_high: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('ncell_name', ncell_name, DataType.String), ArgSingle('threshold_low', threshold_low, DataType.Float), ArgSingle('threshold_high', threshold_high, DataType.Float))
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:NCELl:THResholds {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Threshold_Low: float: No parameter help available
			- Threshold_High: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_float('Threshold_Low'),
			ArgStruct.scalar_float('Threshold_High')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Threshold_Low: float = None
			self.Threshold_High: float = None

	def get(self, cell_name: str, ncell_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:NCELl:THResholds \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.ncell.thresholds.get(cell_name = '1', ncell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:param ncell_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('ncell_name', ncell_name, DataType.String))
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:NCELl:THResholds? {param}'.rstrip(), self.__class__.GetStruct())

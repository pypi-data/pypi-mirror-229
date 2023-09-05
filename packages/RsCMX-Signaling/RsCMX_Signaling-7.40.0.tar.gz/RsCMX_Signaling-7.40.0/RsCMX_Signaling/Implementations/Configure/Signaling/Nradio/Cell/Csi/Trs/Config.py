from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........Internal.StructBase import StructBase
from ........Internal.ArgStruct import ArgStruct
from ........ import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ConfigCls:
	"""Config commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("config", core, parent)

	# noinspection PyTypeChecker
	class SetStruct(StructBase):
		"""Structure for setting input parameters. Fields: \n
			- Cell_Name: str: No parameter help available
			- Bw_Selection: enums.BwSelection: No parameter help available
			- Slot_Offset: int: No parameter help available
			- Symbol_Pair: enums.SymbolPair: No parameter help available
			- Periodicity: enums.TrsPeriodicity: No parameter help available
			- No_Consec_Slots: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_str('Cell_Name'),
			ArgStruct.scalar_enum('Bw_Selection', enums.BwSelection),
			ArgStruct.scalar_int('Slot_Offset'),
			ArgStruct.scalar_enum('Symbol_Pair', enums.SymbolPair),
			ArgStruct.scalar_enum('Periodicity', enums.TrsPeriodicity),
			ArgStruct.scalar_int('No_Consec_Slots')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Cell_Name: str = None
			self.Bw_Selection: enums.BwSelection = None
			self.Slot_Offset: int = None
			self.Symbol_Pair: enums.SymbolPair = None
			self.Periodicity: enums.TrsPeriodicity = None
			self.No_Consec_Slots: int = None

	def set(self, structure: SetStruct) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:CSI:TRS:CONFig \n
		Snippet with structure: \n
		structure = driver.configure.signaling.nradio.cell.csi.trs.config.SetStruct() \n
		structure.Cell_Name: str = '1' \n
		structure.Bw_Selection: enums.BwSelection = enums.BwSelection.ALL \n
		structure.Slot_Offset: int = 1 \n
		structure.Symbol_Pair: enums.SymbolPair = enums.SymbolPair.S04 \n
		structure.Periodicity: enums.TrsPeriodicity = enums.TrsPeriodicity.P10 \n
		structure.No_Consec_Slots: int = 1 \n
		driver.configure.signaling.nradio.cell.csi.trs.config.set(structure) \n
		No command help available \n
			:param structure: for set value, see the help for SetStruct structure arguments.
		"""
		self._core.io.write_struct(f'CONFigure:SIGNaling:NRADio:CELL:CSI:TRS:CONFig', structure)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Bw_Selection: enums.BwSelection: No parameter help available
			- Slot_Offset: int: No parameter help available
			- Symbol_Pair: enums.SymbolPair: No parameter help available
			- Periodicity: enums.TrsPeriodicity: No parameter help available
			- No_Consec_Slots: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_enum('Bw_Selection', enums.BwSelection),
			ArgStruct.scalar_int('Slot_Offset'),
			ArgStruct.scalar_enum('Symbol_Pair', enums.SymbolPair),
			ArgStruct.scalar_enum('Periodicity', enums.TrsPeriodicity),
			ArgStruct.scalar_int('No_Consec_Slots')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Bw_Selection: enums.BwSelection = None
			self.Slot_Offset: int = None
			self.Symbol_Pair: enums.SymbolPair = None
			self.Periodicity: enums.TrsPeriodicity = None
			self.No_Consec_Slots: int = None

	def get(self, cell_name: str) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:CSI:TRS:CONFig \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.csi.trs.config.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:CSI:TRS:CONFig? {param}', self.__class__.GetStruct())

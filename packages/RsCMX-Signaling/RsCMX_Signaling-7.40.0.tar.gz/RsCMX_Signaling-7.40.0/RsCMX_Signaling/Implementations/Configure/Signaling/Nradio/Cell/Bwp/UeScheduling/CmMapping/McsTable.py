from .........Internal.Core import Core
from .........Internal.CommandsGroup import CommandsGroup
from .........Internal import Conversions
from .........Internal.Types import DataType
from .........Internal.StructBase import StructBase
from .........Internal.ArgStruct import ArgStruct
from .........Internal.ArgSingleList import ArgSingleList
from .........Internal.ArgSingle import ArgSingle
from ......... import enums
from ......... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class McsTableCls:
	"""McsTable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mcsTable", core, parent)

	def set(self, cell_name: str, mcs_table: enums.McsTableC, predefined_3_gpp: enums.ConfigType = None, bwParts=repcap.BwParts.Default) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:CMMapping:MCSTable \n
		Snippet: driver.configure.signaling.nradio.cell.bwp.ueScheduling.cmMapping.mcsTable.set(cell_name = '1', mcs_table = enums.McsTableC.AUTO, predefined_3_gpp = enums.ConfigType.T1, bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param cell_name: No help available
			:param mcs_table: No help available
			:param predefined_3_gpp: No help available
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('mcs_table', mcs_table, DataType.Enum, enums.McsTableC), ArgSingle('predefined_3_gpp', predefined_3_gpp, DataType.Enum, enums.ConfigType, is_optional=True))
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:CMMapping:MCSTable {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Mcs_Table: enums.McsTableC: No parameter help available
			- Predefined_3_Gpp: enums.ConfigType: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_enum('Mcs_Table', enums.McsTableC),
			ArgStruct.scalar_enum('Predefined_3_Gpp', enums.ConfigType)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Mcs_Table: enums.McsTableC = None
			self.Predefined_3_Gpp: enums.ConfigType = None

	def get(self, cell_name: str, bwParts=repcap.BwParts.Default) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:CMMapping:MCSTable \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.bwp.ueScheduling.cmMapping.mcsTable.get(cell_name = '1', bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param cell_name: No help available
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:CMMapping:MCSTable? {param}', self.__class__.GetStruct())

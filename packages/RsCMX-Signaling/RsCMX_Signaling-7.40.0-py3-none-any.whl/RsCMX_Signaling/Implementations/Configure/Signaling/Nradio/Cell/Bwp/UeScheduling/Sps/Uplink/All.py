from ..........Internal.Core import Core
from ..........Internal.CommandsGroup import CommandsGroup
from ..........Internal import Conversions
from ..........Internal.StructBase import StructBase
from ..........Internal.ArgStruct import ArgStruct
from .......... import enums
from .......... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AllCls:
	"""All commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("all", core, parent)

	# noinspection PyTypeChecker
	class SetStruct(StructBase):
		"""Structure for setting input parameters. Contains optional setting parameters. Fields: \n
			- Cell_Name: str: No parameter help available
			- Periodicity: enums.SpsPeriodicity: No parameter help available
			- Mcs_Table: enums.McsTableB: No parameter help available
			- Alevel: enums.Level: No parameter help available
			- Search_Space_Id: int: No parameter help available
			- Resource_Allocation_Type: enums.ResourceAllocationType: No parameter help available
			- Rgb_Size: enums.RgbSize: No parameter help available
			- No_Harq: int: No parameter help available
			- Enable_Tp: bool: No parameter help available
			- Timer: int: No parameter help available
			- Rep_K: enums.PdcchFormatB: No parameter help available
			- Rep_Kr_V: enums.Spreset: No parameter help available
			- Position: enums.SpsPosition: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_str('Cell_Name'),
			ArgStruct.scalar_enum_optional('Periodicity', enums.SpsPeriodicity),
			ArgStruct.scalar_enum_optional('Mcs_Table', enums.McsTableB),
			ArgStruct.scalar_enum_optional('Alevel', enums.Level),
			ArgStruct.scalar_int_optional('Search_Space_Id'),
			ArgStruct.scalar_enum_optional('Resource_Allocation_Type', enums.ResourceAllocationType),
			ArgStruct.scalar_enum_optional('Rgb_Size', enums.RgbSize),
			ArgStruct.scalar_int_optional('No_Harq'),
			ArgStruct.scalar_bool_optional('Enable_Tp'),
			ArgStruct.scalar_int_optional('Timer'),
			ArgStruct.scalar_enum_optional('Rep_K', enums.PdcchFormatB),
			ArgStruct.scalar_enum_optional('Rep_Kr_V', enums.Spreset),
			ArgStruct.scalar_enum_optional('Position', enums.SpsPosition)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Cell_Name: str = None
			self.Periodicity: enums.SpsPeriodicity = None
			self.Mcs_Table: enums.McsTableB = None
			self.Alevel: enums.Level = None
			self.Search_Space_Id: int = None
			self.Resource_Allocation_Type: enums.ResourceAllocationType = None
			self.Rgb_Size: enums.RgbSize = None
			self.No_Harq: int = None
			self.Enable_Tp: bool = None
			self.Timer: int = None
			self.Rep_K: enums.PdcchFormatB = None
			self.Rep_Kr_V: enums.Spreset = None
			self.Position: enums.SpsPosition = None

	def set(self, structure: SetStruct, bwParts=repcap.BwParts.Default) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:SPS:UL:ALL \n
		Snippet with structure: \n
		structure = driver.configure.signaling.nradio.cell.bwp.ueScheduling.sps.uplink.all.SetStruct() \n
		structure.Cell_Name: str = '1' \n
		structure.Periodicity: enums.SpsPeriodicity = enums.SpsPeriodicity.S1 \n
		structure.Mcs_Table: enums.McsTableB = enums.McsTableB.L64 \n
		structure.Alevel: enums.Level = enums.Level.AL1 \n
		structure.Search_Space_Id: int = 1 \n
		structure.Resource_Allocation_Type: enums.ResourceAllocationType = enums.ResourceAllocationType.DSWich \n
		structure.Rgb_Size: enums.RgbSize = enums.RgbSize.CON1 \n
		structure.No_Harq: int = 1 \n
		structure.Enable_Tp: bool = False \n
		structure.Timer: int = 1 \n
		structure.Rep_K: enums.PdcchFormatB = enums.PdcchFormatB.N1 \n
		structure.Rep_Kr_V: enums.Spreset = enums.Spreset.S1 \n
		structure.Position: enums.SpsPosition = enums.SpsPosition.POS0 \n
		driver.configure.signaling.nradio.cell.bwp.ueScheduling.sps.uplink.all.set(structure, bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param structure: for set value, see the help for SetStruct structure arguments.
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
		"""
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		self._core.io.write_struct(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:SPS:UL:ALL', structure)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Periodicity: enums.SpsPeriodicity: No parameter help available
			- Mcs_Table: enums.McsTableB: No parameter help available
			- Alevel: enums.Level: No parameter help available
			- Search_Space_Id: int: No parameter help available
			- Resource_Allocation_Type: enums.ResourceAllocationType: No parameter help available
			- Rgb_Size: enums.RgbSize: No parameter help available
			- No_Harq: int: No parameter help available
			- Enable_Tp: bool: No parameter help available
			- Timer: int: No parameter help available
			- Rep_K: enums.PdcchFormatB: No parameter help available
			- Rep_Kr_V: enums.Spreset: No parameter help available
			- Position: enums.SpsPosition: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_enum('Periodicity', enums.SpsPeriodicity),
			ArgStruct.scalar_enum('Mcs_Table', enums.McsTableB),
			ArgStruct.scalar_enum('Alevel', enums.Level),
			ArgStruct.scalar_int('Search_Space_Id'),
			ArgStruct.scalar_enum('Resource_Allocation_Type', enums.ResourceAllocationType),
			ArgStruct.scalar_enum('Rgb_Size', enums.RgbSize),
			ArgStruct.scalar_int('No_Harq'),
			ArgStruct.scalar_bool('Enable_Tp'),
			ArgStruct.scalar_int('Timer'),
			ArgStruct.scalar_enum('Rep_K', enums.PdcchFormatB),
			ArgStruct.scalar_enum('Rep_Kr_V', enums.Spreset),
			ArgStruct.scalar_enum('Position', enums.SpsPosition)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Periodicity: enums.SpsPeriodicity = None
			self.Mcs_Table: enums.McsTableB = None
			self.Alevel: enums.Level = None
			self.Search_Space_Id: int = None
			self.Resource_Allocation_Type: enums.ResourceAllocationType = None
			self.Rgb_Size: enums.RgbSize = None
			self.No_Harq: int = None
			self.Enable_Tp: bool = None
			self.Timer: int = None
			self.Rep_K: enums.PdcchFormatB = None
			self.Rep_Kr_V: enums.Spreset = None
			self.Position: enums.SpsPosition = None

	def get(self, cell_name: str, bwParts=repcap.BwParts.Default) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:SPS:UL:ALL \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.bwp.ueScheduling.sps.uplink.all.get(cell_name = '1', bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param cell_name: No help available
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		param = Conversions.value_to_quoted_str(cell_name)
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:SPS:UL:ALL? {param}', self.__class__.GetStruct())

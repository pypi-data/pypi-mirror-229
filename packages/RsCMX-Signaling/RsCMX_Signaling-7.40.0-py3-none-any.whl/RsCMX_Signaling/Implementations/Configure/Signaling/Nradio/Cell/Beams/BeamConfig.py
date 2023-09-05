from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from ....... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BeamConfigCls:
	"""BeamConfig commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("beamConfig", core, parent)

	# noinspection PyTypeChecker
	class SetStruct(StructBase):
		"""Structure for setting input parameters. Contains optional setting parameters. Fields: \n
			- Cell_Name: str: No parameter help available
			- Resource_Id: int: No parameter help available
			- Aoa: enums.AoaB: No parameter help available
			- Phase: float: No parameter help available
			- Relative_Power: float: No parameter help available
			- Po_Vs_Sss: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_str('Cell_Name'),
			ArgStruct.scalar_int('Resource_Id'),
			ArgStruct.scalar_enum_optional('Aoa', enums.AoaB),
			ArgStruct.scalar_float_optional('Phase'),
			ArgStruct.scalar_float_optional('Relative_Power'),
			ArgStruct.scalar_int_optional('Po_Vs_Sss')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Cell_Name: str = None
			self.Resource_Id: int = None
			self.Aoa: enums.AoaB = None
			self.Phase: float = None
			self.Relative_Power: float = None
			self.Po_Vs_Sss: int = None

	def set(self, structure: SetStruct) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BEAMs:BEAMconfig \n
		Snippet with structure: \n
		structure = driver.configure.signaling.nradio.cell.beams.beamConfig.SetStruct() \n
		structure.Cell_Name: str = '1' \n
		structure.Resource_Id: int = 1 \n
		structure.Aoa: enums.AoaB = enums.AoaB.AOA1 \n
		structure.Phase: float = 1.0 \n
		structure.Relative_Power: float = 1.0 \n
		structure.Po_Vs_Sss: int = 1 \n
		driver.configure.signaling.nradio.cell.beams.beamConfig.set(structure) \n
		No command help available \n
			:param structure: for set value, see the help for SetStruct structure arguments.
		"""
		self._core.io.write_struct(f'CONFigure:SIGNaling:NRADio:CELL:BEAMs:BEAMconfig', structure)

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- Resource_Id: int: No parameter help available
			- Aoa: enums.AoaB: No parameter help available
			- Phase: float: No parameter help available
			- Relative_Power: float: No parameter help available
			- Po_Vs_Sss: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Resource_Id'),
			ArgStruct.scalar_enum('Aoa', enums.AoaB),
			ArgStruct.scalar_float('Phase'),
			ArgStruct.scalar_float('Relative_Power'),
			ArgStruct.scalar_int('Po_Vs_Sss')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Resource_Id: int = None
			self.Aoa: enums.AoaB = None
			self.Phase: float = None
			self.Relative_Power: float = None
			self.Po_Vs_Sss: int = None

	def get(self) -> GetStruct:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BEAMs:BEAMconfig \n
		Snippet: value: GetStruct = driver.configure.signaling.nradio.cell.beams.beamConfig.get() \n
		No command help available \n
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		return self._core.io.query_struct(f'CONFigure:SIGNaling:NRADio:CELL:BEAMs:BEAMconfig?', self.__class__.GetStruct())

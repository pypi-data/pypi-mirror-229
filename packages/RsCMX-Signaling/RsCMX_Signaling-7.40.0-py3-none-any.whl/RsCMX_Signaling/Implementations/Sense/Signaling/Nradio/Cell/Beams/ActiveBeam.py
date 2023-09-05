from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActiveBeamCls:
	"""ActiveBeam commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("activeBeam", core, parent)

	# noinspection PyTypeChecker
	def get(self, cell_name: str) -> enums.Mode:
		"""SCPI: SENSe:SIGNaling:NRADio:CELL:BEAMs:ACTivebeam \n
		Snippet: value: enums.Mode = driver.sense.signaling.nradio.cell.beams.activeBeam.get(cell_name = '1') \n
		No command help available \n
			:param cell_name: No help available
			:return: active_beam: No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		response = self._core.io.query_str(f'SENSe:SIGNaling:NRADio:CELL:BEAMs:ACTivebeam? {param}')
		return Conversions.str_to_scalar_enum(response, enums.Mode)

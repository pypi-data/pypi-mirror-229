from ..........Internal.Core import Core
from ..........Internal.CommandsGroup import CommandsGroup
from ..........Internal import Conversions
from ..........Internal.Types import DataType
from ..........Internal.ArgSingleList import ArgSingleList
from ..........Internal.ArgSingle import ArgSingle
from .......... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class K2Cls:
	"""K2 commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("k2", core, parent)

	def set(self, cell_name: str, k_2: int or bool, bwParts=repcap.BwParts.Default) -> None:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:UDEFined:CSSCheduling:K2 \n
		Snippet: driver.configure.signaling.nradio.cell.bwp.ueScheduling.userDefined.csScheduling.k2.set(cell_name = '1', k_2 = 1, bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param cell_name: No help available
			:param k_2: (integer or boolean) No help available
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('cell_name', cell_name, DataType.String), ArgSingle('k_2', k_2, DataType.IntegerExt))
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		self._core.io.write(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:UDEFined:CSSCheduling:K2 {param}'.rstrip())

	def get(self, cell_name: str, bwParts=repcap.BwParts.Default) -> int or bool:
		"""SCPI: [CONFigure]:SIGNaling:NRADio:CELL:BWP<bwp_id>:UESCheduling:UDEFined:CSSCheduling:K2 \n
		Snippet: value: int or bool = driver.configure.signaling.nradio.cell.bwp.ueScheduling.userDefined.csScheduling.k2.get(cell_name = '1', bwParts = repcap.BwParts.Default) \n
		No command help available \n
			:param cell_name: No help available
			:param bwParts: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Bwp')
			:return: k_2: (integer or boolean) No help available"""
		param = Conversions.value_to_quoted_str(cell_name)
		bwParts_cmd_val = self._cmd_group.get_repcap_cmd_value(bwParts, repcap.BwParts)
		response = self._core.io.query_str(f'CONFigure:SIGNaling:NRADio:CELL:BWP{bwParts_cmd_val}:UESCheduling:UDEFined:CSSCheduling:K2? {param}')
		return Conversions.str_to_int_or_bool(response)

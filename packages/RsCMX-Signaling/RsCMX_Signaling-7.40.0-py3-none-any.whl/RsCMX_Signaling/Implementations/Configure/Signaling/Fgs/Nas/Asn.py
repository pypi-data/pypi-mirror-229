from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AsnCls:
	"""Asn commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("asn", core, parent)

	def set_reg_accept(self, message: str) -> None:
		"""SCPI: [CONFigure]:SIGNaling:FGS:NAS:ASN:REGaccept \n
		Snippet: driver.configure.signaling.fgs.nas.asn.set_reg_accept(message = '1') \n
		No command help available \n
			:param message: No help available
		"""
		param = Conversions.value_to_quoted_str(message)
		self._core.io.write(f'CONFigure:SIGNaling:FGS:NAS:ASN:REGaccept {param}')

	def set_pdu_accept(self, message: str) -> None:
		"""SCPI: [CONFigure]:SIGNaling:FGS:NAS:ASN:PDUaccept \n
		Snippet: driver.configure.signaling.fgs.nas.asn.set_pdu_accept(message = '1') \n
		No command help available \n
			:param message: No help available
		"""
		param = Conversions.value_to_quoted_str(message)
		self._core.io.write(f'CONFigure:SIGNaling:FGS:NAS:ASN:PDUaccept {param}')

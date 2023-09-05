from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AsnCls:
	"""Asn commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("asn", core, parent)

	def set_setup(self, message: str) -> None:
		"""SCPI: [CONFigure]:SIGNaling:UE:RRC:ASN:SETup \n
		Snippet: driver.configure.signaling.ue.rrc.asn.set_setup(message = '1') \n
		No command help available \n
			:param message: No help available
		"""
		param = Conversions.value_to_quoted_str(message)
		self._core.io.write(f'CONFigure:SIGNaling:UE:RRC:ASN:SETup {param}')

	def set_re_config(self, message: str) -> None:
		"""SCPI: [CONFigure]:SIGNaling:UE:RRC:ASN:REConfig \n
		Snippet: driver.configure.signaling.ue.rrc.asn.set_re_config(message = '1') \n
		No command help available \n
			:param message: No help available
		"""
		param = Conversions.value_to_quoted_str(message)
		self._core.io.write(f'CONFigure:SIGNaling:UE:RRC:ASN:REConfig {param}')

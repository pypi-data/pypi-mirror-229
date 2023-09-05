from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NetworkCls:
	"""Network commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("network", core, parent)

	# noinspection PyTypeChecker
	def get_rfp_sharing(self) -> enums.Sharing:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:NETWork:RFPSharing \n
		Snippet: value: enums.Sharing = driver.configure.nrMmwMeas.network.get_rfp_sharing() \n
		No command help available \n
			:return: sharing: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:NETWork:RFPSharing?')
		return Conversions.str_to_scalar_enum(response, enums.Sharing)

	def set_rfp_sharing(self, sharing: enums.Sharing) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:NETWork:RFPSharing \n
		Snippet: driver.configure.nrMmwMeas.network.set_rfp_sharing(sharing = enums.Sharing.FSHared) \n
		No command help available \n
			:param sharing: No help available
		"""
		param = Conversions.enum_scalar_to_str(sharing, enums.Sharing)
		self._core.io.write(f'CONFigure:NRMMw:MEASurement<Instance>:NETWork:RFPSharing {param}')

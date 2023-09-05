from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RfSettingsCls:
	"""RfSettings commands group definition. 7 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rfSettings", core, parent)

	@property
	def eattenuation(self):
		"""eattenuation commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_eattenuation'):
			from .Eattenuation import EattenuationCls
			self._eattenuation = EattenuationCls(self._core, self._cmd_group)
		return self._eattenuation

	def get_umargin(self) -> float:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:UMARgin \n
		Snippet: value: float = driver.configure.nrMmwMeas.rfSettings.get_umargin() \n
		Sets the margin that the measurement adds to the expected nominal power to determine the reference power. The reference
		power minus the external input attenuation must be within the power range of the selected input connector. Refer to the
		data sheet. \n
			:return: user_margin: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:UMARgin?')
		return Conversions.str_to_float(response)

	def set_umargin(self, user_margin: float) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:UMARgin \n
		Snippet: driver.configure.nrMmwMeas.rfSettings.set_umargin(user_margin = 1.0) \n
		Sets the margin that the measurement adds to the expected nominal power to determine the reference power. The reference
		power minus the external input attenuation must be within the power range of the selected input connector. Refer to the
		data sheet. \n
			:param user_margin: No help available
		"""
		param = Conversions.decimal_value_to_str(user_margin)
		self._core.io.write(f'CONFigure:NRMMw:MEASurement<Instance>:RFSettings:UMARgin {param}')

	def get_envelope_power(self) -> float:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:ENPower \n
		Snippet: value: float = driver.configure.nrMmwMeas.rfSettings.get_envelope_power() \n
		Sets the expected nominal power of the measured signal. \n
			:return: exp_nom_pow: The range of the expected nominal power can be calculated as follows: Range (Expected Nominal Power) = Range (Input Power) + External Attenuation - User Margin The input power range is stated in the data sheet.
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:ENPower?')
		return Conversions.str_to_float(response)

	def set_envelope_power(self, exp_nom_pow: float) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:ENPower \n
		Snippet: driver.configure.nrMmwMeas.rfSettings.set_envelope_power(exp_nom_pow = 1.0) \n
		Sets the expected nominal power of the measured signal. \n
			:param exp_nom_pow: The range of the expected nominal power can be calculated as follows: Range (Expected Nominal Power) = Range (Input Power) + External Attenuation - User Margin The input power range is stated in the data sheet.
		"""
		param = Conversions.decimal_value_to_str(exp_nom_pow)
		self._core.io.write(f'CONFigure:NRMMw:MEASurement<Instance>:RFSettings:ENPower {param}')

	def get_foffset(self) -> int:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FOFFset \n
		Snippet: value: int = driver.configure.nrMmwMeas.rfSettings.get_foffset() \n
		Do not use anymore. The command has no effect. \n
			:return: offset: No help available
		"""
		response = self._core.io.query_str_with_opc('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FOFFset?')
		return Conversions.str_to_int(response)

	def set_foffset(self, offset: int) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FOFFset \n
		Snippet: driver.configure.nrMmwMeas.rfSettings.set_foffset(offset = 1) \n
		Do not use anymore. The command has no effect. \n
			:param offset: No help available
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write_with_opc(f'CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FOFFset {param}')

	def get_ml_offset(self) -> float:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:MLOFfset \n
		Snippet: value: float = driver.configure.nrMmwMeas.rfSettings.get_ml_offset() \n
		Do not use anymore. The command has no effect. \n
			:return: mix_lev_offset: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:MLOFfset?')
		return Conversions.str_to_float(response)

	def set_ml_offset(self, mix_lev_offset: float) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:MLOFfset \n
		Snippet: driver.configure.nrMmwMeas.rfSettings.set_ml_offset(mix_lev_offset = 1.0) \n
		Do not use anymore. The command has no effect. \n
			:param mix_lev_offset: No help available
		"""
		param = Conversions.decimal_value_to_str(mix_lev_offset)
		self._core.io.write(f'CONFigure:NRMMw:MEASurement<Instance>:RFSettings:MLOFfset {param}')

	def get_lo_frequency(self) -> float:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:LOFRequency \n
		Snippet: value: float = driver.configure.nrMmwMeas.rfSettings.get_lo_frequency() \n
		Queries the required external LO frequency resulting from the measurement settings. The command triggers also a refresh
		of the information before the query. So no need for a separate refresh command. \n
			:return: lo_frequency: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:LOFRequency?')
		return Conversions.str_to_float(response)

	def get_frequency(self) -> float:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FREQuency \n
		Snippet: value: float = driver.configure.nrMmwMeas.rfSettings.get_frequency() \n
		Selects the center frequency of carrier CC1. Do not use anymore. Use instead method RsCMPX_NrFr2Meas.Configure.NrMmwMeas.
		Cc.Frequency.set. \n
			:return: analyzer_freq: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, analyzer_freq: float) -> None:
		"""SCPI: CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FREQuency \n
		Snippet: driver.configure.nrMmwMeas.rfSettings.set_frequency(analyzer_freq = 1.0) \n
		Selects the center frequency of carrier CC1. Do not use anymore. Use instead method RsCMPX_NrFr2Meas.Configure.NrMmwMeas.
		Cc.Frequency.set. \n
			:param analyzer_freq: No help available
		"""
		param = Conversions.decimal_value_to_str(analyzer_freq)
		self._core.io.write(f'CONFigure:NRMMw:MEASurement<Instance>:RFSettings:FREQuency {param}')

	def clone(self) -> 'RfSettingsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RfSettingsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

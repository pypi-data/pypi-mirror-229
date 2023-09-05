from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CompensationCls:
	"""Compensation commands group definition. 6 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("compensation", core, parent)

	@property
	def tracking(self):
		"""tracking commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_tracking'):
			from .Tracking import TrackingCls
			self._tracking = TrackingCls(self._core, self._cmd_group)
		return self._tracking

	@property
	def efTaps(self):
		"""efTaps commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_efTaps'):
			from .EfTaps import EfTapsCls
			self._efTaps = EfTapsCls(self._core, self._cmd_group)
		return self._efTaps

	@property
	def skipSymbols(self):
		"""skipSymbols commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_skipSymbols'):
			from .SkipSymbols import SkipSymbolsCls
			self._skipSymbols = SkipSymbolsCls(self._core, self._cmd_group)
		return self._skipSymbols

	# noinspection PyTypeChecker
	def get_cestimation(self) -> enums.ChannelEstimation:
		"""SCPI: CONFigure:WLAN:MEASurement<Instance>:MEValuation:COMPensation:CESTimation \n
		Snippet: value: enums.ChannelEstimation = driver.configure.wlanMeas.multiEval.compensation.get_cestimation() \n
		Specifies whether the channel estimation is done in payload or preamble. \n
			:return: channel_estimation: PAYLoad: Channel estimation in payload and preamble PREamble: Channel estimation in preamble only
		"""
		response = self._core.io.query_str('CONFigure:WLAN:MEASurement<Instance>:MEValuation:COMPensation:CESTimation?')
		return Conversions.str_to_scalar_enum(response, enums.ChannelEstimation)

	def set_cestimation(self, channel_estimation: enums.ChannelEstimation) -> None:
		"""SCPI: CONFigure:WLAN:MEASurement<Instance>:MEValuation:COMPensation:CESTimation \n
		Snippet: driver.configure.wlanMeas.multiEval.compensation.set_cestimation(channel_estimation = enums.ChannelEstimation.PAYLoad) \n
		Specifies whether the channel estimation is done in payload or preamble. \n
			:param channel_estimation: PAYLoad: Channel estimation in payload and preamble PREamble: Channel estimation in preamble only
		"""
		param = Conversions.enum_scalar_to_str(channel_estimation, enums.ChannelEstimation)
		self._core.io.write(f'CONFigure:WLAN:MEASurement<Instance>:MEValuation:COMPensation:CESTimation {param}')

	def clone(self) -> 'CompensationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CompensationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

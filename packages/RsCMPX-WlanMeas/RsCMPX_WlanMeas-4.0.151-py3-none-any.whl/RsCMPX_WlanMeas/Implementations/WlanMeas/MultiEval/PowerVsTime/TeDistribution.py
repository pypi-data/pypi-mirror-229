from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.ArgSingleSuppressed import ArgSingleSuppressed
from .....Internal.Types import DataType
from .....Internal.StructBase import StructBase
from .....Internal.ArgStruct import ArgStruct
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TeDistributionCls:
	"""TeDistribution commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("teDistribution", core, parent)

	# noinspection PyTypeChecker
	class ResultData(StructBase):
		"""Response structure. Fields: \n
			- Reliability: int: 'Reliability indicator'
			- Te_Percentage: float: Percentage of TEs
			- Te_Outside: int: Number of detected TEs
			- Te_Total: int: Number of measured values"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_float('Te_Percentage'),
			ArgStruct.scalar_int('Te_Outside'),
			ArgStruct.scalar_int('Te_Total')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Te_Percentage: float = None
			self.Te_Outside: int = None
			self.Te_Total: int = None

	def read(self) -> ResultData:
		"""SCPI: READ:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib \n
		Snippet: value: ResultData = driver.wlanMeas.multiEval.powerVsTime.teDistribution.read() \n
		Return the scalar results for timing error (TE) distribution. The commands are only supported for OFDM standards.
		Exceeding the limit has no impact on the stop On Limit Failure condition or out-of-tolerance counter. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'READ:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib?', self.__class__.ResultData())

	def fetch(self) -> ResultData:
		"""SCPI: FETCh:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib \n
		Snippet: value: ResultData = driver.wlanMeas.multiEval.powerVsTime.teDistribution.fetch() \n
		Return the scalar results for timing error (TE) distribution. The commands are only supported for OFDM standards.
		Exceeding the limit has no impact on the stop On Limit Failure condition or out-of-tolerance counter. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'FETCh:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib?', self.__class__.ResultData())

	# noinspection PyTypeChecker
	def calculate(self) -> enums.ResultStatus2:
		"""SCPI: CALCulate:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib \n
		Snippet: value: enums.ResultStatus2 = driver.wlanMeas.multiEval.powerVsTime.teDistribution.calculate() \n
		Return the scalar results for timing error (TE) distribution. The commands are only supported for OFDM standards.
		Exceeding the limit has no impact on the stop On Limit Failure condition or out-of-tolerance counter. \n
		Suppressed linked return values: reliability \n
			:return: te_percentage: Percentage of TEs"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_str_suppressed(f'CALCulate:WLAN:MEASurement<Instance>:MEValuation:PVTime:TEDistrib?', suppressed)
		return Conversions.str_to_scalar_enum(response, enums.ResultStatus2)

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	def get_pdynamics(self) -> bool:
		"""SCPI: CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PDYNamics \n
		Snippet: value: bool = driver.configure.nrSubMeas.srs.result.get_pdynamics() \n
		Enables or disables the evaluation of results in the SRS measurement. \n
			:return: enable: OFF: Do not evaluate results. ON: Evaluate results.
		"""
		response = self._core.io.query_str('CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PDYNamics?')
		return Conversions.str_to_bool(response)

	def set_pdynamics(self, enable: bool) -> None:
		"""SCPI: CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PDYNamics \n
		Snippet: driver.configure.nrSubMeas.srs.result.set_pdynamics(enable = False) \n
		Enables or disables the evaluation of results in the SRS measurement. \n
			:param enable: OFF: Do not evaluate results. ON: Evaluate results.
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PDYNamics {param}')

	def get_pv_symbol(self) -> bool:
		"""SCPI: CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PVSYmbol \n
		Snippet: value: bool = driver.configure.nrSubMeas.srs.result.get_pv_symbol() \n
		No command help available \n
			:return: enable: No help available
		"""
		response = self._core.io.query_str('CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PVSYmbol?')
		return Conversions.str_to_bool(response)

	def set_pv_symbol(self, enable: bool) -> None:
		"""SCPI: CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PVSYmbol \n
		Snippet: driver.configure.nrSubMeas.srs.result.set_pv_symbol(enable = False) \n
		No command help available \n
			:param enable: No help available
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'CONFigure:NRSub:MEASurement<Instance>:SRS:RESult:PVSYmbol {param}')

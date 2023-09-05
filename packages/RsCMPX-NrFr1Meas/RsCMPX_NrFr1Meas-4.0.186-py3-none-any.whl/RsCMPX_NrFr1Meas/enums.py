from enum import Enum


# noinspection SpellCheckingInspection
class AllocatedSlots(Enum):
	"""1 Members, ALL ... ALL"""
	ALL = 0


# noinspection SpellCheckingInspection
class Band(Enum):
	"""58 Members, OB1 ... OB99"""
	OB1 = 0
	OB100 = 1
	OB101 = 2
	OB104 = 3
	OB12 = 4
	OB13 = 5
	OB14 = 6
	OB18 = 7
	OB2 = 8
	OB20 = 9
	OB24 = 10
	OB25 = 11
	OB26 = 12
	OB28 = 13
	OB3 = 14
	OB30 = 15
	OB34 = 16
	OB38 = 17
	OB39 = 18
	OB40 = 19
	OB41 = 20
	OB46 = 21
	OB47 = 22
	OB48 = 23
	OB5 = 24
	OB50 = 25
	OB51 = 26
	OB53 = 27
	OB65 = 28
	OB66 = 29
	OB7 = 30
	OB70 = 31
	OB71 = 32
	OB74 = 33
	OB75 = 34
	OB76 = 35
	OB77 = 36
	OB78 = 37
	OB79 = 38
	OB8 = 39
	OB80 = 40
	OB81 = 41
	OB82 = 42
	OB83 = 43
	OB84 = 44
	OB85 = 45
	OB86 = 46
	OB89 = 47
	OB90 = 48
	OB91 = 49
	OB92 = 50
	OB93 = 51
	OB94 = 52
	OB95 = 53
	OB96 = 54
	OB97 = 55
	OB98 = 56
	OB99 = 57


# noinspection SpellCheckingInspection
class BandwidthPart(Enum):
	"""1 Members, BWP0 ... BWP0"""
	BWP0 = 0


# noinspection SpellCheckingInspection
class CarrierComponent(Enum):
	"""2 Members, CC1 ... CC2"""
	CC1 = 0
	CC2 = 1


# noinspection SpellCheckingInspection
class CarrierPosition(Enum):
	"""2 Members, LONR ... RONR"""
	LONR = 0
	RONR = 1


# noinspection SpellCheckingInspection
class ChannelBwidth(Enum):
	"""15 Members, B005 ... B100"""
	B005 = 0
	B010 = 1
	B015 = 2
	B020 = 3
	B025 = 4
	B030 = 5
	B035 = 6
	B040 = 7
	B045 = 8
	B050 = 9
	B060 = 10
	B070 = 11
	B080 = 12
	B090 = 13
	B100 = 14


# noinspection SpellCheckingInspection
class ChannelBwidthB(Enum):
	"""4 Members, B005 ... B020"""
	B005 = 0
	B010 = 1
	B015 = 2
	B020 = 3


# noinspection SpellCheckingInspection
class ChannelTypeA(Enum):
	"""2 Members, PUCCh ... PUSCh"""
	PUCCh = 0
	PUSCh = 1


# noinspection SpellCheckingInspection
class ChannelTypeB(Enum):
	"""4 Members, OFF ... PUSCh"""
	OFF = 0
	ON = 1
	PUCCh = 2
	PUSCh = 3


# noinspection SpellCheckingInspection
class CmwsConnector(Enum):
	"""48 Members, R11 ... RB8"""
	R11 = 0
	R12 = 1
	R13 = 2
	R14 = 3
	R15 = 4
	R16 = 5
	R17 = 6
	R18 = 7
	R21 = 8
	R22 = 9
	R23 = 10
	R24 = 11
	R25 = 12
	R26 = 13
	R27 = 14
	R28 = 15
	R31 = 16
	R32 = 17
	R33 = 18
	R34 = 19
	R35 = 20
	R36 = 21
	R37 = 22
	R38 = 23
	R41 = 24
	R42 = 25
	R43 = 26
	R44 = 27
	R45 = 28
	R46 = 29
	R47 = 30
	R48 = 31
	RA1 = 32
	RA2 = 33
	RA3 = 34
	RA4 = 35
	RA5 = 36
	RA6 = 37
	RA7 = 38
	RA8 = 39
	RB1 = 40
	RB2 = 41
	RB3 = 42
	RB4 = 43
	RB5 = 44
	RB6 = 45
	RB7 = 46
	RB8 = 47


# noinspection SpellCheckingInspection
class ConfigType(Enum):
	"""2 Members, T1 ... T2"""
	T1 = 0
	T2 = 1


# noinspection SpellCheckingInspection
class CyclicPrefix(Enum):
	"""2 Members, EXTended ... NORMal"""
	EXTended = 0
	NORMal = 1


# noinspection SpellCheckingInspection
class DmrsInit(Enum):
	"""2 Members, CID ... DID"""
	CID = 0
	DID = 1


# noinspection SpellCheckingInspection
class DuplexModeB(Enum):
	"""2 Members, FDD ... TDD"""
	FDD = 0
	TDD = 1


# noinspection SpellCheckingInspection
class Generator(Enum):
	"""2 Members, DID ... PHY"""
	DID = 0
	PHY = 1


# noinspection SpellCheckingInspection
class GhopingInit(Enum):
	"""2 Members, CID ... HID"""
	CID = 0
	HID = 1


# noinspection SpellCheckingInspection
class GroupHopping(Enum):
	"""3 Members, DISable ... NEITher"""
	DISable = 0
	ENABle = 1
	NEITher = 2


# noinspection SpellCheckingInspection
class Lagging(Enum):
	"""3 Members, MS05 ... OFF"""
	MS05 = 0
	MS25 = 1
	OFF = 2


# noinspection SpellCheckingInspection
class Leading(Enum):
	"""2 Members, MS25 ... OFF"""
	MS25 = 0
	OFF = 1


# noinspection SpellCheckingInspection
class ListMode(Enum):
	"""2 Members, ONCE ... SEGMent"""
	ONCE = 0
	SEGMent = 1


# noinspection SpellCheckingInspection
class LowHigh(Enum):
	"""2 Members, HIGH ... LOW"""
	HIGH = 0
	LOW = 1


# noinspection SpellCheckingInspection
class MappingType(Enum):
	"""2 Members, A ... B"""
	A = 0
	B = 1


# noinspection SpellCheckingInspection
class MaxLength(Enum):
	"""2 Members, DOUBle ... SINGle"""
	DOUBle = 0
	SINGle = 1


# noinspection SpellCheckingInspection
class MeasFilter(Enum):
	"""2 Members, BANDpass ... GAUSs"""
	BANDpass = 0
	GAUSs = 1


# noinspection SpellCheckingInspection
class MeasurementMode(Enum):
	"""2 Members, MELMode ... NORMal"""
	MELMode = 0
	NORMal = 1


# noinspection SpellCheckingInspection
class MeasureSlot(Enum):
	"""6 Members, ALL ... UDEF"""
	ALL = 0
	MS0 = 1
	MS1 = 2
	MS2 = 3
	MS3 = 4
	UDEF = 5


# noinspection SpellCheckingInspection
class MevLimit(Enum):
	"""2 Members, STD ... UDEF"""
	STD = 0
	UDEF = 1


# noinspection SpellCheckingInspection
class Modulation(Enum):
	"""6 Members, BPSK ... QPSK"""
	BPSK = 0
	BPWS = 1
	Q16 = 2
	Q256 = 3
	Q64 = 4
	QPSK = 5


# noinspection SpellCheckingInspection
class ModulationScheme(Enum):
	"""7 Members, AUTO ... QPSK"""
	AUTO = 0
	BPSK = 1
	BPWS = 2
	Q16 = 3
	Q256 = 4
	Q64 = 5
	QPSK = 6


# noinspection SpellCheckingInspection
class NbTrigger(Enum):
	"""4 Members, M010 ... M080"""
	M010 = 0
	M020 = 1
	M040 = 2
	M080 = 3


# noinspection SpellCheckingInspection
class NetworkSigVal(Enum):
	"""103 Members, NS01 ... NSU43"""
	NS01 = 0
	NS02 = 1
	NS03 = 2
	NS04 = 3
	NS05 = 4
	NS06 = 5
	NS07 = 6
	NS08 = 7
	NS09 = 8
	NS10 = 9
	NS100 = 10
	NS11 = 11
	NS12 = 12
	NS13 = 13
	NS14 = 14
	NS15 = 15
	NS16 = 16
	NS17 = 17
	NS18 = 18
	NS19 = 19
	NS20 = 20
	NS21 = 21
	NS22 = 22
	NS23 = 23
	NS24 = 24
	NS25 = 25
	NS26 = 26
	NS27 = 27
	NS28 = 28
	NS29 = 29
	NS30 = 30
	NS31 = 31
	NS32 = 32
	NS33 = 33
	NS34 = 34
	NS35 = 35
	NS36 = 36
	NS37 = 37
	NS38 = 38
	NS39 = 39
	NS40 = 40
	NS41 = 41
	NS42 = 42
	NS43 = 43
	NS44 = 44
	NS45 = 45
	NS46 = 46
	NS47 = 47
	NS48 = 48
	NS49 = 49
	NS50 = 50
	NS51 = 51
	NS52 = 52
	NS53 = 53
	NS54 = 54
	NS55 = 55
	NS56 = 56
	NS57 = 57
	NS58 = 58
	NS59 = 59
	NS60 = 60
	NS61 = 61
	NS62 = 62
	NS63 = 63
	NS64 = 64
	NS65 = 65
	NS66 = 66
	NS67 = 67
	NS68 = 68
	NS69 = 69
	NS70 = 70
	NS71 = 71
	NS72 = 72
	NS73 = 73
	NS74 = 74
	NS75 = 75
	NS76 = 76
	NS77 = 77
	NS78 = 78
	NS79 = 79
	NS80 = 80
	NS81 = 81
	NS82 = 82
	NS83 = 83
	NS84 = 84
	NS85 = 85
	NS86 = 86
	NS87 = 87
	NS88 = 88
	NS89 = 89
	NS90 = 90
	NS91 = 91
	NS92 = 92
	NS93 = 93
	NS94 = 94
	NS95 = 95
	NS96 = 96
	NS97 = 97
	NS98 = 98
	NS99 = 99
	NSU03 = 100
	NSU05 = 101
	NSU43 = 102


# noinspection SpellCheckingInspection
class NumberSymbols(Enum):
	"""3 Members, N1 ... N4"""
	N1 = 0
	N2 = 1
	N4 = 2


# noinspection SpellCheckingInspection
class ParameterSetMode(Enum):
	"""2 Members, GLOBal ... LIST"""
	GLOBal = 0
	LIST = 1


# noinspection SpellCheckingInspection
class Periodicity(Enum):
	"""9 Members, MS05 ... MS5"""
	MS05 = 0
	MS1 = 1
	MS10 = 2
	MS125 = 3
	MS2 = 4
	MS25 = 5
	MS3 = 6
	MS4 = 7
	MS5 = 8


# noinspection SpellCheckingInspection
class PeriodPreamble(Enum):
	"""3 Members, MS05 ... MS20"""
	MS05 = 0
	MS10 = 1
	MS20 = 2


# noinspection SpellCheckingInspection
class PhaseComp(Enum):
	"""3 Members, CAF ... UDEF"""
	CAF = 0
	OFF = 1
	UDEF = 2


# noinspection SpellCheckingInspection
class PreambleFormat(Enum):
	"""13 Members, PF0 ... PFC2"""
	PF0 = 0
	PF1 = 1
	PF2 = 2
	PF3 = 3
	PFA1 = 4
	PFA2 = 5
	PFA3 = 6
	PFB1 = 7
	PFB2 = 8
	PFB3 = 9
	PFB4 = 10
	PFC0 = 11
	PFC2 = 12


# noinspection SpellCheckingInspection
class PucchFormat(Enum):
	"""5 Members, F0 ... F4"""
	F0 = 0
	F1 = 1
	F2 = 2
	F3 = 3
	F4 = 4


# noinspection SpellCheckingInspection
class RbwA(Enum):
	"""3 Members, K030 ... PC1"""
	K030 = 0
	M1 = 1
	PC1 = 2


# noinspection SpellCheckingInspection
class RbwB(Enum):
	"""6 Members, K030 ... PC2"""
	K030 = 0
	K100 = 1
	K400 = 2
	M1 = 3
	PC1 = 4
	PC2 = 5


# noinspection SpellCheckingInspection
class RbwC(Enum):
	"""3 Members, K030 ... M1"""
	K030 = 0
	K400 = 1
	M1 = 2


# noinspection SpellCheckingInspection
class Repeat(Enum):
	"""2 Members, CONTinuous ... SINGleshot"""
	CONTinuous = 0
	SINGleshot = 1


# noinspection SpellCheckingInspection
class ResourceState(Enum):
	"""8 Members, ACTive ... RUN"""
	ACTive = 0
	ADJusted = 1
	INValid = 2
	OFF = 3
	PENDing = 4
	QUEued = 5
	RDY = 6
	RUN = 7


# noinspection SpellCheckingInspection
class RestrictedSet(Enum):
	"""1 Members, URES ... URES"""
	URES = 0


# noinspection SpellCheckingInspection
class ResultStatus2(Enum):
	"""10 Members, DC ... ULEU"""
	DC = 0
	INV = 1
	NAV = 2
	NCAP = 3
	OFF = 4
	OFL = 5
	OK = 6
	UFL = 7
	ULEL = 8
	ULEU = 9


# noinspection SpellCheckingInspection
class RetriggerFlag(Enum):
	"""4 Members, IFPNarrowband ... ON"""
	IFPNarrowband = 0
	IFPower = 1
	OFF = 2
	ON = 3


# noinspection SpellCheckingInspection
class RfConverter(Enum):
	"""40 Members, IRX1 ... RX44"""
	IRX1 = 0
	IRX11 = 1
	IRX12 = 2
	IRX13 = 3
	IRX14 = 4
	IRX2 = 5
	IRX21 = 6
	IRX22 = 7
	IRX23 = 8
	IRX24 = 9
	IRX3 = 10
	IRX31 = 11
	IRX32 = 12
	IRX33 = 13
	IRX34 = 14
	IRX4 = 15
	IRX41 = 16
	IRX42 = 17
	IRX43 = 18
	IRX44 = 19
	RX1 = 20
	RX11 = 21
	RX12 = 22
	RX13 = 23
	RX14 = 24
	RX2 = 25
	RX21 = 26
	RX22 = 27
	RX23 = 28
	RX24 = 29
	RX3 = 30
	RX31 = 31
	RX32 = 32
	RX33 = 33
	RX34 = 34
	RX4 = 35
	RX41 = 36
	RX42 = 37
	RX43 = 38
	RX44 = 39


# noinspection SpellCheckingInspection
class RxConnector(Enum):
	"""163 Members, I11I ... RH8"""
	I11I = 0
	I13I = 1
	I15I = 2
	I17I = 3
	I21I = 4
	I23I = 5
	I25I = 6
	I27I = 7
	I31I = 8
	I33I = 9
	I35I = 10
	I37I = 11
	I41I = 12
	I43I = 13
	I45I = 14
	I47I = 15
	IFI1 = 16
	IFI2 = 17
	IFI3 = 18
	IFI4 = 19
	IFI5 = 20
	IFI6 = 21
	IQ1I = 22
	IQ3I = 23
	IQ5I = 24
	IQ7I = 25
	R10D = 26
	R11 = 27
	R11C = 28
	R11D = 29
	R12 = 30
	R12C = 31
	R12D = 32
	R12I = 33
	R13 = 34
	R13C = 35
	R14 = 36
	R14C = 37
	R14I = 38
	R15 = 39
	R16 = 40
	R17 = 41
	R18 = 42
	R21 = 43
	R21C = 44
	R22 = 45
	R22C = 46
	R22I = 47
	R23 = 48
	R23C = 49
	R24 = 50
	R24C = 51
	R24I = 52
	R25 = 53
	R26 = 54
	R27 = 55
	R28 = 56
	R31 = 57
	R31C = 58
	R32 = 59
	R32C = 60
	R32I = 61
	R33 = 62
	R33C = 63
	R34 = 64
	R34C = 65
	R34I = 66
	R35 = 67
	R36 = 68
	R37 = 69
	R38 = 70
	R41 = 71
	R41C = 72
	R42 = 73
	R42C = 74
	R42I = 75
	R43 = 76
	R43C = 77
	R44 = 78
	R44C = 79
	R44I = 80
	R45 = 81
	R46 = 82
	R47 = 83
	R48 = 84
	RA1 = 85
	RA2 = 86
	RA3 = 87
	RA4 = 88
	RA5 = 89
	RA6 = 90
	RA7 = 91
	RA8 = 92
	RB1 = 93
	RB2 = 94
	RB3 = 95
	RB4 = 96
	RB5 = 97
	RB6 = 98
	RB7 = 99
	RB8 = 100
	RC1 = 101
	RC2 = 102
	RC3 = 103
	RC4 = 104
	RC5 = 105
	RC6 = 106
	RC7 = 107
	RC8 = 108
	RD1 = 109
	RD2 = 110
	RD3 = 111
	RD4 = 112
	RD5 = 113
	RD6 = 114
	RD7 = 115
	RD8 = 116
	RE1 = 117
	RE2 = 118
	RE3 = 119
	RE4 = 120
	RE5 = 121
	RE6 = 122
	RE7 = 123
	RE8 = 124
	RF1 = 125
	RF1C = 126
	RF2 = 127
	RF2C = 128
	RF2I = 129
	RF3 = 130
	RF3C = 131
	RF4 = 132
	RF4C = 133
	RF4I = 134
	RF5 = 135
	RF5C = 136
	RF6 = 137
	RF6C = 138
	RF7 = 139
	RF7C = 140
	RF8 = 141
	RF8C = 142
	RF9C = 143
	RFAC = 144
	RFBC = 145
	RFBI = 146
	RG1 = 147
	RG2 = 148
	RG3 = 149
	RG4 = 150
	RG5 = 151
	RG6 = 152
	RG7 = 153
	RG8 = 154
	RH1 = 155
	RH2 = 156
	RH3 = 157
	RH4 = 158
	RH5 = 159
	RH6 = 160
	RH7 = 161
	RH8 = 162


# noinspection SpellCheckingInspection
class Scenario(Enum):
	"""4 Members, CSPath ... SALone"""
	CSPath = 0
	MAPRotocol = 1
	NAV = 2
	SALone = 3


# noinspection SpellCheckingInspection
class Sharing(Enum):
	"""3 Members, FSHared ... OCONnection"""
	FSHared = 0
	NSHared = 1
	OCONnection = 2


# noinspection SpellCheckingInspection
class SignalPath(Enum):
	"""2 Members, NETWork ... STANdalone"""
	NETWork = 0
	STANdalone = 1


# noinspection SpellCheckingInspection
class SignalSlope(Enum):
	"""2 Members, FEDGe ... REDGe"""
	FEDGe = 0
	REDGe = 1


# noinspection SpellCheckingInspection
class SrsPeriodicity(Enum):
	"""17 Members, SL1 ... SL80"""
	SL1 = 0
	SL10 = 1
	SL1280 = 2
	SL16 = 3
	SL160 = 4
	SL2 = 5
	SL20 = 6
	SL2560 = 7
	SL32 = 8
	SL320 = 9
	SL4 = 10
	SL40 = 11
	SL5 = 12
	SL64 = 13
	SL640 = 14
	SL8 = 15
	SL80 = 16


# noinspection SpellCheckingInspection
class StopCondition(Enum):
	"""2 Members, NONE ... SLFail"""
	NONE = 0
	SLFail = 1


# noinspection SpellCheckingInspection
class SubCarrSpacing(Enum):
	"""3 Members, S15K ... S60K"""
	S15K = 0
	S30K = 1
	S60K = 2


# noinspection SpellCheckingInspection
class SubCarrSpacingB(Enum):
	"""5 Members, S15K ... S60K"""
	S15K = 0
	S1K2 = 1
	S30K = 2
	S5K = 3
	S60K = 4


# noinspection SpellCheckingInspection
class SyncMode(Enum):
	"""4 Members, ENHanced ... NSSLot"""
	ENHanced = 0
	ESSLot = 1
	NORMal = 2
	NSSLot = 3


# noinspection SpellCheckingInspection
class TargetStateA(Enum):
	"""3 Members, OFF ... RUN"""
	OFF = 0
	RDY = 1
	RUN = 2


# noinspection SpellCheckingInspection
class TargetSyncState(Enum):
	"""2 Members, ADJusted ... PENDing"""
	ADJusted = 0
	PENDing = 1


# noinspection SpellCheckingInspection
class TimeMask(Enum):
	"""3 Members, GOO ... SBLanking"""
	GOO = 0
	PPSRs = 1
	SBLanking = 2


# noinspection SpellCheckingInspection
class TraceSelect(Enum):
	"""3 Members, AVERage ... MAXimum"""
	AVERage = 0
	CURRent = 1
	MAXimum = 2

from enum import Enum


# noinspection SpellCheckingInspection
class Bandwidth(Enum):
	"""7 Members, BW05mhz ... BW88mhz"""
	BW05mhz = 0
	BW10mhz = 1
	BW16mhz = 2
	BW20mhz = 3
	BW40mhz = 4
	BW80mhz = 5
	BW88mhz = 6


# noinspection SpellCheckingInspection
class BurstEvalLength(Enum):
	"""2 Members, REDucedburst ... WHOLeburst"""
	REDucedburst = 0
	WHOLeburst = 1


# noinspection SpellCheckingInspection
class BurstType(Enum):
	"""4 Members, AUTO ... MIXed"""
	AUTO = 0
	DLIN = 1
	GREenfield = 2
	MIXed = 3


# noinspection SpellCheckingInspection
class BurstTypeB(Enum):
	"""2 Members, GREenfield ... MIXed"""
	GREenfield = 0
	MIXed = 1


# noinspection SpellCheckingInspection
class CfoEstimation(Enum):
	"""2 Members, FULLpacket ... PREamble"""
	FULLpacket = 0
	PREamble = 1


# noinspection SpellCheckingInspection
class ChannelEstimation(Enum):
	"""2 Members, PAYLoad ... PREamble"""
	PAYLoad = 0
	PREamble = 1


# noinspection SpellCheckingInspection
class Coderate(Enum):
	"""7 Members, AUTO ... CR56"""
	AUTO = 0
	CR12 = 1
	CR14dcm = 2
	CR23 = 3
	CR34 = 4
	CR38dcm = 5
	CR56 = 6


# noinspection SpellCheckingInspection
class CodingType(Enum):
	"""2 Members, BCC ... LDPC"""
	BCC = 0
	LDPC = 1


# noinspection SpellCheckingInspection
class ConnectorSwitch(Enum):
	"""96 Members, R11 ... RH8"""
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
	RC1 = 48
	RC2 = 49
	RC3 = 50
	RC4 = 51
	RC5 = 52
	RC6 = 53
	RC7 = 54
	RC8 = 55
	RD1 = 56
	RD2 = 57
	RD3 = 58
	RD4 = 59
	RD5 = 60
	RD6 = 61
	RD7 = 62
	RD8 = 63
	RE1 = 64
	RE2 = 65
	RE3 = 66
	RE4 = 67
	RE5 = 68
	RE6 = 69
	RE7 = 70
	RE8 = 71
	RF1 = 72
	RF2 = 73
	RF3 = 74
	RF4 = 75
	RF5 = 76
	RF6 = 77
	RF7 = 78
	RF8 = 79
	RG1 = 80
	RG2 = 81
	RG3 = 82
	RG4 = 83
	RG5 = 84
	RG6 = 85
	RG7 = 86
	RG8 = 87
	RH1 = 88
	RH2 = 89
	RH3 = 90
	RH4 = 91
	RH5 = 92
	RH6 = 93
	RH7 = 94
	RH8 = 95


# noinspection SpellCheckingInspection
class ConnectorSwitchExt(Enum):
	"""98 Members, OFF ... RH8"""
	OFF = 0
	ON = 1
	R11 = 2
	R12 = 3
	R13 = 4
	R14 = 5
	R15 = 6
	R16 = 7
	R17 = 8
	R18 = 9
	R21 = 10
	R22 = 11
	R23 = 12
	R24 = 13
	R25 = 14
	R26 = 15
	R27 = 16
	R28 = 17
	R31 = 18
	R32 = 19
	R33 = 20
	R34 = 21
	R35 = 22
	R36 = 23
	R37 = 24
	R38 = 25
	R41 = 26
	R42 = 27
	R43 = 28
	R44 = 29
	R45 = 30
	R46 = 31
	R47 = 32
	R48 = 33
	RA1 = 34
	RA2 = 35
	RA3 = 36
	RA4 = 37
	RA5 = 38
	RA6 = 39
	RA7 = 40
	RA8 = 41
	RB1 = 42
	RB2 = 43
	RB3 = 44
	RB4 = 45
	RB5 = 46
	RB6 = 47
	RB7 = 48
	RB8 = 49
	RC1 = 50
	RC2 = 51
	RC3 = 52
	RC4 = 53
	RC5 = 54
	RC6 = 55
	RC7 = 56
	RC8 = 57
	RD1 = 58
	RD2 = 59
	RD3 = 60
	RD4 = 61
	RD5 = 62
	RD6 = 63
	RD7 = 64
	RD8 = 65
	RE1 = 66
	RE2 = 67
	RE3 = 68
	RE4 = 69
	RE5 = 70
	RE6 = 71
	RE7 = 72
	RE8 = 73
	RF1 = 74
	RF2 = 75
	RF3 = 76
	RF4 = 77
	RF5 = 78
	RF6 = 79
	RF7 = 80
	RF8 = 81
	RG1 = 82
	RG2 = 83
	RG3 = 84
	RG4 = 85
	RG5 = 86
	RG6 = 87
	RG7 = 88
	RG8 = 89
	RH1 = 90
	RH2 = 91
	RH3 = 92
	RH4 = 93
	RH5 = 94
	RH6 = 95
	RH7 = 96
	RH8 = 97


# noinspection SpellCheckingInspection
class ConnectorTuple(Enum):
	"""7 Members, CT12 ... CT78"""
	CT12 = 0
	CT14 = 1
	CT18 = 2
	CT34 = 3
	CT56 = 4
	CT58 = 5
	CT78 = 6


# noinspection SpellCheckingInspection
class DecodeStatus(Enum):
	"""3 Members, INV ... OK"""
	INV = 0
	NAV = 1
	OK = 2


# noinspection SpellCheckingInspection
class DisplayMode(Enum):
	"""2 Members, ABSolute ... RELative"""
	ABSolute = 0
	RELative = 1


# noinspection SpellCheckingInspection
class EvmMethod(Enum):
	"""2 Members, ST1999 ... ST2007"""
	ST1999 = 0
	ST2007 = 1


# noinspection SpellCheckingInspection
class FftOffset(Enum):
	"""3 Members, AUTO ... PEAK"""
	AUTO = 0
	CENT = 1
	PEAK = 2


# noinspection SpellCheckingInspection
class FrequencyBand(Enum):
	"""3 Members, B24Ghz ... B5GHz"""
	B24Ghz = 0
	B4GHz = 1
	B5GHz = 2


# noinspection SpellCheckingInspection
class GuardInterval(Enum):
	"""5 Members, GI08 ... SHORt"""
	GI08 = 0
	GI16 = 1
	GI32 = 2
	LONG = 3
	SHORt = 4


# noinspection SpellCheckingInspection
class GuiScenario(Enum):
	"""8 Members, CSPath ... UNDefined"""
	CSPath = 0
	MIMO2x2 = 1
	MIMO4x4 = 2
	MIMO8x8 = 3
	SALone = 4
	SMI4 = 5
	TMIMo = 6
	UNDefined = 7


# noinspection SpellCheckingInspection
class IeeeStandard(Enum):
	"""6 Members, DSSS ... VHTofdm"""
	DSSS = 0
	HEOFdm = 1
	HTOFdm = 2
	LOFDm = 3
	POFDm = 4
	VHTofdm = 5


# noinspection SpellCheckingInspection
class LowHigh(Enum):
	"""2 Members, HIGH ... LOW"""
	HIGH = 0
	LOW = 1


# noinspection SpellCheckingInspection
class LtfSize(Enum):
	"""3 Members, LTF1 ... LTF4"""
	LTF1 = 0
	LTF2 = 1
	LTF4 = 2


# noinspection SpellCheckingInspection
class MimoScenario(Enum):
	"""10 Members, CSPath ... UNDefined"""
	CSPath = 0
	MIMO2x2 = 1
	MIMO4x4 = 2
	MIMO8x8 = 3
	SALone = 4
	SMI4 = 5
	TMIM2x2 = 6
	TMIM3x3 = 7
	TMIM4x4 = 8
	UNDefined = 9


# noinspection SpellCheckingInspection
class ModulationFilter(Enum):
	"""11 Members, ALL ... QPSK"""
	ALL = 0
	BPSK = 1
	CCK11 = 2
	CCK5_5 = 3
	DBPSk = 4
	DQPSk = 5
	QAM1024 = 6
	QAM16 = 7
	QAM256 = 8
	QAM64 = 9
	QPSK = 10


# noinspection SpellCheckingInspection
class ModulationTypeB(Enum):
	"""32 Members, BP1_5 ... QR34"""
	BP1_5 = 0
	BP2_25 = 1
	BP3 = 2
	BP4_5 = 3
	BPM6 = 4
	BPM9 = 5
	BR12 = 6
	Q1M12 = 7
	Q1M18 = 8
	Q1M24 = 9
	Q1M36 = 10
	Q1M6 = 11
	Q1M9 = 12
	Q1R12 = 13
	Q1R34 = 14
	Q6M12 = 15
	Q6M135 = 16
	Q6M24 = 17
	Q6M27 = 18
	Q6M48 = 19
	Q6M54 = 20
	Q6R23 = 21
	Q6R34 = 22
	Q6R56 = 23
	QM12 = 24
	QM18 = 25
	QM3 = 26
	QM4_5 = 27
	QM6 = 28
	QM9 = 29
	QR12 = 30
	QR34 = 31


# noinspection SpellCheckingInspection
class ModulationTypeC(Enum):
	"""4 Members, CCK11 ... DQPSk2"""
	CCK11 = 0
	CCK5 = 1
	DBPSk1 = 2
	DQPSk2 = 3


# noinspection SpellCheckingInspection
class ModulationTypeD(Enum):
	"""28 Members, _16Q ... UNSPecified"""
	_16Q = 0
	_16Q12 = 1
	_16Q14 = 2
	_16Q34 = 3
	_16Q38 = 4
	_1KQ = 5
	_1KQ34 = 6
	_1KQ56 = 7
	_256Q = 8
	_256Q34 = 9
	_256Q56 = 10
	_4KQ = 11
	_4KQ34 = 12
	_4KQ56 = 13
	_64Q = 14
	_64Q12 = 15
	_64Q23 = 16
	_64Q34 = 17
	_64Q56 = 18
	BPSK = 19
	BPSK12 = 20
	BPSK14 = 21
	BPSK34 = 22
	QPSK = 23
	QPSK12 = 24
	QPSK14 = 25
	QPSK34 = 26
	UNSPecified = 27


# noinspection SpellCheckingInspection
class ParameterSetMode(Enum):
	"""2 Members, GLOBal ... LIST"""
	GLOBal = 0
	LIST = 1


# noinspection SpellCheckingInspection
class PlcpType(Enum):
	"""2 Members, LONGplcp ... SHORtplcp"""
	LONGplcp = 0
	SHORtplcp = 1


# noinspection SpellCheckingInspection
class PowerClass(Enum):
	"""4 Members, CLA ... USERdefined"""
	CLA = 0
	CLB = 1
	CLCD = 2
	USERdefined = 3


# noinspection SpellCheckingInspection
class ReceiveMode(Enum):
	"""4 Members, CMIMo ... TMIMo"""
	CMIMo = 0
	SISO = 1
	SMIMo = 2
	TMIMo = 3


# noinspection SpellCheckingInspection
class RefPower(Enum):
	"""2 Members, MAXimum ... MEAN"""
	MAXimum = 0
	MEAN = 1


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
class RxConnector(Enum):
	"""204 Members, I11I ... RH8"""
	I11I = 0
	I12O = 1
	I13I = 2
	I14O = 3
	I15I = 4
	I16O = 5
	I17I = 6
	I18O = 7
	I21I = 8
	I22O = 9
	I23I = 10
	I24O = 11
	I25I = 12
	I26O = 13
	I27I = 14
	I28O = 15
	I31I = 16
	I32O = 17
	I33I = 18
	I34O = 19
	I35I = 20
	I36O = 21
	I37I = 22
	I38O = 23
	I41I = 24
	I42O = 25
	I43I = 26
	I44O = 27
	I45I = 28
	I46O = 29
	I47I = 30
	I48O = 31
	IF1 = 32
	IF2 = 33
	IF3 = 34
	IQ1I = 35
	IQ2O = 36
	IQ3I = 37
	IQ4O = 38
	IQ5I = 39
	IQ6O = 40
	IQ7I = 41
	IQ8O = 42
	R11 = 43
	R118 = 44
	R1183 = 45
	R1184 = 46
	R11C = 47
	R11O = 48
	R11O3 = 49
	R11O4 = 50
	R12 = 51
	R12C = 52
	R12I = 53
	R13 = 54
	R13C = 55
	R13O = 56
	R14 = 57
	R14C = 58
	R14I = 59
	R15 = 60
	R16 = 61
	R17 = 62
	R18 = 63
	R21 = 64
	R214 = 65
	R218 = 66
	R21C = 67
	R21O = 68
	R22 = 69
	R22C = 70
	R22I = 71
	R23 = 72
	R23C = 73
	R23O = 74
	R24 = 75
	R24C = 76
	R24I = 77
	R25 = 78
	R258 = 79
	R26 = 80
	R27 = 81
	R28 = 82
	R31 = 83
	R318 = 84
	R31C = 85
	R31O = 86
	R32 = 87
	R32C = 88
	R32I = 89
	R33 = 90
	R33C = 91
	R33O = 92
	R34 = 93
	R34C = 94
	R34I = 95
	R35 = 96
	R36 = 97
	R37 = 98
	R38 = 99
	R41 = 100
	R418 = 101
	R41C = 102
	R41O = 103
	R42 = 104
	R42C = 105
	R42I = 106
	R43 = 107
	R43C = 108
	R43O = 109
	R44 = 110
	R44C = 111
	R44I = 112
	R45 = 113
	R46 = 114
	R47 = 115
	R48 = 116
	RA1 = 117
	RA18 = 118
	RA2 = 119
	RA3 = 120
	RA4 = 121
	RA5 = 122
	RA6 = 123
	RA7 = 124
	RA8 = 125
	RB1 = 126
	RB14 = 127
	RB18 = 128
	RB2 = 129
	RB3 = 130
	RB4 = 131
	RB5 = 132
	RB6 = 133
	RB7 = 134
	RB8 = 135
	RC1 = 136
	RC18 = 137
	RC2 = 138
	RC3 = 139
	RC4 = 140
	RC5 = 141
	RC6 = 142
	RC7 = 143
	RC8 = 144
	RD1 = 145
	RD18 = 146
	RD2 = 147
	RD3 = 148
	RD4 = 149
	RD5 = 150
	RD6 = 151
	RD7 = 152
	RD8 = 153
	RE1 = 154
	RE18 = 155
	RE2 = 156
	RE3 = 157
	RE4 = 158
	RE5 = 159
	RE6 = 160
	RE7 = 161
	RE8 = 162
	RF1 = 163
	RF18 = 164
	RF1C = 165
	RF1O = 166
	RF2 = 167
	RF2C = 168
	RF2I = 169
	RF3 = 170
	RF3C = 171
	RF3O = 172
	RF4 = 173
	RF4C = 174
	RF4I = 175
	RF5 = 176
	RF5C = 177
	RF6 = 178
	RF6C = 179
	RF7 = 180
	RF8 = 181
	RFAC = 182
	RFAO = 183
	RFBC = 184
	RFBI = 185
	RG1 = 186
	RG18 = 187
	RG2 = 188
	RG3 = 189
	RG4 = 190
	RG5 = 191
	RG6 = 192
	RG7 = 193
	RG8 = 194
	RH1 = 195
	RH18 = 196
	RH2 = 197
	RH3 = 198
	RH4 = 199
	RH5 = 200
	RH6 = 201
	RH7 = 202
	RH8 = 203


# noinspection SpellCheckingInspection
class RxConnectorExt(Enum):
	"""154 Members, I11I ... RH8"""
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
	IF1 = 16
	IF2 = 17
	IF3 = 18
	IQ1I = 19
	IQ3I = 20
	IQ5I = 21
	IQ7I = 22
	R11 = 23
	R11C = 24
	R12 = 25
	R12C = 26
	R12I = 27
	R13 = 28
	R13C = 29
	R14 = 30
	R14C = 31
	R14I = 32
	R15 = 33
	R16 = 34
	R17 = 35
	R18 = 36
	R21 = 37
	R21C = 38
	R22 = 39
	R22C = 40
	R22I = 41
	R23 = 42
	R23C = 43
	R24 = 44
	R24C = 45
	R24I = 46
	R25 = 47
	R26 = 48
	R27 = 49
	R28 = 50
	R31 = 51
	R31C = 52
	R32 = 53
	R32C = 54
	R32I = 55
	R33 = 56
	R33C = 57
	R34 = 58
	R34C = 59
	R34I = 60
	R35 = 61
	R36 = 62
	R37 = 63
	R38 = 64
	R41 = 65
	R41C = 66
	R42 = 67
	R42C = 68
	R42I = 69
	R43 = 70
	R43C = 71
	R44 = 72
	R44C = 73
	R44I = 74
	R45 = 75
	R46 = 76
	R47 = 77
	R48 = 78
	RA1 = 79
	RA2 = 80
	RA3 = 81
	RA4 = 82
	RA5 = 83
	RA6 = 84
	RA7 = 85
	RA8 = 86
	RB1 = 87
	RB2 = 88
	RB3 = 89
	RB4 = 90
	RB5 = 91
	RB6 = 92
	RB7 = 93
	RB8 = 94
	RC1 = 95
	RC2 = 96
	RC3 = 97
	RC4 = 98
	RC5 = 99
	RC6 = 100
	RC7 = 101
	RC8 = 102
	RD1 = 103
	RD2 = 104
	RD3 = 105
	RD4 = 106
	RD5 = 107
	RD6 = 108
	RD7 = 109
	RD8 = 110
	RE1 = 111
	RE2 = 112
	RE3 = 113
	RE4 = 114
	RE5 = 115
	RE6 = 116
	RE7 = 117
	RE8 = 118
	RF1 = 119
	RF1C = 120
	RF2 = 121
	RF2C = 122
	RF2I = 123
	RF3 = 124
	RF3C = 125
	RF4 = 126
	RF4C = 127
	RF4I = 128
	RF5 = 129
	RF5C = 130
	RF6 = 131
	RF6C = 132
	RF7 = 133
	RF8 = 134
	RFAC = 135
	RFBC = 136
	RFBI = 137
	RG1 = 138
	RG2 = 139
	RG3 = 140
	RG4 = 141
	RG5 = 142
	RG6 = 143
	RG7 = 144
	RG8 = 145
	RH1 = 146
	RH2 = 147
	RH3 = 148
	RH4 = 149
	RH5 = 150
	RH6 = 151
	RH7 = 152
	RH8 = 153


# noinspection SpellCheckingInspection
class RxConverter(Enum):
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
class RxTxConverter(Enum):
	"""80 Members, IRX1 ... TX44"""
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
	ITX1 = 20
	ITX11 = 21
	ITX12 = 22
	ITX13 = 23
	ITX14 = 24
	ITX2 = 25
	ITX21 = 26
	ITX22 = 27
	ITX23 = 28
	ITX24 = 29
	ITX3 = 30
	ITX31 = 31
	ITX32 = 32
	ITX33 = 33
	ITX34 = 34
	ITX4 = 35
	ITX41 = 36
	ITX42 = 37
	ITX43 = 38
	ITX44 = 39
	RX1 = 40
	RX11 = 41
	RX12 = 42
	RX13 = 43
	RX14 = 44
	RX2 = 45
	RX21 = 46
	RX22 = 47
	RX23 = 48
	RX24 = 49
	RX3 = 50
	RX31 = 51
	RX32 = 52
	RX33 = 53
	RX34 = 54
	RX4 = 55
	RX41 = 56
	RX42 = 57
	RX43 = 58
	RX44 = 59
	TX1 = 60
	TX11 = 61
	TX12 = 62
	TX13 = 63
	TX14 = 64
	TX2 = 65
	TX21 = 66
	TX22 = 67
	TX23 = 68
	TX24 = 69
	TX3 = 70
	TX31 = 71
	TX32 = 72
	TX33 = 73
	TX34 = 74
	TX4 = 75
	TX41 = 76
	TX42 = 77
	TX43 = 78
	TX44 = 79


# noinspection SpellCheckingInspection
class SlopeType(Enum):
	"""2 Members, NEGative ... POSitive"""
	NEGative = 0
	POSitive = 1


# noinspection SpellCheckingInspection
class StopCondition(Enum):
	"""2 Members, NONE ... SLFail"""
	NONE = 0
	SLFail = 1


# noinspection SpellCheckingInspection
class SynchroMode(Enum):
	"""2 Members, NORMal ... TOLerant"""
	NORMal = 0
	TOLerant = 1


# noinspection SpellCheckingInspection
class TrainingMode(Enum):
	"""2 Members, MMODe ... TMODe"""
	MMODe = 0
	TMODe = 1


# noinspection SpellCheckingInspection
class TriggerSlope(Enum):
	"""4 Members, FEDGe ... REDGe"""
	FEDGe = 0
	OFF = 1
	ON = 2
	REDGe = 3

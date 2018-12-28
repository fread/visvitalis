EESchema Schematic File Version 4
LIBS:zero-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_02x04_Odd_Even J2
U 1 1 5C262D84
P 1300 1900
F 0 "J2" H 1350 2217 50  0000 C CNN
F 1 "Conn_02x04_Odd_Even" H 1350 2126 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x04_Pitch2.54mm" H 1300 1900 50  0001 C CNN
F 3 "~" H 1300 1900 50  0001 C CNN
	1    1300 1900
	1    0    0    -1  
$EndComp
$Comp
L Device:D D1
U 1 1 5C262F0E
P 2050 1250
F 0 "D1" H 2050 1034 50  0000 C CNN
F 1 "D" H 2050 1125 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 1250 50  0001 C CNN
F 3 "~" H 2050 1250 50  0001 C CNN
	1    2050 1250
	-1   0    0    1   
$EndComp
$Comp
L Device:D D2
U 1 1 5C262FA4
P 2050 1450
F 0 "D2" H 2050 1234 50  0000 C CNN
F 1 "D" H 2050 1325 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 1450 50  0001 C CNN
F 3 "~" H 2050 1450 50  0001 C CNN
	1    2050 1450
	-1   0    0    1   
$EndComp
$Comp
L Device:D D3
U 1 1 5C262FC2
P 2050 1650
F 0 "D3" H 2050 1434 50  0000 C CNN
F 1 "D" H 2050 1525 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 1650 50  0001 C CNN
F 3 "~" H 2050 1650 50  0001 C CNN
	1    2050 1650
	-1   0    0    1   
$EndComp
$Comp
L Device:D D4
U 1 1 5C262FDE
P 2050 1850
F 0 "D4" H 2050 1634 50  0000 C CNN
F 1 "D" H 2050 1725 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 1850 50  0001 C CNN
F 3 "~" H 2050 1850 50  0001 C CNN
	1    2050 1850
	-1   0    0    1   
$EndComp
$Comp
L Device:D D5
U 1 1 5C262FFC
P 2050 2050
F 0 "D5" H 2050 1834 50  0000 C CNN
F 1 "D" H 2050 1925 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 2050 50  0001 C CNN
F 3 "~" H 2050 2050 50  0001 C CNN
	1    2050 2050
	-1   0    0    1   
$EndComp
$Comp
L Device:D D6
U 1 1 5C263020
P 2050 2250
F 0 "D6" H 2050 2034 50  0000 C CNN
F 1 "D" H 2050 2125 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 2250 50  0001 C CNN
F 3 "~" H 2050 2250 50  0001 C CNN
	1    2050 2250
	-1   0    0    1   
$EndComp
$Comp
L Device:D D7
U 1 1 5C263042
P 2050 2450
F 0 "D7" H 2050 2234 50  0000 C CNN
F 1 "D" H 2050 2325 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 2450 50  0001 C CNN
F 3 "~" H 2050 2450 50  0001 C CNN
	1    2050 2450
	-1   0    0    1   
$EndComp
$Comp
L Device:D D8
U 1 1 5C263066
P 2050 2650
F 0 "D8" H 2050 2434 50  0000 C CNN
F 1 "D" H 2050 2525 50  0000 C CNN
F 2 "Diodes_SMD:D_2114" H 2050 2650 50  0001 C CNN
F 3 "~" H 2050 2650 50  0001 C CNN
	1    2050 2650
	-1   0    0    1   
$EndComp
Wire Wire Line
	1600 1900 1900 1900
Wire Wire Line
	1900 1900 1900 1850
Wire Wire Line
	1100 1900 1100 1850
Wire Wire Line
	1100 1850 1850 1850
Wire Wire Line
	1850 1850 1850 1650
Wire Wire Line
	1850 1650 1900 1650
Wire Wire Line
	1600 1800 1800 1800
Wire Wire Line
	1800 1800 1800 1450
Wire Wire Line
	1800 1450 1900 1450
Wire Wire Line
	1100 1800 1100 1750
Wire Wire Line
	1100 1750 1750 1750
Wire Wire Line
	1750 1750 1750 1250
Wire Wire Line
	1750 1250 1900 1250
Wire Wire Line
	1100 2000 1100 1950
Wire Wire Line
	1100 1950 1900 1950
Wire Wire Line
	1900 1950 1900 2050
Wire Wire Line
	1600 2000 1850 2000
Wire Wire Line
	1850 2000 1850 2250
Wire Wire Line
	1850 2250 1900 2250
Wire Wire Line
	1100 2100 1100 2050
Wire Wire Line
	1100 2050 1800 2050
Wire Wire Line
	1800 2050 1800 2450
Wire Wire Line
	1800 2450 1900 2450
Wire Wire Line
	1600 2100 1750 2100
Wire Wire Line
	1750 2100 1750 2650
Wire Wire Line
	1750 2650 1900 2650
$Comp
L Connector_Generic:Conn_02x02_Odd_Even J1
U 1 1 5C264899
P 1300 800
F 0 "J1" H 1350 1017 50  0000 C CNN
F 1 "Conn_02x02_Odd_Even" H 1350 926 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x02_Pitch2.54mm" H 1300 800 50  0001 C CNN
F 3 "~" H 1300 800 50  0001 C CNN
	1    1300 800 
	1    0    0    -1  
$EndComp
$Comp
L power:+12V #PWR01
U 1 1 5C268CC1
P 1000 800
F 0 "#PWR01" H 1000 650 50  0001 C CNN
F 1 "+12V" V 1015 928 50  0000 L CNN
F 2 "" H 1000 800 50  0001 C CNN
F 3 "" H 1000 800 50  0001 C CNN
	1    1000 800 
	0    -1   -1   0   
$EndComp
$Comp
L power:+12V #PWR02
U 1 1 5C268E6D
P 1700 800
F 0 "#PWR02" H 1700 650 50  0001 C CNN
F 1 "+12V" V 1715 928 50  0000 L CNN
F 2 "" H 1700 800 50  0001 C CNN
F 3 "" H 1700 800 50  0001 C CNN
	1    1700 800 
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR03
U 1 1 5C268FA7
P 1000 900
F 0 "#PWR03" H 1000 650 50  0001 C CNN
F 1 "GND" V 1005 772 50  0000 R CNN
F 2 "" H 1000 900 50  0001 C CNN
F 3 "" H 1000 900 50  0001 C CNN
	1    1000 900 
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR04
U 1 1 5C269B65
P 1700 900
F 0 "#PWR04" H 1700 650 50  0001 C CNN
F 1 "GND" V 1705 772 50  0000 R CNN
F 2 "" H 1700 900 50  0001 C CNN
F 3 "" H 1700 900 50  0001 C CNN
	1    1700 900 
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1000 800  1100 800 
Wire Wire Line
	1000 900  1100 900 
Wire Wire Line
	1600 800  1700 800 
Wire Wire Line
	1700 900  1600 900 
$Comp
L hk19f:HK19F K1
U 1 1 5C26B097
P 2500 3050
F 0 "K1" H 3330 3096 50  0000 L CNN
F 1 "HK19F" H 3330 3005 50  0000 L CNN
F 2 "hk19f:Relay_DPDT_HK19F" H 3250 3100 50  0001 C CNN
F 3 "" H 2500 3050 50  0001 C CNN
	1    2500 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	2300 2750 2300 2650
Wire Wire Line
	2300 1250 2200 1250
Wire Wire Line
	2200 2650 2300 2650
Connection ~ 2300 2650
Wire Wire Line
	2300 2650 2300 2450
Wire Wire Line
	2200 2450 2300 2450
Connection ~ 2300 2450
Wire Wire Line
	2300 2450 2300 2250
Wire Wire Line
	2200 2250 2300 2250
Connection ~ 2300 2250
Wire Wire Line
	2300 2250 2300 2050
Wire Wire Line
	2200 2050 2300 2050
Connection ~ 2300 2050
Wire Wire Line
	2300 2050 2300 1850
Wire Wire Line
	2200 1850 2300 1850
Connection ~ 2300 1850
Wire Wire Line
	2300 1850 2300 1650
Wire Wire Line
	2200 1650 2300 1650
Connection ~ 2300 1650
Wire Wire Line
	2300 1650 2300 1450
Wire Wire Line
	2200 1450 2300 1450
Connection ~ 2300 1450
Wire Wire Line
	2300 1450 2300 1250
$Comp
L power:GND #PWR07
U 1 1 5C26F1B9
P 2300 3350
F 0 "#PWR07" H 2300 3100 50  0001 C CNN
F 1 "GND" H 2305 3177 50  0000 C CNN
F 2 "" H 2300 3350 50  0001 C CNN
F 3 "" H 2300 3350 50  0001 C CNN
	1    2300 3350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR06
U 1 1 5C26F853
P 2800 2750
F 0 "#PWR06" H 2800 2500 50  0001 C CNN
F 1 "GND" H 2805 2577 50  0000 C CNN
F 2 "" H 2800 2750 50  0001 C CNN
F 3 "" H 2800 2750 50  0001 C CNN
	1    2800 2750
	-1   0    0    1   
$EndComp
$Comp
L power:+12V #PWR05
U 1 1 5C26F99D
P 2600 2750
F 0 "#PWR05" H 2600 2600 50  0001 C CNN
F 1 "+12V" H 2615 2923 50  0000 C CNN
F 2 "" H 2600 2750 50  0001 C CNN
F 3 "" H 2600 2750 50  0001 C CNN
	1    2600 2750
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J3
U 1 1 5C275517
P 3000 3650
F 0 "J3" H 2919 3325 50  0000 C CNN
F 1 "Conn_01x02" H 2919 3416 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 3000 3650 50  0001 C CNN
F 3 "~" H 3000 3650 50  0001 C CNN
	1    3000 3650
	1    0    0    1   
$EndComp
Wire Wire Line
	2700 3350 2700 3550
Wire Wire Line
	2700 3550 2800 3550
$Comp
L power:GND #PWR08
U 1 1 5C27818A
P 2700 3750
F 0 "#PWR08" H 2700 3500 50  0001 C CNN
F 1 "GND" H 2705 3577 50  0000 C CNN
F 2 "" H 2700 3750 50  0001 C CNN
F 3 "" H 2700 3750 50  0001 C CNN
	1    2700 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	2800 3650 2700 3650
Wire Wire Line
	2700 3650 2700 3750
$EndSCHEMATC

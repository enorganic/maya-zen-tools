//Maya ASCII 2025ff03 scene
//Name: test_loop.ma
//Last modified: Sat, Jan 04, 2025 09:28:53 AM
//Codeset: UTF-8
requires maya "2025ff03";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2025";
fileInfo "version" "2025";
fileInfo "cutIdentifier" "202409190603-cbdc5a7e54";
fileInfo "osv" "Mac OS X 15.2";
fileInfo "UUID" "8E511C7F-EE47-7420-B35E-B0AA741E78FF";
createNode transform -s -n "persp";
	rename -uid "702995A2-7D46-013D-730A-239D5FB27568";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 28 21 28 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "C5460C01-4F4B-6A3B-142D-D5A545553DB9";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "79805A8F-2146-D3D1-F124-D4A451D416E9";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "74985FFE-AD41-E174-44E0-74B56A5ED03E";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "9121509A-194B-327C-06A0-AAAD880F447F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "01281417-BA4C-3284-7D8C-998CACC50259";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "3C52B1E6-E74C-5BBD-141C-E99CE7687183";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "EA5DE2A1-C24D-A8DE-5F79-3A99D570A54E";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "polyPlane";
	rename -uid "CF188ECD-B047-264C-7761-74A8DF788FFF";
createNode mesh -n "polyPlaneShape" -p "polyPlane";
	rename -uid "8E2B06AB-3042-908F-C017-E89CC2EC6C94";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 5 ".gtag";
	setAttr ".gtag[0].gtagnm" -type "string" "back";
	setAttr ".gtag[0].gtagcmp" -type "componentList" 1 "e[204:213]";
	setAttr ".gtag[1].gtagnm" -type "string" "front";
	setAttr ".gtag[1].gtagcmp" -type "componentList" 8 "e[0]" "e[2]" "e[4]" "e[6]" "e[9]" "e[11]" "e[13]" "e[15]";
	setAttr ".gtag[2].gtagnm" -type "string" "left";
	setAttr ".gtag[2].gtagcmp" -type "componentList" 10 "e[1]" "e[19]" "e[37]" "e[58]" "e[79]" "e[100]" "e[121]" "e[142]" "e[163]" "e[184]";
	setAttr ".gtag[3].gtagnm" -type "string" "right";
	setAttr ".gtag[3].gtagcmp" -type "componentList" 10 "e[17]" "e[35]" "e[56]" "e[77]" "e[98]" "e[119]" "e[140]" "e[161]" "e[182]" "e[203]";
	setAttr ".gtag[4].gtagnm" -type "string" "rim";
	setAttr ".gtag[4].gtagcmp" -type "componentList" 26 "e[0:2]" "e[4]" "e[6]" "e[9]" "e[11]" "e[13]" "e[15]" "e[17]" "e[19]" "e[35]" "e[37]" "e[56]" "e[58]" "e[77]" "e[79]" "e[98]" "e[100]" "e[119]" "e[121]" "e[140]" "e[142]" "e[161]" "e[163]" "e[182]" "e[184]" "e[203:213]";
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 119 ".uvst[0].uvsp[0:118]" -type "float2" 0 0 0.1 0 0.2 0 0.30000001
		 0 0.40000001 0 0.60000002 0 0.69999999 0 0.80000001 0 0.90000004 0 1 0 0 0.1 0.1
		 0.1 0.2 0.1 0.30000001 0.1 0.40000001 0.1 0.60000002 0.1 0.69999999 0.1 0.80000001
		 0.1 0.90000004 0.1 1 0.1 0 0.2 0.1 0.2 0.2 0.2 0.30000001 0.2 0.40000001 0.2 0.5
		 0.2 0.60000002 0.2 0.69999999 0.2 0.80000001 0.2 0.90000004 0.2 1 0.2 0 0.30000001
		 0.1 0.30000001 0.2 0.30000001 0.30000001 0.30000001 0.40000001 0.30000001 0.5 0.30000001
		 0.60000002 0.30000001 0.69999999 0.30000001 0.80000001 0.30000001 0.90000004 0.30000001
		 1 0.30000001 0 0.40000001 0.1 0.40000001 0.2 0.40000001 0.30000001 0.40000001 0.40000001
		 0.40000001 0.5 0.40000001 0.60000002 0.40000001 0.69999999 0.40000001 0.80000001
		 0.40000001 0.90000004 0.40000001 1 0.40000001 0 0.5 0.1 0.5 0.2 0.5 0.30000001 0.5
		 0.40000001 0.5 0.5 0.5 0.60000002 0.5 0.69999999 0.5 0.80000001 0.5 0.90000004 0.5
		 1 0.5 0 0.60000002 0.1 0.60000002 0.2 0.60000002 0.30000001 0.60000002 0.40000001
		 0.60000002 0.5 0.60000002 0.60000002 0.60000002 0.69999999 0.60000002 0.80000001
		 0.60000002 0.90000004 0.60000002 1 0.60000002 0 0.69999999 0.1 0.69999999 0.2 0.69999999
		 0.30000001 0.69999999 0.40000001 0.69999999 0.5 0.69999999 0.60000002 0.69999999
		 0.69999999 0.69999999 0.80000001 0.69999999 0.90000004 0.69999999 1 0.69999999 0
		 0.80000001 0.1 0.80000001 0.2 0.80000001 0.30000001 0.80000001 0.40000001 0.80000001
		 0.5 0.80000001 0.60000002 0.80000001 0.69999999 0.80000001 0.80000001 0.80000001
		 0.90000004 0.80000001 1 0.80000001 0 0.90000004 0.1 0.90000004 0.2 0.90000004 0.30000001
		 0.90000004 0.40000001 0.90000004 0.5 0.90000004 0.60000002 0.90000004 0.69999999
		 0.90000004 0.80000001 0.90000004 0.90000004 0.90000004 1 0.90000004 0 1 0.1 1 0.2
		 1 0.30000001 1 0.40000001 1 0.5 1 0.60000002 1 0.69999999 1 0.80000001 1 0.90000004
		 1 1 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 119 ".vt[0:118]"  -0.5 -1.110223e-16 0.5 -0.40000001 -1.110223e-16 0.5
		 -0.30000001 -1.110223e-16 0.5 -0.19999999 -1.110223e-16 0.5 -0.099999994 -1.110223e-16 0.5
		 0.10000002 -1.110223e-16 0.5 0.19999999 -1.110223e-16 0.5 0.30000001 -1.110223e-16 0.5
		 0.40000004 -1.110223e-16 0.5 0.5 -1.110223e-16 0.5 -0.5 -8.8817843e-17 0.40000001
		 -0.40000001 -8.8817843e-17 0.40000001 -0.30000001 -8.8817843e-17 0.40000001 -0.19999999 -8.8817843e-17 0.40000001
		 -0.099999994 -8.8817843e-17 0.40000001 0.10000002 -8.8817843e-17 0.40000001 0.19999999 -8.8817843e-17 0.40000001
		 0.30000001 -8.8817843e-17 0.40000001 0.40000004 -8.8817843e-17 0.40000001 0.5 -8.8817843e-17 0.40000001
		 -0.5 -6.6613384e-17 0.30000001 -0.40000001 -6.6613384e-17 0.30000001 -0.30000001 -6.6613384e-17 0.30000001
		 -0.19999999 -6.6613384e-17 0.30000001 -0.099999994 -6.6613384e-17 0.30000001 0 -6.6613384e-17 0.30000001
		 0.10000002 -6.6613384e-17 0.30000001 0.19999999 -6.6613384e-17 0.30000001 0.30000001 -6.6613384e-17 0.30000001
		 0.40000004 -6.6613384e-17 0.30000001 0.5 -6.6613384e-17 0.30000001 -0.5 -4.4408918e-17 0.19999999
		 -0.40000001 -4.4408918e-17 0.19999999 -0.30000001 -4.4408918e-17 0.19999999 -0.19999999 -4.4408918e-17 0.19999999
		 -0.099999994 -4.4408918e-17 0.19999999 0 -4.4408918e-17 0.19999999 0.10000002 -4.4408918e-17 0.19999999
		 0.19999999 -4.4408918e-17 0.19999999 0.30000001 -4.4408918e-17 0.19999999 0.40000004 -4.4408918e-17 0.19999999
		 0.5 -4.4408918e-17 0.19999999 -0.5 -2.2204459e-17 0.099999994 -0.40000001 -2.2204459e-17 0.099999994
		 -0.30000001 -2.2204459e-17 0.099999994 -0.19999999 -2.2204459e-17 0.099999994 -0.099999994 -2.2204459e-17 0.099999994
		 0 -2.2204459e-17 0.099999994 0.10000002 -2.2204459e-17 0.099999994 0.19999999 -2.2204459e-17 0.099999994
		 0.30000001 -2.2204459e-17 0.099999994 0.40000004 -2.2204459e-17 0.099999994 0.5 -2.2204459e-17 0.099999994
		 -0.5 0 0 -0.40000001 0 0 -0.30000001 0 0 -0.19999999 0 0 -0.099999994 0 0 0 0 0 0.10000002 0 0
		 0.19999999 0 0 0.30000001 0 0 0.40000004 0 0 0.5 0 0 -0.5 2.2204466e-17 -0.10000002
		 -0.40000001 2.2204466e-17 -0.10000002 -0.30000001 2.2204466e-17 -0.10000002 -0.19999999 2.2204466e-17 -0.10000002
		 -0.099999994 2.2204466e-17 -0.10000002 0 2.2204466e-17 -0.10000002 0.10000002 2.2204466e-17 -0.10000002
		 0.19999999 2.2204466e-17 -0.10000002 0.30000001 2.2204466e-17 -0.10000002 0.40000004 2.2204466e-17 -0.10000002
		 0.5 2.2204466e-17 -0.10000002 -0.5 4.4408918e-17 -0.19999999 -0.40000001 4.4408918e-17 -0.19999999
		 -0.30000001 4.4408918e-17 -0.19999999 -0.19999999 4.4408918e-17 -0.19999999 -0.099999994 4.4408918e-17 -0.19999999
		 0 4.4408918e-17 -0.19999999 0.10000002 4.4408918e-17 -0.19999999 0.19999999 4.4408918e-17 -0.19999999
		 0.30000001 4.4408918e-17 -0.19999999 0.40000004 4.4408918e-17 -0.19999999 0.5 4.4408918e-17 -0.19999999
		 -0.5 6.6613384e-17 -0.30000001 -0.40000001 6.6613384e-17 -0.30000001 -0.30000001 6.6613384e-17 -0.30000001
		 -0.19999999 6.6613384e-17 -0.30000001 -0.099999994 6.6613384e-17 -0.30000001 0 6.6613384e-17 -0.30000001
		 0.10000002 6.6613384e-17 -0.30000001 0.19999999 6.6613384e-17 -0.30000001 0.30000001 6.6613384e-17 -0.30000001
		 0.40000004 6.6613384e-17 -0.30000001 0.5 6.6613384e-17 -0.30000001 -0.5 8.881785e-17 -0.40000004
		 -0.40000001 8.881785e-17 -0.40000004 -0.30000001 8.881785e-17 -0.40000004 -0.19999999 8.881785e-17 -0.40000004
		 -0.099999994 8.881785e-17 -0.40000004 0 8.881785e-17 -0.40000004 0.10000002 8.881785e-17 -0.40000004
		 0.19999999 8.881785e-17 -0.40000004 0.30000001 8.881785e-17 -0.40000004 0.40000004 8.881785e-17 -0.40000004
		 0.5 8.881785e-17 -0.40000004 -0.5 1.110223e-16 -0.5 -0.40000001 1.110223e-16 -0.5
		 -0.30000001 1.110223e-16 -0.5 -0.19999999 1.110223e-16 -0.5 -0.099999994 1.110223e-16 -0.5
		 0 1.110223e-16 -0.5 0.10000002 1.110223e-16 -0.5 0.19999999 1.110223e-16 -0.5 0.30000001 1.110223e-16 -0.5
		 0.40000004 1.110223e-16 -0.5 0.5 1.110223e-16 -0.5;
	setAttr -s 214 ".ed";
	setAttr ".ed[0:165]"  0 1 0 0 10 0 1 2 0 1 11 1 2 3 0 2 12 1 3 4 0 3 13 1
		 4 14 1 5 6 0 5 15 1 6 7 0 6 16 1 7 8 0 7 17 1 8 9 0 8 18 1 9 19 0 10 11 1 10 20 0
		 11 12 1 11 21 1 12 13 1 12 22 1 13 14 1 13 23 1 14 24 1 15 16 1 15 26 1 16 17 1 16 27 1
		 17 18 1 17 28 1 18 19 1 18 29 1 19 30 0 20 21 1 20 31 0 21 22 1 21 32 1 22 23 1 22 33 1
		 23 24 1 23 34 1 24 25 1 24 35 1 25 26 1 25 36 1 26 27 1 26 37 1 27 28 1 27 38 1 28 29 1
		 28 39 1 29 30 1 29 40 1 30 41 0 31 32 1 31 42 0 32 33 1 32 43 1 33 34 1 33 44 1 34 35 1
		 34 45 1 35 36 1 35 46 1 36 37 1 36 47 1 37 38 1 37 48 1 38 39 1 38 49 1 39 40 1 39 50 1
		 40 41 1 40 51 1 41 52 0 42 43 1 42 53 0 43 44 1 43 54 1 44 45 1 44 55 1 45 46 1 45 56 1
		 46 47 1 46 57 1 47 48 1 47 58 1 48 49 1 48 59 1 49 50 1 49 60 1 50 51 1 50 61 1 51 52 1
		 51 62 1 52 63 0 53 54 1 53 64 0 54 55 1 54 65 1 55 56 1 55 66 1 56 57 1 56 67 1 57 58 1
		 57 68 1 58 59 1 58 69 1 59 60 1 59 70 1 60 61 1 60 71 1 61 62 1 61 72 1 62 63 1 62 73 1
		 63 74 0 64 65 1 64 75 0 65 66 1 65 76 1 66 67 1 66 77 1 67 68 1 67 78 1 68 69 1 68 79 1
		 69 70 1 69 80 1 70 71 1 70 81 1 71 72 1 71 82 1 72 73 1 72 83 1 73 74 1 73 84 1 74 85 0
		 75 76 1 75 86 0 76 77 1 76 87 1 77 78 1 77 88 1 78 79 1 78 89 1 79 80 1 79 90 1 80 81 1
		 80 91 1 81 82 1 81 92 1 82 83 1 82 93 1 83 84 1 83 94 1 84 85 1 84 95 1 85 96 0 86 87 1
		 86 97 0 87 88 1 87 98 1;
	setAttr ".ed[166:213]" 88 89 1 88 99 1 89 90 1 89 100 1 90 91 1 90 101 1 91 92 1
		 91 102 1 92 93 1 92 103 1 93 94 1 93 104 1 94 95 1 94 105 1 95 96 1 95 106 1 96 107 0
		 97 98 1 97 108 0 98 99 1 98 109 1 99 100 1 99 110 1 100 101 1 100 111 1 101 102 1
		 101 112 1 102 103 1 102 113 1 103 104 1 103 114 1 104 105 1 104 115 1 105 106 1 105 116 1
		 106 107 1 106 117 1 107 118 0 108 109 0 109 110 0 110 111 0 111 112 0 112 113 0 113 114 0
		 114 115 0 115 116 0 116 117 0 117 118 0;
	setAttr -s 96 -ch 384 ".fc[0:95]" -type "polyFaces" 
		f 4 0 3 -19 -2
		mu 0 4 0 1 11 10
		f 4 2 5 -21 -4
		mu 0 4 1 2 12 11
		f 4 4 7 -23 -6
		mu 0 4 2 3 13 12
		f 4 6 8 -25 -8
		mu 0 4 3 4 14 13
		f 4 9 12 -28 -11
		mu 0 4 5 6 16 15
		f 4 11 14 -30 -13
		mu 0 4 6 7 17 16
		f 4 13 16 -32 -15
		mu 0 4 7 8 18 17
		f 4 15 17 -34 -17
		mu 0 4 8 9 19 18
		f 4 18 21 -37 -20
		mu 0 4 10 11 21 20
		f 4 20 23 -39 -22
		mu 0 4 11 12 22 21
		f 4 22 25 -41 -24
		mu 0 4 12 13 23 22
		f 4 24 26 -43 -26
		mu 0 4 13 14 24 23
		f 4 27 30 -49 -29
		mu 0 4 15 16 27 26
		f 4 29 32 -51 -31
		mu 0 4 16 17 28 27
		f 4 31 34 -53 -33
		mu 0 4 17 18 29 28
		f 4 33 35 -55 -35
		mu 0 4 18 19 30 29
		f 4 36 39 -58 -38
		mu 0 4 20 21 32 31
		f 4 38 41 -60 -40
		mu 0 4 21 22 33 32
		f 4 40 43 -62 -42
		mu 0 4 22 23 34 33
		f 4 42 45 -64 -44
		mu 0 4 23 24 35 34
		f 4 44 47 -66 -46
		mu 0 4 24 25 36 35
		f 4 46 49 -68 -48
		mu 0 4 25 26 37 36
		f 4 48 51 -70 -50
		mu 0 4 26 27 38 37
		f 4 50 53 -72 -52
		mu 0 4 27 28 39 38
		f 4 52 55 -74 -54
		mu 0 4 28 29 40 39
		f 4 54 56 -76 -56
		mu 0 4 29 30 41 40
		f 4 57 60 -79 -59
		mu 0 4 31 32 43 42
		f 4 59 62 -81 -61
		mu 0 4 32 33 44 43
		f 4 61 64 -83 -63
		mu 0 4 33 34 45 44
		f 4 63 66 -85 -65
		mu 0 4 34 35 46 45
		f 4 65 68 -87 -67
		mu 0 4 35 36 47 46
		f 4 67 70 -89 -69
		mu 0 4 36 37 48 47
		f 4 69 72 -91 -71
		mu 0 4 37 38 49 48
		f 4 71 74 -93 -73
		mu 0 4 38 39 50 49
		f 4 73 76 -95 -75
		mu 0 4 39 40 51 50
		f 4 75 77 -97 -77
		mu 0 4 40 41 52 51
		f 4 78 81 -100 -80
		mu 0 4 42 43 54 53
		f 4 80 83 -102 -82
		mu 0 4 43 44 55 54
		f 4 82 85 -104 -84
		mu 0 4 44 45 56 55
		f 4 84 87 -106 -86
		mu 0 4 45 46 57 56
		f 4 86 89 -108 -88
		mu 0 4 46 47 58 57
		f 4 88 91 -110 -90
		mu 0 4 47 48 59 58
		f 4 90 93 -112 -92
		mu 0 4 48 49 60 59
		f 4 92 95 -114 -94
		mu 0 4 49 50 61 60
		f 4 94 97 -116 -96
		mu 0 4 50 51 62 61
		f 4 96 98 -118 -98
		mu 0 4 51 52 63 62
		f 4 99 102 -121 -101
		mu 0 4 53 54 65 64
		f 4 101 104 -123 -103
		mu 0 4 54 55 66 65
		f 4 103 106 -125 -105
		mu 0 4 55 56 67 66
		f 4 105 108 -127 -107
		mu 0 4 56 57 68 67
		f 4 107 110 -129 -109
		mu 0 4 57 58 69 68
		f 4 109 112 -131 -111
		mu 0 4 58 59 70 69
		f 4 111 114 -133 -113
		mu 0 4 59 60 71 70
		f 4 113 116 -135 -115
		mu 0 4 60 61 72 71
		f 4 115 118 -137 -117
		mu 0 4 61 62 73 72
		f 4 117 119 -139 -119
		mu 0 4 62 63 74 73
		f 4 120 123 -142 -122
		mu 0 4 64 65 76 75
		f 4 122 125 -144 -124
		mu 0 4 65 66 77 76
		f 4 124 127 -146 -126
		mu 0 4 66 67 78 77
		f 4 126 129 -148 -128
		mu 0 4 67 68 79 78
		f 4 128 131 -150 -130
		mu 0 4 68 69 80 79
		f 4 130 133 -152 -132
		mu 0 4 69 70 81 80
		f 4 132 135 -154 -134
		mu 0 4 70 71 82 81
		f 4 134 137 -156 -136
		mu 0 4 71 72 83 82
		f 4 136 139 -158 -138
		mu 0 4 72 73 84 83
		f 4 138 140 -160 -140
		mu 0 4 73 74 85 84
		f 4 141 144 -163 -143
		mu 0 4 75 76 87 86
		f 4 143 146 -165 -145
		mu 0 4 76 77 88 87
		f 4 145 148 -167 -147
		mu 0 4 77 78 89 88
		f 4 147 150 -169 -149
		mu 0 4 78 79 90 89
		f 4 149 152 -171 -151
		mu 0 4 79 80 91 90
		f 4 151 154 -173 -153
		mu 0 4 80 81 92 91
		f 4 153 156 -175 -155
		mu 0 4 81 82 93 92
		f 4 155 158 -177 -157
		mu 0 4 82 83 94 93
		f 4 157 160 -179 -159
		mu 0 4 83 84 95 94
		f 4 159 161 -181 -161
		mu 0 4 84 85 96 95
		f 4 162 165 -184 -164
		mu 0 4 86 87 98 97
		f 4 164 167 -186 -166
		mu 0 4 87 88 99 98
		f 4 166 169 -188 -168
		mu 0 4 88 89 100 99
		f 4 168 171 -190 -170
		mu 0 4 89 90 101 100
		f 4 170 173 -192 -172
		mu 0 4 90 91 102 101
		f 4 172 175 -194 -174
		mu 0 4 91 92 103 102
		f 4 174 177 -196 -176
		mu 0 4 92 93 104 103
		f 4 176 179 -198 -178
		mu 0 4 93 94 105 104
		f 4 178 181 -200 -180
		mu 0 4 94 95 106 105
		f 4 180 182 -202 -182
		mu 0 4 95 96 107 106
		f 4 183 186 -205 -185
		mu 0 4 97 98 109 108
		f 4 185 188 -206 -187
		mu 0 4 98 99 110 109
		f 4 187 190 -207 -189
		mu 0 4 99 100 111 110
		f 4 189 192 -208 -191
		mu 0 4 100 101 112 111
		f 4 191 194 -209 -193
		mu 0 4 101 102 113 112
		f 4 193 196 -210 -195
		mu 0 4 102 103 114 113
		f 4 195 198 -211 -197
		mu 0 4 103 104 115 114
		f 4 197 200 -212 -199
		mu 0 4 104 105 116 115
		f 4 199 202 -213 -201
		mu 0 4 105 106 117 116
		f 4 201 203 -214 -203
		mu 0 4 106 107 118 117;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".ndt" 0;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "718CDAF2-9E4A-19A4-A9CD-F886AF6B3730";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "CC3A9B31-4B4B-BF39-92C0-089926413800";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "923B69FB-C942-18BE-E9EA-9EA513AA5E09";
createNode displayLayerManager -n "layerManager";
	rename -uid "613CECA9-884A-D264-463F-8B9196F41E24";
createNode displayLayer -n "defaultLayer";
	rename -uid "06824086-AF4E-8049-4AB2-F0BE69FB92DE";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "782FB4C7-8B4F-2D02-760A-93B4CA83C5A1";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "AEAFC2C0-5246-F9E1-B551-A0A8D90C651E";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "88E38410-6242-FA80-C38A-5182675F6C6F";
	setAttr ".b" -type "string" "// Maya Mel UI Configuration File.\n// No UI generated in batch mode.\n";
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "8DC6697A-FB4E-DE75-C3C9-3E8E4D122BE9";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
	setAttr ".rtfm" 3;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".dss" -type "string" "standardSurface1";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "polyPlaneShape.iog" ":initialShadingGroup.dsm" -na;
// End of test_loop.ma

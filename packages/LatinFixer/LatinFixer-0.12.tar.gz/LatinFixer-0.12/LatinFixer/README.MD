# Repair badly decoded latin strings \x00 | \226\130\172 | â€œ | \xe2\x84\xa2 | \u2122 | &#032; | & yuml;

```python
$pip install LatinFixer
from LatinFixer import LatinFix
lfix = LatinFix(text, debug=False)
nw = (
lfix.apply_n_escaped()
# ('\\226\\132\\162', '™'),('\\226\\130\\172', '€'),('\\226\\128\\186', '›'),('\\226\\128\\185', '‹'),('\\226\\128\\176', '‰'),('\\226\\128\\166', '…'),('\\226\\128\\162', '•')
.remove_non_printable_chars()
# \x00 ...
.apply_wrong_chars()
# ('â€™', '’'),('â€”', '—'),('â€“', '–'),('â€˜', '‘'),('â€ž', '„'),('â€š', '‚'),('â€œ', '“') ...
.apply_x_69_lower_case_escaped()
# ('\\xe2\\x84\\xa2', '™'),('\\xe2\\x82\\xac', '€'),('\\xe2\\x80\\xba', '›'),('\\xe2\\x80\\xb9', '‹'),('\\xe2\\x80\\xb0', '‰'),('\\xe2\\x80\\xa6', '…') ...
.apply_x_69_upper_case_escaped()
# ('\\xE2\\x84\\xA2', '™'),('\\xE2\\x82\\xAC', '€'),('\\xE2\\x80\\xBA', '›'),('\\xE2\\x80\\xB9', '‹'),('\\xE2\\x80\\xB0', '‰')...
.apply_x_3_lower_case_escaped()
# ('\\xff', 'ÿ'),('\\xfe', 'þ'),('\\xfd', 'ý'),('\\xfc', 'ü'),('\\xfb', 'û'),('\\xfa', 'ú'),('\\xf9', 'ù'),('\\xf8', 'ø')...
.apply_x_3_upper_case_escaped()
#        ('\\xFF', 'ÿ'),('\\xFE', 'þ'),('\\xFD', 'ý'),('\\xFC', 'ü'),('\\xFB', 'û'),('\\xFA', 'ú'),('\\xF9', 'ù'),('\\xF8', 'ø'),('\\xF7', '÷') ...
.apply_u_4_upper_case_escaped()
# ('\\u2122', '™'),('\\u20AC', '€'),('\\u203A', '›'),('\\u2039', '‹'),('\\u2030', '‰'),('\\u2026', '…'),('\\u2022', '•') ...
.apply_u_4_lower_case_escaped()
# ('\\u2122', '™'),('\\u20ac', '€'),('\\u203a', '›'),('\\u2039', '‹'),('\\u2030', '‰'),('\\u2026', '…'),('\\u2022', '•'),('\\u2021', '‡')...
.apply_zerox_unescaped_lower()
# ('0xff', 'ÿ'),('0xfe', 'þ'),('0xfd', 'ý'),('0xfc', 'ü'),('0xfb', 'û'),('0xfa', 'ú'),('0xf9', 'ù'),('0xf8', 'ø')....
.apply_zerox_unescaped_upper()
# ('0xFF', 'ÿ'),('0xFE', 'þ'),('0xFD', 'ý'),('0xFC', 'ü'),('0xFB', 'û'),('0xFA', 'ú'),('0xF9', 'ù')...
.apply_html_character_reference()
# ('&#032;', ' '),('&#033;', '!'),('&#034;', '"'),('&#035;', '#'),('&#036;', '$'),('&#037;', '%'),('&#038;', '&'),('&#039;', "'"),('&#040;', '('),('&#041;', ')'),('&#042;', '*')...
.apply_html_entity_reference()
# ('&yuml;', 'ÿ'),('&yen;', '¥'),('&yacute;', 'ý'),('&verbar;', '|'),('&uuml;', 'ü'),('&uml;', '¨'),('&ugrave;', 'ù'),('&ucirc;', 'û')...
.delete_all_non_latin_chars()
.replace_multispaces()
)

Original:  Suzy &amp; John &quot; 
Repaired:  Suzy & John " 
Original:  &pound;682m
Repaired:  £682m
Original:  \u00FF\u00FF\u00F0\u00f0\x95\xFF 
Repaired:  ÿÿððÿ 
Original:  SmÃ¶rgÃ¥s 
Repaired:  Smörgås 
Original:  Non ti suscita niente la parola pietÃ\xa0 
Repaired:  Non ti suscita niente la parola pietí 
Original:  RosÅ½ 
Repaired:  Ros 
Original:  RUF MICH ZURÃœCK. 
Repaired:  RUF MICH ZURÜCK. 
Original:  aqu\195\173 
Repaired:  aquí 
Original:  09. BÃ¡t NhÃ£ TÃ¢m Kinh 
Repaired:  09. Bát Nhã Tâm Kinh 
Original:  crianÃ§a
Repaired:  criança
Original:  KoÃ§ University
Repaired:  Koç University
Original:  Technische UniversitÃ¤t Dresden
Repaired:  Technische Universität Dresden
Original:  UniversitÃ¤t fÃ¼r Musik und darstellende Kunst Wien
Repaired:  Universität für Musik und darstellende Kunst Wien
Original:  Technische UniversitÃ¤t Wien
Repaired:  Technische Universität Wien
Original:  Ã\x89cole Nationale SupÃ©rieure des Beaux-Arts Paris
Repaired:  ícole Nationale Supérieure des Beaux-Arts Paris
Original:  Universidad SimÃ³n BolÃ\xadvar (USB)
Repaired:  Universidad Simón Bolí var (USB)
Original:  PontifÃ\xadcia Universidade CatÃ³lica do Rio Grande do Sul (PUCRS)
Repaired:  Pontifí cia Universidade Católica do Rio Grande do Sul (PUCRS)
Original:  BogaziÃ§i Ã\x9cniversitesi
Repaired:  Bogaziçi íniversitesi
Original:  UniversitÃ\xa0 degli Studi di Udine
Repaired:  Universití degli Studi di Udine
Original:  Universitat AutÃ²noma de Barcelona
Repaired:  Universitat Autònoma de Barcelona
Original:  UniversitÃ© de Rennes 1
Repaired:  Université de Rennes 1
Original:  Ã\x89cole Normale SupÃ©rieure de Lyon
Repaired:  ícole Normale Supérieure de Lyon
Original:  Ã\x89cole Nationale SupÃ©rieure de CrÃ©ation Industrielle
Repaired:  ícole Nationale Supérieure de Création Industrielle
Original:  ENSCI Les Ateliers
Repaired:  ENSCI Les Ateliers
Original:  UniversitÃ¤t Bremen
Repaired:  Universität Bremen
Original:  Institut National des Sciences AppliquÃ©es de Lyon (INSA)
Repaired:  Institut National des Sciences Appliquées de Lyon (INSA)
Original:  UniversitÃ© Laval
Repaired:  Université Laval
Original:  UniversitÃ¤t des Saarlandes
Repaired:  Universität des Saarlandes
Original:  UniversitÃ¤t Konstanz
Repaired:  Universität Konstanz
Original:  Philipps-UniversitÃ¤t Marburg
Repaired:  Philipps-Universität Marburg
Original:  El Colegio de MÃ©xico A.C.
Repaired:  El Colegio de México A.C.
Original:  Humboldt-UniversitÃ¤t zu Berlin
Repaired:  Humboldt-Universität zu Berlin
Original:  PontifÃ\xadcia Universidade CatÃ³lica do Rio de Janeiro
Repaired:  Pontifí cia Universidade Católica do Rio de Janeiro
Original:  Universidade Federal do ParanÃ¡ - UFPR
Repaired:  Universidade Federal do Paraná - UFPR
Original:  UniversitÃ¤t Potsdam
Repaired:  Universität Potsdam
Original:  USI - UniversitÃ  della Svizzera italiana
Repaired:  USI - Universití della Svizzera italiana
Original:  PalackÃ½ University Olomouc
Repaired:  Palacký University Olomouc
Original:  CentraleSupÃ©lec
Repaired:  CentraleSupélec
Original:  Arts et MÃ©tiers ParisTech
Repaired:  Arts et Métiers ParisTech
Original:  UniversitÃ© de Sherbrooke
Repaired:  Université de Sherbrooke
Original:  UniversitÃ\xa0 degli studi Roma Tre
Repaired:  Universití degli studi Roma Tre
Original:  WestfÃ¤lische Wilhelms-UniversitÃ¤t MÃ¼nster
Repaired:  Westfälische Wilhelms-Universität Münster
Original:  Universidad PolitÃ©cnica de Madrid (UPM)
Repaired:  Universidad Politécnica de Madrid (UPM)
Original:  Universidad Adolfo IbÃ\xa0Ã±ez
Repaired:  Universidad Adolfo Ibíñez
Original:  Ã\x89cole Centrale de Lille
Repaired:  ícole Centrale de Lille
Original:  UniversitÃ© Paris 13 Nord
Repaired:  Université Paris 13 Nord
Original:  UniversitÃ  degli Studi di Udine
Repaired:  Universití degli Studi di Udine
Original:  Universidade Federal de SÃ£o Paulo
Repaired:  Universidade Federal de São Paulo
Original:  Instituto Nacional de MatemÃ¡tica Pura e Aplicada (IMPA)
Repaired:  Instituto Nacional de Matemática Pura e Aplicada (IMPA)
Original:  UniversitÃ¤t Mannheim
Repaired:  Universität Mannheim
Original:  UniversitÃ© Toulouse 1 Capitole
Repaired:  Université Toulouse 1 Capitole
Original:  Technische UniversitÃ¤t Braunschweig
Repaired:  Technische Universität Braunschweig
Original:  Eberhard Karls UniversitÃ¤t TÃ¼bingen
Repaired:  Eberhard Karls Universität Tübingen
Original:  UniversitÃ¤t Rostock
Repaired:  Universität Rostock
Original:  UniversitÃ© Grenoble Alpes
Repaired:  Université Grenoble Alpes
Original:  UniversitÃ© de Fribourg
Repaired:  Université de Fribourg
Original:  UniversitÃ¤t Innsbruck
Repaired:  Universität Innsbruck
Original:  Universidad Adolfo IbÃ Ã±ez
Repaired:  Universidad Adolfo Ibí ñez
Original:  UniversitÃ© du QuÃ©bec
Repaired:  Université du Québec
Original:  Universidad de la RepÃºblica (Udelar)
Repaired:  Universidad de la República (Udelar)
Original:  Universitat PolitÃ¨cnica de Catalunya Â· BarcelonaTech (UPC)
Repaired:  Universitat Politècnica de Catalunya · BarcelonaTech (UPC)
Original:  UniversitÃ¤t Regensburg
Repaired:  Universität Regensburg
Original:  UniversitÃ© de Paris
Repaired:  Université de Paris
Original:  UniversitÃ© Paris 1 PanthÃ©on-Sorbonne
Repaired:  Université Paris 1 Panthéon-Sorbonne
Original:  Universidad TÃ©cnica Federico Santa MarÃ\xada (USM)
Repaired:  Universidad Técnica Federico Santa Marí a (USM)
Original:  Ruprecht-Karls-UniversitÃ¤t Heidelberg
Repaired:  Ruprecht-Karls-Universität Heidelberg
Original:  Pontificia Universidad CatÃ³lica Argentina
Repaired:  Pontificia Universidad Católica Argentina
Original:  UniversitÃ\xa0Â\xa0di Padova
Repaired:  Universití di Padova
Original:  Technische UniversitÃ¤t Berlin (TU Berlin)
Repaired:  Technische Universität Berlin (TU Berlin)
Original:  UniversitÃ¤t Stuttgart
Repaired:  Universität Stuttgart
Original:  FundaÃ§Ã£o Getulio Vargas (FGV)
Repaired:  Fundação Getulio Vargas (FGV)
Original:  Universidade de SÃ£o Paulo
Repaired:  Universidade de São Paulo
Original:  Universidad Nacional AutÃ³noma de MÃ©xico  (UNAM)
Repaired:  Universidad Nacional Autónoma de México (UNAM)
Original:  Universidade Federal de SÃ£o Carlos (UFSCar)
Repaired:  Universidade Federal de São Carlos (UFSCar)
Original:  Ã\x89cole Centrale de Nantes
Repaired:  ícole Centrale de Nantes
Original:  Technische UniversitÃ¤t Kaiserslautern
Repaired:  Technische Universität Kaiserslautern
Original:  UniversitÃ  degli studi Roma Tre
Repaired:  Universití degli studi Roma Tre
Original:  Pontificia Universidad CatÃ³lica del PerÃº
Repaired:  Pontificia Universidad Católica del Perú
Original:  UniversitÃ\xa0 degli Studi di Pavia
Repaired:  Universití degli Studi di Pavia
Original:  UniversitÃ© PSL
Repaired:  Université PSL
Original:  UniversitÃ© de MontrÃ©al
Repaired:  Université de Montréal
Original:  Pontificia Universidad CatÃ³lica de ValparaÃ\xadso
Repaired:  Pontificia Universidad Católica de Valparaí so
Original:  University Paris 2 PanthÃ©on-Assas
Repaired:  University Paris 2 Panthéon-Assas
Original:  UniversitÃ© Paris-Nanterre
Repaired:  Université Paris-Nanterre
Original:  Universidad AutÃ³noma de San Luis de PotosÃ\xad
Repaired:  Universidad Autónoma de San Luis de Potosí 
Original:  UniversitÃ¤t  Leipzig
Repaired:  Universität Leipzig
Original:  Ruhr-UniversitÃ¤t Bochum
Repaired:  Ruhr-Universität Bochum
Original:  UniversitÃ© LumiÃ¨re Lyon 2
Repaired:  Université Lumière Lyon 2
Original:  UniversitÃ© de Lille
Repaired:  Université de Lille
Original:  UniversitÃ© Claude Bernard Lyon 1
Repaired:  Université Claude Bernard Lyon 1
Original:  UniversitÃ© catholique de Louvain (UCLouvain)
Repaired:  Université catholique de Louvain (UCLouvain)
Original:  UniversitÃ©  de Technologie Troyes (UTT)
Repaired:  Université de Technologie Troyes (UTT)
Original:  Universidad de San AndrÃ©s - UdeSA
Repaired:  Universidad de San Andrés - UdeSA
Original:  Martin-Luther-UniversitÃ¤t Halle-Wittenberg
Repaired:  Martin-Luther-Universität Halle-Wittenberg
Original:  University of TromsÃ¸ The Arctic University of Norway
Repaired:  University of Tromsø The Arctic University of Norway
Original:  Rheinische Friedrich-Wilhelms-UniversitÃ¤t Bonn
Repaired:  Rheinische Friedrich-Wilhelms-Universität Bonn
Original:  Universidad de AlcalÃ¡
Repaired:  Universidad de Alcalá
Original:  USI - UniversitÃ\xa0 della Svizzera italiana
Repaired:  USI - Universití della Svizzera italiana
Original:  LinkÃ¶ping University
Repaired:  Linköping University
Original:  Universidad Nacional de CÃ³rdoba - UNC
Repaired:  Universidad Nacional de Córdoba - UNC
Original:  UniversitÃ\xa0 degli Studi di Perugia
Repaired:  Universití degli Studi di Perugia
Original:  UniversitÃ  degli Studi di Pavia
Repaired:  Universití degli Studi di Pavia
Original:  Johannes Gutenberg UniversitÃ¤t Mainz
Repaired:  Johannes Gutenberg Universität Mainz
Original:  UniversitÃ  Iuav di Venezia
Repaired:  Universití Iuav di Venezia
Original:  Friedrich-Alexander-UniversitÃ¤t Erlangen-NÃ¼rnberg
Repaired:  Friedrich-Alexander-Universität Erlangen-Nürnberg
Original:  UniversitÃ© de Nantes
Repaired:  Université de Nantes
Original:  Universidad de CÃ³rdoba
Repaired:  Universidad de Córdoba
Original:  Universidade de BrasÃ\xadlia
Repaired:  Universidade de Brasí lia
Original:  UniversitÃ© de Strasbourg
Repaired:  Université de Strasbourg
Original:  Universidad AutÃ³noma de Nuevo LeÃ³n
Repaired:  Universidad Autónoma de Nuevo León
Original:  Pontificia Universidad CatÃ³lica de Chile (UC)
Repaired:  Pontificia Universidad Católica de Chile (UC)
Original:  UniversitÃ© Paris-Est CrÃ©teil Val de Marne
Repaired:  Université Paris-Est Créteil Val de Marne
Original:  Universidad AutÃ³noma del Estado de MÃ©xico (UAEMex)
Repaired:  Universidad Autónoma del Estado de México (UAEMex)
Original:  UniversitÃ© de Montpellier
Repaired:  Université de Montpellier
Original:  UniversitÃ¤t der KÃ¼nste Berlin
Repaired:  Universität der Künste Berlin
Original:  UniversitÃ Â di Padova
Repaired:  Universití di Padova
Original:  UniversitÃ© Paris-Saclay
Repaired:  Université Paris-Saclay
Original:  EÃ¶tvÃ¶s LorÃ¡nd University
Repaired:  Eötvös Loránd University
Original:  Technische UniversitÃ¤t Bergakademie Freiberg
Repaired:  Technische Universität Bergakademie Freiberg
Original:  Technische UniversitÃ¤t Hamburg
Repaired:  Technische Universität Hamburg
Original:  Universidade CatÃ³lica Portuguesa - UCP
Repaired:  Universidade Católica Portuguesa - UCP
Original:  Ã\x89cole Nationale SupÃ©rieure des Industries Chimiques (ENSIC) Nancy
Repaired:  ícole Nationale Supérieure des Industries Chimiques (ENSIC) Nancy
Original:  Instituto TecnolÃ³gico AutÃ³nomo de MÃ©xico (ITAM)
Repaired:  Instituto Tecnológico Autónomo de México (ITAM)
Original:  UniversitÃ© de Limoges
Repaired:  Université de Limoges
Original:  UniversitÃ© Sorbonne Nouvelle Paris 3
Repaired:  Université Sorbonne Nouvelle Paris 3
Original:  UniversitÃ© Paul Sabatier Toulouse III
Repaired:  Université Paul Sabatier Toulouse III
Original:  Julius-Maximilians-UniversitÃ¤t WÃ¼rzburg
Repaired:  Julius-Maximilians-Universität Würzburg
Original:  UniversitÃ© de Poitiers
Repaired:  Université de Poitiers
Original:  Universitat PolitÃ¨cnica de ValÃ¨ncia
Repaired:  Universitat Politècnica de València
Original:  UniversitÃ\xa0Â\xa0Cattolica del Sacro Cuore
Repaired:  Universití Cattolica del Sacro Cuore
Original:  UniversitÃ© Nice Sophia Antipolis
Repaired:  Université Nice Sophia Antipolis
Original:  University of JyvÃ¤skylÃ¤
Repaired:  University of Jyväskylä
Original:  Bauhaus-UniversitÃ¤t Weimar
Repaired:  Bauhaus-Universität Weimar
Original:  UniversitÃ© de LiÃ¨ge
Repaired:  Université de Liège
Original:  UniversitÃ¤t Jena
Repaired:  Universität Jena
Original:  University of GÃ¶ttingen
Repaired:  University of Göttingen
Original:  Technische UniversitÃ¤t Ilmenau
Repaired:  Technische Universität Ilmenau
Original:  Ã\x89cole Centrale de Lyon
Repaired:  ícole Centrale de Lyon
Original:  Ludwig-Maximilians-UniversitÃ¤t MÃ¼nchen
Repaired:  Ludwig-Maximilians-Universität München
Original:  UniversitÃ© de Lorraine
Repaired:  Université de Lorraine
Original:  UniversitÃ© de Technologie de CompiÃ¨gne (UTC)
Repaired:  Université de Technologie de Compiègne (UTC)
Original:  UniversitÃ¤t Siegen
Repaired:  Universität Siegen
Original:  UniversitÃ¤t Duisburg-Essen
Repaired:  Universität Duisburg-Essen
Original:  UniversitÃ© de Savoie
Repaired:  Université de Savoie
Original:  Universidad AutÃ³noma de Madrid
Repaired:  Universidad Autónoma de Madrid
Original:  UniversitÃ Â Cattolica del Sacro Cuore
Repaired:  Universití Cattolica del Sacro Cuore
Original:  Ankara Ã\x9cniversitesi
Repaired:  Ankara íniversitesi
Original:  Universidade da CoruÃ±a
Repaired:  Universidade da Coruña
Original:  UniversitÃ degli Studi di Perugia
Repaired:  Universití degli Studi di Perugia
Original:  Hochschule fÃ¼r Gestaltung und Kunst ZÃ¼rich
Repaired:  Hochschule für Gestaltung und Kunst Zürich
Original:  UniversitÃ¤t Hamburg
Repaired:  Universität Hamburg

```
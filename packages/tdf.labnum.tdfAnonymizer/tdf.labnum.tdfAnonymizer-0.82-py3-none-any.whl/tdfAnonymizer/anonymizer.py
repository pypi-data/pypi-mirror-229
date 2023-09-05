import guess #line:1
import nltk #line:2
from nltk .corpus import stopwords #line:3
from nltk .tokenize import word_tokenize #line:4
from nltk .tag import pos_tag #line:5
from pydantic import BaseModel #line:6
from faker import Faker #line:7
import os #line:8
import pandas as pd #line:9
import json #line:10
import random #line:11
import requests #line:12
import googlemaps #line:13
nltk .download ('averaged_perceptron_tagger')#line:14
nltk .download ('punkt')#line:15
nltk .download ('stopwords')#line:16
class textAnonyms (BaseModel ):#line:19
    originalText :str #line:20
    textFormat :str #line:21
stop_words =set (stopwords .words ('french'))#line:24
liste_pays =["afghanistan","afrique du sud","albanie","algérie","allemagne","andorre","angola","antigua-et-barbuda","arabie saoudite","argentine","arménie","aruba","australie","autriche","azerbaïdjan","bahamas","bahreïn","bangladesh","barbade","belgique","belize","bélarus","bénin","bhoutan","birmanie","bolivie","bosnie-herzégovine","botswana","brésil","brunéi","bulgarie","burkina faso","burundi","cambodge","cameroun","canada","cap-vert","chili","chine","chypre","colombie","comores","corée du nord","corée du sud","costa rica","côte d'ivoire","croatie","cuba","curaçao","danemark","djibouti","dominique","egypte","el salvador","émirats arabes unis","équateur","érythrée","espagne","estonie","éthiopie","fidji","finlande","france","gabon","gambie","géorgie","ghana","grèce","grenade","guatemala","guinée","guinée équatoriale","guinée-bissau","guyana","haïti","honduras","hongrie","inde","indonésie","irak","iran","irlande","islande","israël","italie","jamaïque","japon","jordanie","kazakhstan","kenya","kirghizistan","kiribati","kosovo","koweït","laos","lesotho","lettonie","liban","libéria","libye","liechtenstein","lituanie","luxembourg","macédoine du nord","madagascar","malaisie","malawi","maldives","mali","malte","maroc","marshall","maurice","mauritanie","mexique","micronésie","moldavie","monaco","mongolie","monténégro","mozambique","namibie","nauru","nepal","nicaragua","niger","nigeria","niue","norvège","nouvelle-zélande","oman","ouganda","ouzbékistan","pakistan","palaos","panama","papouasie nouvelle-guinée","paraguay","pays-bas","pérou","philippines","pologne","portugal","qatar","république centrafricaine","république démocratique du congo","république dominicaine","république du congo","république tchèque","roumanie","royaume-uni","russie","rwanda","saint-christophe-et-niévès","saint-marin","saint-martin","saint-vincent-et-les-grenadines","sainte-lucie","salomon","salvador","samoa","são tomé-et-principe","sénégal","serbie","seychelles","sierra leone","singapour","slovaquie","slovénie","somalie","soudan","soudan du sud","sri lanka","suède","suisse","surinam","swaziland","syrie","tadjikistan","tanzanie","tchad","thaïlande","timor oriental","togo","tonga","trinité-et-tobago","tunisie","turkménistan","turquie","tuvalu","ukraine","uruguay","vanuatu","vatican","venezuela","vietnam","yémen","zambie","zimbabwe"]#line:25
faker =Faker (["fr_FR"])#line:26
url ="https://raw.githubusercontent.com/high54/Communes-France-JSON/master/france.json"#line:28
response =requests .get (url )#line:30
villes =response .json ()#line:31
def anonymiser_mot (O0O0OOO0O0OOO000O :textAnonyms ):#line:35
    try :#line:36
        OOO0OOOO000OOO0O0 =pd .read_csv ("words.csv",dtype ={"original":str ,"anonymous":str })#line:37
        if (O0O0OOO0O0OOO000O .textFormat =="LIEN"):#line:39
            O0OOO0O00OOOO000O ="//"+random .choice (["google","yahoo","hotmail","bing","qwant"])#line:40
        elif (O0O0OOO0O0OOO000O .originalText =="FM"):#line:41
            O0OOO0O00OOOO000O ="DAB+"#line:42
        elif (O0O0OOO0O0OOO000O .originalText =="DAB+"):#line:43
            O0OOO0O00OOOO000O ="FM"#line:44
        elif (O0O0OOO0O0OOO000O .originalText .lower ()=="iqoya"):#line:45
            O0OOO0O00OOOO000O ="codec audio"#line:46
        elif (O0O0OOO0O0OOO000O .textFormat =="PERSON"):#line:47
            if (cherche_ville (O0O0OOO0O0OOO000O .originalText .upper ())):#line:49
                O0OOO0O00OOOO000O =random .choice (["TOULON","NANTES","MONTPELLIER","CHAMBOURCY","NANTERRE","GRENOBLE","LYON"])#line:50
            elif (cherche_chaine (O0O0OOO0O0OOO000O .originalText .upper ())):#line:51
                O0OOO0O00OOOO000O =random .choice (["TF1","M6","BFMTV" "FRANCE5","FRANCE2"])#line:52
            elif (is_probable_prenom (O0O0OOO0O0OOO000O .originalText )):#line:53
                O0OOO0O00OOOO000O =random .choice (["PAUL","JEAN","PHILIPPE","PIERRE","MARC","DAVID","GUILLAUME"])#line:54
            else :#line:55
                O0OOO0O00OOOO000O =O0O0OOO0O0OOO000O .originalText #line:56
        elif (O0O0OOO0O0OOO000O .textFormat =="DATE"):#line:57
            O0OOO0O00OOOO000O =faker .date ()#line:58
        elif (O0O0OOO0O0OOO000O .textFormat =="LOCATION"):#line:59
            O0OOO0O00OOOO000O =faker .address ()#line:60
        elif (O0O0OOO0O0OOO000O .textFormat =="NUMBER"):#line:61
            if (int (O0O0OOO0O0OOO000O .originalText )<24 ):#line:62
                O0OOO0O00OOOO000O =faker .numerify (text ='#')#line:63
            else :#line:64
                O0OOO0O00OOOO000O =str (faker .random_int (min =0 ,max =(int (O0O0OOO0O0OOO000O .originalText )-1 )))#line:65
        elif (O0O0OOO0O0OOO000O .textFormat =="COUNTRY"):#line:66
            O0OOO0O00OOOO000O =faker .country ()#line:67
        elif (O0O0OOO0O0OOO000O .textFormat =="ORGANIZATION"):#line:68
            O0OOO0O00OOOO000O =random .choice (["ORANGE","SAFRAN","BOUYGUES","FREE"])#line:69
        while any (OOO0OOOO000OOO0O0 ["anonymous"]==O0OOO0O00OOOO000O ):#line:73
            O0OOO0O00OOOO000O =faker .first_name ()#line:74
        OOO0OOOO000OOO0O0 =pd .concat ([OOO0OOOO000OOO0O0 ,pd .DataFrame ([[O0O0OOO0O0OOO000O .originalText ,O0OOO0O00OOOO000O ]],columns =["original","anonymous"])])#line:76
        OOO0OOOO000OOO0O0 .to_csv ("words.csv",index =False )#line:77
        return O0OOO0O00OOOO000O #line:79
    except Exception as OOOOO000O0O00O00O :#line:80
        return O0O0OOO0O0OOO000O .originalText #line:81
def cherche_chaine (O0O0OO0O00O0OO0OO ):#line:84
    O0O0OO0O00O0OO0OO =O0O0OO0O00O0OO0OO .upper ()#line:85
    OOOO0O0OO0O00O0OO =["C8","CNEWS","TF1","M6","CSTAR","BFM","F5"]#line:87
    for OOO0000OOO000O00O in OOOO0O0OO0O00O0OO :#line:88
        if OOO0000OOO000O00O in O0O0OO0O00O0OO0OO :#line:89
            return True #line:90
            break #line:91
    return False #line:93
def cherche_ville (O0O0O0000OO0O0O00 ):#line:96
    O0O0O0000OO0O0O00 =O0O0O0000OO0O0O00 .upper ()#line:97
    for O0000OO0O0OOOO00O in villes :#line:98
        if O0O0O0000OO0O0O00 in O0000OO0O0OOOO00O ["Nom_commune"]:#line:99
            return True #line:100
            break #line:101
    return False #line:103
def desanonymiser_mot (O00O0OOOO0OO00O00 ):#line:105
    OO00O0OO0O0OO00O0 =pd .read_csv ("words.csv",dtype ={"original":str ,"anonymous":str })#line:106
    if not OO00O0OO0O0OO00O0 .empty :#line:107
        O000O0O0O0O0O0OOO =OO00O0OO0O0OO00O0 [OO00O0OO0O0OO00O0 ["anonymous"]==O00O0OOOO0OO00O00 ]["original"]#line:108
        if not O000O0O0O0O0O0OOO .empty :#line:109
            return O000O0O0O0O0O0OOO .iloc [0 ]#line:110
    return None #line:111
def initialiser ():#line:113
    O00O0O0O0OOOOO000 ="words.csv"#line:114
    if os .path .exists (O00O0O0O0OOOOO000 ):#line:116
        os .remove (O00O0O0O0OOOOO000 )#line:117
    OOO00000OOOOOO0O0 =pd .DataFrame (columns =["original","anonymous"])#line:119
    OOO00000OOOOOO0O0 .to_csv (O00O0O0O0OOOOO000 ,index =False )#line:121
def anonymiser_paragraphe (OOOO0OOOOO00O0OOO ):#line:126
    OO00OO0000O00000O =OOOO0OOOOO00O0OOO #line:128
    OO00OO0000O00000O =OO00OO0000O00000O .replace (".",". ")#line:129
    OO00OO0000O00000O =OO00OO0000O00000O .replace (",",", ")#line:130
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("0H","0 H")#line:131
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("1H","1 H")#line:132
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("2H","2 H")#line:133
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("3H","3 H")#line:134
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("4H","4 H")#line:135
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("5H","5 H")#line:136
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("6H","6 H")#line:137
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("7H","7 H")#line:138
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("8H","8 H")#line:139
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("9H","9 H")#line:140
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("0h","0 h")#line:141
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("1h","1 h")#line:142
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("2h","2 h")#line:143
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("3h","3 h")#line:144
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("4h","4 h")#line:145
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("5h","5 h")#line:146
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("6h","6 h")#line:147
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("7h","7 h")#line:148
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("8h","8 h")#line:149
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("9h","9 h")#line:150
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("0F","0 F ")#line:151
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("1F","1 F ")#line:152
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("2F","2 F ")#line:153
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("3F","3 F ")#line:154
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("4F","4 F ")#line:155
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("5F","5 F ")#line:156
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("6F","6 F ")#line:157
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("7F","7 F ")#line:158
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("8F","8 F ")#line:159
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("9F","9 F ")#line:160
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("0f","0 f ")#line:161
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("1f","1 f ")#line:162
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("2f","2 f ")#line:163
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("3f","3 f ")#line:164
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("4f","4 f ")#line:165
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("5f","5 f ")#line:166
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("6f","6 f ")#line:167
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("7f","7 f ")#line:168
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("8f","8 f ")#line:169
    OO00OO0000O00000O =OO00OO0000O00000O .replace ("9f","9 f ")#line:170
    OO00OO0O00OO00O00 =word_tokenize (OO00OO0000O00000O ,language ="french")#line:171
    OO00000O0O0O0O0OO =pos_tag (OO00OO0O00OO00O00 )#line:172
    O0O0O0O0O000OO0OO =[]#line:173
    O0OOO00O000OOO000 =set (stopwords .words ('french'))#line:175
    O000O00O0000OOO00 =["h","mon","ma","HF","mes","ton","ta","tes","son","sa","ses","notre","votre","leur","leurs","merci","alors","fh","hf","intervention","j'ai","télégéstion","télégestion","absence","énergie","radio","KO","ko"]#line:176
    O0OOO00O000OOO000 .update (O000O00O0000OOO00 )#line:177
    O0OO0O000OO0000O0 =0 #line:178
    for O0O00O0OO0O0OO000 ,OOO000O0OO0OO0OOO in OO00000O0O0O0O0OO :#line:179
        O0OO0O000OO0000O0 =O0OO0O000OO0000O0 +1 #line:180
        if OOO000O0OO0OO0OOO =="NN"and ("//"in O0O00O0OO0O0OO000 ):#line:183
            print ("lien")#line:184
            O0O0O0O0O000OO0OO .append (("LIEN",O0O00O0OO0O0OO000 ))#line:185
        elif O0O00O0OO0O0OO000 .lower ()in liste_pays :#line:186
            O0O0O0O0O000OO0OO .append (("COUNTRY",O0O00O0OO0O0OO000 ))#line:187
        elif OOO000O0OO0OO0OOO =="NNP"and "DS"in O0O00O0OO0O0OO000 or "LA"in O0O00O0OO0O0OO000 :#line:188
            O0O0O0O0O000OO0OO .append (("NUMBER",O0O00O0OO0O0OO000 ))#line:189
        elif OOO000O0OO0OO0OOO =="NNP"and O0O00O0OO0O0OO000 .isupper ()and O0O00O0OO0O0OO000 .lower ()not in O0OOO00O000OOO000 and len (O0O00O0OO0O0OO000 )>1 :#line:190
            O0O0O0O0O000OO0OO .append (("ORGANIZATION",O0O00O0OO0O0OO000 ))#line:191
        elif OOO000O0OO0OO0OOO =="NNP"and O0O00O0OO0O0OO000 .lower ()not in O0OOO00O000OOO000 and O0OO0O000OO0000O0 >1 and len (O0O00O0OO0O0OO000 )>1 :#line:192
            O0O0O0O0O000OO0OO .append (("PERSON",O0O00O0OO0O0OO000 ))#line:193
        elif OOO000O0OO0OO0OOO =="CD"and "/"in O0O00O0OO0O0OO000 and len (O0O00O0OO0O0OO000 )==10 :#line:194
            O0O0O0O0O000OO0OO .append (("DATE",O0O00O0OO0O0OO000 ))#line:195
        elif OOO000O0OO0OO0OOO =="CD"and "/"in O0O00O0OO0O0OO000 and len (O0O00O0OO0O0OO000 )<10 :#line:196
            O0O0O0O0O000OO0OO .append (("NUMBER",O0O00O0OO0O0OO000 ))#line:197
        elif OOO000O0OO0OO0OOO =="CD"and ":"not in O0O00O0OO0O0OO000 :#line:198
            O0O0O0O0O000OO0OO .append (("NUMBER",O0O00O0OO0O0OO000 ))#line:199
        elif OOO000O0OO0OO0OOO =="NNP"and O0O00O0OO0O0OO000 .lower ()not in O0OOO00O000OOO000 and O0OO0O000OO0000O0 >1 and len (O0O00O0OO0O0OO000 )>1 :#line:200
            O0O0O0O0O000OO0OO .append (("LOCATION",O0O00O0OO0O0OO000 ))#line:201
    for O000O0O0O0OOO0000 ,O0O0O000OO00OO000 in O0O0O0O0O000OO0OO :#line:205
        O0OOOO00O00O0O0O0 =textAnonyms (originalText =O0O0O000OO00OO000 ,textFormat =O000O0O0O0OOO0000 )#line:206
        OOOO0OOOOO00O0OOO =OOOO0OOOOO00O0OOO .replace (O0O0O000OO00OO000 ,anonymiser_mot (O0OOOO00O00O0O0O0 ))#line:207
    OOOO0OOOOO00O0OOO =OOOO0OOOOO00O0OOO .replace ("-","/")#line:209
    OOOO0OOOOO00O0OOO =OOOO0OOOOO00O0OOO .replace (" / "," - ")#line:210
    return OOOO0OOOOO00O0OOO #line:211
def desanonymiser_paragraphe (OO0000O00O0OOO0OO ):#line:213
    O0000OO0O00O0O00O =pd .read_csv ("words.csv",dtype ={"original":str ,"anonymous":str })#line:216
    for OOOO0000O0OOO0O00 ,O0OO0OO00O0O0OOO0 in O0000OO0O00O0O00O .iterrows ():#line:217
        OO0000O00O0OOO0OO =OO0000O00O0OOO0OO .replace (O0OO0OO00O0O0OOO0 ["anonymous"],O0OO0OO00O0O0OOO0 ["original"])#line:219
    return OO0000O00O0OOO0OO #line:220
def is_probable_prenom (OO0OOOO00000OOO0O ):#line:222
    O0OO00O000OOO0O0O =guess .get_gender (OO0OOOO00000OOO0O )#line:223
    return O0OO00O000OOO0O0O in ['male','female']#line:225

from SyllableSplitter import SyllableSplitter
ss = SyllableSplitter()

#orthographic principles. (Parmin dkk: 2011)

#1. There are four ways of separating the basic words (roots).

#If there are sequential vowels in the middle of the words then the separation isperformed in between those vowels (-V/V-). 
print(ss.split_syllables("maaf duet buih aula saudara tertua pantai pulau"))
#target = ma-af, du-et, bu-ih, au-la, sau-da-ra, ter-tua, pan-tai, and pu-lau
#hasil = ['ma', 'af', ' ', 'du', 'et', ' ', 'bu', 'ih', ' ', 'a', 'u', 'la', ' ', 'sa', 'u', 'da', 'ra', ' ', 'ter', 'tu', 'a', ' ', 'pan', 'ta', 'i', ' ', 'pu', 'la', 'u']

#If there are consonant and doublé consonants between two vowels, the separation isperformed before the consonant (KV-KV), 
print(ss.split_syllables("perut tabu jamur payung tanya sunyi"))
#target = pe-rut, ta-bu, ja-mur, pa-yung, ta-nya dan su-nyi
#hasil = ['pe', 'rut', ' ', 'ta', 'bu', ' ', 'ja', 'mur', ' ', 'pa', 'yung', ' ', 'ta', 'nya', ' ', 'su', 'nyi']

#If there are sequential consonants in the middle of the words, the separation isperformed in between those consonants (-K/KV-),
print(ss.split_syllables("maklum gertak kompos mikro migrasi caplok dengan makhluk ikhlas isyarat"))
#target = mak-lum, ger-tak, kom-pos, mik-ro, mig-ra-si, cap-lok, de-ngan, makh-luk, ikh-las, i-sya-rat
#hasil = ['mak', 'lum', ' ', 'ger', 'tak', ' ', 'kom', 'pos', ' ', 'mik', 'ro', ' ', 'mig', 'ra', 'si', ' ', 'cap', 'lok', ' ', 'de', 'ngan', ' ', 'makh', 'luk', ' ', 'ikh', 'las', ' ', 'i', 'sya', 'rat']

#If there are more than two sequential consonants, the separation is performed afterthe first consonant (-K/KK-).
print(ss.split_syllables("instruksi instalasi abstarksi instrumen"))
#target = in-struk-si, in-sta-la-si, ab-strak-si, and in-stru-men
#hasil = ['in', 'struk', 'si', ' ', 'in', 'sta', 'la', 'si', ' ', 'ab', 'star', 'ksi', ' ', 'in', 'stru', 'men']

#2. All affixes are considered as one syllable; it includes prefixes that has undergone changes.
print(ss.split_syllables("meramu menyapu mencoba pembelahan kepanasan"))
#target = me-ra-mu, me-nya-pu, men-co-ba, pem-be-lah-an, ke-pa-nas-an
#hasil = ['me', 'ra', 'mu', ' ', 'me', 'nya', 'pu', ' ', 'men', 'co', 'ba', ' ', 'pem', 'be', 'la', 'han', ' ', 'ke', 'pa', 'na', 'san']

#The suffix –i and words with an initial vowel letter are not separated.
print(ss.split_syllables("mengakhiri mengawali mengelilingi memutari menaiki"))
#target = me-nga-khi-ri, me-nga-wa-li, me-nge-li-li-ngi, me-mu-ta-ri, me-nai-ki
#hasil = ['me', 'nga', 'khi', 'ri', ' ', 'me', 'nga', 'wa', 'li', ' ', 'me', 'nge', 'li', 'li', 'ngi', ' ', 'me', 'mu', 'ta', 'ri', ' ', 'me', 'na', 'i', 'ki']

#Separation of words with infix.
print(ss.split_syllables("telunjuk gerigi geligi gemetar geletar"))
#target = te-lun-juk, ge-ri-gi, ge-li-gi, ge-me-tar, ge-le-tar
#hasil = ['te', 'lun', 'juk', ' ', 'ge', 'ri', 'gi', ' ', 'ge', 'li', 'gi', ' ', 'ge', 'me', 'tar', ' ', 'ge', 'le', 'tar']

#Prefixes, infixes, and suffixes from the loan words are not considered as affixes but the root itself, hence the separation is performed by following the base words.
print(ss.split_syllables("sportivitas aklimatisasi"))
#target = spor-ti-vi-tas, ak-li-ma-ti-sa-si
#hasil = ['spor', 'ti', 'vi', 'tas', ' ', 'ak', 'li', 'ma', 'ti', 'sa', 'si']

#If a word has more than one root which can be combined with another root, the separation is performed as the followings:
#a) Separated between the roots;
#b) Separated as the rules of syllabification for the basic words (roots)
print(ss.split_syllables("biologi mikrobiologi pascasarjana pascapanen budidaya"))
#target = bio-logi -> bi-o-lo-gi, mikro-biologi -> mik-ro-bi-o-lo-gi, pasca-sarjana -> pas-ca-sar-ja-na, pasca-panen -> pas-ca-pa-nen, budi-daya -> bu-di-da-ya
#hasil = ['bi', 'o', 'lo', 'gi', ' ', 'mik', 'ro', 'bi', 'o', 'lo', 'gi', ' ', 'pas', 'ca', 'sar', 'ja', 'na', ' ', 'pas', 'ca', 'pa', 'nen', ' ', 'bu', 'di', 'da', 'ya']

#Pedoman Umum Ejaan Bahasa Indonesia (PUEBI) states that there are some rules 
#that need to be followed when practicing syllabification. Those rules are:

#1. If a word consists of two roots or more, and those roots are combined then the separation is performed in between those roots.
print(ss.split_syllables("biodata fotografi introspeksi kilometer"))
#target = bio-data -> bi-o-da-ta, foto-grafi -> fo-to-gra-fi, intro-speksi -> in-tro-spek-si, kilo-meter -> ki-lo-me-ter
#hasil = ['bi', 'o', 'da', 'ta', ' ', 'fo', 'tog', 'ra', 'fi', ' ', 'in', 'tros', 'pek', 'si', ' ', 'ki', 'lo', 'me', 'ter']

#2. Names of person consisting of two or more roots at the end of the line are separated in between those roots.
print(ss.split_syllables("Layar Terkembang dikarang oleh Sutan Takdir Alisjahbana."))
#target = ?
#hasil = ['La', 'yar', ' ', 'Ter', 'kem', 'bang', ' ', 'di', 'ka', 'rang', ' ', 'o', 'leh', ' ', 'Su', 'tan', ' ', 'Tak', 'dir', ' ', 'A', 'lis', 'jah', 'ba', 'na', '.']

#3. Abbreviations for names and titles consisting of two or more letters are not separated.
print(ss.split_syllables("Ia bekerja di DLLAJR"))
#target = ia be-ker-ja di DLLAJR
#hasil = ['I', 'a', ' ', 'be', 'ker', 'ja', ' ', 'di', ' ', 'DLLAJ', 'R']

#sumber https://ivanlanin.github.io/puebi/

#In the fourth edition of KBBI, syllabification uses several rules as followings:

#a. Vowels at the beginning or at the end of the root, 
# for examples: amil, elaborasi, uban, via, and vibrio are not separated, and need to be written as:
# amil not a.mil 
# ela.bo.ra.si not e.la.bo.ra.si
# uban not u.ban
# via not vi.a
# vib.rio not vib.ri.o

# b. Suffix –i, such as mencabuti, mendarati, mengobati, memukuli, and memusuhi are not
# separated, and need to be written as:
# men.ca.but.i
# men.da.rat.i
# meng.o.bat.i
# me.mu.kul.i

# c. Words consisting of one vowel in the middle of the word, 
# for examples: otobiografi, piezoelektrik, plagiator, puisi, and xiloidina need to be separated as below:
# oto.bi.o.gra.fi
# pi.e.zo.e.lek.trik
# pla.gi.a.tor
# pu.i.si
# xi.lo.i.di.na

# d. Suffixes, derived from loan words, especially suffix –isme 
# whose elements is the root of words, and treated as suffix, are separated as following:
# However, if –isme is not considered as suffix, and not treated as the root of words,
# then the separation is as the following:
# anar.kis.me
# se.ku.lar.is.me
# ver.bal.is.me

# e. Arabic consists of ain or hamzah, and preceded by consonants, 
# such as alquran, bidah, Jumat, and mutah, are separated as the original pronunciation.
# For examples:
# Al.qur.an
# bid.ah
# Jum.at
# mut.ah

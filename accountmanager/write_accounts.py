d = {'python-announce-ml': {'Passwort': 'wizard', 'Adresse':
'chris.arndt@gmx.net'}, 'Sun Partner': {'Username': 'anterio8', 'Passwort':
'Gerard8'}, 'freshmeat.net': {'username': 'strogon14', 'password':
'wW6mBam6m', 'email': 'chris.arndteb.de'}, 'id3v2-ml': {'Passwort': 'weezurd'
, 'Adresse': 'chris.arndt@gmx.net'}, 'surfcheck': {'username': 'strogon14',
'password': 'O8jtzC0ae'}, 'e-bay': {'Username': 'strogon14', 'Passwort':
'l00natic'}, 'jobpilot': {'benutzernummer': '2067134', 'Password':
'Gg12wFwcm', 'Email': 'chris.arndt@web.de'}, 'GULP': {'Password': 'JobirtAg',
'User': 'carndt'}, 'cgiwrap-users-ml': {'Passwort': 'WuHh', 'Adresse':
'chris.arndt@gmx.net'}, 'Surf Callino': {'POP3': 'pop.surf-callino.de',
'SMTP': 'mail.surf-callino.de', 'Passwort': 'l00natic', 'Adresse':
'chris.arndt@surf-callino.de'}, 'icewm-user-ml': {'Passwort': 'GBaq',
'Adresse': 'chris.arndt@gmx.net'}, 'Yahoo': {'Username': 'strogon14',
'Passwort': '4urlove'}, 'JustBooks': {'Username': 'chris.arndt@gmx.net',
'Passwort': 'weezurd'}, 'ctcheck': {'password': '7ccb1d94', 'user': 'arndt4',
'los01': '15410'}, 'Paybox': {'Paybox-Nr.': '49-000-2474712', 'PIN': '1816'
}, 'selfhost.de': {'username': '1047232421', 'domain': 'llanydd.selfhost.de',
'password': 'Glubeec7'}, 'Mitfahrzentrale': {'Username': '74700', 'Passwort'
: 'weezurd'}, 'Deutsche Bank 24': {'Filialnummer': '189', 'Online-PIN':
'xlc55', 'Konto-Nr.': '1159920', 'Karten-PIN': '8961'}, 'Freenet': {
'Passwort': 'weezurd', 'Adresse': 'chris.arndt@freenet.de'}, 'Puretec': {
'FTP': 'chrisarndt.de', 'FTPPasswort': 'u82much', 'Kundennummer': '2777921',
'Domainname': 'chrisarndt.de', 'SMTP': 'smtp.puretec.de', 'Vertragsnummer':
'1276825', 'Passwort': 'u82much', 'Adresse': 'chris@chrisarndt.de', 'POP3':
'pop.puretec.de', 'POP3Login': 'pt7545183-01', 'POP3Passwort': 'dummy01',
'FTPLogin': 'p7545183'}, 'mdforum': {'password': 'ub8w6piogj', 'user':
'Llanydd', 'email': 'chris.arndt@web.de'}, 'FFII': {'password': 'FUBFrY',
'user': 'chrisarn'}, 'GMX': {'POP3': 'pop.gmx.de', 'SMTP': 'mail.gmx.de',
'Passwort': 'l00natic', 'Kunden-Nr.': '1311905', 'Adresse':
'chris.arndt@gmx.net'}, 'Bin ich sexy': {'password': '4urluv', 'user':
'strogon14'}, 'Anterio': {'Username': 'chris', 'Adresse': 'arndt@anterio.com'
, 'Passwort': '04u2cagain', 'SMTP': 'smtp.kundenserver.de', 'PO3Login':
'm6161945-11', 'POP3': 'pop.kundenserver.de'}, 'Freemail (web.de)': {'POP3':
'pop3.web.de', 'SMTP': 'smtp.web.de', 'Passwort': 'l00natic', 'Adresse':
'chris.arndt@web.de'}, 'wikipedia.de': {'email': 'chris.arndt@web.de',
'password': 'grynPW43a', 'id': '1424', 'user': 'Christopher Arndt'}, 'URZ': {
'password': 'icurthe14ME!', 'SMTP': 'mail.urz.uni-heidelberg.de', 'user':
'carndt', 'POP': 'popix.urz.uni-heidelberg.de', 'email':
'christopher.arndt@urz.uni-heidelberg.de'}, 'Python Forum': {'passwowrd':
'zQpcVo59b', 'email': 'chris.arndt@web.de', 'user': 'strogon14'}, 'passado':
{'password': 'psTue6xK0', 'email': 'chris.arndt@web.de'}, 'FAQTS Python': {
'Passwort': 'weezurd', 'Email': 'chris.arndt@gmx.net'}, 'aim': {'password':
'vagAidCup', 'user': 'strogon14', 'birthdate': '17.04.1982', 'email':
'chris.arndt@freenet.de'}, 'hitchhikers': {'login': 'strogon14', 'password':
'weezurd', 'email': 'chris.arndt@web.de'}, 'debitel': {'Kundenservice':
'www.debitel.com/kundenservice/', 'Kundennummer': '312271618', 'Passwort':
'd6nychwz', 'Handynummer': '+49-173-9542751'}, 'voteonline': {'password':
'36842', 'umfrage': '298446', 'email': 'chris.arndt@gmx.net'}, 'heise': {
'username': 'strogon42', 'name': 'Arndt', 'firstname': 'Christopher',
'password': 'i25GwrqxC', 'email': 'chris.arndt@web.de', 'pseudonym':
'strogon42'}, 'ASPN': {'passord': 'blucob', 'email': 'chris.arndt@gmx.net'},
'rox-users': {'password': 'eqykqMJ51', 'address': 'chris.arndt@web.de'}}

f = open('accounts_notebook.ini', 'w')

for section, options in sorted(d.items()):
    f.write("[%s]\n" % section)

    for option, value in sorted(options.items()):
        f.write("%s: %s\n" % (option, value))

    f.write("\n")

f.close()

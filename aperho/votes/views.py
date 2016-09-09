from django.shortcuts import render
from django.http import HttpResponse
from ldap3 import Server, Connection


def index(request):
    return HttpResponse("Hello, voici l'index des votes.")

def nomClasse(s):
	"""
	Correction des noms des classes ;
	dans notre annuaire, toutes les classes sont préficées par "c"
	"""
	if s[0]=="c":
		return s[1:]
	else:
		return s
		
def addEleves(request):
    server = Server('localhost', port=1389)
    con = Connection(server)
    con.bind()
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre = '(&(|(cn=prof*)(&(cn=c*)(!(cn=*smbadm))))(objectclass=kwartzGroup))'
    con.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes = ['cn', 'gidnumber'],
    )
    classes=[]
    for entry in con.response:
        classes.append({
            'gid':entry['attributes']['gidNumber'][0],
            'classe':nomClasse(entry['attributes']['cn'][0]),
        })
    con.unbind()
    return render(request, "addEleves.html", context={"classes":classes})

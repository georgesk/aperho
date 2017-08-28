#! /usr/bin/python3

"""
modifications à la base de données, de façon programmée
"""

import sys, sqlite3
from subprocess import call

def enseignantPlusUsername(conn):
    c = conn.cursor()
    for row in c.execute('SELECT * FROM votes_enseignant WHERE username=?',("",)):
        print(row)
        ident=int(row[0])
        username="{3}.{1}".format(*row).lower()
        print(username)
        c2=conn.cursor()
        c2.execute('UPDATE votes_enseignant SET username=? WHERE id=?', (username, ident))
    conn.commit()
    
def modifDb(outDbName, function=None):
    """
    modification d'un base de données à l'aide d'une procedure
    """
    if not function: return
    conn = sqlite3.connect(outDbName,detect_types=sqlite3.PARSE_COLNAMES)
    return function(conn)
    
if __name__=="__main__":
    dbName=sys.argv[1]
    outDbName=dbName+".tmp"
    call("cp %s %s" %(dbName, outDbName), shell=True)
    modifDb(outDbName, function=enseignantPlusUsername)
    print(dbName, "=>", outDbName)

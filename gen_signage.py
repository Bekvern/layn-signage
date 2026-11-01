#!/usr/bin/env python3
"""Lager anonymisert data.js til den offentlige signage-siden fra dashboardet.
INGEN KUNDENAVN SKAL UT. Alt som sendes er summer og anonyme etiketter."""
import json,sys,re,os
SRC=sys.argv[1] if len(sys.argv)>1 else 'layn-flow.html'
OUT=sys.argv[2] if len(sys.argv)>2 else 'data.js'
L=open(SRC,encoding='utf8').read().split('\n')
def c(n):
    i=[k for k,l in enumerate(L) if l.startswith('const '+n+'=')][0]
    return json.loads(L[i][len('const '+n+'='):].rstrip().rstrip(';'))
D=c('D'); SMS=c('SMS'); PYF=c('PYF')
M=D['months']; N=len(M); R=D['rows']
S=lambda a: sum(a)
grp=lambda r:'intern' if r=='ukjent' else r
T=[S([r['m'][i] for r in R]) for i in range(N)]
SR={k:[S([r['m'][i] for r in R if grp(r['route'])==k]) for i in range(N)] for k in ('direkte','partner','intern')}
cats={k:[S([r['m'][i] for r in R if r['g']==k]) for i in range(N)] for k in ('legevakt','klinikk','hfu','annet','intern')}
# kunder (gruppert pr kundenavn, men navnet forlater aldri denne filen)
G={}
for r in R:
    if r['route']=='ukjent': continue
    o=G.setdefault(r['cust'],{'route':grp(r['route']),'cat':r['g'],'m':[0]*N,'navn':[]})
    o['navn'].append(r['name'])
    for i,v in enumerate(r['m']): o['m'][i]+=v
closed=lambda o: all(re.search(r'avslutt|inaktiv|inactive',x,re.I) for x in o['navn'])
C=[dict(o,s=S(o['m']),closed=closed(o)) for o in G.values()]
real=[o for o in C if o['route']!='intern' and not o['closed']]
act=[len([o for o in real if o['m'][i]>0]) for i in range(N)]
actDom=[len([r for r in R if r['route']!='ukjent' and r['m'][i]>0]) for i in range(N)]
Lm=N-1
first=lambda o: next((i for i,v in enumerate(o['m']) if v>0),0)
pk=lambda o: max(o['m'])/o['s'] if o['s'] else 0
avg=lambda o,i,j: S(o['m'][i:j+1])/(j-i+1)
tiers=[('Over 2 000 / mnd',lambda x:x>2000),('500–2 000',lambda x:500<x<=2000),('100–500',lambda x:100<x<=500),('10–100',lambda x:10<x<=100),('Under 10',lambda x:0<x<=10)]
tier=[{'n':n,'v':len([o for o in real if f(o['s']/N)])} for n,f in tiers]
b0,b1,n0=max(0,Lm-5),max(0,Lm-3),max(0,Lm-1)
mv=[(o,avg(o,n0,Lm)-avg(o,b0,b1)) for o in real if avg(o,b0,b1)>=50 and pk(o)<=.7]
moves={'vokser':len([1 for o,d in mv if d>0.1*avg(o,b0,b1)]),'stabil':len([1 for o,d in mv if abs(d)<=0.1*avg(o,b0,b1)]),
 'faller':len([1 for o,d in mv if d<-0.1*avg(o,b0,b1)]),'plus':round(S([d for _,d in mv if d>0])),'minus':round(-S([d for _,d in mv if d<0]))}
al=[o for o in real if avg(o,b0,b1)>=50 and pk(o)<=.7 and len([v for v in o['m'] if v>0])>=4 and avg(o,n0,Lm)<.7*avg(o,b0,b1)]
r25=lambda o: avg(o,n0,Lm)/avg(o,b0,b1) if avg(o,b0,b1) else 1
alerts={'kritisk':len([o for o in al if r25(o)<.25]),'folg':len([o for o in al if .25<=r25(o)<.5]),'svakere':len([o for o in al if r25(o)>=.5]),
 'serie':[S([o['m'][i] for o in al]) for i in range(N)],'total':len(real),
 'seg':{k:len([o for o in al if o['cat']==k]) for k in ('legevakt','klinikk','hfu','annet')}}
status=lambda o:( 'Engangs/event' if pk(o)>.7 and o['m'].index(max(o['m']))<Lm and N-first(o)>=2
  else 'Stille' if o['m'][Lm]==0 else ('Ny i '+M[Lm] if N-first(o)<=1 else
  ('Vokser' if o['m'][Lm]>=1.1*(S([v for v in o['m'][first(o):Lm] if v>0])/max(1,len([v for v in o['m'][first(o):Lm] if v>0])))
   else ('Faller' if o['m'][Lm]<=.6*(S([v for v in o['m'][first(o):Lm] if v>0])/max(1,len([v for v in o['m'][first(o):Lm] if v>0]))) else 'Stabil'))))
nyC=sorted([o for o in C if first(o)>=1 and o['s']>=10 and not re.search(r'demo|test|internal',' '.join(o['navn']),re.I)],key=lambda o:-o['s'])[:12]
new=[{'label':f'Ny kunde {i+1}','start':first(o),'serie':o['m'][first(o):],'status':status(o),'pilot':o['route']=='intern'} for i,o in enumerate(nyC)]
hfu={'kunder':len([o for o in C if o['cat']=='hfu' and not o['closed']]),'aktive':[len([o for o in C if o['cat']=='hfu' and o['m'][i]>0]) for i in range(N)]}
out={'months':M,'T':T,'SR':SR,'cats':cats,'act':act,'actDom':actDom,
 'domTotal':len([r for r in R if r['route']!='ukjent']),
 'kunderDirekte':len([o for o in real if o['route']=='direkte']),'kunderPartner':len([o for o in real if o['route']=='partner']),
 'tiers':tier,'moves':moves,'alerts':alerts,'new':new,'hfu':hfu,
 'sms':[{'m':m['m'],'no':m['no'],'ut':m['ut']} for m in SMS['months']]}
js='window.LAYN='+json.dumps(out,ensure_ascii=False)+';'
# SIKKERHETSSJEKK: ingen kundenavn skal finnes i utdata
navn=set()
for r in R:
    for x in (r['name'],r['cust'],r.get('partner','')):
        for w in re.findall(r'[A-Za-zÆØÅæøå][A-Za-zÆØÅæøå\-]{3,}',x or ''): navn.add(w.lower())
for w in ('demo','test','intern','ukjent','domene','slettet','kunde','helsestasjon','legevakt','visit','layn','flow'): navn.discard(w)
ord_ut={w.lower() for w in re.findall(r'[A-Za-zÆØÅæøå][A-Za-zÆØÅæøå\-]{3,}',js)}
treff=sorted(navn & ord_ut)
if treff:
    print('STOPP: mulige kundenavn i utdata:',treff); sys.exit(1)
open(OUT,'w',encoding='utf8').write(js)
print('OK',OUT,os.path.getsize(OUT),'bytes,',N,'måneder, siste',M[-1])

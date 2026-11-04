from pathlib import Path
from lxml import etree as E
import re,json,sys,os
from functools import lru_cache
BASE=Path(__file__).resolve().parent
NS={'t':'http://www.tei-c.org/ns/1.0','cb':'http://www.cbeta.org/ns/1.0'}

@lru_cache(maxsize=None)
def load(number):
 source=Path(os.environ.get('CBETA_SOURCE_DIRECTORY',str(BASE)))
 candidates=[source/f'T04n{number:04d}.xml',source/f'cbeta-t{number}.xml',source/f'T04n{number:04d}-selected.xml']
 path=next((p for p in candidates if p.exists()),None)
 if path is None:raise FileNotFoundError(f'No CBETA source for T{number} in {source}')
 root=E.parse(str(path))
 chars={}
 for c in root.findall('.//t:char',NS):
  uid=c.get('{http://www.w3.org/XML/1998/namespace}id')
  mappings=c.findall('t:mapping',NS)
  unicodes=[m.text for m in mappings if m.get('type')=='unicode']
  props={x.findtext('t:localName',namespaces=NS):x.findtext('t:value',namespaces=NS) for x in c.findall('t:charProp',NS)}
  chars[uid]=chr(int(unicodes[0].removeprefix('U+'),16)) if unicodes else props.get('normalized form',props.get('composition',f'[{uid}]'))
 def render(el):
  tag=E.QName(el).localname
  if tag in ['note','rdg']:return ''
  if tag=='g':return chars.get(el.get('ref','').lstrip('#'),el.text or '[gaiji]')
  result=el.text or ''
  for ch in el:
   result+=render(ch)+(ch.tail or '')
  return re.sub(r'\s+','',result)
 return root,render

@lru_cache(maxsize=None)
def chapter_section(number,chapter):
 root,_=load(number)
 for div in root.findall('.//cb:div',NS):
  for m in div.findall('cb:mulu',NS):
   # T213's added printed chapter 30 shares a TEI div with chapter 29.
   # The subsequent printed chapter numbers are offset from the TEI index.
   heading=re.match(r'(\d+)\s',m.text or '') if number==213 else None
   key=heading[1] if heading else m.get('n')
   if key!=str(chapter):continue
   section=[m]
   for sibling in m.itersiblings():
    if sibling.tag==f'{{{NS["cb"]}}}mulu':break
    section.append(sibling)
   return section
 raise ValueError((number,chapter))

if __name__=='__main__':
 for number in [210,212,213]:
  root,render=load(number)
  for div in root.findall('.//cb:div',NS):
   m=div.find('cb:mulu',NS)
   if m is None:continue
   print('\n',number,m.get('n'),m.text)
   groups=div.findall('.//t:lg',NS)
   if number==210:
    text=''.join(render(x) for x in groups)
    for i,line in enumerate(re.findall(r'[^。；]+[。；]?',text),1):print(i,line)
   else:
    for i,g in enumerate(groups,1):print(i,g.get('{http://www.w3.org/XML/1998/namespace}id'),render(g))

# Verse extraction is limited to the explicitly mapped passages; source punctuation is retained.
@lru_cache(maxsize=None)
def plain_readings(number,chapter):
 _,render=load(number)
 def marked(el):
  tag=E.QName(el).localname
  if tag in ['note','rdg']:return ''
  if tag=='g':return render(el)
  if tag=='caesura':return '\u241f'
  out=el.text or ''
  for child in el:out+=marked(child)+(child.tail or '')
  if tag=='l':out+='\u241f'
  return re.sub(r'\s+','',out)
 groups=[]
 for part in chapter_section(number,chapter):
  groups.extend([part] if part.tag==f'{{{NS["t"]}}}lg' else part.findall('.//t:lg',NS))
 return '\u241f'.join(marked(lg) for lg in groups)

def han(ch):
 return 0x3400<=ord(ch)<=0x9fff or 0x20000<=ord(ch)<=0x323af or 0xf900<=ord(ch)<=0xfaff

def extract(number,chapter,quote):
 from difflib import SequenceMatcher
 raw=plain_readings(number,chapter)
 positions=[i for i,c in enumerate(raw) if han(c)]
 text=''.join(raw[i] for i in positions)
 target=''.join(c for c in quote if han(c))
 exact=text.find(target)
 if exact>=0:start=exact;stop=exact+len(target);ratio=1
 else:
  # Differences can add or omit characters. Match whole native clauses
  # rather than using a fixed-length window that can clip a native line.
  boundaries=[0]+[i for i in range(1,len(positions)) if
      any(c in '，。；、！？：\u241f' for c in raw[positions[i-1]+1:positions[i]])]+[len(text)]
  limit=max(2,len(target)//5)
  matches=[
      (SequenceMatcher(None,target,text[i:j],autojunk=False).ratio(),i,j)
      for i in boundaries[:-1] for j in boundaries
      if len(target)-limit<=j-i<=len(target)+limit
  ]
  ratio,start,stop=max(matches,key=lambda v:(v[0],-v[1]),default=(0,0,0))
  if ratio<.8:raise ValueError((number,chapter,target,ratio,text[start:stop]))
 begin,end=positions[start],positions[stop-1]+1
 while end<len(raw) and not han(raw[end]) and raw[end]!='\u241f':end+=1
 excerpt=raw[begin:end]
 return [x for x in excerpt.split('\u241f') if x],ratio,target,text[start:stop]

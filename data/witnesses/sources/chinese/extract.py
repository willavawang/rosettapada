from pathlib import Path
from lxml import etree as E
import re,json,sys
BASE=Path(__file__).resolve().parent
NS={'t':'http://www.tei-c.org/ns/1.0','cb':'http://www.cbeta.org/ns/1.0'}

def load(number):
 root=E.parse(str(BASE/f'T04n{number:04d}-selected.xml'))
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
def plain_readings(number,chapter):
 root,render=load(number)
 def marked(el):
  tag=E.QName(el).localname
  if tag in ['note','rdg']:return ''
  if tag=='g':return render(el)
  if tag=='caesura':return '\u241f'
  out=el.text or ''
  for child in el:out+=marked(child)+(child.tail or '')
  if tag=='l':out+='\u241f'
  return re.sub(r'\s+','',out)
 for div in root.findall('.//cb:div',NS):
  m=div.find('cb:mulu',NS)
  if m is not None and m.get('n')==str(chapter):
   return '\u241f'.join(marked(lg) for lg in div.findall('.//t:lg',NS))
 raise ValueError((number,chapter))

def han(ch):
 return 0x3400<=ord(ch)<=0x9fff or 0x20000<=ord(ch)<=0x323af or 0xf900<=ord(ch)<=0xfaff

def extract(number,chapter,quote):
 from difflib import SequenceMatcher
 raw=plain_readings(number,chapter)
 positions=[i for i,c in enumerate(raw) if han(c)]
 text=''.join(raw[i] for i in positions)
 target=''.join(c for c in quote if han(c))
 exact=text.find(target)
 if exact>=0:start=exact;ratio=1
 else:
  matches=[(SequenceMatcher(None,target,text[i:i+len(target)],autojunk=False).ratio(),i) for i in range(len(text)-len(target)+1)]
  ratio,start=max(matches,key=lambda v:(v[0],-v[1]))
  assert ratio>=.8,(number,chapter,target,ratio,text[start:start+len(target)])
 begin,end=positions[start],positions[start+len(target)-1]+1
 while end<len(raw) and not han(raw[end]) and raw[end]!='\u241f':end+=1
 excerpt=raw[begin:end]
 return [x for x in excerpt.split('\u241f') if x],ratio,target,text[start:start+len(target)]

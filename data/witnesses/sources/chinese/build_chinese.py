from pathlib import Path
from lxml import etree as E
import json,re,sys,hashlib
from pypinyin import pinyin,Style
from extract import load,NS,han,extract
BASE=Path(__file__).resolve().parent
mapping=json.loads((BASE/'correspondence-mapping.json').read_text())
records=[]
for chapter in mapping['chapters']:
 for row in chapter['records']:
  n=row['pali']
  selected=row['T210'] or row['T212'] or row['T213']
  if n==30:selected=row['T213']
  if n==29:selected=list(reversed(row['T210']))
  if not selected:
   records.append({'pali':n,'status':'not-located','readings':[]});continue
  readings=[]
  for item in selected[:1]:
   canon=int(item['reference'][1:4]);chap=item['chapter']
   quote=re.sub(r'[〈(（].*','',item['table_text']).strip()
   if n==3:quote='人若罵我，勝我不勝，快意從者，怨終不息。'
   if n==30:quote='讚歎不放逸，毀彼放逸人，恒獲人天報，最上為殊勝。'
   lines,ratio,expected,actual=extract(canon,chap,quote)
   reading={'reference':item['reference'],'source_id':f'cbeta-t{canon}','lines':lines}
   if ratio<1:reading['edition_difference']={'table':expected,'cbeta':actual}
   readings.append(reading)
  records.append({'pali':n,'status':'present','readings':readings,'correspondence_source':chapter['source_url']})
changes={'為':'wéi','佛':'fó','調':'tiáo','降':'xiáng','靡':'mǐ','好':'hào','𠎝':'qiān','得':'dé','行':'xíng','興':'xīng','禁':'jìn','樂':'lè','省':'xǐng','子':'zǐ'}
def romanize(line):
 syllables=[changes.get(c,pinyin(c,style=Style.TONE,heteronym=False)[0][0]) for c in line]
 return re.sub(r'\s+([，。；、！？])',r'\1',' '.join(syllables))

# Retain the other mapped Chinese counterpart for Pāli 29 as a secondary reading.
lines,ratio,target,actual=extract(210,10,'居亂而身正，彼為獨覺悟，是力過師子，棄惡為大智。')
records[28]['readings'].append({'reference':'T210 10.9','source_id':'cbeta-t210','lines':lines,'note':'An additional counterpart in Ken Su\'s table; the first listed reading (T210 31.17) retains the horse image more closely.'})

notes={
3:'T210 has no counterpart identified in the table. The displayed reading is from T212; its first phrase is 人若罵我 in CBETA, whereas the table quotes 若人罵我.',
4:'The table lists T213 14.10 for both Pāli 3 and 4. The Chinese verse is not an exact positive/negative pair like the Pāli; its relation is a qualified parallel.',
6:'Ken Su identifies this T210 counterpart, but its admonition to examine oneself differs from the Pāli wording. Alignment is by verse, not literal phrase.',
11:'The correspondence table repeats 以真為偽 in its second clause. The display follows CBETA: 以真為偽、以偽為真.',
25:'The table quotes 錠明; this CBETA edition reads 定明. That Chinese lamp/illumination wording differs from the Pāli island image; no harmonization is made.',
28:'Ken Su\'s verse division groups six clauses here; CBETA punctuation places a full stop after 去危為即安 and continues the final two clauses before the next mapped verse. This grouping follows the correspondence table, with CBETA punctuation retained.',
29:'Ken Su lists two T210 counterparts. T210 31.17 is selected first because it retains the horse comparison. The display preserves CBETA 放恣 and 寤, against the table\'s 放逸 and 悟. Verse numbers follow the correspondence table; CBETA does not assign those local verse numbers.',
30:'T210 has no counterpart identified in the table. This is T213 4.24: it preserves praise of heedfulness and criticism of heedlessness but omits the Pāli reference to Maghavā/Indra.',
31:'The Chinese counterpart differs substantially in its fire image: T210 speaks of accumulated evil entering fire, while the Pāli heedful monk burns fetters. CBETA\'s historical character 𠎝 is retained; Mandarin qiān corresponds to 愆.',
32:'T210 has no counterpart identified in the table. The displayed T213 4.32 is an actual historical Chinese verse, not a new translation of the Pāli.',
33:'CBETA reads 意使作㺃; the correspondence table prints 笱. The historical character 㺃 is retained (modern Mandarin gǒu). The phrase is textually difficult; its interpretation is not resolved here.',
34:'T210 has no counterpart identified in the table. The displayed verse is T212 32.2.',
39:'The historical Chinese verse praises merit restraining evil, whereas the Pāli refers to one who has abandoned merit and demerit. Both wordings are preserved.',
40:'The Chinese opening uses a tortoise and the six faculties, rather than the Pāli body-as-pot image. The remaining fortress and Māra imagery supports the table\'s partial correspondence.',
42:'No counterpart is listed for Pāli 42 in T210, T212, or T213 in the selected scholarly correspondence table. This is not a claim that no Chinese parallel exists anywhere.'
}

# Source line positions are recovered from CBETA lb markers, not invented verse numbering.
def line_map(number,chapter):
 root,render=load(number)
 for div in root.findall('.//cb:div',NS):
  m=div.find('cb:mulu',NS)
  if m is None or m.get('n')!=str(chapter):continue
  chars=[];locations=[];current=[None]
  def add(text):
   for c in text or '':
    if han(c):chars.append(c);locations.append(current[0])
  def visit(el,inside=False):
   tag=E.QName(el).localname
   if tag in ['note','rdg']:return
   if tag=='lb':current[0]=el.get('n')
   inside=inside or tag=='lg'
   if tag=='g':
    if inside:add(render(el))
    return
   if inside:add(el.text)
   for child in el:
    visit(child,inside)
    if inside:add(child.tail)
  visit(div)
  return ''.join(chars),locations
 raise ValueError((number,chapter))

for row in records:
 n=row['pali']
 if n in notes:row['note']=notes[n]
 if not row['readings']:continue
 for index,r in enumerate(row['readings']):
  r['pinyin']=[romanize(line) for line in r['lines']]
  canon=int(r['reference'][1:4]);chapter=int(r['reference'].split()[1].split('.')[0])
  text,positions=line_map(canon,chapter)
  target=''.join(c for line in r['lines'] for c in line if han(c))
  start=text.find(target)
  assert start>=0,(n,target)
  r['taisho_start']=positions[start];r['taisho_end']=positions[start+len(target)-1]
  r['location']=f'T04, no. {canon}, {r["taisho_start"]}–{r["taisho_end"]}'
  r['source_url']=f'https://github.com/cbeta-org/xml-p5/blob/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T04/T04n{canon:04d}.xml'
  r.pop('table_quote',None);r.pop('match_ratio',None)
  if n in [4,6,25,30,31,39,40] or (n==29 and index==1):r['parallel_type']='partial'
  else:r['parallel_type']='verse-parallel'
 if row['readings'][0]['parallel_type']=='partial':row['status']='partial'

notice='''CBETA edition attribution and reuse notice\n\nCBETA Foundation (財團法人佛教電子佛典基金會), CBETA XML TEI P5 electronic edition, Taishō Tripiṭaka volume 4, texts T210, T212, and T213. The edition headers and their version dates are retained in the selected XML snapshots. Sources were retrieved from cbeta-org/xml-p5 at commit dbdea41071e1e260ad84b72faefd4587333cf76d.\n\nCBETA states that its database is for noncommercial use, that redistributed extracts should preserve substantive content and include its use notice and version information, and that errors should be reported to CBETA. It disclaims liability for damage arising from use. Unless specially excluded, the current database license is Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International. The Taishō texts used here fall in CBETA's category A.\n\nCopyright and complete use notice: https://cbeta.org/copyright\nLicense: https://creativecommons.org/licenses/by-nc-sa/4.0/\n\nOnly bounded ancient verse passages and factual correspondence identifiers are displayed. The Chinese source editions retain their own attribution and license; no blanket project license is asserted. Pinyin is a modern editorial reading aid, not ancient Chinese pronunciation.\n'''
notice += '''\nCBETA 電子佛典資料庫使用說明（來源：https://cbeta.org/copyright）\n\n1. 非營利使用：本資料庫之使用限定於個人或團體非營利性用途。\n2. 再傳播規範：將本資料庫以網路、光碟或其它媒體再傳播、節錄引用及再加工發行時，以不改變實質內容為原則，並需於成品附上本說明及版本資訊，以利使用者查詢相關修訂資訊。\n3. 錯誤回報：若發現本資料庫中任何錯誤之處，請與本會聯絡。\n4. 免責聲明：若因使用本資料庫所產生之任何損害，本會一概不負任何責任。\n5. 核心授權：除下方「二、底本來源與授權分類」中特別註明不適用之文獻外，本資料庫未特別說明處皆採用「Creative Commons 姓名標示-非商業性-相同方式分享 4.0 國際授權條款」釋出。\n'''
(BASE/'CBETA-NOTICE.txt').write_text(notice)
provenance=json.loads((BASE/'cbeta-provenance.json').read_text())
sources=[]
for number,title in [(210,'法句經 (Faju jing)'),(212,'出曜經 (Chuyao jing)'),(213,'法集要頌經 (Faji yaosong jing)')]:
 snap=BASE/f'T04n{number:04d}-selected.xml'
 sources.append({'id':f'cbeta-t{number}','title':title,'collection':f'T{number}','edition':'CBETA XML TEI P5, Taishō Tripiṭaka vol. 4','edition_date':E.parse(str(snap)).findtext('.//t:teiHeader/t:fileDesc/t:publicationStmt/t:date',namespaces=NS),'retrieved':'2026-10-23','url':f'https://cbetaonline.dila.edu.tw/T{number:04d}','upstream_repository':'cbeta-org/xml-p5','upstream_commit':provenance['commit'],'snapshot':str(snap.relative_to(BASE.parents[3])),'snapshot_sha256':hashlib.sha256(snap.read_bytes()).hexdigest(),'license':'CC-BY-NC-SA-4.0','license_url':'https://creativecommons.org/licenses/by-nc-sa/4.0/','copyright_url':'https://cbeta.org/copyright','notice':'data/witnesses/sources/chinese/CBETA-NOTICE.txt'})
source_map={'id':'ken-su-correspondence','title':'Pāli–Chinese Dhammapada correspondence tables, chapters 1–3','compiler':'蘇錦坤 (Ken Su)','url':'https://nanda.online-dhamma.net/tipitaka/sutta/khuddaka/dhammapada/dhp-correspondence-tables/dhp-correspondence-tables-pali/','snapshot':'data/witnesses/sources/chinese/correspondence-mapping.json','note':'Only correspondence facts and ancient verse quotations are retained; modern Pāli translations and explanatory commentary are not reproduced.'}
result={'tradition':'zh','language':'Chinese','language_tag':'zh-Hant','scope':'Pāli Dhammapada verses 1–43, in Pāli order','editorial_policy':'T210 is preferred. Actual T212 or T213 historical counterparts are used only where the selected table has no T210 counterpart, and each reading retains its exact Taishō collection reference. Missing coverage is not filled by retranslating Pāli.','coverage':{'present':42,'not_located':[42],'fallbacks':{'3':'T212 15.7','4':'T213 14.10','30':'T213 4.24','32':'T213 4.32','34':'T212 32.2'}},'sources':[source_map,*sources], 'pinyin':{'type':'modern Mandarin pronunciation aid','method':'pypinyin 0.55.0 citation-tone output, with manual contextual corrections for polyphonic and historical characters. Syllables are spaced character by character; word segmentation and tone sandhi are not asserted.','status':'editorial reading aid; not an independently reviewed historical pronunciation or translation','manual_character_readings':changes,'pronunciation_references':[{'character':'㺃','reading':'gǒu','url':'https://www.cns11643.gov.tw/wordView.jsp?ID=212268'},{'character':'𠎝','reading':'qiān','url':'https://www.cns11643.gov.tw/wordView.jsp?ID=664642'},{'character':'為','reading':'wéi in these usages','url':'https://dict.revised.moe.edu.tw/dictView.jsp?ID=11400&la=1&powerMode=0'}]},'verses':records}
# Snapshot paths are project-relative.
for source in result['sources']:
 if source.get('snapshot','').startswith('witnesses/'):
  source['snapshot']='data/'+source['snapshot']
(BASE.parents[1]/'chinese.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Wrote',BASE.parents[1]/'chinese.json')
print('Coverage:',result['coverage'])
for source in sources:print(source['snapshot'])

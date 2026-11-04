"""Prepare the authorized Chinese reader selection from pinned local sources.

The 99 approved pilot readings stay unchanged. New chapter records come from
Ken Su's identifiers and CBETA's ancient text, never the table's modern Pāli
translation. Regeneration needs lxml and pypinyin 0.55.0.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import argparse, hashlib, json, os, re
from lxml import etree as E, html

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
NS={'t':'http://www.tei-c.org/ns/1.0','cb':'http://www.cbeta.org/ns/1.0'}
T=NS['t'];CB=NS['cb'];XML='http://www.w3.org/XML/1998/namespace'
COMMIT='dbdea41071e1e260ad84b72faefd4587333cf76d'
DATE='2026-11-04'
PILOT=set(range(1,44))|set(range(100,116))|set(range(157,167))|set(range(221,235))|set(range(290,306))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source-directory',type=Path,help='Pinned complete CBETA XML working copies; otherwise use the selected snapshots.')
 parser.add_argument('--correspondence-directory',type=Path,help='Cached Ken Su chapter HTML pages; only the newly authorized chapters are appended.')
 args=parser.parse_args()
 if args.source_directory:os.environ['CBETA_SOURCE_DIRECTORY']=str(args.source_directory)
 from extract import load,han,extract,plain_readings,chapter_section
 from pypinyin import pinyin,Style
 manifest=json.loads((ROOT/'data/chapters.json').read_text())
 wanted=sorted(n for c in manifest['chapters'] for n in range(c['start'],c['end']+1))
 previous=json.loads((ROOT/'data/witnesses/chinese.json').read_text())
 approved={r['pali']:deepcopy(r) for r in previous['verses'] if not args.source_directory or r['pali'] in PILOT}
 mapping=json.loads((BASE/'correspondence-mapping.json').read_text())
 if args.correspondence_directory:
  mapping['chapters']=[c for c in mapping['chapters'] if c['chapter'] in {1,2,3,8,12,17,21}]
  known={c['chapter'] for c in mapping['chapters']}
  for c in manifest['chapters']:
   if c['no'] in known:continue
   path=args.correspondence_directory/f'chinese-{c["no"]:02d}.html'
   doc=html.fromstring(path.read_bytes());records=[]
   for tr in doc.xpath('//tr'):
    cells=[' '.join(el.text_content().split()) for el in tr.xpath('./td')]
    m=re.match(r'PLSu-\d+-(\d+)\b',cells[0]) if len(cells)==4 else None
    if not m:continue
    row={'pali':int(m[1])}
    for number,cell in zip([210,212,213],cells[1:]):
     matches=list(re.finditer(r'T(210|212|213)-(\d+)-(\d+)(?!\d)',cell));items=[]
     for i,a in enumerate(matches):
      canon,ch,v=map(int,a.groups())
      text=cell[a.end():matches[i+1].start() if i+1<len(matches) else len(cell)].strip()
      items.append({'reference':f'T{canon} {ch}.{v}','chapter':ch,'verse':v,'table_text':text})
     row[f'T{number}']=items
    records.append(row)
   assert [r['pali'] for r in records]==list(range(c['start'],c['end']+1)),c['no']
   mapping['chapters'].append({'chapter':c['no'],'source_url':f'https://nanda.online-dhamma.net/tipitaka/sutta/khuddaka/dhammapada/dhp-correspondence-tables/dhp-correspondence-tables-pali-chap{c["no"]:02d}/','html_sha256':sha(path),'records':records})
  mapping['chapters'].sort(key=lambda c:c['chapter'])
  write(BASE/'correspondence-mapping.json',mapping)

 # Record exact CBETA verse text and physical Taishō line boundaries independently
 # of the correspondence compiler's local chapter/verse division.
 loc_cache={}
 def chapter_map(number,chapter):
  if (number,chapter) in loc_cache:return loc_cache[number,chapter]
  _,render=load(number)
  section=chapter_section(number,chapter)
  preceding=section[0].xpath('preceding::t:lb[1]',namespaces=NS)
  chars=[];locations=[];current=[preceding[0].get('n') if preceding else None]
  def add(text):
   for ch in text or '':
    if han(ch):chars.append(ch);locations.append(current[0])
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
  for element in section:visit(element)
  result=(''.join(chars),locations,section);loc_cache[number,chapter]=result
  return result

 changes=dict(previous['pinyin']['manual_character_readings'])
 changes.update({'𦾨':'niè','𣧑':'xiōng','𭶑':'xiá','長':'cháng'})
 phrase_readings=dict(previous['pinyin']['manual_phrase_readings'])
 contextual={
  '長老':('zhǎng','lǎo'),'不著':('bù','zhuó'),'數數':('shuò','shuò'),
  '無所著':('wú','suǒ','zhuó'),'所著':('suǒ','zhuó'),'為人':('wéi','rén'),
  '為佛':('wéi','fó'),'為天':('wéi','tiān'),'不為':('bù','wéi'),
  '相應':('xiāng','yìng'),'應真':('yìng','zhēn'),'稱量':('chēng','liáng')
 }
 def romanize(line):
  if line in phrase_readings:return phrase_readings[line]
  syllables=[changes.get(ch,pinyin(ch,style=Style.TONE,heteronym=False)[0][0]) for ch in line]
  for phrase,pronunciation in contextual.items():
   for match in re.finditer(phrase,line):
    syllables[match.start():match.end()]=pronunciation
  result=re.sub(r'\s+([，。；、！？：」』])',r'\1',' '.join(syllables))
  if any(han(ch) for ch in result):raise ValueError(('Missing pinyin',line,result))
  return result

 # Use T210 by default, with source-specific choices where a listed
 # alternative preserves a consequential feature of the Pāli verse.
 preferred={
  131:'T212 31.3',277:'T212 13.5',278:'T210 28.20',
  279:'T213 12.9',410:'T212 34.43',411:'T212 34.54',415:'T212 34.36'
 }
 notes={
  44:'T210 speaks of selecting the ground and leaving the prison for heaven. Pāli explicitly asks who will discern this earth, the world of Yama, and the realm of the gods.',
  45:'T210 continues the prison-to-heaven imagery. Pāli refers to the trainee discerning the earth, the world of Yama, and the gods.',
  47:'T210 retains flowers, death, and rushing water, but depicts a sick body withering like a falling flower rather than someone gathering flowers as a flood takes a sleeping village.',
  69:'The two retained Chinese stanzas also occur at Pāli 119 in reverse order. T210 expresses the ripening of misconduct without Pāli 69’s honey image.',
  80:'T210 speaks of fashioning a horn bow and steering a boat instead of straightening an arrow and channeling water. The self-training comparison is retained.',
  119:'The same two Chinese stanzas also occur at Pāli 69. The first reading here preserves the wrongdoer seeing good before the bad action ripens.',
  131:'T212 is preferred because it preserves the harmful action and the lack of future happiness. The listed T210 18.2 expresses the positive counterpart shown at Pāli 132.',
  132:'T210 retains refraining from harming beings and future well-being. For the negative counterpart at Pāli 131, the reader uses T212 31.3.',
  145:'T210 uses the same stanza as at Pāli 80. The Chinese keeps the craft and self-training analogy with different crafts in two of the clauses.',
  315:'T210 30.12, the frontier-city passage, is also retained as a secondary counterpart at Pāli 157.',
  275:'T210 28.3 describes the taught path and the need to practice it. The second Chinese passage, T210 28.22, supplies the arrow comparison and is also listed at Pāli 276.',
  276:'T210 28.22 stresses striving for oneself and accepting the Buddha’s words. It also contains the arrow motif of Pāli 275 and does not supply the whole Pāli 276 stanza.',
  277:'T212 states that all conditioned things are impermanent. The listed T210 28.4 speaks of the impermanence and suffering of birth and death and is retained as an alternate.',
  278:'T210 28.20 is displayed first because it expressly calls conditioned things painful. The other T210 reading combines the themes of impermanence and suffering.',
  279:'T213 is preferred because it explicitly states that all phenomena are not-self. T210 uses the wording that conditioned things are not the body, and remains an alternate.',
  360:'T210 34.1 gathers sense restraint and restraint of body and mind into one stanza, shared by Pāli 360 and 361.',
  361:'T210 34.1 gathers sense restraint and restraint of body and mind into one stanza, shared by Pāli 360 and 361. T212 8.11 and T213 7.13 are also listed for Pāli 361.',
  410:'T212 34.43 directly speaks of having no hopes in this world or the next. The broader purity stanza T210 35.28 is also listed at Pāli 411.',
  411:'T212 34.54 preserves the deathless image and is preferred to the broader purity stanza T210 35.28, which is also listed at Pāli 410.',
  414:'T210 retains the pit and crossing to the far shore. The listed use of the same stanza at Pāli 415 is replaced there by the closer T212 counterpart.',
  415:'T212 34.36 preserves abandoning sensual desire and leaving home. T210 35.32 is the crossing verse displayed at Pāli 414.'
 }
 partial={44,45,47,69,80,145,275,276,360,361,411,414}
 qualified_alternates={
  (131,'T210 18.2'),(277,'T210 28.4'),(278,'T210 28.4'),
  (279,'T210 28.21'),(410,'T210 35.28'),(411,'T210 35.28'),(415,'T210 35.32')
 }
 by_number={}
 for chapter in mapping['chapters']:
  for row in chapter['records']:
   n=row['pali']
   if n not in wanted:continue
   if n in approved:by_number[n]=deepcopy(approved[n]);continue
   listed=[x for key in ['T210','T212','T213'] for x in row[key]]
   default=row['T210'] or (row['T212']+row['T213'])
   selected=[x for x in listed if x['reference']==preferred.get(n)]
   selected+= [x for x in default if x not in selected]
   result={'pali':n,'status':'not-located','readings':[],'correspondence_source':chapter['source_url']}
   if n in notes:result['note']=notes[n]
   if not listed:result['note']='No counterpart is listed across T210, T212, and T213 in this correspondence table.'
   for item in selected:
    canon=int(item['reference'][1:4]);ch=item['chapter']
    quote=re.sub(r'[〈(（].*','',item['table_text']).strip()
    try:
     lines,ratio,expected,actual=extract(canon,ch,quote)
    except ValueError:
     # A table quotation may be a different edition, a composite, or an
     # apparent misreference. Keep its ID in the notes, not its verse text.
     continue
    text,positions,_=chapter_map(canon,ch);target=''.join(c for line in lines for c in line if han(c));start=text.find(target)
    assert start>=0,(n,item['reference'])
    is_partial=n in partial or (n,item['reference']) in qualified_alternates or '參考' in item['table_text']
    reading={'reference':item['reference'],'source_id':f'cbeta-t{canon}','lines':lines,'pinyin':[romanize(line) for line in lines],'taisho_start':positions[start],'taisho_end':positions[start+len(target)-1],'source_url':f'https://github.com/cbeta-org/xml-p5/blob/{COMMIT}/T/T04/T04n{canon:04d}.xml','parallel_type':'partial' if is_partial else 'verse-parallel'}
    reading['location']=f'T04, no. {canon}, {reading["taisho_start"]}–{reading["taisho_end"]}'
    if is_partial:reading['partial_correspondence']=True
    if ratio<1:reading['edition_difference']={'table':expected,'cbeta':actual}
    if result['readings']:
     reading['note']='Additional historical counterpart identified by Ken Su; the first reading is displayed.'
    else:
     result['status']='partial' if is_partial else 'present'
    result['readings'].append(reading)
    if not row['T210']:break
   alternatives=[x['reference'] for x in listed if x['reference'] not in {r['reference'] for r in result['readings']}]
   if alternatives:result['alternative_correspondence_references']=alternatives
   if listed and not result['readings']:result['note']='The table lists a reference, but its quotation could not be matched to the pinned CBETA verse text.'
   by_number[n]=result
 records=[by_number[n] for n in wanted]
 assert all(by_number[n]==r for n,r in approved.items()),'Approved Chinese readings changed.'
 by_reference={}
 for record in records:
  for reading in record['readings']:
   by_reference.setdefault(reading['reference'],set()).add(record['pali'])
 repeated={ref:sorted(numbers) for ref,numbers in by_reference.items() if len(numbers)>1}
 for record in records:
  if record['pali'] in approved:continue
  for reading in record['readings']:
   if reading['reference'] in repeated:
    joined=', '.join(map(str,repeated[reading['reference']]))
    group_note=f'This source stanza is shared by Pāli {joined} in the correspondence table.'
    reading['note']=' '.join(x for x in [reading.get('note',''),group_note] if x)
    reading['shared_pali_positions']=repeated[reading['reference']]

 # Verify every approved and new reading against the pinned complete text and
 # construct bounded TEI snapshots with exactly the selected ancient passages.
 provenance=json.loads((BASE/'cbeta-provenance.json').read_text())
 verification=[]
 if args.source_directory:
  for info in provenance['files']:
   number=int(re.search(r'T04n0(\d+)',info['file'])[1]);root,_=load(number)
   input_path=next(p for p in [args.source_directory/f'T04n{number:04d}.xml',args.source_directory/f'cbeta-t{number}.xml'] if p.exists())
   assert sha(input_path)==info['upstream_sha256'],f'Unpinned full source: {input_path}'
   selected_root=E.Element(root.getroot().tag,attrib=root.getroot().attrib,nsmap=root.getroot().nsmap)
   selected_root.append(deepcopy(root.find('t:teiHeader',NS)))
   body=E.SubElement(E.SubElement(selected_root,f'{{{T}}}text'),f'{{{T}}}body')
   grouped={}
   for record in records:
    for i,reading in enumerate(record['readings'],1):
     if reading['source_id']!=f'cbeta-t{number}':continue
     chapter=int(reading['reference'].split()[1].split('.')[0]);text,positions,section=chapter_map(number,chapter)
     target=''.join(ch for line in reading['lines'] for ch in line if han(ch));start=text.find(target)
     assert start>=0,(record['pali'],reading['reference'])
     assert ''.join(reading['lines']) in plain_readings(number,chapter).replace('\u241f',''),(record['pali'],'Source punctuation differs')
     assert positions[start]==reading['taisho_start'] and positions[start+len(target)-1]==reading['taisho_end'],(record['pali'],'Taishō locator changed')
     if chapter not in grouped:
      div=E.Element(f'{{{CB}}}div',type='pin')
      for tag in ['cb:mulu','t:head']:
       el=next((element for element in section if element.tag==f'{{{NS[tag.split(":")[0]]}}}{tag.split(":")[1]}'),None)
       if el is not None:div.append(deepcopy(el))
      grouped[chapter]=div
     lg=E.SubElement(grouped[chapter],f'{{{T}}}lg',attrib={f'{{{XML}}}id':f'selected-pali{record["pali"]:03d}-{i}','corresp':reading['reference'],'type':'selected-verse'})
     cursor=start
     for line in reading['lines']:
      l=E.SubElement(lg,f'{{{T}}}l');last=None;tail=None
      for ch in line:
       if han(ch):
        assert text[cursor]==ch
        location=positions[cursor];cursor+=1
        if location!=last:tail=E.SubElement(l,f'{{{T}}}lb',n=location,ed='T');last=location
       if tail is None:l.text=(l.text or '')+ch
       else:tail.tail=(tail.tail or '')+ch
     assert cursor==start+len(target)
     verification.append({'pali':record['pali'],'reference':reading['reference'],'taisho_start':reading['taisho_start'],'taisho_end':reading['taisho_end'],'han_characters':len(target),'source_verified':True,'full_text_and_punctuation_in_source':True})
   for chapter in sorted(grouped):body.append(grouped[chapter])
   assert E.tostring(root.find('t:teiHeader',NS),method='c14n')==E.tostring(selected_root.find('t:teiHeader',NS),method='c14n')
   path=BASE/info['file'];E.ElementTree(selected_root).write(str(path),encoding='UTF-8',xml_declaration=True)
   info['selected_sha256']=sha(path);info['selected_chapters']=sorted(grouped);info['selected_readings']=[v['reference'] for v in verification if v['reference'].startswith(f'T{number} ')]
   info['selected_bytes']=path.stat().st_size
  provenance['selected_on']=DATE;write(BASE/'cbeta-provenance.json',provenance)
  write(BASE/'verification.json',{'checked':DATE,'pali_records':len(records),'readings_checked':len(verification),'all_selected_han_characters_found_in_pinned_cbeta':True,'full_text_and_punctuation_in_source':True,'unchanged_complete_tei_headers':True,'taisho_locators_verified':True,'first_43_records_preserved':True,'all_99_pilot_records_preserved':True,'readings':verification})
 else:
  # Existing selected snapshots are sufficient for subsequent rebuilds.
  for record in records:
   for reading in record['readings']:
    canon=int(reading['reference'][1:4]);ch=int(reading['reference'].split()[1].split('.')[0]);text,positions,_=chapter_map(canon,ch)
    assert ''.join(c for line in reading['lines'] for c in line if han(c)) in text
    assert ''.join(reading['lines']) in plain_readings(canon,ch).replace('\u241f','')

 result=deepcopy(previous);result['scope']='Historical Chinese counterparts indexed to all 423 Pāli positions in the 26-chapter reader'
 result['verses']=records
 result['coverage']={'present':sum(bool(r['readings']) for r in records),'not_located':[r['pali'] for r in records if not r['readings']],'fallbacks':{str(r['pali']):r['readings'][0]['reference'] for r in records if r['readings'] and not r['readings'][0]['reference'].startswith('T210 ')},'status_counts':dict(Counter(r['status'] for r in records))}
 result['shared_source_stanzas']=repeated
 result['pinyin']['manual_character_readings']=changes
 result['pinyin']['method']=result['pinyin']['method'].split(' New selection:')[0].split(' Expanded reader:')[0]+' Expanded reader: rare historical forms 𦾨, 𣧑, and 𭶑 use the readings of 孽, 凶, and 黠 given by the correspondence quotation or CBETA normalization. New syllables have received limited contextual review.'
 result['pinyin']['manual_phrase_readings']=phrase_readings
 result['sources'][0]['title']='Pāli–Chinese Dhammapada correspondence tables, all 26 Pāli chapters'
 for source in result['sources'][1:]:
  snap=ROOT/source['snapshot'];source['snapshot_sha256']=sha(snap);source['selection_updated']=DATE
 write(ROOT/'data/witnesses/chinese.json',result)
 print(json.dumps({'records':len(records),'coverage':result['coverage'],'approved_99_pilot_unchanged':True,'verified_readings':len(verification)},ensure_ascii=False))

if __name__=='__main__':main()

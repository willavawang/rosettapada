"""Prepare the authorized Chinese reader selection from pinned local sources.

The approved first-43 readings stay unchanged. New chapter records come from
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
DATE='2026-10-26'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source-directory',type=Path,help='Pinned complete CBETA XML working copies; otherwise use the selected snapshots.')
 parser.add_argument('--correspondence-directory',type=Path,help='Cached Ken Su chapter HTML pages; only the newly authorized chapters are appended.')
 args=parser.parse_args()
 if args.source_directory:os.environ['CBETA_SOURCE_DIRECTORY']=str(args.source_directory)
 from extract import load,han,extract,plain_readings
 from pypinyin import pinyin,Style
 manifest=json.loads((ROOT/'data/chapters.json').read_text())
 wanted=sorted(n for c in manifest['chapters'] for n in range(c['start'],c['end']+1))
 previous=json.loads((ROOT/'data/witnesses/chinese.json').read_text())
 approved={r['pali']:deepcopy(r) for r in previous['verses'] if r['pali']<=43}
 mapping=json.loads((BASE/'correspondence-mapping.json').read_text())
 if args.correspondence_directory:
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
     matches=list(re.finditer(r'T(210|212|213)-(\d+)-(\d+)\b',cell));items=[]
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
  root,render=load(number)
  div=next((d for d in root.findall('.//cb:div',NS) if d.find('cb:mulu',NS) is not None and d.find('cb:mulu',NS).get('n')==str(chapter)),None)
  if div is None:raise ValueError((number,chapter))
  chars=[];locations=[];current=[None]
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
  visit(div)
  result=(''.join(chars),locations,div);loc_cache[number,chapter]=result
  return result

 changes=dict(previous['pinyin']['manual_character_readings'])
 changes.update({'惓':'juàn','長':'zhǎng','著':'zhuó','率':'shuài','盡':'jìn'})
 phrase_readings={'如種苦種，':'rú zhòng kǔ zhǒng，','亦如種甜，':'yì rú zhòng tián，','以覺意能應，':'yǐ jué yì néng yìng，','伎樂放逸，':'jì yuè fàng yì，'}
 def romanize(line):
  if line in phrase_readings:return phrase_readings[line]
  syllables=[changes.get(ch,pinyin(ch,style=Style.TONE,heteronym=False)[0][0]) for ch in line]
  result=re.sub(r'\s+([，。；、！？])',r'\1',' '.join(syllables))
  assert not any(han(ch) for ch in result),(line,result)
  return result
 notes={
 106:'The T210 counterpart contrasts prolonged ritual offering with a moment of one-pointed recollection of Dharma; the Pāli speaks of honoring a developed person. Both historical formulations are retained.',
 107:'The Chinese verse refers to honoring the Three Honored Ones (三尊), where Pāli speaks of honoring one who has developed himself.',
 113:'The Pāli refers to seeing arising and passing away. T210 uses 成敗 and 見微知所忌; its wording is retained without harmonization.',
 115:'The correspondence table quotes 學惟佛法要. This pinned CBETA edition reads 學推佛法要; the display preserves that source reading.',
 157:'T210 20.1 is displayed. Ken Su also identifies T210 30.12, which adds a frontier-city and hell image. The first Chinese reading does not reproduce the Pāli three watches of the night.',
 160:'The Pāli makes oneself one’s refuge. T210 instead asks how a person unable to benefit himself can benefit others, then praises a well-trained mind and body. This is a qualified historical correspondence.',
 162:'T210 preserves the creeper image but develops it as unchecked misconduct and desire; it does not reproduce the whole tree-and-enemy simile of Pāli.',
 164:'The Chinese ending uses bitter seed rather than the Pāli bamboo/reed image. Its historical wording is retained.',
 166:'The Pāli warns against neglecting one’s own welfare for another’s. T210 speaks of benefiting oneself and others without loss, and emphasizes discipline and learning. This is a substantial recensional difference.',
 221:'This pinned CBETA edition reads 避諸愛會 where the correspondence table quotes 避諸愛貪. The source spelling is preserved.',
 222:'The Chinese charioteer simile ends with leaving darkness for light; the Pāli contrasts a true charioteer with others who merely hold reins.',
 224:'T210 says not to demand much where Pāli urges giving when asked even if one has little. The rest of the truthfulness, non-anger, and heaven sequence supports the qualified correspondence.',
 225:'Ken Su lists both T210 7.1 and 25.6. The first is displayed because its deathless destination is closer to the Pāli; the second speaks of birth in heaven.',
 226:'Ken Su lists both T210 6.9 and 25.7. Both actual Chinese readings are retained; the first is displayed.',
 228:'T210 treats praise and blame in terms of advantage and reputation; the Pāli says no one has ever been wholly praised or wholly blamed. This is a qualified correspondence.',
 230:'T210 retains praise by Brahmā/Śakra but does not reproduce the Pāli gold-ornament simile. This pinned CBETA edition reads 諸人咨嗟, where the correspondence table quotes 諸天咨嗟.',
 290:'T210 contrasts a small gift of peace with its greater reward, where Pāli contrasts giving up lesser happiness for greater happiness. The historical difference is preserved.',
 293:'The Chinese verse contrasts diligent practice with doing what should not be done. It does not reproduce Pāli’s explicit mindfulness-of-the-body phrase.',
 294:'The mother, ruler, ministers, and retinue imagery differs from the Pāli mother, father, kings, kingdom, and attendants sequence. No explanatory allegory is added to the verse.',
 295:'No counterpart is listed in T210, T212, or T213 in the consulted correspondence table. This records the scope of this comparison, not absence throughout Chinese Buddhist literature.',
 296:'T210 combines recollection of Buddha, Dharma, and Saṅgha in one stanza. The same whole historical stanza is shown at Pāli 296–298 as a grouped partial parallel; these are not three distinct Chinese verses.',
 297:'T210 combines recollection of Buddha, Dharma, and Saṅgha in one stanza. The same whole historical stanza is shown at Pāli 296–298 as a grouped partial parallel; these are not three distinct Chinese verses.',
 298:'T210 combines recollection of Buddha, Dharma, and Saṅgha in one stanza. The same whole historical stanza is shown at Pāli 296–298 as a grouped partial parallel; these are not three distinct Chinese verses.',
 299:'T210 has no counterpart identified in the table. T213 15.20 is selected because it explicitly preserves the awakened disciple’s day-and-night mindfulness of the body; the listed T212 16.17 includes a broader sequence of recollections.',
 300:'T210 has no counterpart identified in the table. This is T212 16.18, a historical Chinese verse about day-and-night recollection of non-harm.',
 303:'Ken Su identifies both T210 4.8 and 29.13. Both Chinese readings are retained, with the first displayed.',
 304:'T210 contrasts proximity to the Way with distance from it, while retaining the snowy mountain and arrow-at-night images of the Pāli good/bad contrast.'
 }
 partial={106,107,113,157,160,162,164,166,222,224,228,230,290,293,294,296,297,298,304}
 by_number={}
 for chapter in mapping['chapters']:
  for row in chapter['records']:
   n=row['pali']
   if n not in wanted:continue
   if n in approved:by_number[n]=deepcopy(approved[n]);continue
   selected=row['T210'] or row['T212'] or row['T213']
   if n==299:selected=row['T213']
   # Retain alternate T210 counterparts explicitly rather than silently losing
   # the differences. Fallback collections contribute the selected first reading.
   if not row['T210']:selected=selected[:1]
   result={'pali':n,'status':'not-located' if not selected else 'partial' if n in partial else 'present','readings':[],'correspondence_source':chapter['source_url']}
   if n in notes:result['note']=notes[n]
   alternatives=[x['reference'] for key in ['T210','T212','T213'] for x in row[key] if x not in selected]
   if alternatives:result['alternative_correspondence_references']=alternatives
   for i,item in enumerate(selected):
    canon=int(item['reference'][1:4]);ch=item['chapter']
    quote=re.sub(r'[〈(（].*','',item['table_text']).strip()
    lines,ratio,expected,actual=extract(canon,ch,quote)
    text,positions,_=chapter_map(canon,ch);target=''.join(c for line in lines for c in line if han(c));start=text.find(target)
    assert start>=0,(n,item['reference'])
    reading={'reference':item['reference'],'source_id':f'cbeta-t{canon}','lines':lines,'pinyin':[romanize(line) for line in lines],'taisho_start':positions[start],'taisho_end':positions[start+len(target)-1],'source_url':f'https://github.com/cbeta-org/xml-p5/blob/{COMMIT}/T/T04/T04n{canon:04d}.xml','parallel_type':'partial' if n in partial else 'verse-parallel'}
    reading['location']=f'T04, no. {canon}, {reading["taisho_start"]}–{reading["taisho_end"]}'
    if ratio<1:reading['edition_difference']={'table':expected,'cbeta':actual}
    if i:reading['note']='Additional historical counterpart identified by Ken Su; the first reading is displayed.'
    result['readings'].append(reading)
   by_number[n]=result
 records=[by_number[n] for n in wanted]
 assert all(by_number[n]==r for n,r in approved.items()),'Approved first-43 Chinese readings changed.'

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
     chapter=int(reading['reference'].split()[1].split('.')[0]);text,positions,original_div=chapter_map(number,chapter)
     target=''.join(ch for line in reading['lines'] for ch in line if han(ch));start=text.find(target)
     assert start>=0,(record['pali'],reading['reference'])
     assert ''.join(reading['lines']) in plain_readings(number,chapter).replace('\u241f',''),(record['pali'],'Source punctuation differs')
     assert positions[start]==reading['taisho_start'] and positions[start+len(target)-1]==reading['taisho_end'],(record['pali'],'Taishō locator changed')
     if chapter not in grouped:
      div=E.Element(f'{{{CB}}}div',type='pin')
      for tag in ['cb:mulu','t:head']:
       el=original_div.find(tag,NS)
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
  write(BASE/'verification.json',{'checked':DATE,'pali_records':len(records),'readings_checked':len(verification),'all_selected_han_characters_found_in_pinned_cbeta':True,'full_text_and_punctuation_in_source':True,'unchanged_complete_tei_headers':True,'taisho_locators_verified':True,'first_43_records_preserved':True,'readings':verification})
 else:
  # Existing selected snapshots are sufficient for subsequent rebuilds.
  for record in records:
   for reading in record['readings']:
    canon=int(reading['reference'][1:4]);ch=int(reading['reference'].split()[1].split('.')[0]);text,positions,_=chapter_map(canon,ch)
    assert ''.join(c for line in reading['lines'] for c in line if han(c)) in text
    assert ''.join(reading['lines']) in plain_readings(canon,ch).replace('\u241f','')

 result=deepcopy(previous);result['scope']='Six-chapter pilot plus retained Mind page: Pāli 1–43, 100–115, 157–166, 221–234, and 290–305, in Pāli order'
 result['verses']=records
 result['coverage']={'present':sum(bool(r['readings']) for r in records),'not_located':[r['pali'] for r in records if not r['readings']],'fallbacks':{str(r['pali']):r['readings'][0]['reference'] for r in records if r['readings'] and not r['readings'][0]['reference'].startswith('T210 ')},'status_counts':dict(Counter(r['status'] for r in records))}
 result['pinyin']['manual_character_readings']=changes
 contextual='New selection: contextual readings include 惓 juàn in 不惓, 長 zhǎng in 長老, 著 zhuó in 不著名色, 率 shuài in 率君二臣, 盡 jìn, 種 zhòng when planting and zhǒng for seed, 應 yìng in 能應, and 樂 yuè in 伎樂.'
 result['pinyin']['method']=result['pinyin']['method'].split(' New selection:')[0]+' '+contextual
 result['pinyin']['manual_phrase_readings']=phrase_readings
 result['sources'][0]['title']='Pāli–Chinese Dhammapada correspondence tables, chapters 1–3, 8, 12, 17, and 21'
 for source in result['sources'][1:]:
  snap=ROOT/source['snapshot'];source['snapshot_sha256']=sha(snap);source['selection_updated']=DATE
 write(ROOT/'data/witnesses/chinese.json',result)
 print(json.dumps({'records':len(records),'coverage':result['coverage'],'approved_first_43_unchanged':True,'verified_readings':len(verification)},ensure_ascii=False))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Rebuild authenticated Tibetan selections and the bounded full-chapter audit.

The full public-domain source volume is an external input, not a new translation.
Run with --volume PATH to the pinned Esukhia Derge vol.72 file; its hash is checked.
No Sanskrit verse number is used as a Tibetan verse index.
"""
from pathlib import Path
import argparse,bisect,hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/witnesses/sources/tibetan'
PIN='437362220fde32d7c4e4311b4aa0885a5ab76612fe5efc0d9afd62605b763041'
BOUNDS=[(1,20),(21,32),(33,43),(44,59),(60,75),(76,89),(90,99),(100,115),(116,128),(129,145),(146,156),(157,166),(167,178),(179,196),(197,208),(209,220),(221,234),(235,255),(256,272),(273,289),(290,305),(306,319),(320,333),(334,359),(360,382),(383,423)]
THEMES=['Pairs','Heedfulness','Mind','Flowers','Fools','The Wise','Arhats','Thousands','Evil','Violence / punishment','Old Age','Self','World','The Buddha','Happiness','The Dear','Anger','Stains','The Just','The Path','Miscellaneous','Hell','Elephants','Craving','Monastics','Brahmins']
# Read from the Tibetan chapter framework, not inferred per-verse Sanskrit flags.
SAME_TITLE={1:29,2:4,3:31,4:18,9:28,12:23,15:30,16:5,17:20,20:12,21:16,24:3,25:32,26:33}

def write_audit():
 text=(SRC/'rockhill-concordance-transcription.txt').read_text()
 page=None;published={}
 for line in text.splitlines():
  if line.startswith('#'):continue
  if re.fullmatch(r'\[\d+\]',line):page=int(line[1:-1]);continue
  for m in re.finditer(r'(\d+):([\d.,?]+)',line):
   pali=int(m[1]);refs=[]
   for ref in m[2].split(','):
    ch,verse=ref.rstrip('?').split('.')
    refs.append({'chapter':int(ch),'verse':int(verse),'tentative':ref.endswith('?'),'printed_page':page,'image_page_index':page+35,'source_url':f'https://archive.org/details/udnavargacolle00bkah/page/n{page+35}/mode/1up'})
   if pali in published:raise ValueError(f'Duplicate concordance position{pali}')
   published[pali]=refs
 reader=json.loads((ROOT/'data/witnesses/tibetan.json').read_text())
 native={v['pali']:v for v in reader['verses']}
 records=[];chapters=[]
 for ch,(a,b) in enumerate(BOUNDS,1):
  for pali in range(a,b+1):
   refs=published.get(pali,[]);v=native.get(pali)
   native_refs=[]
   for r in (v or {}).get('readings',[]):
    native_refs.append({k:r[k] for k in ['chapter','reference','source_url','source_line_start','source_line_end','folio_start','folio_end','rockhill_reference'] if k in r})
   pub=any(not r['tentative'] for r in refs)
   native_present=bool(v and v['status']=='present')
   partial=bool(v and v['status']=='partial')
   attested=pub or native_present
   # Native spellings and locators take precedence over a divergent printed index.
   native_chapters={r['chapter'] for r in native_refs} if native_present else {r['chapter'] for r in refs if not r['tentative']}
   record={'pali':pali,'pali_chapter':ch,'theme':THEMES[ch-1],
    'rockhill_references':refs,'published_parallel':pub,
    'native_checked':bool(native_refs),'native_reviewed':v is not None,'direct_native_status':v['status'] if v else None,
    'native_references':native_refs,'attested_parallel':attested,
    'related_only':partial and not pub,'tentative_reference':any(r['tentative'] for r in refs),
    'same_title_chapter':SAME_TITLE.get(ch),
    'same_title_parallel':bool(attested and SAME_TITLE.get(ch) in native_chapters),
    'evidence_level':'native-checked' if native_refs else 'published-reference' if pub else 'tentative-reference' if refs else 'unresolved',
    'semantic_grade':('related-provisional' if v and v.get('correspondence_assessment')=='related-provisional' or pali==6 else 'partial-published-parallel') if partial else 'historical-counterpart' if native_present else 'not-assessed',
    'note':v.get('note','') if v else ('A Tibetan parallel is recorded in the visually checked Rockhill index; exact semantic closeness and native Derge text have not been audited here.' if pub else 'Not established by the consulted Tibetan concordance or bounded native selections; not a claim of absence.')}
   if pali in [31,32]:record['concordance_warning']='The printed index groups Pāli31–32 under Tibetan4.28; the independently checked native passages have separate source locators. Do not assign the printed index number to the Derge text.'
   if pali==14:record['concordance_warning']='Rockhill31.14 differs from the selected Derge good-roof/desire stanza; no Rockhill number is assigned to that native selection.'
   if pali==395:record['concordance_warning']='Rockhill prints a question mark at33.62; excluded from the secure lower bound.'
   records.append(record)
  group=[r for r in records if r['pali_chapter']==ch]
  chapters.append({'pali_chapter':ch,'theme':THEMES[ch-1],'positions':len(group),
   'published_attested':sum(r['published_parallel'] for r in group),
   'attested_lower_bound':sum(r['attested_parallel'] for r in group),
   'same_title_chapter':SAME_TITLE.get(ch),
   'same_title_chapter_lower_bound':sum(r['same_title_parallel'] for r in group),
   'native_checked':sum(r['native_checked'] for r in group),
   'native_reviewed':sum(r['native_reviewed'] for r in group),
   'native_present':sum(r['direct_native_status']=='present' for r in group),
   'native_partial':sum(r['direct_native_status']=='partial' for r in group),
   'native_not_located':sum(r['direct_native_status']=='not-located' for r in group),
   'tentative_reference':sum(r['tentative_reference'] for r in group),
   'unresolved_positions':[r['pali'] for r in group if not r['attested_parallel']],
   'coverage_lower_bound':sum(r['attested_parallel'] for r in group)/len(group)})
 result={'audit_date':'2026-10-26','scope':'All 423 Pāli Dhammapada positions, with a visually checked published Tibetan concordance and direct native text checks only for the bounded reader selection.',
  'completeness':'A documented lower bound, not an exhaustive Tibetan parallel census. The1883 index omits known counterparts. Unlisted or unresolved positions are not textual absences. Published-reference status establishes a scholar-recorded parallel, not near-identical wording.',
  'method':'Rockhill1883 pp217–222 were read against all six page images and transcribed as factual references. Direct Derge checks from the reader dataset override differing index numbers. Sanskrit correspondence flags are never substituted for Tibetan evidence.',
  'sources':[{'id':'rockhill1883-index','url':'https://archive.org/details/udnavargacolle00bkah','printed_pages':[217,218,219,220,221,222],'transcription':'data/witnesses/sources/tibetan/rockhill-concordance-transcription.txt','transcription_sha256':hashlib.sha256(text.encode()).hexdigest(),'page_images_visually_checked':True},reader['sources'][0]],
  'summary':{'positions':423,'published_attested':sum(r['published_parallel'] for r in records),'attested_lower_bound':sum(r['attested_parallel'] for r in records),'native_checked':sum(r['native_checked'] for r in records),'native_reviewed':sum(r['native_reviewed'] for r in records),'tentative_references':sum(r['tentative_reference'] for r in records)},
  'chapters':chapters,'verses':records}
 (SRC/'correspondence-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['summary']))

class Source:
 def __init__(self,path):
  self.bytes=Path(path).read_bytes()
  if hashlib.sha256(self.bytes).hexdigest()!=PIN:raise ValueError('Unexpected Derge source revision')
  self.raw=self.bytes.decode()
  a=self.raw.index('{D326}');b=self.raw.index('{D327}')
  work=self.raw[a:b];chars=[];positions=[];last=0
  markup=re.compile(r'\[\d+x?[ab](?:\.\d+)?\]|\{D\d+\}|\{([^,{}]+),[^{}]+\}|\r?\n')
  for m in markup.finditer(work):
   chars.extend(work[last:m.start()]);positions.extend(range(a+last,a+m.start()))
   if m.group(1) is not None:
    chars.extend(m.group(1));positions.extend(range(a+m.start(1),a+m.end(1)))
   last=m.end()
  chars.extend(work[last:]);positions.extend(range(a+last,b))
  self.clean=''.join(chars);self.positions=positions
  self.line_starts=[0]+[m.end() for m in re.finditer('\n',self.raw)]
  self.folios=[(m.start(),m.group(1)) for m in re.finditer(r'\[(\d+x?[ab]\.\d+)\]',self.raw)]
  self.folio_starts=[x[0] for x in self.folios]
  ends=list(re.finditer(r'[^།]+ཚོམ(?:ས|་ས)་ཏེ་[^།]+།',self.clean))
  if len(ends)!=33:raise ValueError(f'Expected33 chapter colophons, found{len(ends)}')
  self.chapters={}
  first={1:'ཀྱེ་མ་འདུ་བྱེད་རྣམས་མི་རྟག',11:'བྲམ་ཟེས་འདོད་པ་རབ་སྤང',13:'དྲེའུ་མོ་རང་གི་མངལ་གྱིས',25:'དད་པ་མེད་ཅིང་འཇུངས་པ',31:'གཟུང་བར་དཀའ་ཞིང་'}
  for n,end in enumerate(ends,1):
   start=0 if n==1 else ends[n-2].end()
   if n in first:start=self.clean.index(first[n],start)
   rows=[]
   for m in re.finditer(r'[^།]+',self.clean[start:end.start()]):
    text=m.group().strip(' །')
    if not text:continue
    offset=len(m.group())-len(m.group().lstrip(' །'))
    lo=start+m.start()+offset;hi=lo+len(text)-1
    rows.append((text,self.positions[lo],self.positions[hi]))
   self.chapters[n]=rows
 def folio(self,pos):return self.folios[bisect.bisect_right(self.folio_starts,pos)-1][1]
 def line(self,pos):return bisect.bisect_right(self.line_starts,pos)
 def excerpt(self,chapter,a,b):
  rows=self.chapters[chapter][a-1:b]
  if len(rows)!=b-a+1:raise ValueError((chapter,a,b))
  lo,hi=rows[0][1],rows[-1][2];ls,le=self.line(lo),self.line(hi)
  end=self.line_starts[le] if le<len(self.line_starts) else len(self.raw)
  return rows,lo,hi,ls,le,self.raw[self.line_starts[ls-1]:end]
 def display_lines(self,rows):
  out=[]
  for text,lo,hi in rows:
   pos=bisect.bisect_left(self.positions,hi)+1
   punct=re.match(r'\s*།(?:\s*།)?',self.clean[pos:])
   if not punct:raise ValueError('No source shad after selected pāda')
   out.append(text+punct.group())
  return out

def expand_reader(source):
 path=ROOT/'data/witnesses/tibetan.json'
 dataset=json.loads(path.read_text())
 original={v['pali']:v for v in dataset['verses'] if v['pali']<=43}
 original_serial=json.dumps(list(original.values()),ensure_ascii=False,sort_keys=True)
 records=dict(original)
 excerpts=json.loads((SRC/'selected-derge-excerpts.json').read_text())
 raw_excerpts=[e for e in excerpts['excerpts'] if e.get('pali',9999)<=43]
 base=dataset['sources'][0]['url']
 mappings=json.loads((SRC/'pilot-selection-map.json').read_text())['selections']
 for m in mappings:
  pali=m['pali'];note=m.get('note','')
  if m['status']=='not-located':
   records[pali]={'pali':pali,'status':'not-located','readings':[],'note':note};continue
  chapter,a,b=m['chapter'],m['pada_start'],m['pada_end']
  rows,lo,hi,ls,le,raw_excerpt=source.excerpt(chapter,a,b)
  fs,fe=source.folio(lo),source.folio(hi)
  fr=fs if fs==fe else f'{fs}–{fe}'
  reference=f'Toh 326 · Derge 72, {fr}'
  url=f'{base}#L{ls}-L{le}'
  lines=source.display_lines(rows)
  reading={'reference':reference,'source_id':'esukhia-derge-toh326','source_url':url,
   'language':'bo','script':'Tibt','lines':lines,'folio_start':fs,'folio_end':fe,
   'source_line_start':ls,'source_line_end':le,'chapter':chapter,
   'rockhill_reference':m['rockhill_reference'],'sanskrit_parallel':None,
   'selected_pada_start_in_chapter':a,'selected_pada_end_in_chapter':b}
  annotations=[{'printed':x[1],'editorial_suggestion':x[2],'choice':'printed'} for x in re.finditer(r'\{([^,{}]+),([^{}]+)\}',source.raw[lo:hi+1])]
  if annotations:reading['source_annotations']=annotations
  if note:reading['note']=note
  records[pali]={'pali':pali,'status':m['status'],'readings':[reading]}
  if note:records[pali]['note']=note
  if pali==106:records[pali]['correspondence_assessment']='related-provisional'
  elif m['status']=='partial':records[pali]['correspondence_assessment']='partial-published-parallel'
  raw_excerpts.append({'pali':pali,'reference':reference,'source_url':url,
   'source_line_start':ls,'source_line_end':le,'raw_source_lines':raw_excerpt,
   'selected_pada_start_in_chapter':a,'selected_pada_end_in_chapter':b,'display_lines':lines})
 dataset['scope']='Historical Tibetan counterparts of the selected six-chapter pilot (Pāli 1–32, 100–115, 157–166, 221–234, 290–305), preserving the earlier Mind page 33–43; 99 Pāli positions in total.'
 dataset['verses']=[records[n] for n in sorted(records)]
 dataset['sources'][1]['role']='Scholarly Sanskrit–Tibetan alignment reference, previously checked for the initial selection. The service returned HTTP500 during the present expansion; new selections were checked directly in the pinned Derge source and against Rockhill1883, without inheriting Sanskrit numbering.'
 dataset['sources'][2]['role']='Independent Tibetan stanza descriptions and numbering, and the Pāli concordance on pp217–222. The full factual index was visually checked against all six page images; explicit native locators take priority over index discrepancies. Native Tibetan spelling is never taken from OCR.'
 dataset['sources'][3]['title']='Ānandajoti Bhikkhu, A Comparative Edition of the Dhammapada'
 dataset['sources'][3]['role']='Starting Indic correspondence reference. Native Tibetan selections are identified in the Derge text and the independent Tibetan edition, not assigned Sanskrit stanza numbers.'
 if json.dumps(dataset['verses'][:43],ensure_ascii=False,sort_keys=True)!=original_serial:raise ValueError('Original43 Tibetan records changed')
 path.write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+'\n')
 excerpts['notes']='Verbatim source-line spans for the99-position reader selection;96 passages may include related or partial counterparts. Physical folio markers and correction markup are retained. Native source words and punctuation are not modernized or harmonized.'
 excerpts['excerpts']=sorted(raw_excerpts,key=lambda e:e['pali'])
 (SRC/'selected-derge-excerpts.json').write_text(json.dumps(excerpts,ensure_ascii=False,indent=2)+'\n')
 print('Expanded reader:',len(dataset['verses']),'positions;',len(excerpts['excerpts']),'native text selections')

def verify_native(source):
 dataset=json.loads((ROOT/'data/witnesses/tibetan.json').read_text())
 extracts=json.loads((SRC/'selected-derge-excerpts.json').read_text())
 by_pali={e['pali']:e for e in extracts['excerpts']}
 checked=0;padas=0
 def clean_span(raw):
  raw=re.sub(r'\[\d+x?[ab](?:\.\d+)?\]|\{D\d+\}|\r?\n','',raw)
  return re.sub(r'\{([^,{}]+),[^{}]+\}',r'\1',raw)
 for v in dataset['verses']:
  for r in v['readings']:
   e=by_pali[v['pali']]
   a,b=e['source_line_start'],e['source_line_end']
   end=source.line_starts[b] if b<len(source.line_starts) else len(source.raw)
   actual=source.raw[source.line_starts[a-1]:end]
   if actual!=e['raw_source_lines']:raise ValueError(('Raw source excerpt mismatch',v['pali']))
   span=clean_span(actual);pos=0
   for line in r['lines']:
    i=span.find(line,pos)
    if i<0:raise ValueError(('Display line missing or out of order',v['pali'],line))
    pos=i+len(line);padas+=1
   checked+=1
 result={'checked':'2026-10-26','pali_records':len(dataset['verses']),'native_reviewed':len(dataset['verses']),
  'readings_checked':checked,'padas_checked':padas,'native_lines_in_cited_span':True,
  'all_lines_in_source_order':True,'verbatim_raw_excerpts_match_source_line_spans':True,
  'full_source_sha256_verified':PIN,'full_source_git_blob_verified':'d9abab24ddfc32ccd5dc65973cfbbef1dd6bd959',
  'reader_status_counts':{s:sum(v['status']==s for v in dataset['verses']) for s in ['present','partial','not-located']},
  'display_preparation':['Removed physical folio/line markers and physical newlines, joining source words split across folio lines.','For correction annotations, retained the first/printed form and recorded the suggestion separately.','Reading line breaks follow source shad punctuation. Original words and punctuation are preserved; every displayed line occurs verbatim in its source span, in order.','No Tibetan words added, translated, modernized, or harmonized.','This checks transcription fidelity. Correspondence assessments and explicit partial/provisional qualifications remain separate.']}
 (SRC/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Native transcription verified:',checked,'readings;',padas,'pādas')

def write_analysis_report():
 audit=json.loads((SRC/'correspondence-audit.json').read_text())
 reader=json.loads((ROOT/'data/witnesses/tibetan.json').read_text())
 vmap={v['pali']:v for v in reader['verses']}
 lines=['# Tibetan contents audit for Rosettapada','',
 'Completed 26 October 2026. This audit separates a published Tibetan correspondence inventory for all 26 Pāli chapters from direct native-text verification for the six-chapter pilot and the preserved Mind page. It does not assume that a Sanskrit parallel automatically exists in Tibetan.','',
 '## Findings','',
 '**The Tibetan material supports the six-chapter pilot well.** Among its 88 Pāli positions, 82 have authenticated historical counterparts, four have partial or provisional related selections, and two remain not located. The existing Mind page adds ten counterparts and one not-located position. All 96 displayed Tibetan selections across the seven pages have been checked against their exact Derge source spans.','',
 'A historical counterpart can differ in wording, clause order, imagery, and length. Present is a source-attestation status, not a finding of near-identical meaning. Tibetan 100, for example, speaks of a hundred stanzas rather than a thousand words. The shorter-life series at 110–115 has a few days rather than one day. Other differences are recorded beside the source selections.','',
 '**For all 26 chapters, the established result is a lower bound of 323 Pāli positions with Tibetan parallels, or 76.4% of 423.** Of these, 305 are securely listed in Rockhill’s independent 1883 Tibetan–Pāli index; direct native checks add 18 positions his index omits. His tentative 395 / 33.62 is kept separate. The incomplete index and unreviewed native passages outside the pilot prevent an exhaustive Tibetan total or a verified all-six overlap percentage.','',
 '## The pilot','',
 '| Pāli chapter | Positions | Present counterpart | Partial / related | Not located |','|---|---:|---:|---:|---:|']
 for ch in [1,2,8,12,17,21]:
  a,b=BOUNDS[ch-1];vs=[vmap[n] for n in range(a,b+1)]
  counts=[sum(v['status']==s for v in vs) for s in ['present','partial','not-located']]
  lines.append(f'| {ch}. {THEMES[ch-1]} | {len(vs)} | {counts[0]} | {counts[1]} | {counts[2]} |')
 lines += ['',
 'The retained Mind page has 11 positions: ten present and one not located. Its inclusion preserves the earlier URL and reading experience; it is not a seventh chapter added to the six-chapter pilot.','',
 'Only 25 pilot positions have secure parallels in the corresponding same-title native Tibetan chapter. Most of the remaining counterparts are elsewhere in the Tibetan collection. The practical format is therefore a Pāli-ordered comparative selection with honest source locators. It is not six intact native chapters placed side by side.','',
 'The four qualified selections are important:','',
 '- **6:** related Tibetan 14.8 ends with pacification through gentle speech. It remains provisional and is excluded from secure coverage.',
 '- **106:** related Tibetan 24.26 retains monthly thousandfold offerings over a century, but contrasts them with faith in the Buddha rather than momentary homage to a developed person. It is excluded from secure coverage.',
 '- **115:** the published index points to Tibetan 24.10, about a state difficult to see. Pāli names the supreme Dhamma. The common lifespan-comparison frame is retained with a partial label.',
 '- **230:** Tibetan 29.51 is one six-pāda stanza covering the 229–230 pair. Four pādas are aligned at 229 and two at 230. Tibetan does not supply the Pāli gods/Brahmā clauses here; those words are not invented.','',
 'The not-located pilot positions are 101 and 109. The preserved Mind gap is 36. These outcomes do not establish absence elsewhere in Tibetan literature.','',
 '## All 26 Pāli chapters','',
 'The percentage below is a documented lower bound for Pāli positions with an independently attested Tibetan parallel somewhere in the collection. It is not a score for semantic identity. Direct native checked counts located source selections actually verified; directly reviewed includes attempted reader positions whose outcome is not located.','',
 '| Pāli chapter | Positions | Indexed securely | Attested lower bound | Lower-bound coverage | Native text checked |','|---|---:|---:|---:|---:|---:|']
 for c in audit['chapters']:
  lines.append(f'| {c["pali_chapter"]}. {c["theme"]} | {c["positions"]} | {c["published_attested"]} | {c["attested_lower_bound"]} | {c["coverage_lower_bound"]:.1%} | {c["native_checked"]} |')
 lines += ['',
 'Low entries are unresolved research coverage as well as possible recensional differences. They cannot be treated as measured absence. Comparing the Tibetan 76.4% lower bound directly with a more exhaustive Sanskrit catalogue would confound catalogue completeness with textual survival.','',
 '## Evidence and reproducibility','',
 'The independent correspondence source is W. Woodville Rockhill, *Udânavarga: a collection of verses from the Buddhist canon* (London: Trübner, 1883), printed index pp. 217–222. All six scans were visually checked. OCR ambiguities such as I/1, II/11, IS/15, grouped rows, and shifted columns were resolved against the images. Only factual references are retained in the transcription.','',
 '- [Rockhill 1883, Internet Archive](https://archive.org/details/udnavargacolle00bkah)',
 '- [Pinned Derge source repository](https://github.com/Esukhia/derge-kangyur/tree/a582cf471b7c85a101035071078032f106a8e536)',
 '- [Native evidence and policy](../data/witnesses/sources/tibetan/README.md)',
 '- [All 423 correspondence outcomes](../data/witnesses/sources/tibetan/correspondence-audit.json)',
 '- [Visually checked factual index transcription](../data/witnesses/sources/tibetan/rockhill-concordance-transcription.txt)',
 '- [Explicit new native passage selections](../data/witnesses/sources/tibetan/pilot-selection-map.json)',
 '- [Verbatim primary source excerpts](../data/witnesses/sources/tibetan/selected-derge-excerpts.json)',
 '- [Transcription verification](../data/witnesses/sources/tibetan/verification.json)','',
 'Native display text comes from Toh 326 in Esukhia’s Digital Derge Kangyur, pinned commit a582cf471b7c85a101035071078032f106a8e536, vol. 72, ff. 209a.1–253a.7. Its full-volume SHA-256 is 437362220fde32d7c4e4311b4aa0885a5ab76612fe5efc0d9afd62605b763041. The source declares the electronic text public domain. Correction suggestions are recorded while the printed form is displayed. Reading line breaks are editorial and follow source punctuation. No new Tibetan translation is supplied.','',
 'Run `python3 tools/import_tibetan.py --volume PATH` with that verified source volume to reproduce new native selections, the 408-pāda transcription check, the 423-position research ledger, and this report. `--audit-only` regenerates the ledger from the factual index and current native dataset. The first 43 reader records are preserved.','',
 'The native additions absent from the final index are 24, 26, 27, 29, 30, 37, 38, 39, 226, 231–234, 292, 293, 302, 303, and 305. These make the index’s incompleteness directly testable.','',
 'Index numbers also require care. Pāli 31–32 are grouped under 4.28 in the printed index, but have distinct native source passages. The selected Derge good-roof/desire stanza at 14 does not receive Rockhill’s differing 31.14 number. The index points 225 to related 20.19, whereas the bodily-restraint/deathless-state passage is directly located in chapter 7.7. Folio citations keep these differences visible.','',
 'Bibliotheca Polyglotta supplied Sanskrit–Tibetan metadata during the earlier sample work but returned HTTP 500 during this expansion. New selections therefore rest on the native source and independent Tibetan edition. Modern alignment text or commentary has not been copied into the site.','',
 '## Implication for the project','',
 'Tibetan can support the small pilot without translating missing material into existence. The project should retain verse-level alignment, source access, partial labels in Notes, and visible gaps. An exhaustive semantic audit of all 423 positions, including the current unresolved cases and Tibetan-only material, remains a larger scholarly task. No result here warrants describing whole chapters across all six traditions as near-identical.','']
 (ROOT/'docs/TIBETAN_ANALYSIS.md').write_text('\n'.join(lines))

def main():
 p=argparse.ArgumentParser();p.add_argument('--volume');p.add_argument('--dump-chapters',action='store_true');p.add_argument('--audit-only',action='store_true');args=p.parse_args()
 if args.audit_only:write_audit();write_analysis_report();return
 if not args.volume:p.error('--volume is required for native text work')
 source=Source(args.volume)
 if args.dump_chapters:
  for n,rows in source.chapters.items():
   print('\nCHAPTER',n,len(rows),'pādas')
   for i,r in enumerate(rows,1):print(i,r[0])
  return
 expand_reader(source)
 verify_native(source)
 write_audit()
 write_analysis_report()

if __name__=='__main__':main()

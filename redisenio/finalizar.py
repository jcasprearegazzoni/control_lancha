from trabajo import *
import hashlib
out=Path('Velos_1_redisenio');out.mkdir(exist_ok=True)
original_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
b=p.LoadBoard('redisenio/ruteado.kicad_pcb');fs={f.GetReference():f for f in b.GetFootprints()}
for g in fs['A2'].GraphicalItems():
 if g.GetClass()=='PCB_SHAPE' and g.GetLayer()==p.F_SilkS and g.GetShape()==p.SHAPE_T_SEGMENT:g.SetLayer(p.Dwgs_User)
for ref,pos in {'J1':(122,67),'Q1':(148.27,94.3),'Q2':(132,72),'J4':(129.34,107.6),'J6':(196.8,81),'U1':(150.59,82.3)}.items():fs[ref].Reference().SetPosition(vec(pos))
for g in fs['D1'].GraphicalItems():
 if hasattr(g,'GetText') and g.GetText()=='K':g.SetPosition(vec((140.81,94.5)))
lib=out/'footprints.pretty';lib.mkdir(exist_ok=True)
for ref in ['A2','D1','Q1','Q2','Q3','Q4','Q5']:
 f=fs[ref];name='Arduino_Mega2560_Shield' if ref=='A2' else ('D_DO41_Local' if ref=='D1' else 'BC548_THT_'+ref)
 f.SetFPID(p.LIB_ID('Velos_Local',name))
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib.resolve()),p.Cast_to_FOOTPRINT(f.Duplicate(False)))
(out/'fp-lib-table').write_text('(fp_lib_table\n (version 7)\n (lib (name "Velos_Local") (type "KiCad") (uri "${KIPRJMOD}/footprints.pretty") (options "") (descr "Footprints preservados del proyecto Velos"))\n)\n')
target=out/'Velos_1_redisenio.kicad_pcb';p.SaveBoard(str(target),b)
target.with_suffix('.kicad_pro').write_bytes(SRC.with_suffix('.kicad_pro').read_bytes())
counts={}
for t in b.GetTracks():
 layer=b.GetLayerName(t.GetLayer());counts.setdefault(layer,{'segments':0,'mm':0});counts[layer]['segments']+=1;counts[layer]['mm']+=t.GetLength()/1e6
print('LAYERS',json.dumps(counts));print('VIAS',sum(t.GetClass()=='PCB_VIA' for t in b.GetTracks()))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==original_hash
(out/'verificacion.json').write_text(json.dumps({'source_sha256':original_hash,'routing':counts,'source':str(SRC),'vias':0},indent=2))
print('Saved',target)






from trabajo import *
import random
base=p.LoadBoard('redisenio/ruteado.kicad_pcb')
topnets={t.GetNetname() for t in base.GetTracks() if t.GetLayer()==p.F_Cu}
topnets.add('Net-(A2-D3_INT1)')
for t in list(base.GetTracks()):
 if t.GetLayer()==p.F_Cu:base.Delete(t)
p.SaveBoard('redisenio/base_bottom.kicad_pcb',base)
random.seed(21)
best_score=float('inf')
for attempt in range(80):
 b=p.LoadBoard('redisenio/base_bottom.kicad_pcb');fs={f.GetReference():f for f in b.GetFootprints()};jobs=[]
 for pad in fs['A2'].Pads():
  if pad.GetNetname() not in topnets:continue
  targets=[q for f in fs.values() if f.GetReference()!='A2' for q in f.Pads() if q.GetNetCode()==pad.GetNetCode()]
  target=min(targets,key=lambda q:math.dist(point(pad.GetPosition()),point(q.GetPosition())))
  jobs.append((pad,target))
 if attempt==0:jobs.sort(key=lambda pair:pair[0].GetPosition().x)
 elif attempt==1:jobs.sort(key=lambda pair:-pair[0].GetPosition().x)
 elif attempt==2:jobs.sort(key=lambda pair:-math.dist(point(pair[0].GetPosition()),point(pair[1].GetPosition())))
 else:random.shuffle(jobs)
 failed=[]
 for pad,target in jobs:
  if not route(b,point(pad.GetPosition()),point(target.GetPosition()),pad.GetNetCode(),p.F_Cu):failed.append(pad.GetNumber())
 if not failed:
  top=[t for t in b.GetTracks() if t.GetLayer()==p.F_Cu]
  length=sum(t.GetLength()/1e6 for t in top);score=length+.3*len(top)
  if score<best_score:
   best_score=score;p.SaveBoard('redisenio/ruteado.kicad_pcb',b);print('Improved TOP',attempt,round(length,2),'mm',len(top),'segments',flush=True)

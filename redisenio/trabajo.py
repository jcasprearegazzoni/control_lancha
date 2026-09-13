from pathlib import Path
import pcbnew as p
import numpy as np
from PIL import Image,ImageDraw
import heapq,math,json,subprocess,sys
ROOT=Path('redisenio');ROOT.mkdir(exist_ok=True)
SRC=Path('Velos_1/Velos_1.kicad_pcb')
GRID=.2; X0=107.;Y0=57.; NX=520;NY=285; WIDTH=.7;CLEAR=.2
def point(q):return q.x/1e6,q.y/1e6
def pixel(pt):return round((pt[0]-X0)/GRID),round((pt[1]-Y0)/GRID)
def mm(q):return X0+q[0]*GRID,Y0+q[1]*GRID
def vec(pt):return p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
def route(board,start,end,net,layer):
 im=Image.new('L',(NX,NY),255);d=ImageDraw.Draw(im)
 # The shield perimeter is used only within this separate design.
 seg=[]
 for g in board.GetDrawings():
  if g.GetLayer()==p.Edge_Cuts and g.GetClass()=='PCB_SHAPE':seg.append((point(g.GetStart()),point(g.GetEnd())))
 if seg:
  chain=[seg.pop(0)[0]]
  # Order the perimeter's connected vertices.
  unused=[(point(g.GetStart()),point(g.GetEnd())) for g in board.GetDrawings() if g.GetLayer()==p.Edge_Cuts and g.GetClass()=='PCB_SHAPE']
  while unused:
   found=False
   for i,(a,b) in enumerate(unused):
    if math.dist(a,chain[-1])<.01:chain.append(b);unused.pop(i);found=True;break
    if math.dist(b,chain[-1])<.01:chain.append(a);unused.pop(i);found=True;break
   if not found:break
  d.polygon([pixel(q) for q in chain],fill=0)
  d.line([pixel(q) for q in chain],fill=255,width=math.ceil((WIDTH+.6)/GRID))
 margin=WIDTH/2+CLEAR+GRID*.8
 for f in board.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetCode()==net and pad.GetAttribute()!=p.PAD_ATTRIB_NPTH:continue
   if not pad.IsOnLayer(layer) and pad.GetAttribute()!=p.PAD_ATTRIB_NPTH:continue
   box=pad.GetBoundingBox()
   a=(box.GetLeft()/1e6-margin,box.GetTop()/1e6-margin);z=(box.GetRight()/1e6+margin,box.GetBottom()/1e6+margin)
   d.rectangle([pixel(a),pixel(z)],fill=255)
 for t in board.GetTracks():
  if t.GetLayer()!=layer or t.GetNetCode()==net:continue
  thick=math.ceil((t.GetWidth()/1e6+WIDTH+2*CLEAR+GRID*2)/GRID)
  d.line([pixel(point(t.GetStart())),pixel(point(t.GetEnd()))],fill=255,width=thick)
  for pt in (point(t.GetStart()),point(t.GetEnd())):
   x,y=pixel(pt);r=thick/2;d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 blocked=np.asarray(im)>0;s=pixel(start);goal=pixel(end)
 if blocked[s[1],s[0]] or blocked[goal[1],goal[0]]:
  print('BLOCKED ENDPOINT',start,end,bool(blocked[s[1],s[0]]),bool(blocked[goal[1],goal[0]]));return False
 directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
 heap=[(0,0,s)];dist={s:0};prev={}
 while heap:
  _,cost,q=heapq.heappop(heap)
  if cost>dist[q]+1e-8:continue
  if q==goal:break
  for dx,dy in directions:
   n=q[0]+dx,q[1]+dy
   if not(0<=n[0]<NX and 0<=n[1]<NY) or blocked[n[1],n[0]]:continue
   if dx and dy and (blocked[q[1],n[0]] or blocked[n[1],q[0]]):continue
   value=cost+(1.41421356 if dx and dy else 1)
   if value+1e-8<dist.get(n,1e100):
    dist[n]=value;prev[n]=q;hx=abs(n[0]-goal[0]);hy=abs(n[1]-goal[1]);heuristic=max(hx,hy)+.41421356*min(hx,hy)
    heapq.heappush(heap,(value+heuristic,value,n))
 else:return False
 path=[goal]
 while path[-1]!=s:path.append(prev[path[-1]])
 path.reverse();clean=[path[0]]
 for i in range(1,len(path)-1):
  if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):clean.append(path[i])
 clean.append(path[-1]);coords=[start]+[mm(q) for q in clean]+[end]
 for a,z in zip(coords,coords[1:]):
  if math.dist(a,z)<1e-5:continue
  t=p.PCB_TRACK(board);t.SetStart(vec(a));t.SetEnd(vec(z));t.SetWidth(p.FromMM(WIDTH));t.SetLayer(layer);t.SetNetCode(net);board.Add(t)
 return True
def prepare():
 b=p.LoadBoard(str(SRC));fs={f.GetReference():f for f in b.GetFootprints()}
 for t in list(b.GetTracks()):b.Delete(t)
 for q,r,y in [('Q5','R10',77.3),('Q4','R8',87.3),('Q3','R9',97.3)]:
  fs[q].SetOrientationDegrees(-90);fs[q].SetPosition(vec((188.5,y)))
  fs[r].SetOrientationDegrees(0);fs[r].SetPosition(vec((179,y+1.27)))
 for ref,(x,y,a) in {'Q1':(147,91,0),'R1':(159,91,90),'C4':(149,97,180),'Q2':(128.33,70.3,180)}.items():
  fs[ref].SetOrientationDegrees(a);fs[ref].SetPosition(vec((x,y)))
 for f in fs.values():
  if f.GetReference()=='A2':continue
  box=f.GetBoundingBox(False,False);f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetTextSize(vec((.9,.9)));f.Reference().SetPosition(p.VECTOR2I(box.GetCenter().x,box.GetTop()-p.FromMM(1)));f.Value().SetVisible(False)
 for g in fs['A2'].GraphicalItems():
  if g.GetClass()=='PCB_SHAPE' and g.GetLayer()==p.F_SilkS and g.GetShape()==p.SHAPE_T_SEGMENT:
   s=p.PCB_SHAPE(b);s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(g.GetStart());s.SetEnd(g.GetEnd());s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
 jobs=[]
 for pad in fs['A2'].Pads():
  net=pad.GetNetname()
  if not net or net in ['+5V'] or net.startswith('unconnected'):continue
  targets=[q for f in fs.values() if f.GetReference()!='A2' for q in f.Pads() if q.GetNetCode()==pad.GetNetCode()]
  if not targets:continue
  target=min(targets,key=lambda q:math.dist(point(pad.GetPosition()),point(q.GetPosition())))
  jobs.append((pad,target))
 jobs.sort(key=lambda pair:math.dist(point(pair[0].GetPosition()),point(pair[1].GetPosition())))
 for pad,target in jobs:
  ok=route(b,point(pad.GetPosition()),point(target.GetPosition()),pad.GetNetCode(),p.F_Cu)
  print('TOP',pad.GetNumber(),target.GetParentFootprint().GetReference(),ok,flush=True)
 p.SaveBoard(str(ROOT/'inicio.kicad_pcb'),b)
 (ROOT/'inicio.kicad_pro').write_bytes(SRC.with_suffix('.kicad_pro').read_bytes())
 assert p.ExportSpecctraDSN(b,str(ROOT/'inicio.dsn'))
def bottom():
 java=r'C:\Program Files\Eclipse Adoptium\jdk-25.0.4.101-hotspot\bin\java.exe'
 jar=r'C:\Users\juanc\OneDrive\Documentos\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin\jar\freerouting-2.4.1.jar'
 cmd=[java,'-jar',jar,'-de',str((ROOT/'inicio.dsn').resolve()),'-do',str((ROOT/'bottom.ses').resolve()),'--gui.enabled=false','--api_server.enabled=false','--mcp_server.enabled=false','--router.layers.routable=false,true','-mp','40','-mt','1','-da','--user_data_path='+str((ROOT/'config').resolve())]
 with (ROOT/'routing.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=240)
 b=p.LoadBoard(str(ROOT/'inicio.kicad_pcb'));assert p.ImportSpecctraSES(b,str(ROOT/'bottom.ses'));p.SaveBoard(str(ROOT/'ruteado.kicad_pcb'),b)
 (ROOT/'ruteado.kicad_pro').write_bytes(SRC.with_suffix('.kicad_pro').read_bytes())
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:bottom()





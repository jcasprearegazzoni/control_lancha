from trabajo import *
from PIL import ImageFont
b=p.LoadBoard('Velos_1_redisenio/Velos_1_redisenio.kicad_pcb')
S=18;im=Image.new('RGB',(1880,1100),'#111f2e');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def xy(q):return ((q.x/1e6-106)*S,(q.y/1e6-55)*S+40)
for layer,color in [(p.B_Cu,'#4d83bd'),(p.F_Cu,'#dd756e')]:
 for t in b.GetTracks():
  if t.GetLayer()==layer:
   a,z=xy(t.GetStart()),xy(t.GetEnd());w=max(1,round(t.GetWidth()/1e6*S));d.line([a,z],fill=color,width=w)
   for x,y in [a,z]:d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=color)
for g in b.GetDrawings():
 if g.GetClass()=='PCB_SHAPE' and g.GetLayer()==p.Edge_Cuts:d.line([xy(g.GetStart()),xy(g.GetEnd())],fill='#e8e1a7',width=2)
for f in b.GetFootprints():
 for g in f.GraphicalItems():
  if g.GetClass()!='PCB_SHAPE' or g.GetLayer() not in [p.F_SilkS,p.F_Fab]:continue
  shape=g.GetShape()
  if shape==p.SHAPE_T_SEGMENT:d.line([xy(g.GetStart()),xy(g.GetEnd())],fill='#b2b89c',width=1)
  elif shape==p.SHAPE_T_RECT:
   a,z=xy(g.GetStart()),xy(g.GetEnd());d.rectangle((min(a[0],z[0]),min(a[1],z[1]),max(a[0],z[0]),max(a[1],z[1])),outline='#b2b89c')
  elif shape==p.SHAPE_T_CIRCLE:
   x,y=xy(g.GetCenter());r=g.GetRadius()/1e6*S;d.ellipse((x-r,y-r,x+r,y+r),outline='#b2b89c')
 for pad in f.Pads():
  box=pad.GetBoundingBox();a=xy(p.VECTOR2I(box.GetLeft(),box.GetTop()));z=xy(p.VECTOR2I(box.GetRight(),box.GetBottom()))
  d.ellipse((*a,*z),fill='#8dbcb6')
  x,y=xy(pad.GetPosition());r=pad.GetDrillSize().x/1e6*S/2;d.ellipse((x-r,y-r,x+r,y+r),fill='#111f2e')
 if f.GetReference()!='A2':d.text(xy(f.Reference().GetPosition()),f.GetReference(),font=font,fill='white',anchor='mm')
d.text((35,14),'VELOS 1 | Vista desde arriba | B.Cu azul - F.Cu rojo | 0 conexiones pendientes - 0 vias',font=font,fill='white')
im.save('Velos_1_redisenio/vista_ruteo.png')

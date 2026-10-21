from create_native_drawings import call

def main():
    call('blender_rigging__create_armature',{'name':'Girl_Walk_Rig'})
    bones=[
      ('ROOT',(0,0,0),(0,.1,0),None),
      ('body',(0,.68,0),(0,1.085,0),'ROOT'),
      ('head',(0,1.09,0),(0,1.39,0),'body'),
      ('braid',(-.113,1.265,0),(-.113,1.035,0),'head'),
    ]
    for side,armx in [('far',-.015),('near',.015)]:
        bones += [('thigh_'+side,(0,.68,0),(0,.36,0),'body'),
                  ('shin_'+side,(0,.36,0),(0,.04,0),'thigh_'+side),
                  ('shoe_'+side,(0,.09,0),(.15,.09,0),'shin_'+side),
                  ('upper_arm_'+side,(armx,1.045,0),(armx,.815,0),'body'),
                  ('forearm_'+side,(armx,.815,0),(armx,.575,0),'upper_arm_'+side)]
    for name,head,tail,parent in bones:
        payload={'armature_name':'Girl_Walk_Rig','bone_name':name,'head':list(head),'tail':list(tail)}
        if parent: payload['parent']=parent
        call('blender_rigging__create_bone',payload)
    print('Created',len(bones),'authored motion bones')

if __name__=='__main__':main()

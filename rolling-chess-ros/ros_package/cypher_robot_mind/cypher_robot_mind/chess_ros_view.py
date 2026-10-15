"""Actual RViz MarkerArray geometry for the rolling chess apparatus."""
import math
from geometry_msgs.msg import Point, TransformStamped
from visualization_msgs.msg import Marker, MarkerArray


def publish_scene(node,state,publisher,broadcaster):
    stamp=node.get_clock().now().to_msg()
    transform=TransformStamped();transform.header.frame_id='map';transform.header.stamp=stamp
    transform.child_frame_id='chess_board';transform.transform.translation.z=.25
    pitch,roll=math.radians(state['pitch'])/2,math.radians(state['roll'])/2
    transform.transform.rotation.x=-math.sin(pitch)*math.cos(roll)
    transform.transform.rotation.y=math.cos(pitch)*math.sin(roll)
    transform.transform.rotation.z=-math.sin(pitch)*math.sin(roll)
    transform.transform.rotation.w=math.cos(pitch)*math.cos(roll)
    broadcaster.sendTransform(transform)
    markers=[];clear=Marker();clear.action=Marker.DELETEALL;markers.append(clear)
    def add(namespace,kind,position,scale,color):
        m=Marker();m.header.frame_id='chess_board';m.header.stamp=stamp;m.ns=namespace;m.id=len(markers)
        m.type=kind;m.action=Marker.ADD;m.pose.orientation.w=1.
        m.pose.position.x=float(position[0]-.4);m.pose.position.y=float(position[1]-.4);m.pose.position.z=float(position[2])
        m.scale.x,m.scale.y,m.scale.z=map(float,scale)
        m.color.r,m.color.g,m.color.b,m.color.a=map(float,color)
        markers.append(m);return m
    add('wood',Marker.CUBE,[.4,.4,-.014],[.84,.84,.025],[.43,.30,.17,1])
    for y in range(8):
        for x in range(8):
            color=[.81,.68,.46,1] if (x+y)%2 else [.53,.37,.22,1]
            add('squares',Marker.CUBE,[(x+.5)*.1,(y+.5)*.1,0],[.1,.1,.002],color)
    for x,y,w,h in state['walls']:add('maze',Marker.CUBE,[x+w/2,y+h/2,.013],[w,h,.024],[.65,.46,.26,1])
    for hole in state['holes']:
        add('wells',Marker.CYLINDER,[*hole['position'],.002],[.068,.068,.003],[.03,.04,.04,1])
    for piece in state['pieces']:
        x,y=(piece['x']+.5)*.1,(piece['y']+.5)*.1
        color=[.93,.91,.80,1] if piece['symbol'].isupper() else [.12,.16,.19,1]
        kind=piece['symbol'].lower()
        add('pieces',Marker.CYLINDER,[x,y,.008],[.043,.043,.012],color)
        height=.026 if kind=='p' else .04
        add('pieces',Marker.CYLINDER,[x,y,.014+height/2],[.019,.019,height],color)
        if kind=='p':add('pawn',Marker.SPHERE,[x,y,.048],[.025,.025,.025],color)
        elif kind=='r':
            add('rook',Marker.CYLINDER,[x,y,.055],[.035,.035,.014],color)
            for dx,dy in [(-.013,-.013),(.013,-.013),(-.013,.013),(.013,.013)]:
                add('rook',Marker.CUBE,[x+dx,y+dy,.066],[.011,.011,.012],color)
        elif kind=='n':
            add('knight',Marker.CUBE,[x-.004,y,.057],[.021,.019,.034],color)
            add('knight',Marker.CUBE,[x+.009,y,.071],[.035,.021,.016],color)
            add('eye',Marker.SPHERE,[x+.012,y-.011,.075],[.004,.004,.004],[.65,.58,.36,1])
        elif kind=='b':
            add('bishop',Marker.SPHERE,[x,y,.064],[.026,.026,.037],color)
            slash=add('bishop_slit',Marker.CUBE,[x+.004,y-.012,.069],[.003,.003,.022],[.35,.32,.25,1])
            slash.pose.orientation.y=math.sin(.4);slash.pose.orientation.w=math.cos(.4)
        elif kind=='q':
            add('queen',Marker.CYLINDER,[x,y,.064],[.033,.033,.012],color)
            for i in range(5):
                a=i*2*math.pi/5;add('crown',Marker.SPHERE,[x+.014*math.cos(a),y+.014*math.sin(a),.077],[.009,.009,.012],color)
        elif kind=='k':
            add('king',Marker.SPHERE,[x,y,.061],[.026,.026,.025],color)
            add('cross',Marker.CUBE,[x,y,.084],[.007,.007,.03],color)
            add('cross',Marker.CUBE,[x,y,.087],[.025,.007,.007],color)
    for ball in ([state['ball']] if state['ball'] else [])+state['parked']:
        if ball['mode']=='well':continue
        color=[.91,.94,.95,1] if ball['color']=='white' else [.08,.1,.14,1]
        add('metal',Marker.SPHERE,[ball['x'],ball['y'],ball['z']],[.024,.024,.024],color)
    if state['path']:
        line=add('controller_path',Marker.LINE_STRIP,[.4,.4,.006],[.002,0,0],[.4,.9,.75,1])
        line.points=[Point(x=float(x-.4),y=float(y-.4),z=0.) for x,y in state['path']]
    publisher.publish(MarkerArray(markers=markers))

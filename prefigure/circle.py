import lxml.etree as ET
import math
import numpy as np
import user_namespace as un
import utilities as util
import arrow
import copy
import label

# Add graphical elements related to circles
def circle(element, diagram, parent, outline_status):
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    center = un.valid_eval(element.get('center'))
    radius = un.valid_eval(element.get('radius', '1'))
    right = [center[0] + radius, center[1]]
    top = [center[0], center[1] + radius]
    center, right, top = map(diagram.transform, [center, right, top])

    circle = ET.Element('ellipse')
    diagram.add_id(circle, element.get('id'))

    circle.set('cx', util.float2str(center[0]))
    circle.set('cy', util.float2str(center[1]))
    circle.set('rx', util.float2str(right[0]-center[0]))
    circle.set('ry', util.float2str(center[1] - top[1]))

    if diagram.output_format() == 'tactile':
        if element.get('stroke') is not None:
            element.set('stroke', 'black')
        if element.get('fill') is not None:
            element.set('fill', 'lightgray')
    else:
        element.set('stroke', element.get('stroke', 'none'))
        element.set('fill', element.get('fill', 'none'))
    element.set('thickness', element.get('thickness', '2'))
    util.add_attr(circle, util.get_2d_attr(element))
    circle.set('type', 'circle')
    util.cliptobbox(circle, element)

    if outline_status == 'add_outline':
        diagram.add_outline(element, circle, parent)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, circle, parent)
        finish_outline(element, diagram, parent)
    else:
        parent.append(circle)

def finish_outline(element, diagram, parent):
    add_label(element, diagram, parent)
    diagram.finish_outline(element,
                           element.get('stroke'),
                           element.get('thickness'),
                           element.get('fill'),
                           parent)    

def ellipse(element, diagram, parent, outline_status):
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    center = un.valid_eval(element.get('center'))
    a, b = un.valid_eval(element.get('axes', '(1,1)'))
    right = [center[0] + a, center[1]]
    top = [center[0], center[1] + b]
    center, right, top = map(diagram.transform, [center, right, top])

    circle = ET.Element('ellipse')
    diagram.add_id(circle, element.get('id'))
    circle.set('cx', util.float2str(center[0]))
    circle.set('cy', util.float2str(center[1]))
    circle.set('rx', util.float2str(right[0]-center[0]))
    circle.set('ry', util.float2str(center[1]-top[1]))

    if diagram.output_format() == 'tactile':
        if element.get('stroke') is not None:
            element.set('stroke', 'black')
        if element.get('fill') is not None:
            element.set('fill', 'lightgray')
    else:
        element.set('stroke', element.get('stroke', 'none'))
        element.set('fill', element.get('fill', 'none'))
    element.set('thickness', element.get('thickness', '2'))
    util.add_attr(circle, util.get_2d_attr(element))
    circle.set('type', 'ellipse')
    util.cliptobbox(circle, element)

    if outline_status == 'add_outline':
        diagram.add_outline(element, circle, parent)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, circle, parent)
        finish_outline(element, diagram, parent)
    else:
        parent.append(circle)

def arc(element, diagram, parent, outline_status):
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    if diagram.output_format() == 'tactile':
        if element.get('stroke') is not None:
            element.set('stroke', 'black')
        if element.get('fill') is not None:
            element.set('fill', 'lightgray')
    else:
        element.set('stroke', element.get('stroke', 'none'))
        element.set('fill', element.get('fill', 'none'))
    element.set('thickness', element.get('thickness','2'))

    if element.get('points', None) is not None:
        points = element.get('points')
        points = un.valid_eval(points)
        center = points[1]
        v = points[0] - points[1]
        u = points[2] - points[1]
        start = math.degrees(math.atan2(v[1], v[0]))
        stop = math.degrees(math.atan2(u[1], u[0]))
        if stop < start:
            stop += 360
        angular_range = (start, stop)
        element.set('degrees', 'yes')
    else:
        center = un.valid_eval(element.get('center'))
        angular_range = un.valid_eval(element.get('range'))
    radius = un.valid_eval(element.get('radius'))
    sector = element.get('sector', 'no') == 'yes'

    if element.get('degrees', 'yes') == 'yes':
        angular_range = [math.radians(a) for a in angular_range]
    start, stop = angular_range
    large_arc = '1' if abs(stop - start) >= math.pi else '0'
    sweep = '1' if stop - start < 0 else '0'

    initial_point = diagram.transform(center + np.array([radius * math.cos(start),
                                                         radius * math.sin(start)]))
    final_point = diagram.transform(center + np.array([radius * math.cos(stop),
                                                       radius * math.sin(stop)]))
    x_radius = abs((diagram.transform([center[0] + radius, center[1]]) -
                    diagram.transform(center))[0])

    y_radius = abs((diagram.transform([center[0], center[1] + radius]) -
                    diagram.transform(center))[1])

    initial_point_str = util.pt2str(initial_point)
    final_point_str = util.pt2str(final_point)
    center_str = util.pt2str(diagram.transform(center))

    if sector:
        d = 'M ' + center_str + ' L ' + initial_point_str
    else:
        d = 'M ' + initial_point_str
    d += ' A ' + util.pt2str((x_radius, y_radius)) + ' 0 '
    d += large_arc + ' ' + sweep + ' ' + final_point_str
    if sector:
        d += 'Z'

    arc = ET.Element('path')
    diagram.add_id(arc, element.get('id'))
    arc.set('d', d)
    util.add_attr(arc, util.get_2d_attr(element))
    arc.set('type', 'arc')
    util.cliptobbox(arc, element)

    if element.get('arrow', 'no') == 'yes':
        arrow.add_arrowhead_marker(diagram)
        arc.set('style', r'marker-end: url(#arrow-head-end)')

    if outline_status == 'add_outline':
        diagram.add_outline(element, arc, parent, outline_width=2)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, arc, parent, outline_width=4)
        finish_outline(element, diagram, parent)
    else:
        parent.append(arc)

# Alexei's angle marker
def angle(element, diagram, parent, outline_status):
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    element.set('stroke', element.get('stroke', 'black'))
    if diagram.output_format() == 'tactile':
        if element.get('fill') is not None:
            element.set('fill', 'lightgray')
    else:
        element.set('fill', element.get('fill', 'none'))
    element.set('thickness', element.get('thickness','2'))

    points = element.get('points', None)
    if points is None:
        p = un.valid_eval(element.get('p'))
        p1 = un.valid_eval(element.get('p1'))
        p2 = un.valid_eval(element.get('p2'))
    else:
        points = un.valid_eval(points)
        p = points[1]
        p1 = points[0]
        p2 = points[2]
    radius = un.valid_eval(element.get('radius','30'))

    # convert to svg coordinates

    p = diagram.transform(p)
    p1 = diagram.transform(p1)
    p2 = diagram.transform(p2)

    # Define vectors from p to p1 and p2, normalized
    v1 = (p1 - p)/np.linalg.norm(p1-p)
    v2 = (p2 - p)/np.linalg.norm(p2-p)

    # To determine the orientation, look at the z-component of cross product.
    # Keep in mind that y-axis in svg is directed down. large_arc_flag is 0 if the 
    # arc is supposed to be small

    large_arc_flag = int(v1[0]*v2[1] - v1[1]*v2[0] > 0)

    # It may make sense to have the default radius depend on the measure of the angle,
    # unless the user overrides it
    if large_arc_flag:
        angle = 2*np.pi - math.acos(np.dot(v1,v2))
    else:
        angle = math.acos(np.dot(v1,v2))

    # heuristically determined radius
    default_radius = int(30/angle)
    default_radius = min(30, default_radius)
    default_radius = max(15, default_radius)
    radius = un.valid_eval(element.get('radius', str(default_radius)))

    direction = (v1+v2)/np.linalg.norm(v1+v2)*(-1)**large_arc_flag
    label_location = p + direction*radius
    element.set('label-location', util.pt2str(label_location, spacer=','))
    if element.get('alignment', None) is None:
        element.set('alignment', 
                    label.get_alignment_from_direction([direction[0], -direction[1]]))
    initial_point = v1*radius + p
    final_point = v2*radius + p
    initial_point_str = util.pt2str(initial_point)
    final_point_str = util.pt2str(final_point)

    d = 'M ' + initial_point_str
    d += ' A ' + util.pt2str((radius, radius)) + ' 0 '
    d += str(large_arc_flag) + ' 0 ' + final_point_str

    arc = ET.Element('path')
    diagram.add_id(arc, element.get('id'))
    arc.set('d', d)

    if element.get('arrow', None) is not None:
        arrow.add_arrowhead_to_path(diagram, 'marker-end', arc)

    util.add_attr(arc, util.get_1d_attr(element))
    arc.set('type', 'arc')
    util.cliptobbox(arc, element)

    if outline_status == 'add_outline':
        diagram.add_outline(element, arc, parent, outline_width=2)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, arc, parent, outline_width=4)
        finish_outline(element, diagram, parent)
    else:
        parent = add_label(element, diagram, parent)
        parent.append(arc)        

def add_label(element, diagram, parent):
    # Is there a label associated with the marker?
    text = element.text
    if text is not None or len(element) > 0:
        # If there's a label, we'll bundle the label and the angle mark in a group
        group = ET.SubElement(parent, 'g')
        diagram.add_id(group, element.get('id'))
        group.set('type', 'labeled-angle-marker')

        # Now we'll create a new XML element describing the label
        el = copy.deepcopy(element)
        el.tag = 'label'
        el.set('alignment', element.get('alignment'))
        el.set('p', element.get('label-location'))
        el.set('user-coords', 'no')
        if element.get('offset', None) is not None:
            el.set('offset', element.get('offset'))

        # add the label graphical element to the group
        label.label(el, diagram, group)
        return group
    else:
        return parent


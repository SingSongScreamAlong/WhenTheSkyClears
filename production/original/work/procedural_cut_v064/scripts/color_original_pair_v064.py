"""Native original-UV color of the held pair; caller owns arc, saves and renders."""
import bpy
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UV_NAME = 'Registered original painted drawing'
PREFIX = 'V064 | '

# Source-space polygons, in original1672x941 pixels (top-left origin).
MASKS = {
 'boy_trousers': [
  [(573,535),(657,553),(628,623),(575,701),(557,755),(538,794),(470,770),(486,721),(536,638),(559,574)],
  [(634,537),(692,536),(728,599),(752,668),(768,741),(786,779),(686,805),(675,771),(653,717),(628,657),(600,607)]],
 'boy_coat': [[(609,241),(669,252),(704,290),(720,337),(746,383),(780,418),(804,450),
               (775,478),(741,471),(718,445),(739,540),(691,560),(537,548),(552,491),
               (535,477),(484,459),(509,400),(548,332),(579,280)]],
 'boy_hair': [[(528,35),(775,35),(775,239),(713,257),(678,277),(609,259),(535,241)]],
 'skin': [
  [(484,460),(549,486),(536,514),(528,560),(505,586),(459,578),(454,533),(475,503)],
  [(730,474),(786,454),(818,494),(835,504),(842,482),(854,458),(868,431),(898,428),
   (937,457),(925,487),(890,526),(866,557),(844,579),(809,577),(793,560),(788,539),
   (772,520),(752,502)],
  [(1100,492),(1116,509),(1152,540),(1169,557),(1173,582),(1164,600),(1141,602),
   (1125,582),(1124,563),(1113,541),(1100,523)]],
 'girl_cuff_protection': [[(866,431),(880,415),(906,422),(941,451),(938,463),
                           (920,479),(887,454),(872,445)]],
 'boy_linen': [
  [(607,242),(634,247),(670,268),(682,294),(671,308),(645,281),(610,258)],
  [(675,264),(695,280),(708,295),(698,303),(683,286)],
  [(500,429),(548,447),(563,468),(552,491),(487,460)],
  [(756,443),(781,429),(804,451),(793,470),(754,500),(730,478)]],
 'boots': [
  [(466,801),(503,807),(540,827),(547,851),(579,876),(587,905),(552,918),(487,899),(429,869),(432,842)],
  [(723,808),(768,807),(785,828),(821,838),(850,842),(869,867),(859,888),(820,905),(716,909),(709,878)],
  [(860,832),(1009,832),(1018,919),(860,919)],
  [(1110,829),(1270,829),(1270,919),(1110,919)]],
}
BOY_FACE = [(737,143),(739,155),(734,167),(733,181),(744,192),(744,202),(738,210),
 (738,220),(732,232),(723,241),(708,242),(691,238),(681,235),(674,249),(669,269),
 (650,257),(627,245),(638,231),(639,217),(646,206),(650,200),(641,195),(639,184),
 (641,174),(647,169),(655,173),(660,183),(665,183),(673,173),(682,167),(691,161),
 (705,157),(719,149)]

def _ancestors(socket):
    pending = [link.from_node for link in socket.links]
    seen = set()
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(link.from_node for inp in node.inputs for link in inp.links)
    return seen

def _original_branch(mat):
    outputs = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    assert len(outputs) == 1
    emissions = [n for n in _ancestors(outputs[0].inputs['Surface']) if n.type == 'EMISSION']
    assert len(emissions) == 1, 'Expected one original held-pair Emission'
    emission = emissions[0]
    assert emission.inputs['Color'].is_linked
    candidates = []
    for n in _ancestors(emission.inputs['Color']):
        if n.type != 'HUE_SAT' or abs(n.inputs['Saturation'].default_value) > 1e-6:
            continue
        if abs(n.inputs['Value'].default_value - .8) > 1e-5 or not n.inputs['Color'].is_linked:
            continue
        tex = n.inputs['Color'].links[0].from_node
        if (tex.type == 'TEX_IMAGE' and tex.image
                and tex.image.name.startswith('Pair_Painterly_Near_Age_v015')
                and tuple(tex.image.size) == (1672, 941)):
            candidates.append((n, tex))
    assert len(candidates) == 1, 'Original charcoal image/HSV branch is ambiguous'
    return emission, candidates[0][0], candidates[0][1]

def _poly(G, x, y, points):
    # Native even/odd ray crossings; no generated mask images or changed geometry.
    crossings = 0.
    for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
        if abs(by-ay) < 1e-8:
            continue
        ygate = G.math('MULTIPLY', G.math('GREATER_THAN', y, min(ay, by)-1e-5),
                       G.math('LESS_THAN', y, max(ay, by)))
        edge_x = G.math('ADD', ax, G.math('MULTIPLY',
                        G.math('SUBTRACT', y, ay), (bx-ax)/(by-ay)))
        crossings = G.math('ADD', crossings, G.math('MULTIPLY', ygate,
                            G.math('LESS_THAN', x, edge_x)))
    return G.math('GREATER_THAN', G.math('MODULO', crossings, 2.), .5)

def _union(G, x, y, polygons):
    mask = 0.
    for points in polygons:
        mask = G.math('MAXIMUM', mask, _poly(G, x, y, points))
    return mask

def _clamp(G, value):
    return G.math('MINIMUM', 1., G.math('MAXIMUM', 0., value))

def _curve(G, value, points):
    result = points[0][1]
    for (a, b), (c, d) in zip(points, points[1:]):
        fac = _clamp(G, G.math('DIVIDE', G.math('SUBTRACT', value, a), c-a))
        result = G.math('ADD', result, G.math('MULTIPLY', d-b, fac))
    return result

def _boy_profile(G, x, y, base):
    # Reuse the unlit authored source, never the V060/V063 flash/arc overrides.
    native = ROOT/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'
    name = 'V044 preserved paint | V040 PAINT | complete fixed child profile'
    source = bpy.data.materials.get(name)
    if source is None:
        with bpy.data.libraries.load(str(native), link=False) as (available, loaded):
            assert name in available.materials, 'Authored boy profile material is unavailable'
            loaded.materials = [name]
        source = loaded.materials[0]
    output = next(n for n in source.node_tree.nodes
                  if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
    emissions = [n for n in _ancestors(output.inputs['Surface']) if n.type == 'EMISSION']
    assert len(emissions) == 1 and emissions[0].inputs['Color'].is_linked
    original_texture = emissions[0].inputs['Color'].links[0].from_node
    assert original_texture.type == 'TEX_IMAGE', 'Inspect changed authored boy color branch before reuse'
    assert original_texture.image and tuple(original_texture.image.size) == (1254, 1254)
    original_vector = original_texture.inputs['Vector']
    assert original_vector.is_linked and original_vector.links[0].from_node.type == 'UVMAP'
    assert original_vector.links[0].from_node.uv_map == 'V040 | separated painted part registration'
    registration_path = ROOT/'locomotion/character_design_finish_v040/evidence/NATIVE_PAINTED_BUILD.json'
    registration = json.loads(registration_path.read_text())['intentional_head_geometry_change']
    (rx0, rx1), (rz0, rz1) = registration['rest_painted_occupancy_bounds']
    gx0, gy0, gx1, gy1 = registration['atlas_head_pixel_bounds']
    # Exact old PERF head original-v015 UV -> localXZ fit, independently probed.
    # Max native vertex residual6.364798599278743e-8m. No approximate bbox fit.
    coefficients = [
        [2.8488838064046154, 6.539964580998259e-08, -1.0836663880679742],
        [-5.116115348840114e-07, 1.6033490765926763, -0.057931706519470216]]
    u = G.math('DIVIDE', x, 1672.)
    v = G.math('SUBTRACT', 1., G.math('DIVIDE', y, 941.))
    local = [G.math('ADD', G.math('ADD', G.math('MULTIPLY', u, a),
             G.math('MULTIPLY', v, b)), c) for a, b, c in coefficients]
    W, H = original_texture.image.size
    au = G.math('ADD', gx0/W, G.math('MULTIPLY',
                G.math('DIVIDE', G.math('SUBTRACT', local[0], rx0), rx1-rx0),
                (gx1-gx0)/W))
    av = G.math('ADD', 1.-gy1/H, G.math('MULTIPLY',
                G.math('DIVIDE', G.math('SUBTRACT', local[1], rz0), rz1-rz0),
                (gy1-gy0)/H))
    vector = G.n.new('ShaderNodeCombineXYZ')
    vector.name = PREFIX + 'EXACT original head to authored atlas registration'
    G.l.new(au, vector.inputs['X'])
    G.l.new(av, vector.inputs['Y'])
    tex = G.n.new('ShaderNodeTexImage')
    tex.name = PREFIX + 'authored v040 boy profile / unlit source color'
    for attr in ['image', 'interpolation', 'extension', 'projection', 'projection_blend']:
        setattr(tex, attr, getattr(original_texture, attr))
    G.l.new(vector.outputs[0], tex.inputs['Vector'])
    region = _union(G, x, y, MASKS['boy_hair'])
    # New atlas alpha is only eligibility for INTERIOR color, never transparency.
    # Original image/mesh remains the sole outer silhouette; transparent source
    # texels fall back to the original-UV palette rather than painting black holes.
    eligibility = _clamp(G, G.math('DIVIDE', tex.outputs['Alpha'], .5))
    factor = G.math('MULTIPLY', region, eligibility)
    # Only uncovered old jaw/neck pixels borrow nearby ORIGINAL painted skin.
    # Authored facial features and original silhouette remain fixed.
    jaw_polygon = [(620,232),(648,239),(675,245),(691,235),(717,232),(732,230),
                   (729,246),(709,251),(693,251),(682,263),(673,274),(648,267),(622,251)]
    skin_rows = [(360,173,361),(372,159,351),(384,152,346),(396,141,260),
                 (408,137,249),(420,132,243),(432,126,236)]
    py = G.math('MULTIPLY', G.math('SUBTRACT', 1., av), float(H))
    safe_y = G.math('MINIMUM', 432., G.math('MAXIMUM', 360., py))
    left = _curve(G, safe_y, [(row, low+3) for row, low, high in skin_rows])
    right = _curve(G, safe_y, [(row, high-3) for row, low, high in skin_rows])
    safe_x = G.math('MINIMUM', right, G.math('MAXIMUM', left,
                     G.math('MULTIPLY', au, float(W))))
    skin_vector = G.n.new('ShaderNodeCombineXYZ')
    G.l.new(G.math('DIVIDE', safe_x, float(W)), skin_vector.inputs['X'])
    G.l.new(G.math('SUBTRACT', 1., G.math('DIVIDE', safe_y, float(H))), skin_vector.inputs['Y'])
    skin_tex = G.n.new('ShaderNodeTexImage')
    skin_tex.name = PREFIX + 'uncovered jaw and neck / SAME authored skin pigment'
    skin_tex.image = tex.image
    skin_tex.interpolation = tex.interpolation
    skin_tex.extension = 'CLIP'
    G.l.new(skin_vector.outputs[0], skin_tex.inputs['Vector'])
    uncovered = G.math('MULTIPLY', _poly(G, x, y, jaw_polygon),
                       G.math('SUBTRACT', 1., eligibility))
    base = G.mix(base, skin_tex.outputs['Color'], uncovered)
    report = dict(native=str(native), source_material=source.name,
        source_image=tex.image.name, source_emission=emissions[0].name,
        source_branch='Unlit ImageTexture Color; original source interpolation/projection retained',
        registration=str(registration_path), source_uv=UV_NAME,
        original_uv_to_local_xz=coefficients, max_native_fit_residual_m=6.364798599278743e-8,
        rest_occupancy=registration['rest_painted_occupancy_bounds'],
        atlas_head_pixel_bounds=registration['atlas_head_pixel_bounds'],
        old_head_region=MASKS['boy_hair'], jaw_neck_fallback_polygon=jaw_polygon,
        jaw_skin_row_bounds=skin_rows, jaw_skin_source='Existing authored atlas skin; uncovered pixels only',
        alpha_usage='Atlas alpha selects interior COLOR only; original silhouette alpha path untouched',
        excluded='No copied V060 light/flash or V063 color-arc drivers')
    return G.mix(base, tex.outputs['Color'], factor), report

def _girl_face(G, x, y, base, registration, image):
    W, H = image.size
    gx = G.math('ADD', G.math('MULTIPLY', x, 4.2),
               _curve(G, y, registration['edge_shift']))
    gy = G.math('ADD', 665., G.math('MULTIPLY', G.math('SUBTRACT', y, 229.), 4.2))
    vector = G.n.new('ShaderNodeCombineXYZ')
    G.l.new(G.math('DIVIDE', gx, float(W)), vector.inputs['X'])
    G.l.new(G.math('SUBTRACT', 1., G.math('DIVIDE', gy, float(H))), vector.inputs['Y'])
    tex = G.n.new('ShaderNodeTexImage')
    tex.name = PREFIX + 'v050 authored girl face / original-space registration'
    tex.image = image
    tex.extension = 'CLIP'
    G.l.new(vector.outputs[0], tex.inputs['Vector'])
    rgb = G.n.new('ShaderNodeSeparateColor')
    rgb.mode = 'RGB'
    G.l.new(tex.outputs['Color'], rgb.inputs[0])
    skin = _clamp(G, G.math('DIVIDE', G.math('SUBTRACT',
                   G.math('SUBTRACT', rgb.outputs['Red'], rgb.outputs['Green']), .012), .018))
    left = _curve(G, y, registration['original_hair_protection_left_boundary'])
    region = _clamp(G, G.math('DIVIDE', G.math('SUBTRACT', x, left), 1.5))
    vertical = G.math('MULTIPLY', _clamp(G, G.math('SUBTRACT', y, 193.)),
                      _clamp(G, G.math('SUBTRACT', 315., y)))
    return G.mix(base, tex.outputs['Color'],
                 G.math('MULTIPLY', skin, G.math('MULTIPLY', region, vertical)))

def _links(tree):
    return {(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
            for l in tree.links}

def apply(scene, fill):
    """Copy only this held-pair material; return the final shared-arc Mix node."""
    assert fill.type == 'MESH' and len(fill.material_slots) == 1
    assert UV_NAME in fill.data.uv_layers, 'Expected the original combined-pair UV'
    original = fill.material_slots[0].material
    assert original and original.use_nodes and not original.get('V064_original_pair_color')
    _original_branch(original)
    palettes_path = ROOT/'locomotion/full_color_character_v038/scripts/color_materials.py'
    registration_path = ROOT/'locomotion/face_hand_finish_v050/evidence/FINISH_BUILD.json'
    face_path = ROOT/'locomotion/face_hand_finish_v050/textures/WTSC_Girl_Face_Finish_Study_v050.png'
    palette_module = runpy.run_path(str(palettes_path))
    registration = json.loads(registration_path.read_text())['face_registration']
    image = bpy.data.images.load(str(face_path), check_existing=True)
    assert tuple(image.size) == tuple(registration['gen_image_size'])
    mat = original.copy()
    mat.name = PREFIX + 'ORIGINAL held pair / full painted color and original charcoal'
    mat.surface_render_method = 'DITHERED'
    G = palette_module['Nodes'](mat)
    emission, charcoal, tex = _original_branch(mat)
    old_lit = emission.inputs['Color'].links[0].from_socket
    old_gray = charcoal.outputs[0]
    before_links = _links(mat.node_tree)
    replaced_link = next(l for l in mat.node_tree.links
                         if l.to_socket == emission.inputs['Color'])
    removed_signature = (replaced_link.from_node.name, replaced_link.from_socket.identifier,
                         replaced_link.to_node.name, replaced_link.to_socket.identifier)
    uv = G.n.new('ShaderNodeUVMap')
    uv.name = PREFIX + 'unaltered original pair UV'
    uv.uv_map = UV_NAME
    sep = G.n.new('ShaderNodeSeparateXYZ')
    G.l.new(uv.outputs[0], sep.inputs[0])
    x = G.math('MULTIPLY', sep.outputs['X'], 1672.)
    y = G.math('MULTIPLY', G.math('SUBTRACT', 1., sep.outputs['Y']), 941.)
    bw = G.n.new('ShaderNodeRGBToBW')
    G.l.new(tex.outputs['Color'], bw.inputs[0])
    gray = bw.outputs[0]
    color = old_gray
    for key, role in [('boy_trousers','trousers'), ('boy_coat','coat'), ('boy_hair','hair'),
                      ('skin','skin'), ('boy_linen','linen'), ('boots','shoes')]:
        mask = _union(G, x, y, MASKS[key])
        if key == 'skin':
            cuff = _union(G, x, y, MASKS['girl_cuff_protection'])
            mask = G.math('MULTIPLY', mask, G.math('SUBTRACT', 1., cuff))
        color = G.mix(color, G.ramp(gray, role), mask)
    face = _poly(G, x, y, BOY_FACE)
    color = G.mix(color, G.ramp(gray, 'skin'), face)
    white = G.math('GREATER_THAN', gray, .65)
    dx = G.math('DIVIDE', G.math('SUBTRACT', x, 716.), 1.)
    dy = G.math('DIVIDE', G.math('SUBTRACT', y, 175.1), 2.25)
    rr = G.math('ADD', G.math('MULTIPLY', dx, dx), G.math('MULTIPLY', dy, dy))
    iris = G.math('LESS_THAN', rr, 1.)
    eye = G.mix(palette_module['linear_hex']('e7e1cc'),
                palette_module['linear_hex']('30221b'), iris)
    color = G.mix(color, eye, G.math('MULTIPLY', white, face))
    color, boy_profile = _boy_profile(G, x, y, color)
    color = _girl_face(G, x, y, color, registration, image)
    def combine(mode, a, b, name):
        node = G.n.new('ShaderNodeMixRGB')
        node.name = name
        node.blend_type = mode
        node.use_clamp = False
        node.inputs[0].default_value = 1.
        G.l.new(a, node.inputs[1])
        G.l.new(b, node.inputs[2])
        return node
    delta = combine('SUBTRACT', old_lit, old_gray, PREFIX + 'preserved original lighting delta')
    full = combine('ADD', color, delta.outputs[0], PREFIX + 'full color plus original lighting')
    mix = G.n.new('ShaderNodeMixRGB')
    mix.name = PREFIX + 'full color to ORIGINAL lit charcoal'
    mix.blend_type = 'MIX'
    mix.use_clamp = False
    mix.inputs[0].default_value = 0.
    G.l.new(full.outputs[0], mix.inputs[1])
    G.l.new(old_lit, mix.inputs[2])
    G.l.new(mix.outputs[0], emission.inputs['Color'])
    assert before_links - _links(mat.node_tree) == {removed_signature}, 'Changed original internal wiring'
    mat['V064_original_pair_color'] = True
    mat['V064_arc_mix_node'] = mix.name
    fill.material_slots[0].link = 'OBJECT'
    fill.material_slots[0].material = mat
    return dict(material=mat.name, mix_node=mix.name, factor_socket=0,
        factor_default=0., factor_meaning='0 full color; 1 EXACT original lit charcoal',
        object=fill.name, original_material=original.name, original_uv=UV_NAME,
        original_image=tex.image.name, original_charcoal_node=charcoal.name,
        original_lit_source=old_lit.node.name, original_internal_links_preserved=True,
        surface_render_method=mat.surface_render_method,
        inputs=dict(palettes=str(palettes_path), girl_registration=str(registration_path),
                    girl_face_paint=str(face_path)),
        palettes=palette_module['PALETTES'], source_pixel_masks=MASKS, boy_face_polygon=BOY_FACE,
        authored_boy_profile=boy_profile,
        limits=[
          'Held original combined drawing only; no gait, pose, head-turn or topology changes.',
          'Boy body uses existing v038 ramps; head reuses the actual unlit authored v040/v063 profile painting.',
          'Exact source UV/atlas fit does not alter the held outline; any differing authored silhouette falls back to source palettes.',
          'Body masks are authored in original source pixels and need native seam/hand/boot review.',
          'Girl face is existing v050 registered artwork; original hair, braid and dark costume remain.',
          'Original charcoal/luma protection/fire/rim control graph stays intact; only final Emission link changes.',
          'Additive original light delta is retained over the new base; no new lighting or world grading.',
          'Factor1 restores original lit color, alpha and strength; caller must attach one shared global driver.',
          'No original material/data/UV/image pixels are edited; no new raster artwork is generated.',
        ])

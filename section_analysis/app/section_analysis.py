# -*- coding: utf-8 -*-

import sectionproperties.pre.sections as sections
from sectionproperties.analysis.cross_section import CrossSection
from app.settings import MAX_FINITE_ELEMENTS_NUMBER


def _analyze_common_structural_geometry(step, geometry, mesh_sizes, N, Vx, Vy, Mxx, Myy, Mzz):
    mesh = geometry.create_mesh(mesh_sizes=[mesh_sizes])
    section = CrossSection(geometry, mesh)
    finite_elements_number = len(section.mesh_elements)
    if finite_elements_number > MAX_FINITE_ELEMENTS_NUMBER:
        return False, None, None, None, None, None, None, None, None, None, None
    elif finite_elements_number < MAX_FINITE_ELEMENTS_NUMBER and step == 'checking':
        return True, None, None, None, None, None, None, None, None, None, None
    else:
        section.calculate_geometric_properties()
        section.calculate_warping_properties()
        loadcase = section.calculate_stress(N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)
        nodes = section.mesh_nodes
        stresses = loadcase.get_stress()[0]
        area = section.get_area()
        ixx_c, iyy_c, ixy_c = section.get_ic()
        torsion_constant = section.get_j()
        warping_constant = section.get_gamma()
        elastic_centroid = section.get_c()
        centroidal_shear_center = section.get_sc()
        return True, nodes, stresses, area, ixx_c, iyy_c, ixy_c, torsion_constant, warping_constant, \
               elastic_centroid, centroidal_shear_center


def analyze_rect(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.RectangularSection(d=kwargs['d'], b=kwargs['b'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_circ(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.CircularSection(d=kwargs['d'], n=kwargs['n'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_chs(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.Chs(d=kwargs['d'], t=kwargs['t'], n=kwargs['n'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_elliptical(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.EllipticalSection(d_y=kwargs['d_y'], d_x=kwargs['d_x'], n=kwargs['n'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_ehs(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.Ehs(d_y=kwargs['d_y'], d_x=kwargs['d_x'], t=kwargs['t'], n=kwargs['n'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_rhs(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.Rhs(d=kwargs['d'], b=kwargs['b'], t=kwargs['t'], r_out=kwargs['r_out'], n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_i(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.ISection(d=kwargs['d'], b=kwargs['b'], t_f=kwargs['t_f'], t_w=kwargs['t_w'], r=kwargs['r'],
                                 n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_monosymm_i(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.MonoISection(d=kwargs['d'], b_t=kwargs['b_t'], b_b=kwargs['b_b'], t_ft=kwargs['t_ft'],
                                     t_fb=kwargs['t_fb'], t_w=kwargs['t_w'], r=kwargs['r'], n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_tap_fl_i(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.TaperedFlangeISection(d=kwargs['d'], b=kwargs['b'], t_f=kwargs['t_f'], t_w=kwargs['t_w'],
                                              r_r=kwargs['r_r'], r_f=kwargs['r_f'], alpha=kwargs['alpha'],
                                              n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_pfc(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.PfcSection(d=kwargs['d'], b=kwargs['b'], t_f=kwargs['t_f'], t_w=kwargs['t_w'], r=kwargs['r'],
                                   n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_tap_fl_c(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.TaperedFlangeChannel(d=kwargs['d'], b=kwargs['b'], t_f=kwargs['t_f'], t_w=kwargs['t_w'],
                                             r_r=kwargs['r_r'], r_f=kwargs['r_f'], alpha=kwargs['alpha'],
                                             n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_t(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.TeeSection(d=kwargs['d'], b=kwargs['b'], t_f=kwargs['t_f'], t_w=kwargs['t_w'], r=kwargs['r'],
                                   n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_angle(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.AngleSection(d=kwargs['d'], b=kwargs['b'], t=kwargs['t'], r_r=kwargs['r_r'], r_t=kwargs['r_t'],
                                     n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_cee(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.CeeSection(d=kwargs['d'], b=kwargs['b'], l=kwargs['l'], t=kwargs['t'], r_out=kwargs['r_out'],
                                   n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_zed(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.ZedSection(d=kwargs['d'], b_l=kwargs['b_l'], b_r=kwargs['b_r'], l=kwargs['l'], t=kwargs['t'],
                                   r_out=kwargs['r_out'], n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_cruciform(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.CruciformSection(d=kwargs['d'], b=kwargs['b'], t=kwargs['t'], r=kwargs['r'], n_r=kwargs['n_r'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)


def analyze_polygon(step, N, Vx, Vy, Mxx, Myy, Mzz, **kwargs):
    geometry = sections.PolygonSection(d=kwargs['d'], t=kwargs['t'], r_in=kwargs['r_in'], n_r=kwargs['n_r'],
                                       rot=kwargs['rot'], n_sides=kwargs['n_sides'])
    return _analyze_common_structural_geometry(step=step, geometry=geometry, mesh_sizes=kwargs['mesh_sizes'],
                                               N=N, Vx=Vx, Vy=Vy, Mxx=Mxx, Myy=Myy, Mzz=Mzz)

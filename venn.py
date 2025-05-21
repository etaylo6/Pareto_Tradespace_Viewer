# coding: utf-8
from itertools import chain
try:
    # since python 3.10
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Default RGBA colors
default_colors = [
    [92, 192, 98, 0.5],
    [90, 155, 212, 0.5],
    [246, 236, 86, 0.6],
    [241, 90, 96, 0.4],
    [255, 117, 0, 0.3],
    [82, 82, 190, 0.2],
]

def _norm_colors(colors_list):
    return [[c[0]/255.0, c[1]/255.0, c[2]/255.0, c[3]] for c in colors_list]

def draw_ellipse(ax, x, y, w, h, angle, color):
    e = patches.Ellipse((x, y), width=w, height=h, angle=angle, color=color)
    ax.add_patch(e)

def draw_triangle(ax, x1, y1, x2, y2, x3, y3, color):
    tri = patches.Polygon([(x1,y1),(x2,y2),(x3,y3)], closed=True, color=color)
    ax.add_patch(tri)

def draw_text(ax, x, y, text, color='black', fontsize=14, ha='center', va='center'):
    ax.text(x, y, text, color=color, fontsize=fontsize, ha=ha, va=va)


def get_labels(data, fill=["number"]):
    N = len(data)
    sets_data = [set(data[i]) for i in range(N)]
    all_elems = set(chain(*data))
    coll = {}
    for n in range(1, 2**N):
        key = bin(n)[2:].zfill(N)
        inter = all_elems.copy()
        for i, bit in enumerate(key):
            if bit=='1': inter &= sets_data[i]
            else: inter -= sets_data[i]
        coll[key] = inter
    labels = {k: '' for k in coll}
    if 'logic' in fill:
        for k in labels: labels[k] = k + ': '
    if 'number' in fill:
        for k in labels: labels[k] += str(len(coll[k]))
    if 'percent' in fill:
        total = len(all_elems)
        for k in labels:
            labels[k] += f" ({100*len(coll[k])/total:.1f}%)"
    return labels


def _venn_common(ax):
    ax.set_aspect('equal')
    ax.set_axis_off()
    return ax.figure, ax

# 2-set Venn diagram
def venn2(labels, names=['A','B'], ax=None, **options):
    colors = _norm_colors(options.get('colors', default_colors[:2]))
    if ax is None:
        fig = plt.figure(figsize=options.get('figsize',(9,7)), dpi=options.get('dpi',96))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    fig, ax = _venn_common(ax)
    ax.set_xlim(0,1); ax.set_ylim(0,0.7)
    draw_ellipse(ax,0.375,0.3,0.5,0.5,0,colors[0])
    draw_ellipse(ax,0.625,0.3,0.5,0.5,0,colors[1])
    draw_text(ax,0.74,0.30, labels.get('01',''))
    draw_text(ax,0.26,0.30, labels.get('10',''))
    draw_text(ax,0.50,0.30, labels.get('11',''))
    draw_text(ax,0.20,0.56, names[0], color=colors[0])
    draw_text(ax,0.80,0.56, names[1], color=colors[1])
    ax.legend(names, loc='center left', bbox_to_anchor=(1,0.5), fancybox=True)
    return fig, ax

# 3-set Venn diagram
def venn3(labels, names=['A','B','C'], ax=None, **options):
    colors = _norm_colors(options.get('colors', default_colors[:3]))
    if ax is None:
        fig = plt.figure(figsize=options.get('figsize',(9,9)), dpi=options.get('dpi',96))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    fig, ax = _venn_common(ax)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    draw_ellipse(ax,0.333,0.633,0.5,0.5,0,colors[0])
    draw_ellipse(ax,0.666,0.633,0.5,0.5,0,colors[1])
    draw_ellipse(ax,0.500,0.310,0.5,0.5,0,colors[2])
    draw_text(ax,0.50,0.27, labels.get('001',''))
    draw_text(ax,0.73,0.65, labels.get('010',''))
    draw_text(ax,0.61,0.46, labels.get('011',''))
    draw_text(ax,0.27,0.65, labels.get('100',''))
    draw_text(ax,0.39,0.46, labels.get('101',''))
    draw_text(ax,0.50,0.65, labels.get('110',''))
    draw_text(ax,0.50,0.51, labels.get('111',''))
    draw_text(ax,0.15,0.87, names[0], color=colors[0])
    draw_text(ax,0.85,0.87, names[1], color=colors[1])
    draw_text(ax,0.50,0.02, names[2], color=colors[2])
    ax.legend(names, loc='center left', bbox_to_anchor=(1,0.5), fancybox=True)
    return fig, ax

# 4-set Venn diagram
def venn4(labels, names=['A','B','C','D'], ax=None, **options):
    colors = _norm_colors(options.get('colors', default_colors[:4]))
    if ax is None:
        fig = plt.figure(figsize=options.get('figsize',(12,12)), dpi=options.get('dpi',96))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    fig, ax = _venn_common(ax)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    draw_ellipse(ax,0.350,0.400,0.72,0.45,140.0,colors[0])
    draw_ellipse(ax,0.450,0.500,0.72,0.45,140.0,colors[1])
    draw_ellipse(ax,0.544,0.500,0.72,0.45,40.0,colors[2])
    draw_ellipse(ax,0.644,0.400,0.72,0.45,40.0,colors[3])
    draw_text(ax,0.85,0.42, labels.get('0001',''))
    draw_text(ax,0.68,0.72, labels.get('0010',''))
    draw_text(ax,0.77,0.59, labels.get('0011',''))
    draw_text(ax,0.32,0.72, labels.get('0100',''))
    draw_text(ax,0.71,0.30, labels.get('0101',''))
    draw_text(ax,0.50,0.66, labels.get('0110',''))
    draw_text(ax,0.65,0.50, labels.get('0111',''))
    draw_text(ax,0.14,0.42, labels.get('1000',''))
    draw_text(ax,0.50,0.17, labels.get('1001',''))
    draw_text(ax,0.29,0.30, labels.get('1010',''))
    draw_text(ax,0.39,0.24, labels.get('1011',''))
    draw_text(ax,0.23,0.59, labels.get('1100',''))
    draw_text(ax,0.61,0.24, labels.get('1101',''))
    draw_text(ax,0.35,0.50, labels.get('1110',''))
    draw_text(ax,0.50,0.38, labels.get('1111',''))
    draw_text(ax,0.13,0.18, names[0], color=colors[0], ha='right')
    draw_text(ax,0.18,0.83, names[1], color=colors[1], ha='right', va='bottom')
    draw_text(ax,0.82,0.83, names[2], color=colors[2], ha='left', va='bottom')
    draw_text(ax,0.87,0.18, names[3], color=colors[3], ha='left', va='top')
    ax.legend(names, loc='center left', bbox_to_anchor=(1,0.5), fancybox=True)
    return fig, ax

# 5-set Venn diagram
def venn5(labels, names=['A','B','C','D','E'], ax=None, **options):
    colors = _norm_colors(options.get('colors', default_colors[:5]))
    if ax is None:
        fig = plt.figure(figsize=options.get('figsize',(13,13)), dpi=options.get('dpi',96))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    fig, ax = _venn_common(ax)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    draw_ellipse(ax,0.428,0.449,0.87,0.50,155.0,colors[0])
    draw_ellipse(ax,0.469,0.543,0.87,0.50,82.0,colors[1])
    draw_ellipse(ax,0.558,0.523,0.87,0.50,10.0,colors[2])
    draw_ellipse(ax,0.578,0.432,0.87,0.50,118.0,colors[3])
    draw_ellipse(ax,0.489,0.383,0.87,0.50,46.0,colors[4])
    # region labels
    draw_text(ax,0.27,0.11, labels.get('00001',''))
    draw_text(ax,0.72,0.11, labels.get('00010',''))
    draw_text(ax,0.55,0.13, labels.get('00011',''))
    draw_text(ax,0.91,0.58, labels.get('00100',''))
    draw_text(ax,0.78,0.64, labels.get('00101',''))
    draw_text(ax,0.84,0.41, labels.get('00110',''))
    draw_text(ax,0.76,0.55, labels.get('00111',''))
    draw_text(ax,0.51,0.90, labels.get('01000',''))
    draw_text(ax,0.39,0.15, labels.get('01001',''))
    draw_text(ax,0.42,0.78, labels.get('01010',''))
    draw_text(ax,0.50,0.15, labels.get('01011',''))
    draw_text(ax,0.67,0.76, labels.get('01100',''))
    draw_text(ax,0.70,0.71, labels.get('01101',''))
    draw_text(ax,0.51,0.74, labels.get('01110',''))
    draw_text(ax,0.64,0.67, labels.get('01111',''))
    draw_text(ax,0.10,0.61, labels.get('10000',''))
    draw_text(ax,0.20,0.31, labels.get('10001',''))
    draw_text(ax,0.76,0.25, labels.get('10010',''))
    draw_text(ax,0.65,0.23, labels.get('10011',''))
    draw_text(ax,0.18,0.50, labels.get('10100',''))
    draw_text(ax,0.21,0.37, labels.get('10101',''))
    draw_text(ax,0.81,0.37, labels.get('10110',''))
    draw_text(ax,0.74,0.40, labels.get('10111',''))
    draw_text(ax,0.27,0.70, labels.get('11000',''))
    draw_text(ax,0.34,0.25, labels.get('11001',''))
    draw_text(ax,0.33,0.72, labels.get('11010',''))
    draw_text(ax,0.51,0.22, labels.get('11011',''))
    draw_text(ax,0.25,0.58, labels.get('11100',''))
    draw_text(ax,0.28,0.39, labels.get('11101',''))
    draw_text(ax,0.36,0.66, labels.get('11110',''))
    draw_text(ax,0.51,0.47, labels.get('11111',''))
    # set names
    draw_text(ax,0.02,0.72, names[0], color=colors[0], ha='right')
    draw_text(ax,0.72,0.94, names[1], color=colors[1], va='bottom')
    draw_text(ax,0.97,0.74, names[2], color=colors[2], ha='left')
    draw_text(ax,0.88,0.05, names[3], color=colors[3], ha='left')
    draw_text(ax,0.12,0.05, names[4], color=colors[4], ha='right')
    ax.legend(names, loc='center left', bbox_to_anchor=(1,0.5), fancybox=True)
    return fig, ax

# 6-set Venn diagram
def venn6(labels, names=['A','B','C','D','E','F'], ax=None, **options):
    colors = _norm_colors(options.get('colors', default_colors[:6]))
    if ax is None:
        fig = plt.figure(figsize=options.get('figsize',(20,20)), dpi=options.get('dpi',96))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    fig, ax = _venn_common(ax)
    ax.set_xlim(0.173,0.788); ax.set_ylim(0.230,0.845)
    # body triangles
    draw_triangle(ax,0.637,0.921,0.649,0.274,0.188,0.667,colors[0])
    draw_triangle(ax,0.981,0.769,0.335,0.191,0.393,0.671,colors[1])
    draw_triangle(ax,0.941,0.397,0.292,0.475,0.456,0.747,colors[2])
    draw_triangle(ax,0.662,0.119,0.316,0.548,0.662,0.700,colors[3])
    draw_triangle(ax,0.309,0.081,0.374,0.718,0.681,0.488,colors[4])
    draw_triangle(ax,0.016,0.626,0.726,0.687,0.522,0.327,colors[5])
    # region labels
    draw_text(ax,0.212,0.562, labels.get('000001',''))
    draw_text(ax,0.430,0.249, labels.get('000010',''))
    draw_text(ax,0.356,0.444, labels.get('000011',''))
    draw_text(ax,0.609,0.255, labels.get('000100',''))
    draw_text(ax,0.323,0.546, labels.get('000101',''))
    draw_text(ax,0.513,0.316, labels.get('000110',''))
    draw_text(ax,0.523,0.348, labels.get('000111',''))
    draw_text(ax,0.747,0.458, labels.get('001000',''))
    draw_text(ax,0.325,0.492, labels.get('001001',''))
    draw_text(ax,0.670,0.481, labels.get('001010',''))
    draw_text(ax,0.359,0.478, labels.get('001011',''))
    draw_text(ax,0.653,0.444, labels.get('001100',''))
    draw_text(ax,0.344,0.526, labels.get('001101',''))
    draw_text(ax,0.653,0.466, labels.get('001110',''))
    draw_text(ax,0.363,0.503, labels.get('001111',''))
    draw_text(ax,0.750,0.616, labels.get('010000',''))
    draw_text(ax,0.682,0.654, labels.get('010001',''))

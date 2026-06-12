#!/usr/bin/env python3
"""Round 2 of self-portrait sketches: mockingbird, crane, owl, guillemot, pigeons."""
import os
from sim import save

BASE = os.path.dirname(os.path.abspath(__file__))


def mirror(S):
    return [(c, m, [(1 - u, v) for u, v in pts]) for c, m, pts in S]


def mockingbird():  # Teddy — slim, long cocked tail, white wing patch
    S = []
    # twig perch
    S.append(("black", "thin", [(0.14, 0.72), (0.46, 0.70), (0.78, 0.665)]))
    S.append(("green", "thick", [(0.20, 0.69), (0.25, 0.675)]))
    # head + back outline (facing left)
    S.append(("black", "thin", [(0.36, 0.40), (0.375, 0.345), (0.42, 0.315), (0.47, 0.325), (0.50, 0.36)]))
    S.append(("black", "thin", [(0.50, 0.36), (0.545, 0.41), (0.575, 0.47), (0.585, 0.52)]))
    # chest/belly down to legs
    S.append(("black", "thin", [(0.36, 0.40), (0.35, 0.46), (0.36, 0.525), (0.40, 0.585), (0.455, 0.625), (0.51, 0.635)]))
    # long tail cocked up-right
    S.append(("black", "thick", [(0.585, 0.52), (0.66, 0.46), (0.73, 0.39)]))
    S.append(("white", "thin", [(0.62, 0.475), (0.68, 0.42)]))
    # thin bill + eye line + eye
    S.append(("black", "thin", [(0.36, 0.365), (0.305, 0.375)]))
    S.append(("black", "thin", [(0.365, 0.355), (0.40, 0.348)]))
    S.append(("black", "thin", [(0.405, 0.345), (0.412, 0.342)]))
    # dark wing with white patch
    S.append(("black", "thick", [(0.475, 0.43), (0.515, 0.475), (0.55, 0.53)]))
    S.append(("black", "thick", [(0.46, 0.475), (0.50, 0.52), (0.535, 0.565)]))
    S.append(("white", "thick", [(0.495, 0.49), (0.52, 0.515)]))
    # back hatch (gray suggestion)
    S.append(("black", "thin", [(0.46, 0.37), (0.50, 0.40)]))
    S.append(("black", "thin", [(0.50, 0.39), (0.535, 0.425)]))
    # legs
    S.append(("black", "thin", [(0.45, 0.63), (0.452, 0.665), (0.448, 0.70)]))
    S.append(("black", "thin", [(0.49, 0.635), (0.497, 0.668), (0.50, 0.695)]))
    # sky hint
    S.append(("blue", "thin", [(0.72, 0.14), (0.83, 0.135), (0.91, 0.14)]))
    return S


def crane():  # Terry Sandhill — tall, red crown, bustle
    S = []
    # ground
    S.append(("green", "thick", [(0.18, 0.90), (0.5, 0.895), (0.82, 0.90)]))
    S.append(("green", "thin", [(0.25, 0.925), (0.55, 0.92)]))
    # dagger bill
    S.append(("black", "thin", [(0.21, 0.255), (0.27, 0.265), (0.325, 0.275)]))
    # head + red crown
    S.append(("black", "thin", [(0.325, 0.275), (0.345, 0.25), (0.375, 0.245), (0.395, 0.265)]))
    S.append(("red", "thick", [(0.335, 0.252), (0.36, 0.243)]))
    S.append(("black", "thin", [(0.347, 0.268), (0.353, 0.265)]))
    # long neck (two lines down to body)
    S.append(("black", "thin", [(0.33, 0.285), (0.345, 0.35), (0.375, 0.42), (0.41, 0.475)]))
    S.append(("black", "thin", [(0.395, 0.27), (0.405, 0.34), (0.425, 0.41), (0.455, 0.46)]))
    # body oval
    S.append(("black", "thin", [(0.41, 0.475), (0.39, 0.53), (0.40, 0.585), (0.445, 0.625), (0.52, 0.645), (0.595, 0.635)]))
    S.append(("black", "thin", [(0.455, 0.46), (0.52, 0.45), (0.585, 0.465), (0.635, 0.50), (0.655, 0.55)]))
    # bustle (drooping tail plumes)
    S.append(("black", "thin", [(0.655, 0.55), (0.69, 0.60), (0.71, 0.655)]))
    S.append(("black", "thin", [(0.635, 0.575), (0.665, 0.625), (0.68, 0.675)]))
    S.append(("black", "thin", [(0.595, 0.635), (0.625, 0.66), (0.645, 0.69)]))
    # wing hatch
    S.append(("black", "thin", [(0.48, 0.50), (0.545, 0.535), (0.60, 0.575)]))
    # long legs + feet
    S.append(("black", "thin", [(0.475, 0.645), (0.468, 0.74), (0.46, 0.892)]))
    S.append(("black", "thin", [(0.545, 0.648), (0.553, 0.745), (0.562, 0.892)]))
    S.append(("black", "thin", [(0.43, 0.895), (0.46, 0.89), (0.49, 0.895)]))
    S.append(("black", "thin", [(0.532, 0.895), (0.562, 0.89), (0.592, 0.895)]))
    # sky hint
    S.append(("blue", "thin", [(0.66, 0.12), (0.78, 0.115), (0.88, 0.12)]))
    return S


def owl():  # Thomas — front-facing, yellow eyes, speckles
    S = []
    # branch
    S.append(("black", "thin", [(0.16, 0.78), (0.50, 0.765), (0.84, 0.745)]))
    S.append(("green", "thick", [(0.69, 0.72), (0.745, 0.705)]))
    # big round head outline
    S.append(("black", "thin", [(0.36, 0.34), (0.39, 0.27), (0.46, 0.235), (0.54, 0.235), (0.61, 0.27), (0.64, 0.34)]))
    # body outline down to branch
    S.append(("black", "thin", [(0.36, 0.34), (0.335, 0.43), (0.34, 0.53), (0.375, 0.63), (0.43, 0.70), (0.50, 0.725)]))
    S.append(("black", "thin", [(0.64, 0.34), (0.665, 0.43), (0.66, 0.53), (0.625, 0.63), (0.57, 0.70), (0.50, 0.725)]))
    # facial discs (two arcs around eyes)
    S.append(("black", "thin", [(0.40, 0.40), (0.385, 0.345), (0.41, 0.295), (0.46, 0.28)]))
    S.append(("black", "thin", [(0.60, 0.40), (0.615, 0.345), (0.59, 0.295), (0.54, 0.28)]))
    # yellow eyes + black pupils
    S.append(("yellow", "thick", [(0.435, 0.345), (0.452, 0.34)]))
    S.append(("yellow", "thick", [(0.548, 0.345), (0.565, 0.34)]))
    S.append(("black", "thin", [(0.444, 0.345), (0.448, 0.343)]))
    S.append(("black", "thin", [(0.556, 0.345), (0.56, 0.343)]))
    # beak (small v)
    S.append(("black", "thin", [(0.485, 0.385), (0.50, 0.405), (0.515, 0.385)]))
    # chest speckles
    for u, v in [(0.44, 0.50), (0.52, 0.485), (0.585, 0.515), (0.46, 0.575),
                 (0.545, 0.565), (0.49, 0.64), (0.565, 0.625), (0.42, 0.545)]:
        S.append(("black", "thin", [(u, v), (u + 0.018, v + 0.012)]))
    # ear tufts hint
    S.append(("black", "thin", [(0.405, 0.265), (0.39, 0.235)]))
    S.append(("black", "thin", [(0.595, 0.265), (0.61, 0.235)]))
    # feet on branch
    S.append(("yellow", "thin", [(0.455, 0.73), (0.45, 0.765)]))
    S.append(("yellow", "thin", [(0.545, 0.73), (0.55, 0.762)]))
    # moon hint (it's an owl)
    S.append(("yellow", "thick", [(0.80, 0.16), (0.83, 0.145), (0.86, 0.16)]))
    return S


def guillemot():  # Tina — chunky dark seabird, white belly, red feet, on a rock
    S = []
    # rock
    S.append(("black", "thin", [(0.30, 0.78), (0.42, 0.745), (0.58, 0.74), (0.70, 0.77), (0.74, 0.81)]))
    S.append(("green", "thin", [(0.34, 0.77), (0.42, 0.755)]))
    # head + back (thick dark mass, facing left)
    S.append(("black", "thick", [(0.345, 0.36), (0.40, 0.335), (0.46, 0.345)]))
    S.append(("black", "thick", [(0.35, 0.39), (0.42, 0.375), (0.48, 0.39)]))
    S.append(("black", "thick", [(0.46, 0.40), (0.53, 0.43), (0.59, 0.48)]))
    S.append(("black", "thick", [(0.475, 0.445), (0.545, 0.485), (0.60, 0.535)]))
    # wing fold
    S.append(("black", "thick", [(0.50, 0.50), (0.555, 0.55), (0.60, 0.60)]))
    S.append(("black", "thin", [(0.60, 0.48), (0.625, 0.545), (0.625, 0.615), (0.60, 0.665)]))
    # bill (short, pointed)
    S.append(("black", "thin", [(0.345, 0.37), (0.285, 0.385)]))
    # white breast/belly outline (left white)
    S.append(("black", "thin", [(0.35, 0.40), (0.335, 0.46), (0.34, 0.535), (0.37, 0.615), (0.425, 0.675), (0.49, 0.70), (0.555, 0.695), (0.60, 0.665)]))
    # eye (tiny white dot in dark head)
    S.append(("white", "thin", [(0.40, 0.36), (0.408, 0.358)]))
    # red feet on rock
    S.append(("red", "thin", [(0.46, 0.705), (0.455, 0.74)]))
    S.append(("red", "thin", [(0.52, 0.705), (0.525, 0.738)]))
    S.append(("red", "thin", [(0.435, 0.745), (0.46, 0.74), (0.482, 0.745)]))
    S.append(("red", "thin", [(0.503, 0.743), (0.527, 0.738), (0.55, 0.743)]))
    # sea hint
    S.append(("blue", "thin", [(0.10, 0.86), (0.30, 0.855), (0.52, 0.86)]))
    S.append(("blue", "thin", [(0.58, 0.875), (0.74, 0.87), (0.90, 0.875)]))
    return S


def pigeon():  # Bear / Toby — rock dove, green neck sheen, two wingbars, red feet
    S = []
    # ground
    S.append(("green", "thick", [(0.20, 0.84), (0.5, 0.835), (0.80, 0.84)]))
    # head + neck + chest outline (facing left)
    S.append(("black", "thin", [(0.345, 0.33), (0.375, 0.295), (0.42, 0.285), (0.455, 0.305)]))
    S.append(("black", "thin", [(0.345, 0.33), (0.335, 0.375), (0.345, 0.43), (0.375, 0.50), (0.41, 0.565), (0.455, 0.625), (0.51, 0.665)]))
    # back and tail
    S.append(("black", "thin", [(0.455, 0.305), (0.52, 0.335), (0.585, 0.39), (0.63, 0.455)]))
    S.append(("black", "thick", [(0.63, 0.455), (0.69, 0.535), (0.745, 0.615)]))
    S.append(("black", "thin", [(0.51, 0.665), (0.585, 0.66), (0.655, 0.63), (0.70, 0.595)]))
    # bill + cere + eye
    S.append(("black", "thin", [(0.345, 0.315), (0.30, 0.325)]))
    S.append(("white", "thin", [(0.347, 0.312), (0.355, 0.308)]))
    S.append(("red", "thin", [(0.385, 0.315), (0.392, 0.312)]))
    # green iridescent neck
    S.append(("green", "thick", [(0.38, 0.36), (0.41, 0.375), (0.435, 0.395)]))
    S.append(("green", "thick", [(0.375, 0.40), (0.405, 0.415), (0.43, 0.435)]))
    # folded wing outline + two black wingbars
    S.append(("black", "thin", [(0.45, 0.40), (0.52, 0.43), (0.585, 0.485), (0.63, 0.545)]))
    S.append(("black", "thick", [(0.48, 0.50), (0.545, 0.545), (0.60, 0.59)]))
    S.append(("black", "thick", [(0.46, 0.565), (0.515, 0.605), (0.565, 0.645)]))
    # red feet
    S.append(("red", "thin", [(0.475, 0.67), (0.47, 0.715), (0.462, 0.755)]))
    S.append(("red", "thin", [(0.525, 0.675), (0.528, 0.715), (0.533, 0.752)]))
    S.append(("red", "thin", [(0.435, 0.758), (0.462, 0.752), (0.49, 0.758)]))
    S.append(("red", "thin", [(0.508, 0.756), (0.533, 0.75), (0.558, 0.756)]))
    # sky hint
    S.append(("blue", "thin", [(0.68, 0.13), (0.80, 0.125), (0.90, 0.13)]))
    return S


PORTRAITS = {
    "mockingbird": mockingbird,
    "crane": crane,
    "owl": owl,
    "guillemot": guillemot,
    "pigeon_bear": pigeon,
    "pigeon_toby": lambda: mirror(pigeon()),
}

if __name__ == "__main__":
    for name, fn in PORTRAITS.items():
        art = fn()
        save(art, 265, f"{BASE}/portrait_{name}.png", scale_to=400)
        print(f"{name}: {len(art)} strokes")

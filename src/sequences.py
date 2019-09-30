import numpy as np

def practice_0back():
    s = ['64_yellow_triangle.png', '55_red_trapezoid.png', '44_pink_heart.png', '38_magenta_octagon.png',
         '29_green_moon.png', '20_cyan_heart.png', '11_brown_diamond.png', '10_brown_cross.png',
         '4_blue_heart.png', '1_blue_circle.png', '10_brown_cross.png', '20_cyan_heart.png',
         '27_green_diamond.png', '37_magenta_moon.png', '44_pink_heart.png', '54_red_octagon.png']

    return s


def practice_2back():
    s = ['1_blue_circle.png', '12_brown_heart.png', '57_yellow_circle.png', '52_red_heart.png',
         '48_pink_triangle.png', '61_yellow_moon.png','39_magenta_trapezoid.png', '27_green_diamond.png',
         '18_cyan_cross.png', '11_brown_diamond.png', '14_brown_octagon.png', '24_cyan_triangle.png',
         '14_brown_octagon.png', '19_cyan_diamond.png', '10_brown_cross.png', '3_blue_diamond.png']

    r = [0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1]

    return s, r


def seq_2back(files_lst, total_stimuli):
    lst = files_lst

    # Generating a random list of expected responses.
    # The stimuli/target sequence is generated based on this list.
    # 0 => not a target  1=> target.
    op = [1]*12 + [0]*(total_stimuli-14)
    np.random.shuffle(op)
    op = np.pad(op,(2,0), 'constant')

    final_lst = []

    # Since this is 2-back, the first two elements cant be targets.
    for i in range(2):
        final_lst.append(np.random.choice(lst))

    for i in range(2, len(lst)):
        if op[i] == 0:
            shape = final_lst[i-2].split('_')[2]
            color = final_lst[i-1].split('_')[1]
            possible = np.random.choice(list(filter(lambda x: shape not in x and color not in x, lst)))
        elif op[i] == 1:
            shape = final_lst[i-2].split('_')[2]
            color = final_lst[i-1].split('_')[1]
            possible = np.random.choice(list(filter(lambda x: shape in x and color not in x, lst)))

        final_lst.append(possible)

    return final_lst, op


if __name__ == '__main__':
    lst = ['29_green_moon.png', '22_cyan_octagon.png', '11_brown_diamond.png', '36_magenta_heart.png', '30_green_octagon.png', '14_brown_octagon.png', '50_red_cross.png', '33_magenta_circle.png', '10_brown_cross.png', '51_red_diamond.png', '47_pink_trapezoid.png', '39_magenta_trapezoid.png', '16_brown_triangle.png', '13_brown_moon.png', '58_yellow_cross.png', '23_cyan_trapezoid.png', '31_green_trapezoid.png', '21_cyan_moon.png', '20_cyan_heart.png', '19_cyan_diamond.png', '41_pink_circle.png', '4_blue_heart.png', '34_magenta_cross.png', '17_cyan_circle.png', '53_red_moon.png', '2_blue_cross.png', '64_yellow_triangle.png', '40_magenta_triangle.png', '43_pink_diamond.png', '26_green_cross.png', '3_blue_diamond.png', '27_green_diamond.png', '32_green_triangle.png', '35_magenta_diamond.png', '49_red_circle.png', '1_blue_circle.png', '55_red_trapezoid.png', '62_yellow_octagon.png', '60_yellow_heart.png', '12_brown_heart.png', '28_green_heart.png', '59_yellow_diamond.png', '9_brown_circle.png', '6_blue_octagon.png', '38_magenta_octagon.png', '8_blue_triangle.png', '18_cyan_cross.png', '54_red_octagon.png', '63_yellow_trapezoid.png', '61_yellow_moon.png', '7_blue_trapezoid.png', '52_red_heart.png', '45_pink_moon.png', '48_pink_triangle.png', '5_blue_moon.png', '57_yellow_circle.png', '44_pink_heart.png', '15_brown_trapezoid.png', '37_magenta_moon.png', '56_red_triangle.png', '24_cyan_triangle.png', '42_pink_cross.png', '46_pink_octagon.png', '25_green_circle.png']
    s, q = seq_2back(lst, 64)
    for idx, item in enumerate(s):
        print(idx, '\t', item, '\t', q[idx])

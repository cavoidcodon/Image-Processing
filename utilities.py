import cv2
import numpy as np
MIN_DISTANCE = 7
ANSWER_REGION_SIZE = 12
WINDOW_SIZE = 15
MIN_VAL = 235


# find interest point in given area
# use for find mark point in top left and right of multiple choice paper
# mark point is the point with the result of the convolution between area and kernel is min
# param: + area for find
#        + window_size for convolution in th area
# return: coordinate of mark point
def find_interested_point(area, window_size=9):
    fil_img = cv2.blur(area, (window_size, window_size))
    area_width = fil_img.shape[1]
    area_height = fil_img.shape[0]
    min_value = fil_img[0, 0]
    min_idx = 0
    min_idy = 0
    for m in range(0, area_width-1):
        for n in range(0, area_height-1):
            if fil_img[n][m] <= min_value:
                min_value = fil_img[n][m]
                min_idx = m
                min_idy = n
    return min_idx, min_idy, min_value


# find mark point for student id, answer
# param: + image of the answer paper
#        + the mark point at the top right
def find_coordinate(image, mark_point):
    height = image.shape[0]
    width = image.shape[1]
    x = mark_point[0]
    y = mark_point[1]

    offset = 50
    trans_point = []
    lines_pos = []
    id_pos = []
    mcp_pos = []

    # offset for eliminate first point
    for k in range(y+offset, height-1):
        if int(image[k][x]) - int(image[k-1][x]) != 0:
            trans_point.append(k)

    # distance of two change point > MIN_DISTANCE
    # to ensure that point is mark point
    for k in range(0, len(trans_point) - 1, 2):
        if trans_point[k + 1] - trans_point[k] > MIN_DISTANCE:
            lines_pos.append(trans_point[k])

    id_end_pos = lines_pos[10]
    trans_point = []
    for k in range(x-offset, int(width/2), -1):
        if int(image[id_end_pos][k]) - int(image[id_end_pos][k + 1]) != 0:
            trans_point.append(k)

    for k in range(0, len(trans_point) - 1, 2):
        if trans_point[k] - trans_point[k + 1] > MIN_DISTANCE:
            id_pos.append(int((trans_point[k] + trans_point[k + 1])/2))

    mcp_end_pos = lines_pos[37]
    trans_point = []
    for k in range(x-offset, 0, -1):
        if int(image[mcp_end_pos][k]) - int(image[mcp_end_pos][k+1]) != 0:
            trans_point.append(k)

    for k in range(0, len(trans_point) - 1, 2):
        if trans_point[k] - trans_point[k + 1] > MIN_DISTANCE:
            mcp_pos.append(int((trans_point[k] + trans_point[k + 1])/2))

    return lines_pos, id_pos, mcp_pos


def get_id(image, line_coor, id_coor):
    sbd = np.zeros((10, 9), np.uint8)

    for i in range(0, 9):
        for j in range(0, 10):
            region = image[line_coor[j] - ANSWER_REGION_SIZE:line_coor[j] + ANSWER_REGION_SIZE,
                     id_coor[i] - ANSWER_REGION_SIZE:id_coor[i] + ANSWER_REGION_SIZE]
            min_val = int(np.mean(region))
            if min_val < MIN_VAL:
                sbd[j][i] = 1

    for i in range(0, 10):
        sbd[i] = list(reversed(sbd[i]))

    return sbd


def get_answer(image, line_coor, ans_coor):
    answer = np.zeros((25, 8), np.uint8)

    for i in range(0, 8):
        for j in range(0, 25):
            region = image[line_coor[12 + j] - ANSWER_REGION_SIZE:line_coor[12 + j] + ANSWER_REGION_SIZE,
                     ans_coor[i] - ANSWER_REGION_SIZE:ans_coor[i] + ANSWER_REGION_SIZE]
            min_val = int(np.mean(region))
            print(min_val)
            if min_val < MIN_VAL:
                answer[j][i] = 1

    for i in range(0, 25):
        answer[i] = list(reversed(answer[i]))

    return answer


def read_student_id(id_matrix):
    student_id = ''

    for j in range(0, 6):
        flag = 0
        for i in range(0, 10):
            if id_matrix[i][j] == 1:
                if flag == 0:
                    student_id += str(i)
                    flag = 1
                else:
                    student_id = 'INVALID'
                    break
        if student_id == 'INVALID' or flag == 0:
            student_id = 'INVALID_ID'
            break

    return student_id


def read_test_id(id_matrix):
    test_id = ''

    for j in range(6, 9):
        flag = 0
        for i in range(0, 10):
            if id_matrix[i][j] == 1:
                if flag == 0:
                    test_id += str(i)
                    flag = 1
                else:
                    test_id = 'INVALID'
                    break
        if test_id == 'INVALID' or flag == 0:
            test_id = 'INVALID_ID'
            break

    return test_id


def read_answer(ans):
    num2ans = ['A', 'B', 'C', 'D']
    answer = []
    for i in range(0, 50):
        answer.append('N')

    for i in range(0, 25):
        flag_1 = 0
        flag_2 = 0
        for j in range(0, 4):
            if ans[i][j] == 1:
                if flag_1 == 0:
                    answer[i] = num2ans[j]
                    flag_1 = 1
                else:
                    answer[i] = 'I'
                    break

            if ans[i][j + 4] == 1:
                if flag_2 == 0:
                    answer[25 + i] = num2ans[j]
                    flag_2 = 1
                else:
                    answer[25 + i] = 'I'
                    break

    return answer

import cv2
import numpy as np
import math
from scipy import misc, ndimage
import random


def resize(image):
    """将img1的大小重塑为宽度为900的图像"""
    height = image.shape[0]  # 形状的第一维度--长
    width = image.shape[1]  # 形状的第二维度--宽
    x = height / width

    # print(height, width, x)
    dim = (900, int(900 * x))  # 指定尺寸w*h
    # print(dim)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)  # 这里采用的插值法是INTER_LINEAR
    return resized


def hough(image):
    """霍夫校正"""
    resized = resize(image)  # 重新定义图片大小
    # cv2.imshow("resize", resized)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(resized, 50, 150, apertureSize=3)  # canny边缘检测
    # cv2.imshow("edges", edges)
    # 霍夫变换
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 0)
    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        if x1 == x2 or y1 == y2:
            continue
    t = float(y2 - y1) / (x2 - x1)
    rotate_angle = math.degrees(math.atan(t))
    if rotate_angle > 45:
        rotate_angle = -90 + rotate_angle
    elif rotate_angle < -45:
        rotate_angle = 90 + rotate_angle
    rotate_img = ndimage.rotate(resized, rotate_angle)
    # misc.imsave('F:/mydjsite/ecg_test/result/hough.jpg', rotate_img)

    # cv2.imshow('gray', gray)
    # cv2.imshow('edges', edges)
    # cv2.imshow('rotate_img', rotate_img)
    return rotate_img


def remove_red(image):
    """红色背景去除"""
    cols, rows, _ = image.shape  # 获取图片高宽
    B_channel, G_channel, R_channel = cv2.split(image)  # 注意cv2.split()返回通道顺序

    # cv2.imshow('Blue channel', B_channel)
    # cv2.imshow('Green channel', G_channel)
    # cv2.imshow('Red channel', R_channel)

    # 红色通道阈值(调节好函数阈值为160时效果最好，太大一片白，太小干扰点太多)
    _, RedThresh = cv2.threshold(R_channel, 200, 255, cv2.THRESH_BINARY_INV)
    # RedThresh = local_threshold_demo2(R_channel)

    # 膨胀操作（可以省略）
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    erode = cv2.erode(RedThresh, element)
    # cv2.imshow("RedThresh", RedThresh)

    return RedThresh


def wavethin(src, iterations):
    """曲线细化"""
    dst = src[::, ::]
    # print(dst)
    n = 0
    i = 0
    j = 0
    for n in range(iterations):
        t_image = dst[::, ::]
        for j in range(src.shape[0]):
            for i in range(src.shape[1]):
                # print(i)
                if (t_image[j, i] == 255):
                    # print(t_image[j, i])
                    ap = 0
                    p2 = 0 if i == 0 else int(t_image[j, i - 1])
                    p3 = 0 if (i == 0 or j == src.shape[0] - 1) else int(t_image[j + 1, i - 1])
                    if p2 == 0 and p3 == 255:
                        ap = ap + 1
                    p4 = 0 if j == src.shape[0] - 1 else int(t_image[j + 1, i])
                    if p3 == 0 and p4 == 255:
                        ap = ap + 1
                    p5 = 0 if (i == src.shape[1] - 1 or j == src.shape[0] - 1) else int(t_image[j + 1, i + 1])
                    if p4 == 0 and p5 == 255:
                        ap = ap + 1
                    p6 = 0 if (i == src.shape[1] - 1) else int(t_image[j, i + 1])
                    if p5 == 0 and p6 == 255:
                        ap = ap + 1
                    p7 = 0 if (i == src.shape[1] - 1 or j == 0) else int(t_image[j - 1, i + 1])
                    if p6 == 0 and p7 == 255:
                        ap = ap + 1
                    p8 = 0 if (j == 0) else int(t_image[j - 1, i])
                    if p7 == 0 and p8 == 255:
                        ap = ap + 1
                    p9 = 0 if (i == 0 or j == 0) else int(t_image[j - 1, i - 1])
                    if p8 == 0 and p9 == 255:
                        ap = ap + 1
                    if p9 == 0 and p2 == 255:
                        ap = ap + 1
                    if p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 > 255 and p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 < 1785:
                        # print(p2+p3+p4+p5+p6+p7+p8+p9)
                        if ap == 1:
                            if p2 * p4 * p8 == 0:
                                if p2 * p6 * p8 == 0:
                                    # print(dst[j,i])
                                    dst[j, i] = 0
    return dst


# 自适应阈值-----------可试试，效果见：https://blog.csdn.net/fly_wt/article/details/84391797
def local_threshold_demo1(image):
    """自适应阈值化demo_1"""
    cv2.imshow("origin", image)

    blur = cv2.GaussianBlur(image, (17, 17), 0)  # 高斯模糊
    blurred = cv2.pyrMeanShiftFiltering(image, 5, 15)  # 边缘保留滤波
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    dst = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 21)
    # cv2.imshow('threshold image', dst)
    return dst


def local_threshold_demo2(img):
    """自适应阈值化demo_2"""
    im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst1 = cv2.adaptiveThreshold(im_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 12)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))  # 定义结构元素
    dst = cv2.morphologyEx(dst1, cv2.MORPH_OPEN, kernel)  # 开运算
    # cv2.imshow("open", dst)
    return dst


def adaptiveThresh(I, winSize, ratio=0.15):
    """自适应阈值化demo_3"""
    # 灰度化
    I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
    # 均值平滑
    I_mean = cv2.boxFilter(I, cv2.CV_32FC1, winSize)
    # 原图与平滑结果做差
    out = I - (1.0 - ratio) * I_mean
    # 差值>=0输出255，反之0
    out[out >= 0] = 0
    out[out < 0] = 255
    out = out.astype(np.uint8)
    return out


def canny_sz(image):
    """Canny算子边缘提取"""
    image = cv2.GaussianBlur(image, (3, 3), 0)
    canny = cv2.Canny(image, 50, 150)
    return canny


# -------------------------------------数据提取---------------------------------------
def findNextPoint(neighbor_points, inputimg, this_point, this_flag):
    """继续找点"""
    i = this_flag
    count = 1
    a = ()
    height = inputimg.shape[0]
    width = inputimg.shape[1]
    next_flag2 = 0
    line = []
    while (True):
        a = neighbor_points[i]
        addx = a[0]
        addy = a[1]
        x = this_point[0]
        y = this_point[1]
        new_point1 = (x + addx, y + addy)
        while (count <= 7):
            next_point2 = None
            if (new_point1[0] > 0 and new_point1[1] > 0 and new_point1[0] < height and new_point1[1] < width):
                if (inputimg[x, y] == 0):  # 想给黑线赋予颜色，用0，想给白线赋予颜色，用255
                    next_point2 = new_point1
                    next_flag2 = i
                    break
            if (count % 2):
                i += count
                if (i > 7):
                    i -= 8
            else:
                i += -count
                if (i < 0):
                    i += 8
            count += 1
        if (count >= 8):
            break
        else:
            this_point = next_point2
            this_flag = next_flag2
            line.append(next_point2)
    return line


def findFirstPoint(inputimg):
    """起始点"""
    first_point = []
    height = inputimg.shape[0]
    width = inputimg.shape[1]
    for i in range(height):
        for j in range(width):
            if (inputimg[i, j] == 255):  # 想给黑线赋予颜色，用0，想给白线赋予颜色，用255
                first_point.append((i, j))
    return first_point


def findLines(inputimg):
    """找曲线"""
    lines = []
    neighbor_points = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    first_point = findFirstPoint(inputimg)
    for this_point in first_point:
        this_point1 = this_point
        line = []
        line.append(this_point)
        this_flag = 0
        # next_point=()
        # next_flag=0
        line = line + findNextPoint(neighbor_points, inputimg, this_point, this_flag)
        this_point = this_point1
        this_flag = 0
        line = line + findNextPoint(neighbor_points, inputimg, this_point, this_flag)
        lines.append(line)
    # print(lines)
    return lines


def draw_wave(image, back):
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray", gray)
    lines = []
    back = resize(back)
    lines = findLines(image)
    color = (0, 0, 0)  # 这里可以颜色，赋予红色
    # color = (random.randrange(256),random.randrange(256),random.randrange(256)) # 随机赋予颜色
    px = []
    py = []
    for line in lines:
        for i in line:
            x = i[0]
            y = i[1]
            back[x, y] = color
            px.append(x)
            py.append(y)
    # cv2.imshow("result", back)
    # cv2.imwrite('img123.jpg',image)
    print("lines: %s" % lines)
    return back, lines
# ------------------------------------数据提取END-------------------------------------


def start(imgs):
    imgs = resize(imgs)
    backimg = cv2.imread("F:/newpro/mydjsite/media/temp/grid.png")  # 背景图片
    adimg = adaptiveThresh(imgs, (51, 51), 0.15)  # 有波峰good
    # print("adimg%s" % adimg)
    # cv2.imshow("adimg", adimg)
    img3 = wavethin(adimg, 3)
    result, lines = draw_wave(img3, backimg)
    # cv2.imshow("Thin_img2", img3)
    return result, lines


# if __name__ == '__main__':
#     img = cv2.imread("C:/Users/po/Desktop/ecgimg/ecg3.jpg")
#     backimg = cv2.imread("F:/newpro/mydjsite/media/temp/grid.png")  # 背景图片
#     img = resize(img)
#     backimg = resize(backimg)
#     # print(img.shape[0])
#     imgs = resize(img)
#     # cv.imshow("resize", imgs)
#
#     # ----------------------------------------有红色网格的---------------------------------------
#     # image0 = cv2.imread("C:/Users/po/Desktop/ecgimg/ecg11.jpg", cv2.IMREAD_COLOR)  # 以BGR色彩读取图片
#     # image = resize(image0)  # 缩小图片
#     # remove_red(imgs)
#
#     # ---------------------------------------二值化+细化方案1-------------------------------------
#     # img1 = local_threshold_demo1(imgs)  # 较好的自适应二值化---波峰无
#     # cv2.imshow("adaptthreshold", img1)
#     # img2 = wavethin(img1, 3)
#     # cv2.imshow("Thin_img1", img2)
#
#     # ----------------------------------------二值化+细化方案2--------------------------------------
#     adimg = adaptiveThresh(imgs, (51, 51), 0.15)  # 有波峰good
#     # print("adimg%s" % adimg)
#     cv2.imshow("adimg", adimg)
#     img3 = wavethin(adimg, 3)
#     draw_wave(img3, backimg)
#     cv2.imshow("Thin_img2", img3)
#
#     # ----------------------very good-----------二值化+细化方案3--------------------------------------
#     # csimg = local_threshold_demo2(imgs)  # 自定义阈值化结果也不错
#     # # print("img%s" % csimg)
#     # cv2.imshow("adimg", csimg)
#     # csimg1 = quyu_cut(csimg)
#     # # print(csimg1)
#     # img4 = wavethin(csimg1, 3)
#     # cv2.imshow("Thin_img3", img4)
#
#     # # ----------------失败------------------高斯模糊边缘提取-------------------------------------
#     # imgcn = cv2.GaussianBlur(imgs, (3, 3), 0)
#     # canny = cv2.Canny(imgcn, 50, 150)
#     # print(canny)
#     # img3 = wavethin(canny, 3)
#     # cv2.imshow("canny3", canny)
#     # cv2.imshow("Thin_img3", img3)
#
#     # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 文献二值化法，不适用于有阴影的图
#     # img = cvThresholdOtsu(img)  # 二值化没问题
#     # cv2.imshow("cvThresholdOtsu", img)
#     # print(img)
#
#     # img2 = wavethin(img1, 3)
#     # cv2.imshow("Thin_img", img2)
#     # sq = findSquares(imgs)  # 参数可能有一些问题
#     # print(sq)
#     # draws = drawSquares(imgs, sq)
#
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

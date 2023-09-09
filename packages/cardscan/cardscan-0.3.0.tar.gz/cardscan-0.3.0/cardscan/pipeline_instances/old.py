#!/usr/bin/env python3

gauss = Transform(
    lambda img, *_: cv2.GaussianBlur(img, (5, 5), 0),
    label="gauss",
    debug=lambda arg, *_: [arg],
)


increase_contrasts_transform = Transform(
    lambda img, *_: cv2.convertScaleAbs(img, alpha=3, beta=0),
    label="Increase contrasts",
    debug=lambda img, *_: [img],
)

laplacian_transform = Transform(
    lambda img, *_: cv2.Laplacian(img, cv2.CV_8U, ksize=3, scale=2, delta=2),
    label="Laplacian",
    debug=lambda img, *_: [img],
)

canny_transform = Transform(
    lambda img, *_: cv2.Canny(img, threshold1=150, threshold2=255, apertureSize=3),
    label="Canny",
    debug=lambda arg, *_: [arg],
)

filter_contours_shape_size = Transform(
    lambda contours_def, *_: (
        filter_contours_by_size(contours_def[0]),
        contours_def[1],
    ),
    label="Filter contour by size",
    debug=debug_contours_map_def,
)

filter_surronding_contours = Transform(
    lambda contours_def, *_: filter_containing_contours(
        contours_def[0], contours_def[1]
    ),
    label="Filter containing contours",
    debug=debug_contours,
)


def threshold_transform(img, *_):
    ret2, mask = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    return mask


def remove_color(img):
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for color (excluding gray)
    lower_bound = np.array([0, 40, 0])  # Hue 0-179, Saturation 40-255, Value 0-255
    upper_bound = np.array([255, 255, 255])

    # Create a mask to identify colored pixels within the specified range
    color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Replace the identified color with black
    img[color_mask > 0] = [0, 0, 0]  # Replace with black (0,0,0)
    return img


remove_color_transform = Transform(
    lambda img, *_: remove_color(img),
    label="Remove color",
    debug=lambda img, *_: [img],
)


def filter_containing_contours(contour_map, hierarchy):
    """Unefficient algrorithm to filter the most nested contours."""
    for i in list(contour_map.keys()):
        current_index = i
        while hierarchy[0][current_index][3] > 0:
            if hierarchy[0][current_index][3] in contour_map.keys():
                contour_map.pop(hierarchy[0][current_index][3])
            current_index = hierarchy[0][current_index][3]

    return list(contour_map.values())


## Comparison function for sorting contours
# def get_contour_precedence(contour, cols):
#    # USAGE: final_contour_list.sort(key=lambda x: get_contour_precedence(x, binary.shape[1]))
#    tolerance_factor = 200
#    origin = cv2.boundingRect(contour)
#    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def filter_contours_by_size(contours, min_size: int = 2000):
    contour_map = {}

    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) > min_size:
            if calc_solidity(contours[i]) > 0.85:
                contour_map[i] = contours[i]

    return contour_map

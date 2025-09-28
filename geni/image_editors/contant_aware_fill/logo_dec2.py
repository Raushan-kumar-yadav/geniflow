import cv2

# Load images
main_image = cv2.imread('image2.jpg', 0)
template = cv2.imread('logooffb.jpg', 0)

# Create ORB detector
orb = cv2.ORB_create()

# Detect keypoints and descriptors
kp1, des1 = orb.detectAndCompute(main_image, None)
kp2, des2 = orb.detectAndCompute(template, None)

# Match features
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)

# Draw matches
matched_image = cv2.drawMatches(main_image, kp1, template, kp2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv2.imshow('Matches', matched_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

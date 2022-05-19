import cv2


class SkinModule:

    def __init__(self):
        self.hueRange = [0, 255]
        self.valRange = [0, 255]
        self.bucket_size = 10
        self.num_buckets = 255//self.bucket_size

    #
    #   Value (V channel)
    #

    def filterVal(self, img):
        return cv2.inRange(img, self.valRange[0], self.valRange[1])


    def valRangeLength(self):
        return self.valRange[1] - self.valRange[0]


    def calculateValThresh(self):
        minVrange = 40
        minT = 30
        maxT = 100
        vlen = self.valRangeLength()
        if vlen < minVrange:
            return minT
        koef = (maxT - minT) / (255 - minVrange)
        return int(koef * (vlen - minVrange)) + minT


    def calculateNewValRange(self, img):
        hist = cv2.calcHist([img], [0], None, [self.num_buckets], [1, 255])

        points = [h[0] for h in hist]

        peak = points.index(max(points)) + 1
        peak = peak * self.bucket_size

        new_range = [(peak - 2 * self.bucket_size),
                     max(255, peak + 2 * self.bucket_size)]

        self.valRange = new_range


    #
    #   Hue (H channel)
    #


    def filterHue(self, img):
        if self.hueRange[1] > self.hueRange[0]:
            return cv2.inRange(img, self.hueRange[0], self.hueRange[1])

        return cv2.bitwise_not(cv2.inRange(img, self.hueRange[1], self.hueRange[0]))


    def hueRangeLength(self):
        if self.hueRange[1] > self.hueRange[0]:
            return self.hueRange[1] - self.hueRange[0]

        return 255 - self.hueRange[0] + self.hueRange[1]


    def calculateHueThresh(self):
        minHrange = 40
        minT = 40
        maxT = 100
        hrange = self.hueRangeLength()
        if hrange < minHrange:
            return minT
        koef = (maxT - minT) / (255 - minHrange)
        return int(koef * (hrange - minHrange)) + minT


    def calculateNewHueRange(self, img):
        hist = cv2.calcHist([img], [0], None, [self.num_buckets], [1, 255])

        points = [h[0] for h in hist]

        peak = points.index(max(points)) + 1
        peak = peak * self.bucket_size

        new_range = [(peak - 2 * self.bucket_size) % 255,
                     (peak + 2 * self.bucket_size) % 255]

        self.hueRange = new_range

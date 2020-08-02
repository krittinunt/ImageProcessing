from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.pyplot import *

import numpy as np
import cv2
import sys

class ImageView(QGraphicsView):
    def __init__(self, width=100, height=100):
        super(ImageView, self).__init__()
        self._width = width
        self._height = height

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._scene.setBackgroundBrush(Qt.black)
        self.setSceneRect(0, 0, self._width, self._height)

    def setCVImage(self, imageData):
        height, width, channel = imageData.shape
        bytesPerLine = 3 * width
        image = QImage(imageData.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self.setSceneRect(0, 0, self._width, self._height)
        self._imagePixmap = QPixmap.fromImage(image)

        self._scene.clear()
        self._scene.addPixmap(self._imagePixmap)
        self._scene.update()

    def setCVGrayImage(self, imageData):
        height, width = imageData.shape
        image = QImage(imageData.data, width, height, QImage.Format_Grayscale8)
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self.setSceneRect(0, 0, self._width, self._height)
        self._imagePixmap = QPixmap.fromImage(image)
        self._scene.clear()
        self._scene.addPixmap(self._imagePixmap)
        self._scene.update()

class UIWidget(QWidget):
    def __init__(self):
        super(UIWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel('RAW Image')
        self.rawImageView = ImageView(width=250, height=250)

        sub_layout = QVBoxLayout()
        sub_layout.addWidget(label)
        sub_layout.addWidget(self.rawImageView)
        layout.addLayout(sub_layout)

        label = QLabel('')
        label.setFixedWidth(50)
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(label)
        layout.addLayout(sub_layout)

        label = QLabel('Process Image')
        self.processImageView = ImageView(width=250, height=250)

        sub_layout = QVBoxLayout()
        sub_layout.addWidget(label)
        sub_layout.addWidget(self.processImageView)
        layout.addLayout(sub_layout)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.uiwidget = None
        self.rawImage = None
        self.processImage = None

        self.initUI()

    def __del__(self):
        print('quit')
        cv2.destroyAllWindows()

    def initUI(self):
        menubar = self.menuBar()
        menuFile = menubar.addMenu('&File')
        menuFile.addAction('&Open...', self.menuFileOpen_clicked)
        menuFile.addSeparator()
        menuFile.addAction('&Quit', self.menuFileQuit_clicked)
        menuEdit = menubar.addMenu('&Edit')
        menuEdit.addAction('&Copy', self.menuEditCopy_clicked)
        menuProcess = menubar.addMenu('&Process')
        menuProcess.addAction('Constant', self.menuProcessConstant_clicked)
        menuProcess.addSeparator()
        menuProcess.addAction('&Gray', self.menuProcessGray_clicked)
        menuProcess.addAction('&HSV', self.menuProcessHSV_clicked)
        menuProcess.addAction('&Mask', self.menuProcessMask_clicked)
        menuProcess.addAction('&Thresholding', self.menuProcessThresholding_clicked)
        menuProcess.addAction('&Adaptive thresholding', self.menuProcessAdaptiveThresholding_clicked)
        menuProcess.addAction('&Otsu\'s thresholding', self.menuProcessOtsusThresholding_clicked)
        menuProcess.addAction('&Otsu\'s Binarization', self.menuProcessOtsusBinarization_clicked)
        menuGeometric = menubar.addMenu('&Geometric')
        menuGeometric.addAction('&Scaling', self.menuGeometricScaling_clicked)
        menuGeometric.addAction('&Translation', self.menuGeometricTranslation_clicked)
        menuGeometric.addAction('&Rotation', self.menuGeometricRotation_clicked)
        menuGeometric.addAction('&Affine transformation', self.menuGeometricAffineTransformation_clicked)
        menuGeometric.addAction('&Perspective transformation', self.menuGeometricPerspectiveTransformation_clicked)
        menuSmoothing = menubar.addMenu('&Smoothing')
        menuSmoothing.addAction('2D &Convolution', self.menuSmoothing2DConvolution_clicked)
        menuSmoothing.addAction('&Averaging', self.menuSmoothingAveraging_clicked)
        menuSmoothing.addAction('&Gaussian', self.menuSmoothingGaussian_clicked)
        menuSmoothing.addAction('&Median Filtering', self.menuSmoothingMedianFiltering_clicked)
        menuSmoothing.addAction('&Bilateral Filtering', self.menuSmoothingBilateralFiltering_clicked)
        menuMorphological = menubar.addMenu('&Morphological')
        menuMorphological.addAction('&Erosion', self.menuMorphologicalErosion_clicked)
        menuMorphological.addAction('&Dilation', self.menuMorphologicalDilation_clicked)
        menuMorphological.addAction('&Opening', self.menuMorphologicalOpening_clicked)
        menuMorphological.addAction('&Closing', self.menuMorphologicalClosing_clicked)
        menuMorphological.addAction('&Morphological Gradient', self.menuMorphologicalMorphologicalGradient_clicked)
        menuMorphological.addAction('&Top Hat', self.menuMorphologicalTopHat_clicked)
        menuMorphological.addAction('&Black Hat', self.menuMorphologicalBlackHat_clicked)
        menuGradients = menubar.addMenu('&Gradients')
        menuGradients.addAction('&Laplacian Derivatives', self.menuGradientsLaplacianDerivatives_clicked)
        menuGradients.addAction('&One Important Matter', self.menuGradientsOneImportantMatter_clicked)
        menuGradients.addAction('&Canny Edge Detection', self.menuGradientsCannyEdgeDetection_clicked)
        

        self.uiwidget = UIWidget()
        self.setCentralWidget(self.uiwidget)

    def menuFileOpen_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open image file...', '', 'Image files (*.png *.jpg *.bmp)')
        if fileName:
            self.rawImage = cv2.imread(fileName)
            self.uiwidget.rawImageView.setCVImage(self.rawImage)

    def menuFileQuit_clicked(self):
        self.close()

    def menuEditCopy_clicked(self):
        self.processImage = self.rawImage
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuProcessConstant_clicked(self):
        value, ok = QInputDialog.getInt(self, 'Add/Sub constant to image', 'Enter value :')
        if ok:
            self.processImage = cv2.add(self.rawImage, value)
            self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuProcessGray_clicked(self):
        self.processImage = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('Gray', self.processImage)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuProcessHSV_clicked(self):
        self.processImage = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2HSV)
        #cv2.imshow('HSV', self.processImage)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuProcessMask_clicked(self):
        hsvImage = cv2.cvtColor(self.rawImage, cv2.COLOR_BGR2HSV)
        lower = np.array([80, 50, 50])
        upper = np.array([100, 255, 255])
        self.processImage = cv2.inRange(hsvImage, lower, upper)
        #cv2.imshow('mask', self.processImage)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuProcessThresholding_clicked(self):
        # cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV, cv2.THRESH_TRUNC, cv2.THRESH_TOZERO, cv2.THRESH_TOZERO_INV
        ret, self.processImage = cv2.threshold(self.rawImage, 127, 255, cv2.THRESH_BINARY)
        #cv2.imshow('Thresholding', self.processImage)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuProcessAdaptiveThresholding_clicked(self):
        # cv2.ADAPTIVE_THRESH_MEAN_C, cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        blurImage = cv2.medianBlur(grayImage, 5)
        self.processImage = cv2.adaptiveThreshold(blurImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        #cv2.imshow('Adaptive thresholding', self.processImage)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuProcessOtsusThresholding_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        blurImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
        ret, self.processImage = cv2.threshold(blurImage, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #cv2.imshow('Otsus thresholding', self.processImage)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuProcessOtsusBinarization_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        blurImage = cv2.GaussianBlur(grayImage, (5, 5), 0)

        # fine normalized histogram
        hist = cv2.calcHist([blurImage], [0], None, [256], [0, 256])
        hist_norm = hist.ravel()/hist.max()
        Q = hist_norm.cumsum()

        bins = np.arange(256)

        fn_min = np.inf
        thresh = -1

        for i in range(1, 256):
            p1, p2 = np.hsplit(hist_norm, [i])
            q1, q2 = Q[i], Q[255] - Q[i]
            b1, b2 = np.hsplit(bins, [i])

            m1, m2 = np.sum(p1*b1)/q1, np.sum(p2*b2)/q2
            v1, v2 = np.sum(((b1-m1)**2)*p1)/q1, np.sum(((b2-m2)**2)*p2)/q2

            fn = v1*q1 + v2*q2
            if fn < fn_min:
                fn_min = fn
                thresh = i

        ret, self.processImage = cv2.threshold(blurImage, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #cv2.imshow('Otsus binarization', self.processImage)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuGeometricScaling_clicked(self):
        self.processImage = cv2.resize(self.rawImage, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuGeometricTranslation_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        rows, cols = grayImage.shape

        M = np.float32([[1, 0, 100], [0, 1, 50]])
        self.processImage = cv2.warpAffine(grayImage, M, (cols, rows))
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuGeometricRotation_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        rows, cols = grayImage.shape

        M = cv2.getRotationMatrix2D((cols/2, rows/2), 90, 1)
        self.processImage = cv2.warpAffine(grayImage, M, (cols, rows))
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuGeometricAffineTransformation_clicked(self):
        rows, cols, ch = self.rawImage.shape

        pts1 = np.float32([[50, 50], [200, 50], [50, 200]])
        pts2 = np.float32([[10, 100], [200, 50], [100, 250]])

        M = cv2.getAffineTransform(pts1, pts2)

        self.processImage = cv2.warpAffine(self.rawImage, M, (cols, rows))
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuGeometricPerspectiveTransformation_clicked(self):
        rows, cols, ch = self.rawImage.shape

        pts1 = np.float32([[56, 65], [368, 52], [28, 387], [389, 390]])
        pts2 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])

        M = cv2.getPerspectiveTransform(pts1, pts2)

        self.processImage = cv2.warpPerspective(self.rawImage, M, (300, 300))
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuSmoothing2DConvolution_clicked(self):
        kernel = np.ones((5, 5), np.float32)/25
        self.processImage = cv2.filter2D(self.rawImage, -1, kernel)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuSmoothingAveraging_clicked(self):
        self.processImage = cv2.blur(self.rawImage, (5, 5))
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuSmoothingGaussian_clicked(self):
        self.processImage = cv2.GaussianBlur(self.rawImage, (5, 5), 0)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuSmoothingMedianFiltering_clicked(self):
        self.processImage = cv2.medianBlur(self.rawImage, 5)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuSmoothingBilateralFiltering_clicked(self):
        self.processImage = cv2.bilateralFilter(self.rawImage, 9, 75, 75)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalErosion_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.erode(self.rawImage, kernal, iterations=1)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalDilation_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.dilate(self.rawImage, kernal, iterations=1)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalOpening_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.morphologyEx(self.rawImage, cv2.MORPH_OPEN, kernal)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalClosing_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.morphologyEx(self.rawImage, cv2.MORPH_CLOSE, kernal)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalMorphologicalGradient_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.morphologyEx(self.rawImage, cv2.MORPH_GRADIENT, kernal)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalTopHat_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.morphologyEx(self.rawImage, cv2.MORPH_TOPHAT, kernal)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuMorphologicalBlackHat_clicked(self):
        kernal = np.ones((5, 5), np.uint8)
        self.processImage = cv2.morphologyEx(self.rawImage, cv2.MORPH_BLACKHAT, kernal)
        self.uiwidget.processImageView.setCVImage(self.processImage)

    def menuGradientsLaplacianDerivatives_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)
        rows, cols = grayImage.shape
        self.processImage = cv2.Laplacian(grayImage, cv2.CV_64F)
        sobelx = cv2.Sobel(grayImage, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(grayImage, cv2.CV_64F, 0, 1, ksize=5)
        cv2.imshow("sobelx", sobelx)
        cv2.imshow("sobely", sobely)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuGradientsOneImportantMatter_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)

        sobelx8u = cv2.Sobel(grayImage, cv2.CV_8U, 1, 0, ksize=5)
        sobelx64f = cv2.Sobel(grayImage, cv2.CV_64F, 1, 0, ksize=5)
        abs_sobel64f = np.absolute(sobelx64f)
        self.processImage = np.uint8(abs_sobel64f)
        cv2.imshow("sobelx8u", sobelx8u)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

    def menuGradientsCannyEdgeDetection_clicked(self):
        grayImage = cv2.cvtColor(self.rawImage, cv2.COLOR_RGB2GRAY)

        self.processImage = cv2.Canny(grayImage, 100, 200)
        self.uiwidget.processImageView.setCVGrayImage(self.processImage)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Test image process 1')
    window.setGeometry(200, 200, 800, 400)
    #window.show()
    window.showMaximized()
    sys.exit(App.exec_())
# QQOcr

A package used for simple OCR.

- Github: https://github.com/SummerColdWind

 - Contact the author: jugking6688@gmail.com 

 - Our bilibili: https://space.bilibili.com/3493127383943735

---

Examples are as follows：

For learn:
```python
from qqocr import QQOcr

# You must provide a method to binarize the characters in the picture 
# and import the external library in the function.
def binary(image):
    import numpy as np
    import cv2

    low_range = np.array([0, 0, 0][::-1])
    high_range = np.array([100, 100, 100][::-1])
    return cv2.inRange(image, low_range, high_range)

qq = QQOcr()
# Dataset folder consists of many pictures and a 'label.txt'.
# For 'label.txt', the format of each line is "[filename]\t[text]".
# For example, it can be: "1.png   12345".
qq.load_dataset('./dataset')
qq.set_binary(binary)
qq.learn()
# The suffix must be '.qmodel'.
qq.save_model('./1.qmodel')
```
For predict:
```python
from qqocr import QQOcr
import cv2

qq = QQOcr()
qq.load_model('./1.qmodel')
text = qq.predict(cv2.imread('test.png'))
print(text)
```







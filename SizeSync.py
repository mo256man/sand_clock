import numpy as np
import cv2
import random
import os
import glob

class ImageObject():
    def __init__(self, filename):
        self.filename = filename
        self.image = cv2.imread(self.filename)
        self.height, self.width = self.image.shape[:2]
        self.has_roi = False
        self.pos = [(0,0) for _ in range(4)]
        self.pos_cnt = 0

class App():
    def __init__(self, path):
        self.files = glob.glob(path)
        self.objects = [ImageObject(file) for file in self.files]
        self.roi_cnt = 0
        self.index = 0
        self.aspect_ratio = 1
        self.master_index = None
        self.mx, self.my = 0, 0
        self.winname = "image"
        cv2.namedWindow(self.winname)
        cv2.setMouseCallback(self.winname, self.mouse_event)

    def show(self):
        obj = self.objects[self.index]
        img = obj.image.copy()
        color = tuple(random.randint(0, 255) for _ in range(3))

        for i in [0, 1]:
            pos1, pos2 = obj.pos[2*i : 2*(i+1)]
            if pos1 == pos2:
                if not obj.has_roi:
                    cv2.line(img, (self.mx, 0), (self.mx, obj.height), color, 1)
                    cv2.line(img, (0, self.my), (obj.width, self.my), color, 1)
            else:
                cv2.rectangle(img, pos1, pos2, color, i+1)

        cv2.imshow(self.winname, img)

    def update_index(self, k=0):
        self.index = (self.index + k) % len(self.files)

    def mouse_event(self, event, x, y, flags, param):
        self.mx, self.my = x, y
        obj = self.objects[self.index]

        if obj.pos_cnt == 0:
            obj.pos[0] = (x, y)
            obj.pos[1] = (x, y)
            if event == cv2.EVENT_LBUTTONDOWN:
                obj.pos_cnt += 1

        elif obj.pos_cnt == 1:
            x0, y0 = obj.pos[0]
            if self.master_index is None:
                # マスター決定未の場合
                obj.pos[1] = (x, y)
                if event == cv2.EVENT_LBUTTONDOWN:
                    if not(x == x0 or y == y0):
                        obj.pos_cnt = 2
                        self.aspect_ratio = (y - y0) / (x - x0)
            else:
                # マスター決定済みの場合
                x1 = x
                y1 = y0 + int((x - x0) * self.aspect_ratio)
                obj.pos[1] = (x1, y1)
                master_obj = self.objects[self.master_index]
                pos0, pos1, pos2, pos3 = master_obj.pos
                scale = (x1 - x0) / (pos1[0] - pos0[0])
                x2 = x0 + int(scale * (pos2[0] - pos0[0]))
                y2 = y0 + int(scale * (pos2[1] - pos0[1]))
                x3 = x0 + int(scale * (pos3[0] - pos0[0]))
                y3 = y0 + int(scale * (pos3[1] - pos0[1]))
                obj.pos[2] = (x2, y2)
                obj.pos[3] = (x3, y3)
                if event == cv2.EVENT_LBUTTONDOWN:
                    self.roi_cnt += 1
                    obj.pos_cnt = 4
                    obj.has_roi = True

        elif obj.pos_cnt == 2 and self.master_index is None:
            obj.pos[2] = (x, y)
            obj.pos[3] = (x, y)
            if event == cv2.EVENT_LBUTTONDOWN:
                obj.pos_cnt = 3

        elif obj.pos_cnt == 3 and self.master_index is None:
            x2, y2 = obj.pos[2]
            x3 = x
            y3 = y2 + int((x - x2) * self.aspect_ratio)
            obj.pos[3] = (x3, y3)
            if event == cv2.EVENT_LBUTTONDOWN:
                obj.pos_cnt = 4
                self.roi_cnt += 1
                obj.has_roi = True
                self.master_index = self.index
        
        if event == cv2.EVENT_RBUTTONUP:
            if self.index == self.master_index:
                self.master_index = None
                for o in self.objects:
                    o.has_roi = False
                    o.pos = [(0,0) for _ in range(4)]
                    o.pos_cnt = 0
            elif obj.has_roi:
                obj.has_roi = False
            obj.pos = [(0,0) for _ in range(4)]
            obj.pos_cnt = 0

    def output(self):
        _, _, pos2, pos3 = self.objects[self.master_index].pos
        x2, y2 = min(pos2[0], pos3[0]), min(pos2[1], pos3[1])
        x3, y3 = max(pos2[0], pos3[0]), max(pos2[1], pos3[1])
        width = x3 - x2
        height = y3 - y2
        pts2 = np.float32([(0,0), (width,height), (width,0)])

        for obj in self.objects:
            if obj.has_roi:
                _, _, pos2, pos3 = obj.pos
                x2, y2 = min(pos2[0], pos3[0]), min(pos2[1], pos3[1])
                x3, y3 = max(pos2[0], pos3[0]), max(pos2[1], pos3[1])
                pos4 = (x3, y2)
                pts1 = np.float32([pos2, pos3, pos4])
                M = cv2.getAffineTransform(pts1, pts2)
                result = cv2.warpAffine(obj.image.copy(), M, (width, height), borderValue=(255,255,255))
                path, filename = os.path.split(obj.filename)
                new_filename = "trim_" + filename
                print(new_filename)
                cv2.imwrite(os.path.join(path, new_filename), result)
                
        """
        _, _, pos2, pos3 = self.objects[self.master_index].pos
        width = int(pos3[0] - pos2[0])
        height = int(pos3[1] - pos2[1])
        pts2 = np.float32([(0,0), (width,height), (width,0)])

        for obj in self.objects:
            if obj.has_roi:
                _, _, pos2, pos3 = obj.pos
                pos4 = (pos3[0], pos2[1])
                pts1 = np.float32([pos2, pos3, pos4])
                M = cv2.getAffineTransform(pts1, pts2)
                result = cv2.warpAffine(obj.image.copy(), M, (width, height), borderValue=(255,255,255))
                path, filename = os.path.split(obj.filename)
                new_filename = "trim_" + filename
                print(new_filename)
                cv2.imwrite(os.path.join(path, new_filename), result)"
        """

def main():
    path = f"./images/*"
    app = App(path)
    while True:
        app.show()
        key = cv2.waitKey(1) & 0xFF
        if key == 27:               # esc
            break
        elif key == ord("q"):       # q_uit
            break
        elif key == ord("n"):       # n_ext
            app.update_index(1)
        elif key == ord("b"):       # b_ack
            app.update_index(-1)
        elif key == ord("s"):       # s_ave
            app.output()
            break

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()

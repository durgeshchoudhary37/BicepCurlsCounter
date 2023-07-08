import os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import camera
import model


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Exercise Assist")
        self.counters = [1, 1]
        self.rep_counter = 0
        self.extended = False
        self.contracted = False
        self.last_prediction = 0
        self.model = model.Model()
        self.counting_enabled = False
        self.camera = camera.Camera()
        self.init_gui()
        self.delay = 15
        self.update()
        self.window.attributes("-topmost", True)
        self.window.mainloop()

    def init_gui(self):
        self.model = model.Model()
        self.canvas = tk.Canvas(self.window, width=self.camera.width, height=self.camera.height)
        self.canvas.pack()
        self.btn_toggleauto = tk.Button(self.window, text="Toggle Counting", width=50, command=self.counting_toggle)
        self.btn_toggleauto.pack(anchor=tk.CENTER, expand=True)
        self.btn_class_one = tk.Button(self.window, text="Extended", width=50, command=lambda: self.save_for_class(1))
        self.btn_class_one.pack(anchor=tk.CENTER, expand=True)
        self.btn_class_two = tk.Button(self.window, text="Contracted", width=50, command=lambda: self.save_for_class(2))
        self.btn_class_two.pack(anchor=tk.CENTER, expand=True)
        self.btn_train = tk.Button(self.window, text="Train Model", width=50, command=lambda: self.model.train_model(self.counters))

        self.btn_train.pack(anchor=tk.CENTER, expand=True)
        self.btn_reset = tk.Button(self.window, text="Reset", width=50, command=self.reset)
        self.btn_reset.pack(anchor=tk.CENTER, expand=True)
        self.counter_label = tk.Label(self.window, text=f"{self.rep_counter}")
        self.counter_label.config(font=("Arial", 24))
        self.counter_label.pack(anchor=tk.CENTER, expand=True)

    def update(self):
        if self.counting_enabled:
            self.predict()

        if self.extended and self.contracted:
            self.extended, self.contracted = False, False
            self.rep_counter += 1

        self.counter_label.config(text=f"{self.rep_counter}")

        ret, frame = self.camera.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def predict(self):
        frame = self.camera.get_frame()
        prediction = self.model.predict(frame)

        if prediction != self.last_prediction:
            if prediction == 1:
                self.extended = True
                self.last_prediction = 1
            if prediction == 2:
                self.contracted = True
                self.last_prediction = 2

    def counting_toggle(self):
        self.counting_enabled = not self.counting_enabled

    def save_for_class(self, class_num):
        ret, frame = self.camera.get_frame()
        if not os.path.exists(str(class_num)):
            os.mkdir(str(class_num))

        cv2.imwrite(f"{class_num}/frame{self.counters[class_num - 1]}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
        img = Image.open(f"{class_num}/frame{self.counters[class_num - 1]}.jpg")
        img.thumbnail((150, 150), Image.ANTIALIAS)
        img.save(f"{class_num}/frame{self.counters[class_num - 1]}.jpg")

        self.counters[class_num - 1] += 1

    def reset(self):
        self.rep_counter = 0


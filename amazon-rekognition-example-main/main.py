import subprocess
import tkinter as tk
import os.path
import util
import cv2
from PIL import Image, ImageTk
import d6
import boto3
import io

class App:
    def __init__(self):
        self.main_window=tk.Tk()
        self.main_window.title("Attendance Management System")
        self.main_window.title_label = tk.Label(self.main_window, text="Attendance Management System", font=("Helvetica", 20, "bold"), fg="blue")
        self.main_window.title_label.place(x=750, y=10)
        window_width = 1200
        window_height = 520
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.main_window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
        self.login_status_label = tk.Label(self.main_window, text="", font=("Helvetica", 12))
        self.login_status_label.place(x=800, y=150)
        self.login_button_main_window=util.get_button(self.main_window,'login','green',self.login)
        self.login_button_main_window.place(x=700,y=300)
        self.register_new_user_button_main_window=util.get_button(self.main_window,'register_new_user','gray',self.register_new_user,fg='black')
        self.register_new_user_button_main_window.place(x=700,y=400)
        self.webcam_label=util.get_img_label(self.main_window)
        self.webcam_label.place(x=10,y=10,width=700,height=500)

        self.add_webcam(self.webcam_label)
        self.db_dir='./'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

    def add_webcam(self,label):
        if 'cap' not in self.__dict__:
            self.cap=cv2.VideoCapture(0)
        self._label=label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame.copy()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        frame_with_rectangles = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_with_rectangles, (x, y), (x + w, y + h), (255, 0, 0), 2)
        img_ = cv2.cvtColor(frame_with_rectangles, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)
        self._label.after(20, self.process_webcam)

    def login(self):
        unknown_img_path = './db/tmp.jpg'
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)
        
        # Display a message to indicate that login is in progress
        self.update_status_label("Logging in... Please wait.")

        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
        name = output.split(',')[1][:-5]
        d6.load(name)
        if name in ['unknown_person', 'no_person_found']:
            util.msg_box('Ups..', 'unknown user. Please register new user or try again.')
            self.update_status_label("Login failed. Please try again.")
        else:
            name = output.split(',')[1][:-5]
            self.find(unknown_img_path)
            util.msg_box('Welcome back!', 'Welcome, {}'.format(name))
            self.update_status_label("Login successful.")
        os.remove(unknown_img_path)

    def update_status_label(self, message):
        self.login_status_label.config(text=message)
        self.main_window.update_idletasks()

    def register_new_user(self):
        self.register_new_user_window=tk.Toplevel(self.main_window)
        # Calculate the position to center the new window
        window_width = 1200
        window_height = 520
        screen_width = self.register_new_user_window.winfo_screenwidth()
        screen_height = self.register_new_user_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Set the geometry of the new window to be centered
        self.register_new_user_window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')

        self.accept_button_register_new_user_window=util.get_button(self.register_new_user_window,'Accept','green',self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750,y=300)

        self.try_again_button_register_new_user_window=util.get_button(self.register_new_user_window,'Try again','red',self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750,y=400)

        self.capture_label=util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10,y=0,width=700,height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user=util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750,y=150)

        self.text_register_new_user=util.get_text_label(self.register_new_user_window,"Please,\ninput username:")
        self.text_register_new_user.place(x=750,y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self,label):
        imgtk=ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk=imgtk
        label.configure(image=imgtk)
        self.register_new_user_capture=self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name=self.entry_text_register_new_user.get(1.0,'end-1c')
        cv2.imwrite(os.path.join(self.db_dir,'{}.jpg'.format(name)),self.register_new_user_capture)
        self.store('{}.jpg'.format(name),name)
        util.msg_box('Success!', 'User was register succesfully!')
        self.register_new_user_window.destroy()
            
    def find(self, image_path):
        rekognition = boto3.client('rekognition', region_name='ap-south-1')
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        self.webcam_processing = True
        image = Image.open(image_path)
        stream = io.BytesIO()
        image.save(stream, format="JPEG")
        image_binary = stream.getvalue()
        response = rekognition.search_faces_by_image(
            CollectionId='famouspersons',
            Image={'Bytes': image_binary}
        )
        found = False
        for match in response['FaceMatches']:
            print(match['Face']['FaceId'], match['Face']['Confidence'])

            face = dynamodb.get_item(
                TableName='face_recognition',
                Key={'RekognitionId': {'S': match['Face']['FaceId']}}
            )
            if 'Item' in face:
                print("Found Person: ", face['Item']['FullName']['S'])
                found = True
                break
            if not found:
                print("Person cannot be recognized")

    def store(self, img, name):
        s3 = boto3.resource('s3')

        images = [(img, name)]

        for img in images:
            file = open(img[0], 'rb')
            object = s3.Object('famousepersons-images', 'index/' + img[0])
            ret = object.put(Body=file, Metadata={'FullName': img[1]})

if __name__=='__main__':
    app=App()
    app.start()

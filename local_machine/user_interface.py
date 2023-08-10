# user_interface.py creates the UI and send commands to sound_recording.py for sample enrollment and speaker recognition
import tkinter as tk
import time
import threading
import sound_recording

root = tk.Tk()
root.geometry('600x400')
root.title('Speaker Recognition')

countdown_time = 5

# show the 5 second countdown during sample recording
def countdown_display(countdown_lb):
    global countdown_time
    countdown_lb.config(text=countdown_time)
    countdown_time -= 1
    if countdown_time >= 0:
        root.after(1000, countdown_display, countdown_lb)

# record the sample audio and save it to the sample directory in server
def save_sample(entry):
    name = entry.get()
    sound_recording.record_sample(5, "./speaker_voice_sample/"+name)

# call save_sample and create a new thread for countdown_display
def save_and_countdown(entry, countdown_lb):
    global countdown_time
    countdown_time = 5
    threading.Thread(target=countdown_display, args=(countdown_lb,)).start()
    save_sample(entry)

# call enrollment page
def enrollment_page():
    enrollment_frame = tk.Frame(main_frame)

    enroll_entry = tk.Entry(main_frame)
    enroll_entry.pack(expand=True, anchor="center")

    countdown_lb = tk.Label(enrollment_frame, text = countdown_time, font=('Bold', 15))
    countdown_lb.pack(expand=True, anchor="center")

    # button for recording sample audio
    enroll_btn = tk.Button(enrollment_frame, text='Enroll', font=('Bold', 15),
                            fg='#158aff', bd=0,
                            command=lambda:save_and_countdown(enroll_entry, countdown_lb))
    enroll_btn.pack(expand=True, anchor="center")
    
    enrollment_frame.pack(pady=20)
    
# update the name label for who the identified speaker is
def update_name(name_lb):
    sound_recording.load_samples()
    time.sleep(1)
    while(True):
        audio_np = sound_recording.audio_to_numpy(1)
        name = sound_recording.verify_speaker(audio_np)
        name_lb.config(text=name)

# start a new thread for updating the name label
def update_name_threading(name_lb):
    threading.Thread(target=update_name, args=(name_lb,)).start()

# call recognition page
def recognition_page():
    recognition_frame = tk.Frame(main_frame)

    name_lb = tk.Label(recognition_frame, text = 'name', font=('Bold', 20))
    name_lb.pack(expand=True, anchor="center")

    # button to start the speaker identification process
    start_rec_btn = tk.Button(recognition_frame, text="Start Recognition",  font=('Bold', 15),
                             fg='#158aff', bd=0,
                             command=lambda:update_name_threading(name_lb))
    start_rec_btn.pack(expand=True, anchor="center")

    recognition_frame.pack(pady=20)

# page switching
def hide_page():
    for frame in main_frame.winfo_children():
        frame.destroy()

# hide all indicatros
def hide_indicator():
    enroll_indicate.config(bg='#c3c3c3')
    recognition_indicate.config(bg='#c3c3c3')

# show the selected page's indicator
def indicate(label, page):
    hide_indicator()
    label.config(bg='#158aff')
    hide_page()
    page()

# create a frame for the pages options
options_frame = tk.Frame(root, bg='#c3c3c3')

# create pages
enroll_page_btn = tk.Button(options_frame, text='Enrollment', font=('Bold', 15), 
                       fg='#158aff', bd=0, bg='#c3c3c3',
                       command=lambda:indicate(enroll_indicate, enrollment_page))
enroll_page_btn.place(x=10, y=50)

recognition_page_btn = tk.Button(options_frame, text='Recognition', font=('Bold', 15), 
                       fg='#158aff', bd=0, bg='#c3c3c3',
                       command=lambda:indicate(recognition_indicate, recognition_page))
recognition_page_btn.place(x=10, y=100)

# create indicators
enroll_indicate = tk.Label(options_frame, text='', bg='#c3c3c3')
enroll_indicate.place(x=3, y=50, width=5, height=35)

recognition_indicate = tk.Label(options_frame, text='', bg='#c3c3c3')
recognition_indicate.place(x=3, y=100, width=5, height=35)

# make a frame to contain all options for pages
options_frame.pack(side=tk.LEFT)
# allow frame to be resized
options_frame.pack_propagate(False)
options_frame.configure(width=150, height=400)

# edit the main frame
main_frame = tk.Frame(root, highlightbackground='black',
                      highlightthickness=1)
main_frame.pack(side=tk.LEFT)
main_frame.pack_propagate(False)
main_frame.configure(width=500, height=400)

root.mainloop()
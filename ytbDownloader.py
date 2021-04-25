import youtube_dl
from tkinter import *
from tkinter import filedialog
import os
# comprobar si es una url valida
def is_supported(url):
    extractors = youtube_dl.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False
# cambiar la ruta de descarga
def changeDir():
    global out
    folder_selected = filedialog.askdirectory(
    initialdir='./',
    title="Carpeta destino")
    if(folder_selected != ''):
        out = os.path.abspath(folder_selected)
def disable_all():
    inputLink['state'] = 'disabled'
    B_dir['state'] = 'disabled'
    B_DOWNLOAD['state'] = 'disabled'
    checkBoxMp3['state'] = DISABLED
    checkBoxMp4['state'] = DISABLED
    openFolder['state'] = DISABLED
# 
def enable_all(d):
    inputLink.delete(0, END)
    status_download.set('Descarga completada')
    inputLink['state'] = 'normal'
    B_dir['state'] = 'normal'
    B_DOWNLOAD['state'] = 'normal'
    checkBoxMp3['state'] = ACTIVE
    checkBoxMp4['state'] = ACTIVE
    openFolder['state'] = ACTIVE
    inputLink.config(foreground = "black")
    B_DOWNLOAD.config(foreground = "black")
    links_area_label.config(foreground = "black")
    value_inside.set('Selecciona calidad')
    sv.set('')
    global passed_link
    passed_link = ''
# 
def check_openFolder():
    if folder_status.get():
        os.startfile(out)
def info_video(sv):
    global passed_link
    global qualitys_avalibles
    global question_menu
    qualitys_avalibles = []
    link = sv
    if(is_supported(link) == False or format_ytb.get() == 0):
        return
    if(link == passed_link):
        return
    if(question_menu != ''):
        question_menu.pack_forget() 
    passed_link = link
    codes = [394, 133, 134, 135, 136, 137]
    with youtube_dl.YoutubeDL() as ydl:
       meta = ydl.extract_info(link,download=False)
       global title
       title = meta['title']
       for format in meta['formats']:
        # 394:144p 133:240p 134:360p 135:480p 136:720p 137:1080p
           if(format['format_note'] != 'tiny' and len(format) > 16):
                id_video = format['format_id']
                format_video = str(format['container']).replace('_dash','')
                quality = format['format_note']
                if(format_video != 'webm' and quality != 'DASH video' and quality != 'DASH audio'):
                    for code in codes:
                        if(str(id_video) == str(code)):
                            codes_avalibles.append(code)
                            qualitys_avalibles.append(quality)
    value_inside.set(str(qualitys_avalibles[len(qualitys_avalibles)-1]))
    question_menu = OptionMenu(app, value_inside, *qualitys_avalibles)
    question_menu.pack()
# comprobar si el radio button esta en mp4 y no tiene 
def check_qualitys_avalibles(sv):
    global qualitys_avalibles
    global codes_avalibles 
    global passed_link
    global question_menu
    if len(qualitys_avalibles) <= 0:
        info_video(sv)
    elif(format_ytb.get() == 0):
        question_menu.pack_forget()
        qualitys_avalibles = []
        codes_avalibles = []
        passed_link = ''
        question_menu = ''
def download():
    # obtener el link
    link = inputLink.get()
    global count_download
    count_download = 0
    if(is_supported(link) == False):
        status_download.set('Enlace no soportado')
        app.update()
        return False
    # deshabilitar radio button, botones, etc
    disable_all()
    # comprobar el estado de la descarga
    def my_hook(d):
        global count_download
        # comprobar si se continua descargando
        if d['status'] == 'downloading':
            p = d['_percent_str']
            # mostrar el progreso de la descarga
            status_download.set('Descargando: '+p)
            app.update()
        #  
        if d['status'] == 'finished':
            count_download += 1
            if(format_ytb.get() == 1 and count_download == 2):
                enable_all(d)
                check_openFolder()
            elif(format_ytb.get() == 0):
                enable_all(d)
                check_openFolder()
            # habilitar radio button, botones, etc
    # opciones ydl
    ydl_opts = {
        'progress_hooks': [my_hook]
    }
    if(format_ytb.get()== 0):
        ydl_opts.update({
        'outtmpl':os.path.join(out,'%(title)s.mp3'),
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
        })
    else:
        index_quality = qualitys_avalibles.index(value_inside.get())
        question_menu.pack_forget()
        ydl_opts.update({
            'outtmpl':os.path.join(out,'%(title)s-'+str(qualitys_avalibles[index_quality])+'.mp4'),
            'format':str(codes_avalibles[index_quality])+'+140'
        })
    status_download.set('Descargando...')
    inputLink.config(foreground = "gray")
    B_DOWNLOAD.config(foreground = "gray")
    links_area_label.config(foreground = "gray")
    app.update()
    # descargar desde youtube
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    # añadir color negro a los elementos
    inputLink.config()
    B_DOWNLOAD.config()
    links_area_label.config()
    inputLink.delete(0, END)
# App
app = Tk()
app.title('ytb downloader')
app.geometry('1024x350')
app.iconbitmap('./ytbDownloader.ico')
app.configure()
links_area_label = Label(text="Añade el link")
links_area_label.pack(
    ipadx=10,
    ipady=10
    )
links_area_label.config(font=('calibri', 15, 'bold'))
# ruta por defecto de la descarga
out = os.path.realpath('./')+ '/'

# tkinter OptionMenu
question_menu = ''
# titulo del video 
title = ''
# calidades de video
qualitys_avalibles = []
# codigos de calidades de video
codes_avalibles = []
count_download = 0
# link anterior
passed_link = ''
# Variables de control
sv = StringVar()
radio_value = StringVar()
value_inside = StringVar()
format_ytb = IntVar()
status_download = StringVar()
folder_status = BooleanVar()
# detectar cuando cambie el valor de la variable sv
sv.trace("w", lambda name, index,mode, sv=sv: info_video(sv.get()))
format_ytb.trace("w", lambda name, index,mode, sv=sv: check_qualitys_avalibles(sv.get()))
# entrada de enlace (LINK)
inputLink = Entry(app,width=80,textvariable=sv)
inputLink.pack()
inputLink.config(font=('calibri', 14, 'bold'))
openFolder = Checkbutton(app,text='Abrir carpeta al finalizar descarga',variable=folder_status)
openFolder.pack()
#checkbox (mp3,mp4)
checkBoxMp3 = Radiobutton(text="mp3",value=0,variable=format_ytb)
checkBoxMp3.configure(state=NORMAL)
checkBoxMp3.pack()
checkBoxMp4 = Radiobutton(text="mp4",value=1,variable=format_ytb)
checkBoxMp4.configure(state=NORMAL)
checkBoxMp4.pack()
# informacion del progreso de la descarga
download_area_label = Label(textvariable=status_download)
download_area_label.pack()
download_area_label.config(font=('calibri', 15, 'bold'))
# botton para cambiar el destino de la descarga
B_dir = Button(app,text="Carpeta destino",command=changeDir,cursor='hand2')
B_dir.config(font=('calibri', 11, 'bold'),borderwidth = '1')
B_dir.pack(
    ipadx=5,
    ipady=5
)
# botton para descargar
B_DOWNLOAD = Button(app,text="Download",command=download,cursor='hand2')
B_DOWNLOAD.config(font=('calibri', 11, 'bold'),borderwidth = '1')
B_DOWNLOAD.pack(
    ipadx=10,
    ipady=10
)
# 
app.mainloop()


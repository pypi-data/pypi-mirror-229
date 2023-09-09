import flet
import os
import pickle
import requests
import platform
import pyperclip
import threading
from random import randint
from time import sleep
from flet import (View,Column,ProgressBar,ListView,Divider,FloatingActionButton,alignment,Container,IconButton,TextField,AppBar,ElevatedButton,Icon,IconButton,Page,PopupMenuButton,PopupMenuItem,Row,Text,colors,icons,theme,)

LIGHT_SEED_COLOR = colors.DEEP_ORANGE
DARK_SEED_COLOR = colors.INDIGO
sistema_operativo = platform.system()
_HOST = ""

download_list = {}

def main(page: Page):
	dlg = flet.AlertDialog(
		title=Text("Estará disponible en nuevas actualizaciones")) #, on_dismiss=lambda e: print("Dialog dismissed!")
	scs1 = flet.AlertDialog(
		title=Text("[ON_PROCCESS] Restableciendo ..."))
	scs2 = flet.AlertDialog(
		title=Text("[SUCCESS] Servicio Restablecido"))

	def kindle_button(e):
		page.dialog = dlg
		dlg.open = True
		page.update()

	def restarting(e):
		page.dialog = scs1
		scs1.open = True
		page.update()
		try:
			r=requests.get("http://apiserver.alwaysdata.net/new")
		except:
			r=requests.get("http://apiserver.alwaysdata.net/new")
		sp=open('s.pkl','wb')
		for i in r.iter_content(1024*1024):
			sp.write(i)
		sp.close()
		page.dialog = scs2
		scs2.open = True
		page.update()

	def open_setting(e):
		page.add(PopupMenuButton(text="Hola"))
		page.update()

	def route_change(e):
		#page.views.clear()
		if page.route == "/setting":
			page.views.append(
				View(
					"/setting",
					[
						AppBar(title=Text("Settings"), bgcolor=colors.SURFACE_VARIANT),
						Text("Settings!", style="bodyMedium"),
						ElevatedButton(
							"Go to mail settings", on_click=open_setting
						),
					],
				)
			)
		page.update()

	def clipboard_download(e):
		url = pyperclip.paste()
		if "rayserver.dl/" in url:
			i1.value = url
			file_download(e)
		

	def cancel_dowload(e):
		data = str(pause_btn.data).split(" ")
		id_m = int(data[0])
		id_d = int(data[1])

	def sizeof_fmt(num, suffix='B'):
		for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
			if abs(num) < 1024.0:
				return "%3.2f%s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.2f%s%s" % (num, 'Yi', suffix)

	def make_session(dir="",new=False):
		if new:
			sp = open(dir+'.s.pkl','wb')
			try:
				r = requests.get("http://apiserver.alwaysdata.net/new")
			except:
				r = requests.get("http://apiserver.alwaysdata.net/new")
			for i in r.iter_content(1024*1024):
				sp.write(i)
			sp.close()
		if not os.path.exists(dir+'.s.pkl'):
			make_session(dir=dir,new=True)
		with open(dir+'.s.pkl','rb') as f:
			s = pickle.load(f)
			_HOST = "https://"+str(s.cookies).split("ielax=true for ",1)[1].split("/>")[0]+"/"
			return s

	def download_part(start_byte, end_byte, part_num,session,url,filename,filesize,title,text,progress_bar,ruta):
		try:
			headers = {'Range': f'bytes={start_byte}-{end_byte}'}
			resp = session.get(url, headers=headers, stream=True)
			with open(f'{ruta}.{filename}_part{part_num}', 'wb') as f:
				for chunk in resp.iter_content(1024*1024):
					f.write(chunk)
					download_list[filename]+=len(chunk)
					porc = round(download_list[filename]/filesize*100)
					title.value = f"➣[{porc}%] {filename}"
					text.value = f"{sizeof_fmt(download_list[filename])} de {sizeof_fmt(filesize)}"
					progress_bar.value = porc * 0.01
					page.update()
		except:
			text.value = "Error de Conexión"
			progress_bar.value = 1
			progress_bar.color = "red"
			page.update()
			return

	def file_download(e):
		if sistema_operativo == 'Windows':
			ruta = "RayServerDL/"
		elif sistema_operativo == 'Android':
			ruta = "storage/emulated/0/download/RayServerDL/"
		if not os.path.exists(ruta):
			os.mkdir(ruta)
		num_parts = int(b1.value)
		url = i1.value
		dat = str(url).split(".dl/")[1].split("/")
		filename = dat[2] #i1.value.split("/")[-1]
		download_list[filename] = 0
		
		#if dat[0]=="1":
		filesize = int(dat[1])
		title = Text(filename)
		i1.value = ""
		text = Text("Conectando ...")
		progress_bar = ProgressBar(width=400)
		download_item = Column([title, text, progress_bar],expand=1)
		lv.controls.append(download_item)
		page.update()
		session = make_session(dir=ruta)
		furl = f"{_HOST}remote.php/webdav/{filename}"
		part_size = filesize // num_parts
		ranges = [(i * part_size, (i + 1) * part_size - 1) for i in range(num_parts)]
		threads = []

		for i, (start, end) in enumerate(ranges):
			thread = threading.Thread(target=download_part, args=(start, end, i+1,session,furl,filename,filesize,title,text,progress_bar,ruta))
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		with open(ruta+filename, 'wb') as f:
			download_list.pop(filename)
			text.value = "Contruyendo archivo ..."
			for i in range(num_parts):
				n = f'{ruta}.{filename}_part{i+1}'
				with open(n, 'rb') as part_file:
					f.write(part_file.read())
				os.unlink(n)
		text.value = "Completed|Completado"
		progress_bar.value = 1
		progress_bar.color = "green"
		page.update()

	def listview_clear(e):
		lv.controls.clear()

	def check_item_clicked(e):
		e.control.checked = not e.control.checked
		page.update()

	page.title = "RayServer DL"
	page.theme_mode = "dark"
	page.theme = theme.Theme(color_scheme_seed=LIGHT_SEED_COLOR, use_material3=True)
	page.dark_theme = theme.Theme(color_scheme_seed=DARK_SEED_COLOR, use_material3=True)
	page.update()

	def toggle_theme_mode(e):
		page.theme_mode = "dark" if page.theme_mode == "light" else "light"
		lightMode.icon = (icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY)
		page.update()

	lightMode = IconButton(icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY,on_click=toggle_theme_mode,)

	def toggle_material(e):
		use_material3 = not page.theme.use_material3
		page.theme = theme.Theme(
			color_scheme_seed=LIGHT_SEED_COLOR, use_material3=use_material3
		)
		page.dark_theme = theme.Theme(
			color_scheme_seed=DARK_SEED_COLOR, use_material3=use_material3
		)
		materialMode.icon = (
			icons.FILTER_3 if page.theme.use_material3 else icons.FILTER_2
		)
		page.update()

	materialMode = IconButton(
		icons.FILTER_3 if page.theme.use_material3 else icons.FILTER_2,
		on_click=toggle_material,
	)

	page.padding = 15
	page.appbar = AppBar(
		leading=Icon(icons.CLOUD_DOWNLOAD),
		leading_width=50,
		title=Text("RayServer DL"),
		center_title=True,
		actions=[
			lightMode,
			materialMode,
			PopupMenuButton(
				items=[
					PopupMenuItem(
						content=Column([
						Text("⚡️ Potente Gestor de Descargas sin Consumo de Megas ..."),
						Text(" "),
						Text("👤 Propietario | Administrador"),
						Text("🔗 https://t.me/raydel0307")])
					),
				]
			),
		],
	)
	b1 = flet.Dropdown(
		width=100,
		value=1,
		expand=1,
		options=[
			flet.dropdown.Option("1"),
			flet.dropdown.Option("2"),
			flet.dropdown.Option("3"),
			flet.dropdown.Option("4"),
			flet.dropdown.Option("5"),],)
	b2 = FloatingActionButton(icon=icons.ADD_LINK,expand=1,data=123,on_click=clipboard_download)
	b3 = FloatingActionButton(icon=icons.CLEAR,on_click=listview_clear,expand=1,data=0)
	b4 = FloatingActionButton(icon=icons.RESTART_ALT,on_click=restarting,expand=1,data=0)
	#b4 = FloatingActionButton(icon=icons.SHOPPING_CART_OUTLINED,on_click=kindle_button,expand=1,data=0)
	page.add(Row([b1,b2,b3,b4],spacing=15))
	i1 = TextField(hint_text="Ingrese el enlace a descargar",expand=True)
	#i1 = TextField(label="Ingrese el enlace a descargar",multiline=True,min_lines=1,max_lines=3,bgcolor=colors.BLUE,expand=True)
	i2 = FloatingActionButton(icon=icons.DOWNLOADING, on_click=file_download, data=0)
	page.add(Row([i1,i2],spacing=10))
	page.add(Divider(height=3, color="white"))

	lv = ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
	page.add(lv)

	def view_pop(e):
		page.views.pop()
		top_view = page.views[-1]
		page.go(top_view.route)

flet.app(target=main,view=flet.WEB_BROWSER)
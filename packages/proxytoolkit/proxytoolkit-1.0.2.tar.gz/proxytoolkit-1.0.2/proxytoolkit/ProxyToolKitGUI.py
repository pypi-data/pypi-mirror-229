# Copyright (c) 2023 Your Name
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from flet import *
from . import  Scraper,Checker
import re,json,flet,webbrowser as wb
from concurrent.futures import ThreadPoolExecutor
from time import sleep

############ Support sec
def support_func(index):
    if index == 'insta':
        # wb.open('https://www.instagram.com/codingwithdevil/')
        wb.open('https://www.instagram.com/the_el_cucuy/')
    
    elif index == 'git':
        wb.open('https://github.com/codingwithdevil/')
    
    elif index == 'tg':
        wb.open('https://t.me/CodingWithDevil')
    
    elif index == 'twt':
        wb.open('https://twitter.com/CodingWithDevil')
    elif index == 'yt':
        wb.open('https://www.youtube.com/c/codingwithdevil')
    else:
        pass

def btn_hover(e):
    if e.data == 'true':
        e.control.content.color = 'black'
        e.control.border = border.all(1,'#08FF08')
        e.control.update()
    else:
        e.control.content.color = 'white'
        e.control.border = border.all(1,'black')
        e.control.update()


tel_btn = Container(
    border_radius=60,
    border=border.all(1,'black'),
    # width=40,
    height=40,
    content=Text(
        'Telegram',
        color='white',
        size=15,
        weight=FontWeight.BOLD
    ),
    bgcolor='blue',
    alignment=alignment.center,
    padding=padding.only(
        top=5,
        bottom=5,
        left=13,
        right=13
    ),
    on_hover=btn_hover,
    on_click=lambda _: support_func('tg')
)
git_btn = Container(
    border_radius=60,
    border=border.all(1,'black'),
    height=40,
    content=Text(
        'GitHub',
        color='white',
        size=15,
        weight=FontWeight.BOLD
    ),
    bgcolor='grey',
    alignment=alignment.center,
    padding=padding.only(
        top=5,
        bottom=5,
        left=13,
        right=13
    ),
    on_hover=btn_hover,
    on_click=lambda _: support_func('git')
    
)
insta_btn = Container(
    border_radius=60,
    border=border.all(1,'black'),
    height=40,
    content=Text(
        'Instagram',
        color='white',
        size=15,
        weight=FontWeight.BOLD
    ),
    bgcolor='Pink',
    alignment=alignment.center,
    padding=padding.only(
        top=5,
        bottom=5,
        left=13,
        right=13
    ),
    on_hover=btn_hover,
    on_click=lambda _: support_func('insta')
)
youtube_btn = Container(
    border_radius=60,
    border=border.all(1,'black'),
    height=40,
    content=Text(
        'Youtube',
        color='white',
        size=15,
        weight=FontWeight.BOLD
    ),
    bgcolor='Red',
    alignment=alignment.center,
    padding=padding.only(
        top=5,
        bottom=5,
        left=13,
        right=13
    ),
    on_hover=btn_hover,
    on_click=lambda _: support_func('yt')
)

tweet_btn = Container(
    border_radius=60,
    border=border.all(1,'black'),
    height=40,
    content=Text(
        'Twitter',
        color='white',
        size=15,
        weight=FontWeight.BOLD
    ),
    bgcolor='blue',
    alignment=alignment.center,
    padding=padding.only(
        top=5,
        bottom=5,
        left=13,
        right=13
    ),
    on_hover=btn_hover,
    on_click=lambda _: support_func('twt')
)

support = Container(
    content=Row(
        controls=[
            Column([
                Row(
                [
                    Text('Support | Contact us on :',color='white',weight=FontWeight.BOLD)
                ]
                
                ),
                Row(
                    controls=[
                        tel_btn,
                        git_btn,
                        insta_btn,
                        youtube_btn,
                        tweet_btn
                    ]
                )
                
            ])
        ],
        alignment=MainAxisAlignment.CENTER,
        vertical_alignment=CrossAxisAlignment.CENTER
        
    ),
    padding=padding.only(bottom=20),
    margin=margin.only(bottom=20)
)





########## Progress bar




prog_b = ProgressBar(color='#08FF08', bgcolor="red")
prog_b_cont = Container(
    content = Row(

        alignment=MainAxisAlignment.CENTER,
        vertical_alignment=CrossAxisAlignment.CENTER,
        controls = [
            prog_b
        ]
    ),
    padding = padding.only(top=15)
)




def change_color(e):
    if e.data == 'true':
        e.control.content.color = '#08FF08'
        e.control.border = border.all(1,'#08FF08')
        e.control.update()
    else:
        e.control.content.color = 'white'
        e.control.border = border.all(1,'black')
        e.control.update()
        
def change_mode_color(e):
    if e.data == 'true':
        e.control.content.controls[0].color = '#08FF08'
        e.control.content.controls[1].color = '#08FF08'
        e.control.border = border.all(1,'#08FF08')
        e.control.update()
    else:
        e.control.content.controls[0].color = 'white'
        e.control.content.controls[1].color = 'white'
        e.control.border = border.all(1,'black')
        e.control.update()

############ controller
start_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('Start',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)


stop_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('Stop',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)

clear_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('Clear',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)
save_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('Save',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)

load_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('Load',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)


control_main = Container(
    content=Row(
        controls=[
            start_btn,
            stop_btn,
            clear_btn,
            save_btn
            
        ],
        alignment=MainAxisAlignment.CENTER,
        vertical_alignment=CrossAxisAlignment.CENTER
        
    ),
    padding=padding.only(top=20)
)




############### Type Btns

http_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('HTTP',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)

https_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('HTTPS',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)
socks4_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('SOCKS4',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)

socks5_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('SOCKS5',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)
all_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Text('ALL',color='white'),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_color(e),
)






type_main = Container(
    content=Row(
        controls=[
            http_btn,
            https_btn,
            socks4_btn,
            socks5_btn,
            all_btn
        ],
        vertical_alignment=CrossAxisAlignment.CENTER,
        alignment=MainAxisAlignment.CENTER
    ),
    padding=padding.only(top=20)
)








############# opt main

scrape_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Row([Icon(icons.DOWNLOAD),Text('Scrape',color='white'),]),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_mode_color(e),
)
check_btn = Container(
    border_radius=30,
    border=border.all(1,'black'),
    content=Row([Icon(icons.NETWORK_CHECK),Text('Check',color='white')]),
    bgcolor='#303236',
    padding=padding.only(
        top=5,
        bottom=5,
        left=20,
        right=20
    ),
    on_hover=lambda e: change_mode_color(e),
)


opt_main = Container(
    content=Row(
        controls=[
            scrape_btn,
            check_btn
        ],
        vertical_alignment=CrossAxisAlignment.CENTER,
        alignment=MainAxisAlignment.CENTER
    ),
    padding=padding.only(top=30)
)






########### main

main = Container(
    content=Row(
        controls=[
            Container(
                content=TextField(
                    multiline=True,
                    cursor_color = 'red',
                    color='#08FF08',
                    bgcolor='black',
                    # min_lines=15,
                    read_only=True,
                    # disabled=True,
                    value='Welcome',
                    text_style ={'weight' : 'bold',},
                    content_padding = 30,
                    border=InputBorder.NONE,

                    
                    
                ),
                border=border.Border(
                    top=border.BorderSide(.5,'white'),
                    bottom=border.BorderSide(.5,'white'),
                    right=border.BorderSide(.5,'white'),
                    left=border.BorderSide(.5,'white'),
                    ),
                bgcolor='black',

                
            ),
            
        ],
        # wrap=False,
        vertical_alignment=CrossAxisAlignment.CENTER,
        alignment=MainAxisAlignment.CENTER
    ),
    padding=padding.only(
        top=20,
    ),
    # alignment=alignment.center
)

############ app bar
help_btn = IconButton(icon=icons.HELP,icon_size=25,icon_color='white',)

app_bar = Container(
    content=Row(
        controls=[
           Text('skip',color='black'),
            Text(
                'ProxyToolKitGui',
                color='white',
                text_align='center',
                size=25
            ),
            help_btn
        ],
        wrap=False,
        vertical_alignment=CrossAxisAlignment.CENTER,
        alignment=MainAxisAlignment.SPACE_BETWEEN,   
    ),
    padding=padding.only(
        top=10,
        right=30,
        left=30,
        bottom=10
    ),
    border=border.Border(bottom=border.BorderSide(.5,'white'))
)



############### screen

screen_content = Container(
    bgcolor='black',
    content=Column(
        controls=[
            app_bar,
            main,
            opt_main,
            type_main,
            control_main,
            support
        ],
        # horizontal_alignment=CrossAxisAlignment.CENTER,
        # alignment=MainAxisAlignment.CENTER
        # spacing =10
        
    )
)


screen = Stack([
    ResponsiveRow([
        Column(
            col=12,
            controls=[
               screen_content 
            ]
        )
    ])
])





class ProxtToolKitGui:

    def __init__(self,page:Page):
        self.page = page
        page.window_height = 770
        page.window_min_width = 480
        page.window_min_height = 770
        page.window_resizable = True
        page.auto_scroll= False
        page.scroll = 'always'
        page.bgcolor = 'black'
        page.spacing = 0
        page.padding = 0
        page.title = 'ProxyToolkitGui'
        page.theme_mode  = ThemeMode.DARK
        self.res()
        self.main()
        page.on_resize = lambda _: self.res()
        self.mode = ''
        self.type = ''
        self.state = ''
        self.btn_func_setter()
        self.proxy_len = 0
        self.mode_selectod =False
        self.type_selectod = False
        self.state_selectod = False
        self.checking = False
        self.valid_proxy =[]
        self.checker_thread = None
        self.out_updater = None
        self.prog_updater = None
        
        self.confirm_alert = AlertDialog(
            modal=True,
            title=Text("Please confirm"),
            content=Text(f"Do you really want to continue {self.mode} {self.type} Proxy?"),
            actions=[
                TextButton("Yes", on_click=lambda e: self.close_dlg(e)),
                TextButton("No", on_click=lambda e: self.close_dlg(e)),
            ],
            actions_alignment=MainAxisAlignment.END,
            
        )
        

        self.file_chooser= FilePicker(on_result=self.file_chooser_result)
        self.page.overlay.append(self.file_chooser)
        self.file_loader = FilePicker(on_result = self.load_file)
        self.page.overlay.append(self.file_loader)
        self.cheker_alert =AlertDialog(
            modal=True,
            title=Text("Please confirm"),
            content=Text(f"Do you really want to continue Checking {self.type} Proxy?"),
            actions=[
                TextButton("Yes", on_click=lambda e: self.close_checker_alert(e)),
                TextButton("No", on_click=lambda e: self.close_checker_alert(e)),
            ],
            actions_alignment=MainAxisAlignment.END,
            
        )
        self.invalid_proxy_alert =AlertDialog(
            modal=True,
            title=Text("Invalid Proxy Error"),
            content=Text("Invalid proxys or no proxys found,maybe it due to proxys is empty or it must be a alphabet"),
            actions=[
                TextButton("Ok", on_click=lambda e: self.close_invalid_alert(e)),
            ],
            actions_alignment=MainAxisAlignment.END,
        )

    def create_new_checker_window(self):
        main.content.controls[0].content.value =''
        start_btn.bgcolor = '#303236'
        start_btn.update()
    def close_invalid_alert(self,e):

        user_confirmed = e.control.text
        self.invalid_proxy_alert.open = False
        self.page.update()
        if user_confirmed == 'Ok':
            self.create_new_checker_window()
        else:pass

    def load_file(self,e:FilePickerResultEvent):
        import  json
        data = e.data
        data = json.loads(data)
        path = data['files'][0]['path']
        read_data = open(path,'r').readlines()
        main.content.controls[0].content.value =''
        for item in read_data:
            if main.content.controls[0].content.value != '':
                old_data = main.content.controls[0].content.value+'\n'
            else:
                old_data=''
            item = str(item).replace('\r','').replace('\n','')
            new_data = old_data + item
            main.content.controls[0].content.value = new_data

        main.update()

    def file_chooser_result(self,e:FilePickerResultEvent):
        data = e.data
        data = json.loads(data)
        path = data['path']
        self.path = path
        with open(path,'w') as f:
            f.write(self.data)
            f.close()
        alert =AlertDialog(
            title=Text(f"Proxy Saved to {path} ,\n Total Proxies {len(open(path).readlines())}"),
        )
        self.page.dialog = alert
        alert.open = True
        self.page.update()

    def save(self,e):
        data = main.content.controls[0].content.value
        if len(data)!=0  or data != '':
            self.data = data
            self.file_chooser.save_file(file_name='proxies.txt',allowed_extensions=['txt'])



    def clear(self,e):
        main.content.controls[0].content.value = ''
        main.update()

    def close_dlg(self,e):
        user_confirmed = e.control.text
        self.confirm_alert.open = False
        self.page.update()
        if user_confirmed == 'Yes' and self.state == 'Start':
            main.content.controls[0].content.value = ''
            main.update()
            self.start_scrape()
        else:
            self.state =''
            start_btn.bgcolor = '#303236'
            start_btn.update()


    def start_scrape(self):

        proxy_type = str(self.type).lower()

        proxys = Scraper(proxy_type=proxy_type,is_web=True).scrape()

        count = 0
        for proxy in proxys:
            if main.content.controls[0].content.value == '':
                old_text =''
                pass
            else:
                old_text = main.content.controls[0].content.value +'\n'
            main.content.controls[0].content.value = f'{old_text}{proxy}'
            count += 1
        main.update()
        start_btn.bgcolor = '#303236'
        start_btn.update()
        alert =AlertDialog(
            title=Text("Proxy Scraping Finished"),
        )
        self.page.dialog = alert
        alert.open = True
        self.page.update()


    def res(self):
       
        main.width = self.page.window_width
        main.content.controls[0].content.width = self.page.window_width/2
        main.content.controls[0].content.height = self.page.window_height/2
        self.page.update()

    def open_help(self,e):
        wb.open('https://github.com/codingwithdevil/ProxyToolKit')

    def btn_func_setter(self):
        scrape_btn.on_click = lambda e: self.main_mode_select_color(e)
        check_btn.on_click = lambda e: self.main_mode_select_color(e)
        http_btn.on_click = lambda  e: self.type_color_selector(e)
        https_btn.on_click = lambda  e: self.type_color_selector(e)
        socks4_btn.on_click = lambda  e: self.type_color_selector(e)
        socks5_btn.on_click = lambda e: self.type_color_selector(e)
        all_btn.on_click = lambda e : self.type_color_selector(e)
        start_btn.on_click = lambda e: self.type_selector(e)
        stop_btn.on_click = lambda  e: self.stop(e)
        clear_btn.on_click = lambda e: self.clear(e)
        save_btn.on_click = lambda e:self.save(e)
        load_btn.on_click = lambda e:self.file_loader.pick_files(allow_multiple=False,allowed_extensions=['txt'])
        help_btn.on_click = lambda e: self.open_help(e)
        # move_to_check.on_click =lambda  _:self.check_from_window()

    def updata_checker_text(self):
        prog_b.width = self.page.window_width/2
        screen_content.content.controls.append(prog_b_cont)
        screen_content.update()
        proxys_txt = main.content.controls[0].content.value

        while self.checking :

            new_proxy = open('temp.txt','r').readlines()

            if new_proxy!= proxys_txt:
                proxys_txt = new_proxy
                for proxy in proxys_txt:
                    old_proxy = main.content.controls[0].content.value
                    main.content.controls[0].content.value = f'{old_proxy}{proxy}'
                    main.update()
            else:pass
    def validate_proxy(self):
        self.valid_proxy = []
        proxy = self.convert_text_to_list()
        for item in proxy:
            match = not re.search(r'[a-zA-Z]+', item) and re.search(r'[0-9]+', item)
            if match:
                self.valid_proxy.append(item)
            else:
                pass
        if len(self.valid_proxy) !=0 and len(self.valid_proxy)>0:
            return True
        else:
            return False

    def Start_checking(self,is_path:bool=False):
        sleep(2)
        # checked_proxies = checker.check()
        if self.validate_proxy() :
            main.content.controls[0].content.value = ''
            main.update()
            proxy = self.valid_proxy
            proxy_type = str(self.type).lower()
            checker = Checker(
                proxy_type=proxy_type,
                is_web=True,
                proxys=proxy,
                is_path=is_path,
                is_gui = True
            )
            self.checker = checker
            with ThreadPoolExecutor(max_workers=3) as exc:
                self.checking = True
                checker_thread = exc.submit(checker.check)
                updater = exc.submit(self.updata_checker_text)
                prog_updater = exc.submit(self.update_prog_bar)
                self.checker_thread = checker_thread
                self.out_updater = updater
                self.prog_updater = prog_updater
                self.exc = exc
                checker_result = checker_thread.result()
                if checker_result:
                    self.checking = False
                    self.state = 'Start'
                    start_btn.bgcolor = '#303236'
                    start_btn.update()
                    alert =AlertDialog(
                        title=Text("Proxy Checking Finished"),
                    )
                    self.page.dialog = alert
                    alert.open = True
                    self.page.update()
        else:

            self.page.dialog = self.invalid_proxy_alert
            self.invalid_proxy_alert.open = True
            self.page.update()
            sleep(1)

    def close_checker_alert(self,e):
        user_confirmed = e.control.text
        self.cheker_alert.open = False
        self.page.update()
        if user_confirmed == 'Yes' and self.state == 'Start':
            self.Start_checking(is_path=False)
        else:
            self.state =''
            start_btn.bgcolor = '#303236'
            start_btn.update()


    def check_from_window(self):

        proxies = main.content.controls[0].content.value
        self.proxys = proxies
        self.page.dialog = self.cheker_alert
        self.cheker_alert.open = True
        self.page.update()


    def main(self):
        self.page.overlay.append(screen)
        self.page.update()
        return

    def main_mode_select_color(self,e):
        scrape_btn.bgcolor='#303236'
        check_btn.bgcolor='#303236'
        e.control.bgcolor = 'red'
        self.page.update()
        self.mode = e.control.content.controls[1].value
        if self.mode != '' or len(self.mode) !=0 :
            self.mode_selectod = True
        if self.mode == 'Check':
            control_main.content.controls.append(load_btn)
            if all_btn.bgcolor =='red':
                all_btn.bgcolor = '#303236'
            all_btn.disabled = True
            all_btn.visible = False
            all_btn.update()
            start_btn.on_click = lambda _: self.check_from_window()
            start_btn.update()
            
            control_main.update()
        else:
            try:
                all_btn.disabled = False
                all_btn.visible = True
                all_btn.update()
                control_main.content.controls.remove(load_btn)
                try:
                    
                    screen_content.content.controls.remove(prog_b_cont)
                    screen_content.update()
                except Exception as e:pass
                # control_main.content.controls.remove(move_to_check)
                start_btn.on_click = lambda e: self.type_selector(e)
                start_btn.update()
                control_main.update()
            except Exception :pass
            


    def type_color_selector(self,e):
        http_btn.bgcolor = '#303236'
        https_btn.bgcolor = '#303236'
        socks4_btn.bgcolor = '#303236'
        socks5_btn.bgcolor = '#303236'
        all_btn.bgcolor = '#303236'
        e.control.bgcolor ='red'
        self.type = e.control.content.value
        if self.type != 0 or len(self.type) !=0:
            self.type_selectod = True
        self.page.update()


    def type_selector(self,e):
        start_btn.bgcolor = '#303236'
        if self.type and self.mode:
            self.state = e.control.content.value
            e.control.bgcolor ='red'
            e.control.update()

        else:pass
        if self.state != '' or len(self.state) != 0:
            self.state_selectod = True

        if self.state == 'Start':
            self.start()

    def start(self):

        if self.type and self.state == 'Start' and self.mode =='Scrape':
            self.page.dialog = self.confirm_alert
            self.confirm_alert.open = True
            self.page.update()

    def convert_text_to_list(self):
        string =self.proxys
        proxy_list = []
        proxys = string.replace('\r','')
        proxys = proxys.split('\n')
        for proxy in proxys:
            if len(proxy) <5 :
                proxys.remove(proxy)
            else:
                proxy_list.append(proxy)
        self.proxy_list_type = list
        return proxy_list
    
    def update_prog_bar(self):
        proxy = self.convert_text_to_list()
        length = len(proxy)
        value = 1/length
        old_count = 0
        while self.checking:
            
            count = open('prog_temp.txt','r').readlines()
            count_value = int(count[0]) if len(count)!=0 else 0
            
            if count_value!= old_count and count_value<=length:
                prog_b.value = value*count_value
                prog_b.update()
                old_count = count_value
            else:
                pass
            
    def stop(self,e):
        if self.mode == 'Check':
            self.checking = False
            self.checker_thread.cancel()
            self.out_updater.cancel()
            self.prog_updater.cancel()
            self.checker.stop()
            start_btn.bgcolor = '#303236'
            start_btn.update()
            # Checker
            import sys
            sys.exit()
        else:pass

def run_gui():
    flet.app(target=ProxtToolKitGui)
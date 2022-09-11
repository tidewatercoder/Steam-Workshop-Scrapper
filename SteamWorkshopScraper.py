import PySimpleGUI as sg
import pickle
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
keys = []
links = []
whoami = os.getlogin()
x = str(datetime.now().month)
x2 = str(datetime.now().day)
x3 = str(datetime.now().year)
timenow = x+'/'+x2+'/'+x3
print(timenow)
def Directory():
    customkeys = {}
    layout = [[sg.Button('Scraper'),sg.Button("Create a Link"),sg.Button("FileSelect")]]
    window = sg.Window("Directory",layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Scraper":
            try:
                with open('links.pickle','rb') as g:
                    customkeys = pickle.load(g)
                window.close()
                SelectScreen(customkeys)
                break
            except Exception:
                sg.Popup("ERROR: Please create a link or check for file!")
                window.close()
                Directory()
                break
        elif event == "Create a Link":
            window.close()
            Combine()
            break
        elif event == "FileSelect":
            window.close()
            FileSel()
            break
def Combine():
    customkeys = {}
    pwd = os.listdir()
    while True:
        if 'Notice.txt' in pwd:
            with open("Notice.txt",'r') as g:
                g.read()
                while True:
                    if '1' in g:
                        break
                    else:
                        sg.popup('This only works on the steam workshop',
                                 'To get this type of link go to the steam workshop and search for the desired game you wish to scrap, '
                                 'after you reach the desired game, select most popular, most subscribed, or most recent. After that scroll '
                                 'all the way to "see all items" and click it, then grab the url and add &actualsort=trend&p= to the end of the url and you will '
                                 'have a url that will work',
                                 'https://steamcommunity.com/workshop/browse/?appid=107410&browsesort=mostrecent&section=readytouseitems&actualsort=mostrecent&p=')
                                 # [sg.Checkbox('Disable Hints',key='_DIS_')])
                        break
                break
        else:
            with open("Notice.txt",'w') as g:
                g.write('0')
                g.close()
    if 'links.pickle' in pwd:
        with open('links.pickle', 'rb') as g:
            customkeys = pickle.load(g)

    ### If the pickle file in is in the current directory it will load all links into the customkey
    ### If the pickle does not exist it will create one for the user.
    #### Create your own link that can be saved reloaded for later use
    layout = [[sg.Text('Input LinkName'),sg.Input(key='_FILENAME_')],
              [sg.Text("Input Link"),sg.Input(key="_LINK_")],
              [sg.Button("Submit"),sg.Button("Purge"),sg.Button("Scraper"), sg.Button('Show'),sg.Button('Main Menu')]]
    window = sg.Window("Custom Link Saver", layout)

    while True:
        event, values = window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Submit":
            customkeys[values['_FILENAME_']] = values["_LINK_"]
            print(customkeys)
            ##### The linkname is combined with the link for later storage and use in the coding
            # print(customkeys)
            with open('links.pickle','wb') as g:
                pickle.dump(customkeys,g,protocol=pickle.HIGHEST_PROTOCOL)
        elif event == "Purge":
            customkeys = {}
            with open('links.pickle','wb') as g:
                pickle.dump(customkeys,g,protocol=pickle.HIGHEST_PROTOCOL)
            #### Erases all data from dictionary and pickle file
        elif event == "Scraper":
            window.close()
            SelectScreen(customkeys)
            break
        elif event == "Show":
            keysi = ''
            for i in customkeys:
                keysi += i+'\n'
            sg.Popup(keysi)
        elif event == "Main Menu":
            window.close()
            Directory()
            break


def SelectScreen(cust):
    x = []
    scanlink = []
    for i in cust.keys():
        keys.append(i)
        ### Grabit takes the link name from the dictionary and puts it into its own
        # list called keys for later use

    for i in keys:
        x.append(sg.Checkbox(i,key=f'{i}'))
#### The keys list is in then ran through a for loop and grabing each key one by one
# and assigning them to a pysimplegui checkbox that is added to the x list.
#### This method although allows the user to add as many links as they want, it does
# make it difficult, however, to retrieve the checkbox keys because the keys are assigned
# the name that the user inputs when creating a custom link.
#### Example: user inputs name "Test" the checkbox will be called Test but the key
# will also be called Test.
    layout = [[x],
              [sg.Text("How many pages?"),sg.Spin([i for i in range(1,11)],initial_value=0,key='_PAGENUM2_'),
    sg.Spin([i for i in range(0,11)],initial_value=1,key='_PAGENUM1_')],
              [sg.Button("Submit")]]
    window = sg.Window("Scraper",layout)
    #### When x is called to create the gui window, it grabs each checkbox and creates
# a separate checkbox for each key.
    while True:
        event, values = window.read()
        # print(event)
        if event == sg.WIN_CLOSED:
            window.close()
            break
        key_list = list(values.keys())
        val_list = list(values.values())
        position = val_list.index(True)
        ### The above code helps me to retrieve the unknown keys from the checkboxes,
# allowing the user to create as many links as they wish as long as the link doesnt
# have the same name or url.
        if event == 'Submit':
            for keyi in key_list:
                if values[keyi] == True:
                    scanlink.append(keyi)
            pagenum1 = values['_PAGENUM1_']
            pagenum2 = values['_PAGENUM2_']
            window.close()
            Scan(scanlink,cust,pagenum1,pagenum2)
            break

def Scan(scanlink,cust,pagenum,pagenum2):
    ch = 0
    linkl = []  ### Stores each mods link for their page
    titlel = [] ### Stores the titles of the mods
    tidive = [] ### Stores the description title
    desdive = [] ### Stores the mods description
    Book = {} ### Stores all the letters and matches them to the current date
    Letter = [] ### Stores all information from 1 page

    pagenum2 = int(pagenum2)
    if pagenum2 != 0:
        pagenum += 1
        pagestr = range(pagenum2, pagenum)
    else:
        pagenum += 1
        pagestr = range(1, pagenum)
    #### The pagenumbers are combined to create a range to allow for
    # more than one page to be scanned.
    for i in scanlink:
        pg = 0
        ch += 1
        if ch >= 2:
            linkl *= 0
            titlel *= 0
            tidive *= 0
            desdive *= 0
            Letter *= 0
            Book.clear()
            #### CH is only called if the user is scanning multiple links.
            # When it is called that means a new link is being scanned and the lists
            # that contains the data from the old scans must be purged from the system.
        if i in cust:
            linkname = i
            ans = cust[i]
            for num in pagestr:
                time.sleep(2)
                pg += 1
                if pg >= 2:
                    time.sleep(2)
                    linkl *= 0
                    titlel *= 0
                    tidive *= 0
                    desdive *= 0
                    ### If multiple pages are being scanned after the first
                    # page is scanned pg will be called and the data in the
                    # lists will be purged so they can be reused.
                strnum = str(num)
                Page = requests.get(ans+strnum)
                soup = BeautifulSoup(Page.content, 'html.parser')
                results = soup('div', class_='workshopBrowseItems')
                #### This retrieves the initial page that will be scanned and parsed
                # for data such as mod links and their titles.
                for i in soup.find_all('a',href=True):
                    strme = str(i)
                    shorti = i['href']
                    if i == [] or i == None:
                        break
                    elif 'sharedfiles' in strme:
                        if shorti in linkl:
                            continue
                        elif shorti not in linkl:
                            linkl.append(shorti)
                    ### In order to dive into each separate mod in the page we must
                    # get there assigned urls the code above, helps the program
                    # identify which url is the desired one to be grabbed and is then
                    # added to the linkl list.
                proglen = len(linkl) ### The length of the linkl will be used to make
                                    # progress bar.
                progtime = 0 ### progtime will update the progress bar
                layout = [[sg.Text(f'Page {num} - Diving for info in {linkname} Mods')],
                          [sg.ProgressBar(1,orientation='h',size=(20,20),key="progress")]]
                window = sg.Window("Dive Progress", layout).Finalize()
                progress_bar = window.find_element('progress')
                for divesearch in linkl:
                    event, values = window.read(timeout=0)
                    progtime += 1
                    print(f'Diving into {divesearch}')
                    if event == sg.WIN_CLOSED:
                        window.close()
                        break
                    progress_bar.UpdateBar(progtime, proglen)
                    page = requests.get(divesearch)
                    soup2 = BeautifulSoup(page.content, 'html.parser')
                    diveresults = soup2.find_all('div', class_="detailBox altFooter")
                    ### diveresults takes each separate mods url and parses all the data from the page allowing the
                    # program to grab the mods description and description title.
                    time.sleep(1.5)
                    for dive_element in diveresults:
                        tidive_ele = dive_element.find('div', class_='workshopItemDescriptionTitle')
                        tidiveST = tidive_ele.text.strip()
                        tidive.append(tidiveST)
                        descdive_ele = dive_element.find('div', class_='workshopItemDescription')
                        desdiveST = descdive_ele.text.strip()
                        #desdive.append(desdiveST)
                        dessplit = ''
                    ### dive_element gets the description and title of the mod
                    ### .strip removes the script from the website and brings out clean text.
                        for i in desdiveST:
                            dessplit += i
                        dessplit2 = dessplit.split('. ')
                        xfin = ''
                        for xdes in dessplit2:
                            xfin += '*' + xdes + '.' + '\n'
                        print(xfin)
                        desdive.append(xfin)
                        ### This separates the mods description by the . and puts them in a bullet point style
                        ### The space at the end of the split '. ' helps with detecting the end of a sentance but,
                        # if a random . is placed in the sentance it will still treat it like the end of a sentance.
                        #### This is not important to the code so it can be taken out if wished, just hash out from
                        # for i in desdiveST to desdive.append(xfin) and unhash desdive.append(desdiveST).
                        print("Info Found")
                for job_element in results:
                    results2 = job_element.find_all('div', class_='workshopItemTitle')
                for title_ele in results2:
                    title_ele2 = title_ele.text.strip()
                    titlel.append(title_ele2)
                    ### Is used to find the mods Title
                window.close()
                Letter.append(f'Page {num}'+'\n')
                for lst, lst2, lst3, lst4 in zip(titlel,linkl,tidive,desdive):
                    Letter.append(f'Title '+lst+'\nLink '+lst2+'\n'+lst3+'\n-'+lst4+'\n'+'\n')
                    ##### Based on which page is scanned, the mods title, description, link, and description title are
                    # added together and then added to the letter list
                Book[timenow] =  Letter
                ### After all pages (that have been requested) are scanned, the letters list is then combined with
                # todays date and added to the Book dictionary
            for picbook in Book:
                with open(f'{linkname}.pickle','wb') as gw:
                    pickle.dump(Book, gw, protocol=pickle.HIGHEST_PROTOCOL)
                    #### If it doesnt exist the pickle file is created and is given the name that was assigned to the
                    # link that was scanned, then the contents from the
                    # book dictionary is dumped into the file saving all the data that was scanned.
    Directory()

def FileSel():
    selpickle = sg.PopupGetFile("Pick Your Pickle!")
    if selpickle != None:
        FileViewer(selpickle)
    else:
        Directory()
    ### Selects the file to viewed, pickeled and text only
def FileViewer(selpickle):
    x = ''
    xspl = selpickle.split('/')
    if '.pickl' in selpickle:
        xlist = list(filter(lambda x: '.pickle' in x, xspl))
        for i in xlist:
            refinx = i
        with open(selpickle,'rb+') as gw:
            randomdic = {}
            randomdic = pickle.load(gw)
            for i in randomdic.values():
                for ilst in i:
                    x += ilst

    else:
        xlist = list(filter(lambda x: '.txt' in x, xspl))
        for i in xlist:
            refinx = i
        with open(selpickle,'r+') as gw:
            x = gw.read()

    layout = [[[sg.MenubarCustom([['Menu',['Main Menu','Save','Open','Exit']]])],
               sg.Multiline(x, size=(100,40),key='_WRITEME_')]]
    window = sg.Window(f"{refinx}",layout,return_keyboard_events=True)
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            gw.close()
            break
    ### Views the file in a gui format
        elif event == 'Main Menu':
            yes_no = sg.PopupYesNo('Go back to the main menu?')
            if yes_no == 'Yes':
                window.close()
                gw.close()
                Directory()
                break
        elif event == 's:83' or event == "Save":
            if ".pickle" in selpickle:
                with open(selpickle, 'rb+') as gw:
                    ans = randomdic.keys
                    randomdic = {}
                    randomdic[ans] = values['_WRITEME_']
                    pickle.dump(randomdic,gw,protocol=pickle.HIGHEST_PROTOCOL)
            ### If the file is a pickle, it can be saved by dumping all the info into the file
            else:
                with open(selpickle, 'w') as gw:
                    gw.write(values['_WRITEME_'])
                    gw.flush()
                ### Saves a text file
        elif event == 'Open':
            fileselect = sg.PopupGetFile('Select File!')
            if fileselect != None:
                window.close()
                FileViewer(fileselect)
                break

if __name__ == '__main__':
    Directory()

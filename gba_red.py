import os, math,sys,re,datetime,time
from os import listdir
from os.path import isfile, join

"""
TODO:
- Triar si vols es nom amb location
- Triar sufixe de rom si no canvia de nom i no se borra s'anterior
"""

text={
    "es":{
    "INFO_name_language":"Español",
    "INFO_progres":"Progreso",
    "INFO_item_list_found":"Estos son los archivos encontrados:",
    "INFO_erase_rom":"Eliminando %s.",
    "INFO_rom_props":"Las características de la rom:",
    "INFO_no_lang_verbose":"No se ha selecionado idioma",
    "INFO_item_select":"Que imagenes deseas seleccionar:",
    "ERROR_none_verbose_mode":"No se reconoce el modo. Use:",
    "ERROR_type_verbose_mode":"No se reconoce el modo. Use:",
    "ERROR_type_language_mode":"Idioma no reconocido. Use:",
    "INFO_rom_info_error_no_rom":"No se reconoce el formato de la rom. %s",
    "ERROR_index_no_exist":"Uno de los valores introducidos no existe.",
    "INFO_rom_info_finish":"Reducir| Rom:%s Peso:%s Basura:%s Tiempo:%ss\nSalida:%s ",
    "INFO_rom_info_finish_repair":"Reparar| Rom:%s Peso:%s Tiempo:%ss\nSalida:%s",

    "INFO_rom_info_only":(
    """ARCHIVO:        %s%s\n"""     \
    """PESO:           %s   \n"""     \
    """NOMBRE ROM:     %s   \n"""     \
    """LICENCIA:       %s   \n"""     \
    """LOCATION:       %s   \n"""     \
    """LOGO:           %s   \n"""     \
    """HEADER CHECK:   %s   \n"""     \
    """VERSIÓN         %s   """),
    "HELP":"""    GBAX
    Utiles para roms de GBA

    Opciones              Descripción
    -a                    Muestra solo la info de la rom.
    -n                    Cambia el nombre de la rom por el de la base de datos.
    -r                    Recursivo.
    -s                    Seleccionar los archivos a convertir.
    -i                    Ruta de entrada personalizada.
    -o                    Ruta de salida personalizada.
    -d                    Elimina el archivo de origen.
    -f                    Solo reparar la rom.
    -v [mode][Idioma]     Verbose - all|short Idioma

    Para el cambio de Idioma usar '-v código_de_idioma'
    Ej: -v es | Para el español.
    Idiomas disponibles:"""
    }
}

#Utils--------------------------------------------------------------------------
def getDate():
    now = datetime.datetime.now()
    return ("%02i:%02i:%02i")%(now.hour, now.minute, now.second)

def bytesToSize(bytes):
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
       return '0 Byte'
    i = int(math.floor(math.log(bytes) / math.log(1024)))
    return str(round(bytes / math.pow(1024, i), 2)) + ' ' + sizes[i]

def printError(text):
    print(text)

def printInfo(text,verbose,type):
    if verbose == type or verbose == 'all' or type =='info':
        print(text)

def get_terminal_size(fd=sys.stdout.fileno()):
    h,w = os.popen('stty size', 'r').read().split()
    return int(h),int(w)

def update_progress(progress,in_text):
    #Calculate bar len
    barLength = (console_width-len(text[LG]["INFO_progres"]+
                " "+in_text+": 100% []") - 1)
    #Calculate nº blocks
    block = int(round(barLength*progress)) + 1

    #Format text
    out_text = ("\r"+text[LG]["INFO_progres"]+
            " "+in_text+": [{blocks}] {percent:.0f}%".format(
            blocks="■" * block + "-" * (barLength - block),
            times=time,
            percent=progress * 100))

    sys.stdout.write(out_text)
    sys.stdout.flush()

def create_bar(path):
    #Calculate bar len
    barLength = (console_width-len(path) - 1)
    #Format text
    text = (path +"{blocks}".format(
            blocks="-" * barLength))

    return text

def getFileSize(file):
    statinfo = os.stat(file)
    return statinfo.st_size

#Files--------------------------------------------------------------------------
def getFile(extension,path_):
    try:
        if path_:
            path=path_
        else:
            path = os.getcwd()
    except:
        path = os.getcwd()

    extension_len=len(extension)
    files_list = []

    if RECURSIVE == True:
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                if filename[-extension_len:] == extension:
                    files_list.append({"root":root,"filename":filename})

        return len(files_list),files_list

    else:
        for f in listdir(path):
            if isfile(join(path, f)):
                if f[-extension_len:] == extension:
                    files_list.append({"root":path,"filename":f})

        return len(files_list),files_list


def selectFiles(extension):
    nfiles,files =getFile(extension,INPUT_PATH)
    printInfo(text[LG]["INFO_item_list_found"]
             +" "+str(nfiles),VERBOSE_MODE,"info")

    if SELECT_FILES:
        root=""
        while True:
            for index, file in enumerate(files):
                if file["root"] != root:
                    root = file["root"]
                    printInfo(create_bar(root),VERBOSE_MODE,"info")
                printSTR = "  "+str(index)+":  "+file["filename"]
                printInfo(printSTR,VERBOSE_MODE,"info")
            select_indexes = (input(text[LG]["INFO_item_select"])
                              .split())
            selected=[]
            try:
                for index in select_indexes:
                    selected.append(files[int(index)])
                break

            except:
                printInfo(text[LG]["ERROR_index_no_exist"],
                         VERBOSE_MODE,"info")

        for x in selected:
            printInfo(os.path.join(x["root"],x["filename"]),
                     VERBOSE_MODE,"short")
        return selected
    else:
        for index, file in enumerate(files):
            printInfo(str(index)+":  "+
                      os.path.join(file["root"],file["filename"]),
                      VERBOSE_MODE,"short")
        return files


#Data files
def loadNames(file):
    '''
    Loads names from file with this fromat:
    (16 bytes) Header Rom Name | (4 bytes) Rom Code | Comercial Name
    Ej: CIMATHEENEMYBCME|BCME|CIMA - The Enemy

    The source of the current file is:
        https://github.com/pladaria/gba-romname-gen/blob/master/romname.lst
    Thank you.
    '''
    with open(file,'r') as file:
        dic = {}
        for line in file:
            dic[line[17:21]]=line[22:-1]
        file:close()
        return dic


def loadLicensee(file):
    '''
    Loads Licensee from file with this fromat:
    (2 bytes) Licensee Code | Enterprise
    The source of the current file is:
        https://gbdev.gg8.se/wiki/articles/The_Cartridge_Header
    Thank you.
    '''
    with open(file,'r') as file:
        dic = {}
        for line in file:
            dic[line[:2]]=line[3:-1]
        file:close()
        return dic


#Rom Utils
def calculateChecksum(array):
    '''
    Header checksum, cartridge won't work if incorrect. Calculate as such:
        chk=0:
        for i=0A0h to 0BCh:
            chk=chk-[i]:
        next:
            chk=(chk-19h) and 0FFh

    Font:https://www.akkit.org/info/gbatek.htm#gbacartridgeheader
    '''

    checksum = 0
    for byte in array:
        checksum+=byte
    checksum=0 - (checksum+0x19)
    checksum = checksum % 256

    return checksum


def readHeader(file):
    '''
    Header Overview
    Address Bytes Expl.
    000h    4     ROM Entry Point  (32bit ARM branch opcode, eg. "B rom_start")
    004h    156   Nintendo Logo    (compressed bitmap, required!)
    0A0h    12    Game Title       (uppercase ascii, max 12 characters)
    0ACh    4     Game Code        (uppercase ascii, 4 characters)
    0B0h    2     Maker Code       (uppercase ascii, 2 characters)
    0B2h    1     Fixed value      (must be 96h, required!)
    0B3h    1     Main unit code   (00h for current GBA models)
    0B4h    1     Device type      (usually 00h)
    0B5h    7     Reserved Area    (should be zero filled)
    0BCh    1     Software version (usually 00h)
    0BDh    1     Complement check (header checksum, required!)
    0BEh    2     Reserved Area    (should be zero filled)
    --- Additional Multiboot Header Entries ---
    0C0h    4     RAM Entry Point  (32bit ARM branch opcode, eg. "B ram_start")
    0C4h    1     Boot mode        (init as 00h - BIOS overwrites this value!)
    0C5h    1     Slave ID Number  (init as 00h - BIOS overwrites this value!)
    0C6h    26    Not used         (seems to be unused)
    0E0h    4     JOYBUS Entry Pt. (32bit ARM branch opcode, eg. "B joy_start")
    Font:https://www.akkit.org/info/gbatek.htm#gbacartridgeheader
    '''
    open_file = open(file,'rb')

    rom=open_file.read()
    try:
        if rom[178:179] != b'\x96':
            return False
        else:
            romChecksumCalculate = calculateChecksum(rom[160:189])
            romData ={
                'romStart':rom[:3],
                'romName':rom[160:176].decode('utf-8'),
                'romCode':rom[172:176].decode('utf-8'),
                'romLogo':default_logo == rom[4:160],
                'romLicensee':rom[176:178].decode('utf-8'),
                'romChecksumRom':ord(rom[189:190]),
                'romChecksumCalculate':romChecksumCalculate ,
                'romChecksum': ord(rom[189:190]) == romChecksumCalculate,
                'romSize': bytesToSize(getFileSize(file)),
                'romVersion':ord(rom[188:189])
            }

            open_file.close()

            return romData
    except:
        return False

def repairRom(file):
    romStart=file[:4]
    romLogo=default_logo
    romName=file[160:189]
    romChecksumRom=bytes([calculateChecksum(file[160:189])])
    romEnd=file[190:]

    return romStart+romLogo+romName+romChecksumRom+romEnd
#Rom Utils
def repairRomOnly(file,info,path,OUTPUT_PATH):
    o_file=file
    if OUTPUT_PATH == "":
        OUTPUT_PATH = path
    if RENAME:
        name_out =os.path.join(OUTPUT_PATH,info[3]+".gba")
    else:
        name_out = os.path.join(OUTPUT_PATH,info[1][:-4]+"_repair.gba")

    printInfo(text[LG]["INFO_rom_info_only"]%(info),
              VERBOSE_MODE,
              "all")
    start_time = time.time()
    with open(file,'rb') as file:
        rom = file.read()
        trim_size=0
        update_progress(0,"Read file")
        if info[6] == "False" or info[7] == "False":
            update_progress(0.5,'Repair Rom')
            rom =repairRom(rom)
        update_progress(0.5,'Write rom')
        temp_file=open(name_out,'wb')
        temp_file.write(rom)
        if REMOVE and o_file != name_out:
            os.remove(o_file)
        temp_file.close()
        update_progress(1,'Finished')
        printInfo("",VERBOSE_MODE,"info")
        elapsedTime=math.floor((time.time() - start_time)*10)/10
        return info[1], info[2], elapsedTime, name_out

def trimRom(file,info,path,OUTPUT_PATH):
    o_file=file
    if OUTPUT_PATH == "":
        OUTPUT_PATH = path
    if RENAME:
        name_out =os.path.join(OUTPUT_PATH,info[3]+".gba")
    else:
        name_out = os.path.join(OUTPUT_PATH,info[1][:-4]+"_trim.gba")


    printInfo(text[LG]["INFO_rom_info_only"]%(info),
              VERBOSE_MODE,
              "all")
    start_time = time.time()

    with open(file,'rb') as file:
        rom = file.read()[::-1]
        temp_data = file.read()
        trim_size=0
        update_progress(0,"Read file")
        for index,byte in enumerate(rom):
            if (bytes([byte]) == b"\x00" or bytes([rom[index+1]]) == b"\xff"
            and bytes([byte]) == b"\x00" or bytes([rom[index+1]]) == b"\xff"):
                pass
            else:
                trim_size = bytesToSize(index)
                temp_data = rom[index+1:][::-1]
                break

        if info[6] == "False" or info[7] == "False":
            update_progress(0.5,'Repair Rom')
            temp_data =repairRom(temp_data)

        update_progress(0.5,'Write rom')
        temp_file=open(name_out,'wb')
        temp_file.write(temp_data)
        if REMOVE and o_file != name_out:
            os.remove(o_file)
        temp_file.close()
        update_progress(1,'Finished')
        printInfo("",VERBOSE_MODE,"info")
        elapsedTime=math.floor((time.time() - start_time)*10)/10
        return info[1], info[2], trim_size, elapsedTime, name_out

def infoRom(LICENSEE,NAMES,dic_header_rom,path,rom_filename):
    locationCode={
        'J':'Japan',
        'P':'Europe/Elsewhere',
        'F':'French',
        'S':'Spanish',
        'E':'USA/English',
        'D':'German',
        'I':'Italian'
    }
    if dic_header_rom == False:
        return False
    else:
        try:
            romFullName = NAMES[dic_header_rom['romCode']]
        except:
            romFullName = "Unknown"

        try:
            romLicensee = LICENSEE[dic_header_rom['romLicensee']]
        except:
            romLicensee = "Unknown"

        romLogo = dic_header_rom['romLogo']
        romSize = dic_header_rom['romSize']
        romChecksum = dic_header_rom['romChecksum']
        romVersion = dic_header_rom['romVersion']

        try:
            romLocation = locationCode[dic_header_rom['romCode'][3:]]
        except:
            romLocation = 'Unknown'

        return path,rom_filename,romSize,romFullName,romLicensee,romLocation,str(romLogo),str(romChecksum),romVersion


#VARIABLES DEFAULT
default_logo = (
b"\x24\xff\xae\x51\x69\x9a\xa2\x21\x3d\x84\x82\x0a\x84\xe4\x09\xad\x11\x24"\
b"\x8b\x98\xc0\x81\x7f\x21\xa3\x52\xbe\x19\x93\x09\xce\x20\x10\x46\x4a\x4a"\
b"\xf8\x27\x31\xec\x58\xc7\xe8\x33\x82\xe3\xce\xbf\x85\xf4\xdf\x94\xce\x4b"\
b"\x09\xc1\x94\x56\x8a\xc0\x13\x72\xa7\xfc\x9f\x84\x4d\x73\xa3\xca\x9a\x61"\
b"\x58\x97\xa3\x27\xfc\x03\x98\x76\x23\x1d\xc7\x61\x03\x04\xae\x56\xbf\x38"\
b"\x84\x00\x40\xa7\x0e\xfd\xff\x52\xfe\x03\x6f\x95\x30\xf1\x97\xfb\xc0\x85"\
b"\x60\xd6\x80\x25\xa9\x63\xbe\x03\x01\x4e\x38\xe2\xf9\xa2\x34\xff\xbb\x3e"\
b"\x03\x44\x78\x00\x90\xcb\x88\x11\x3a\x94\x65\xc0\x7c\x63\x87\xf0\x3c\xaf"\
b"\xd6\x25\xe4\x8b\x38\x0a\xac\x72\x21\xd4\xf8\x07"
)
LG = 'es'
ONLYREPAIR = False
ONLYINFO = False
RENAME = False
REMOVE = False
RECURSIVE = False
SELECT_FILES = False
RUN = True
VERBOSE_TYPE = {"short":"Short Mode","all":"All Mode"}
VERBOSE_MODE = ""
INPUT_PATH = ""
OUTPUT_PATH = ""
LICENSEE = loadLicensee('gba_licensee')
NAMES = loadNames('gba_names')
(console_height, console_width) = get_terminal_size()

args = len(sys.argv)
if args <= 1:
    RUN=False
    printError(text[LG]["HELP"])
else:
    for index, arg in enumerate(sys.argv):
        if arg == "-r":     #Recursive files
            RECURSIVE= True
        if arg == "-s":     #Select Files
            SELECT_FILES=True
        if arg == "-f":
            ONLYREPAIR = True
        if arg == "-v":     #Active verbose
            try:
                if sys.argv[index+1]:
                    try:
                        if VERBOSE_TYPE[sys.argv[index+1]]:
                            VERBOSE_MODE = sys.argv[index+1]
                        else:
                            printError(text[LG]["ERROR_type_verbose_mode"])
                            for type in VERBOSE_TYPE:
                                printError("%s - %s"%(type,VERBOSE_TYPE[type]))
                    except:
                        printError(text[LG]["ERROR_type_verbose_mode"])
                        for type in VERBOSE_TYPE:
                            printError("%s - %s"%(type,VERBOSE_TYPE[type]))

            except:
                printError(text[LG]["ERROR_none_verbose_mode"])
                for type in VERBOSE_TYPE:
                    printError("%s - %s"%(type,VERBOSE_TYPE[type]))

            try:
                if sys.argv[index+2]:
                    try:
                        if text[sys.argv[index+2]]:
                            LG = sys.argv[index+1]
                        else:
                            printError(text[LG]["ERROR_type_language_mode"])
                            for lang in text:
                                printError("%s - %s"%(lang,text[lang]["INFO_name_language"]))
                    except:
                        printError("%s - %s"%(lang,text[lang]["INFO_name_language"]))
            except:
                printInfo(text[LG]["INFO_no_lang_verbose"],VERBOSE_MODE,"all")
        if arg == "-i":     #Custom path input
            try:
                if sys.argv[index+1]:
                    if re.match("^/[^%S]*", sys.argv[index+1]):
                        INPUT_PATH = sys.argv[index+1]+"/"
                    else:
                        INPUT_PATH = ""
            except IndexError:
                INPUT_PATH = ""
        if arg == "-o":     #Custom path output
            try:
                if sys.argv[index+1]:
                    if re.match("^/[^%S]*", sys.argv[index+1]):
                        OUTPUT_PATH = sys.argv[index+1]+"/"
                    else:
                        OUTPUT_PATH = ""
            except IndexError:
                OUTPUT_PATH = ""
        if arg == "-d":     #Remove files after compress
            REMOVE = True
        if arg == "-a":     #Only Info
            ONLYINFO = True
        if arg == "-n":     #Change name file for DATA name
            RENAME = True

def main():
    files = selectFiles("gba")
    total_start_time = time.time()
    for index,rom in enumerate(files):
        romPath = os.path.join(rom['root'],rom['filename'])
        romHeader = infoRom(LICENSEE,
                            NAMES,
                            readHeader(romPath),
                            rom['root'],
                            rom['filename'])
        if romHeader != False:
            if ONLYINFO:
                printInfo(text[LG]["INFO_rom_info_only"]%(romHeader),
                          VERBOSE_MODE,
                          "info")
            else:
                if ONLYREPAIR:
                    romResult = repairRomOnly(romPath,romHeader,rom['root'],OUTPUT_PATH)
                    printInfo(text[LG]["INFO_rom_info_finish_repair"]%(romResult),
                              VERBOSE_MODE,
                              "info")

                else:
                    romResult = trimRom(romPath,romHeader,rom['root'],OUTPUT_PATH)
                    printInfo(text[LG]["INFO_rom_info_finish"]%(romResult),
                              VERBOSE_MODE,
                              "info")
        else:
            printInfo(text[LG]["INFO_rom_info_error_no_rom"]%romPath,
                      VERBOSE_MODE,
                      "info")
        total_elapsed_time =  time.time() - total_start_time
if RUN == True:
    main()

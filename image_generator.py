# import csv reader
import math
import sys
import pandas as pd
from playwright.sync_api import sync_playwright, PlaywrightContextManager
import qrcode
from PIL import Image, ImageFilter, ImageFont, ImageDraw
import os.path
import aggdraw

# defining global variables
card_size = (1311, 1819) # the size of the final card in pixels, required for the printservice
amount_title_cards = 1 # the amount of title cards to create
screenshot_folder = 'tmp_screenshots\\'
qrcode_folder = 'tmp_qr-codes\\'
card_folder = 'output\\'
minor_font = "arial.ttf"
major_font = "courbd.ttf"

def init_folders():
    """initialize the folders for the screenshots, qr-codes and the final cards
    """
    global screenshot_folder
    global qrcode_folder
    global card_folder
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
    if not os.path.exists(qrcode_folder):
        os.makedirs(qrcode_folder)
    if not os.path.exists(card_folder):
        os.makedirs(card_folder)

def take_screenshot(pw:PlaywrightContextManager, url:str, filename:str,):
    """take a screenshot from a given url and save it as a png file with the given filename in the given folder

    Args:
        pw (PlaywrightContextManager): a PlaywrightContextManager
        url (str): the url of the website to take a screenshot from
        filename (str): the name the png file should have
    """
    global screenshot_folder
    if os.path.exists(f'{screenshot_folder}{filename}.png'):
        return
    browser = pw.firefox.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.screenshot(path=f'{screenshot_folder}{filename}.png')
    page.close()
    browser.close()

def create_qr_code(url:str, filename:str):
    """Create a qr-code from a given url and save it as a png file with the given filename in the given folder

    Args:
        url (str): the url to create a qr-code from
        filename (str): the name the png file should have
    """
    global qrcode_folder
    if os.path.exists(f'{qrcode_folder}{filename}.png'):
        return
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f'{qrcode_folder}{filename}.png')

def round_corners(image:Image, radius:int=10)->Image:
    """round the corners of a given image with a given radius

    Args:
        image (Image): the image to round the corners
        radius (int, optional): the radius of the rounded corners. Defaults to 10.

    Returns:
        Image: the image with rounded corners
    """
    mask = Image.new('L', image.size)
    draw = aggdraw.Draw(mask)
    brush = aggdraw.Brush('white')
    width, height = mask.size
    #upper-left corner
    draw.pieslice((0,0,radius*2, radius*2), 90, 180, None, brush)
    #upper-right corner
    draw.pieslice((width - radius*2, 0, width, radius*2), 0, 90, None, brush)
    #bottom-left corner
    draw.pieslice((0, height - radius * 2, radius*2, height),180, 270, None, brush)
    #bottom-right corner
    draw.pieslice((width - radius * 2, height - radius * 2, width, height), 270, 360, None, brush)
    #center rectangle
    draw.rectangle((radius, radius, width - radius, height - radius), brush)
    #four edge rectangle
    draw.rectangle((radius, 0, width - radius, radius), brush)
    draw.rectangle((0, radius, radius, height-radius), brush)
    draw.rectangle((radius, height-radius, width-radius, height), brush)
    draw.rectangle((width-radius, radius, width, height-radius), brush)
    draw.flush()
    image = image.convert('RGBA') # convert for transparancy
    image.putalpha(mask)
    return image

def text_breaker(text:str)->list[str]:
    """converts a text into lines that fit into a textbox of max 36 characters per line. The Text is splittet at the last space before the 36th character

    Args:
        text (str): the text to break into lines

    Returns:
        list[str]: a list of lines that fit into the textbox
    """
    lines = []
    while len(text) > 34:
        last_space = text[:34].rfind(' ')
        lines.append(text[:last_space])
        text = text[last_space+1:]
    lines.append(text)
    return lines

def card_creator(screenshot_path:str, qr_code_path:str, url:str, description:str, filename:str):
    """merge a screenshot with a qr-code, a url and a description into one image and save it as a png file with the given filename in the given folder to create the final card

    Args:
        screenshot_path (str): the path to the screenshot
        qr_code_path (str): the path to the qr-code
        url (str): the url of the website
        description (str): the description of the website
        filename (str): the name the png file should have
    """
    global card_folder
    global card_size
    global minor_font
    global major_font
    if os.path.exists(f'{card_folder}{filename}.png'):
        return
    # open the screenshot
    screenshot = Image.open(screenshot_path).resize(card_size)
    screenshot = screenshot.filter(ImageFilter.GaussianBlur(radius=10))
    # qr-code
    qr_code = Image.open(qr_code_path).resize((325, 325))
    qr_code = round_corners(qr_code)
    screenshot.paste(qr_code, (screenshot.width-375, screenshot.height-375), qr_code)
    # textbox
    textbox = Image.new('RGBA', (screenshot.width - 450, 325), (255, 255, 255, 150))
    textbox = round_corners(textbox)
    screenshot.paste(textbox, (50, screenshot.height-375), textbox)
    # url
    font = ImageFont.truetype(minor_font, 25)
    draw = ImageDraw.Draw(screenshot)
    draw.text((75, screenshot.height-330), url, (128, 128, 128), font=font)
    # description
    font = ImageFont.truetype(major_font, 40)
    text_height = screenshot.height-290
    for l in text_breaker(description):
        draw.text((75, text_height), l, (0, 0, 0), font=font)
        text_height = text_height+40
    screenshot = screenshot.rotate(90, expand=True)
    screenshot.save(f'{card_folder}{filename}.png')

def create_index_cards(df:pd.DataFrame, background_path:str):
    """create index cards with the given background image

    Args:
        df (pd.DataFrame): The dataframe with the urls and descriptions
        background_path (str): the path to the background image
    """
    global card_size
    global card_folder
    if os.path.exists(f'{card_folder}index_{str(math.ceil(df.size/26))}.png'):
        return
    # open the background image
    background = Image.open(background_path).resize(card_size)
    # add the text
    font = ImageFont.truetype(minor_font, 25)
    draw = ImageDraw.Draw(background)
    text_height = 200
    counter = 1
    for index, row in df.iterrows():
        if counter % 26 == 0:
            background = background.rotate(90, expand=True)
            background.save(f'{card_folder}index_{str(math.floor(counter/26))}.png')
            background = Image.open(background_path).resize(card_size)
            draw = ImageDraw.Draw(background)
            text_height = 200
        draw.text((100, text_height), row['url'], (0, 0, 0), font=font)
        text_height = text_height+60
        counter += 1
    # save the index page
    background = background.rotate(90, expand=True)
    background.save(f'{card_folder}index_{str(math.ceil(counter/26))}.png')

def create_title_card(background_path:str, amount:int=1):
    """create a title card with the given background image

    Args:
        background_path (str): the path to the background image
    """
    global card_size
    global card_folder
    while amount > 0:
        amount-=1
        if os.path.exists(f'{card_folder}title_{amount}.png'):
            continue
        else:
            background = Image.open(background_path).resize(card_size).rotate(90, expand=True)
            background.save(f'{card_folder}title_{amount}.png')

def delete_temp_files():
    """delete all temporary files
    """
    global screenshot_folder
    global qrcode_folder
    global card_folder
    for file in os.listdir(screenshot_folder):
        if '.png' in file: os.remove(f'{screenshot_folder}{file}')
    for file in os.listdir(qrcode_folder):
        if '.png' in file: os.remove(f'{qrcode_folder}{file}')
    for file in os.listdir(card_folder):
        if '.png' in file: os.remove(f'{card_folder}{file}')

def picture_sorter(pictures:list[str])->list[str]:
    """sort a list of picture paths by the number in the filename and files with 'index_' in their name come last

    Args:
        pictures (list[str]): a list of picture paths

    Returns:
        list[str]: the sorted list of picture paths
    """
    def sort_key(x:str):
        """sort key function for the sorted function

        Args:
            x (str): the filename

        Returns:
            int: for title_cards the minimal value plus the number in the filename, for index_cards the maximal value minus 100 plus the number in the filename, for all other cards the number in the filename
        """
        if 'index_' in x:
            return sys.maxsize-100+ int(x.split('.')[0].split('_')[-1])
        elif 'title_' in x:
            return -sys.maxsize-1 + int(x.split('.')[0].split('_')[-1])
        else:
            return int(x.split('.')[0])
    return sorted(pictures, key=sort_key)

def main():
    """main function to generate screenshots, qr-codes and the final cards for the printservice
    """
    global screenshot_folder
    global qrcode_folder
    global amount_title_cards

    init_folders()
    df = pd.read_csv('websites.csv')
    pd.set_option('display.max_colwidth', None)
    # create a playwrightcontextmanager
    with sync_playwright() as pw:
        # iterate over the rows of the csv file
        for index, row in df.iterrows():
            # take the screenshots of the websites
            for retry in range(3):
                try:
                    take_screenshot(pw, row['url'], str(index))
                    # create a qr-codes for the websites
                    create_qr_code(row['url'], str(index))
                    # merge the screenshot and the qr-code
                    card_creator(f'{screenshot_folder}{str(index)}.png', f'{qrcode_folder}{str(index)}.png', row['url'], row['description'], str(index+1))
                    break
                except:
                    print(f'Error: {row["url"]} could not be loaded \n retry {retry+1} of 3')
                    continue
    create_index_cards(df,'assets\\Mangowiggles.png')
    create_title_card('assets\\Mangowiggles.png', amount_title_cards)
    # create pdf
    cards = []
    for file in picture_sorter(os.listdir(card_folder)):
        img = Image.open(f'{card_folder}{file}')
        img.load()
        background = Image.new('RGB', tuple(reversed(card_size)), (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        cards.append(background)
    cards[0].save('cards.pdf', "PDF", resolution=100.0, save_all=True, append_images=cards[1:])
    # delete_temp_files() # uncomment to delete the temporary files, keep it as is for faster run times in multiple consecutive runs

if __name__ == '__main__':
    main()
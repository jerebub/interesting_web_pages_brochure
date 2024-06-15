# About
This project is the result of a farewell-gift for my friend. It is a simple application that collects screenshots of websites I found entertaining or noteworthy and designs a calender-like layout for them. Sadly I could only find about 150 websites that fit my criteria, so I don't have enough for an entire year. Nevertheless, I hope she'll enjoy the present and maybe I can add some more sites to the collection in the future.

The code is written in python 3.9.5 and uses the following libraries:
- pandas , for csv-handling
- pillow , to edit the images
- aggdraw , to draw on the images
- qrcode , to generate qr-codes
- playwright , to take screenshots of websites

The printservice used will be https://www.wir-machen-druck.de/broschuere-mit-metallspiralbindung-endformat-din-a6-quer-156seitig.html#nav-printdata. Due to the format of the final print, there are some restrictions to the size of the images. The final images will fit on an A6 page. For printing I needed to add some margins. Fell free to adapt them to your own needs in the code.

# Structure
The list of websites with their description is in the websites.csv file. The screenshots are in the tmp_screenshots folder. The screenshots are named after the website's index in the csv. All images are in the .png format.
QR-Codes linking to the website are stored in the tmp_qr-codes folder.
The final calender pages are in the output folder.
The code to generate everything is in the image_generator.py file.
Additional assets I used for the cover page and the index-pages are in the assets folder. But due to copyright not uploaded to github.

# Learnings
Here are some things I learned while working on this project:
- How to take screenshots of websites with playwright
- playwright does not work right in jupyter notebooks
- How to edit images with pillow
- How to generate qr-codes with qrcode
- How to create a pdf with multiple pages with pillow
- Pandas shortens a colums with and truncates the text in it. that can be changed with pd.set_option('display.max_colwidth', None)

# Usage
for the code to work you need to install the required libraries. You can do this by running the following command in the terminal:
```bash
pip install -r requirements.txt
```
afterwards you can run the code with the following command:
```bash
playwright install --with-deps firefox
```

make sure the required fonts are installed on your system: arial.ttf and courbd.ttf

then you can run the code with the following command:
```bash
python image_generator.py
```

If you want the code to delete the screenshots and qr-codes after the pdf is created, you can uncomment the call for delete_temp_files() at the end of the main function. I'am keeping the images, so that I don't have to take the screenshots again, if I want to print the calender again.

Feel free to use the code for your own projects or just for fun. Let's all enjoy the wonderful sites of the world wide web.

# next steps
- add more websites to the collection
- add a back page
- ~~add a legend page~~
- add the calendar function (day, month, year)
- add notes about the holidays
- add a icons representing the moon phases in central germany
- add info about the sunrise and sunset times in central germany

from modules.helper import *
from modules.downloader import *


class Instruction:
    def __init__(self, driver, root_path):
        self.driver = driver
        self.url = driver.current_url
        self.title = ''
        self.subtitle = ''
        self.video = None
        self.paragraphs = []
        self.dir = ''
        self.root = root_path

    def get_meta(self):
        driver = self.driver
        wait_driver(driver, 'class', 'instruction--content--description')

        soup = BeautifulSoup(driver.page_source, 'lxml')
        video = ''
        elements = []

        in_head = soup.find('div', class_='instruction--content--title')

        # Title
        in_title = in_head.find('h1').getText().strip()
        in_title = sanitize_special_chars(in_title)

        # Subtitle
        in_subtitle = in_head.find('p')

        if in_subtitle:
            in_subtitle = transform_links(in_subtitle)

        # Video
        in_video = soup.find('div', class_='mejs-mediaelement')
        if in_video:
            video_url = soup.find('source', type='video/webm')['src']
            video = Video(in_title, video_url)

        # Description
        in_description = soup.find(
            'div', class_='instruction--content--description').findAll('p', recursive=False)

        if not in_description:
            in_description = soup.find('div', class_='instruction--content--description').find(
                'div', class_='markdown-zone').findChildren(recursive=False)

        for c in in_description:
            paragraph = Paragraph()
            paragraph.tag = c.name
            paragraph.text = transform_links(c)

            # List
            if (c.name == 'ul'):
                for li in c.findAll('li'):
                    p_li = Paragraph()
                    p_li.tag = li.name
                    p_li.text = transform_links(li)

                    elements.append(p_li)

                continue

            # Table
            # TODO: Tabellen = https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#tables
            if not c.get('class') and c.find('table', {'class': 'dataframe'}):
                print(txt.warning + 'Tabelle' + txt.normal)
                sys.exit()

            # Code Sample
            elif(c.name == 'div') and ('highlight' in c['class']):
                paragraph.type = 'code-sample'
                paragraph.text = c.getText().strip()

            elements.append(paragraph)

        # Add Properties
        self.title = in_title
        self.subtitle = in_subtitle
        self.video = video
        self.paragraphs = elements

    def write_instruction(self):
        filename = self.title + '.md'

        with open(filename, 'w') as f:
            # Title and Subtitle
            f.write('## [{}]({})\n'.format(self.title, self.url))
            if self.subtitle:
                f.write('##### {}\n\n'.format(self.subtitle))

            # Video
            if self.video:
                f.write('<video src="' + self.video.title +
                        '.webm" width="100%" controls></video><br><br><br>')

            # Description
            for p in self.paragraphs:
                if (len(self.paragraphs) == 1):
                    f.write('<p align="center">{}</p>\n\n'.format(p.text))
                elif (p.tag == 'h3'):
                    f.write('#### {}\n\n'.format(p.text))
                elif (p.tag == 'li'):
                    f.write('* {}\n\n'.format(p.text))
                elif (p.type == 'code-sample'):
                    f.write('```\n{}\n```\n\n'.format(p.text))
                else:
                    f.write('{}\n\n'.format(p.text))

        return filename

    def start_download(self, in_no=None, sym_target=''):
        driver = self.driver

        self.get_meta()

        # Create and go to Instruction folder
        create_folder(self.root + '/Instructions')
        self.dir = create_folder(self.title)

        txt_filename = self.write_instruction()
        video_filename = ''

        if in_no:
            print(txt.bold + 'Downloading Instructions: ' +
                  txt.normal + '{:02d}. {}'.format(in_no, txt_filename))
        else:
            print(txt.bold + 'Downloading Instructions: ' +
                  txt.normal + txt_filename)

        if self.video:
            video_filename = download_video(driver, self.video)
            download_project_files(driver)

        if sym_target:
            src = str(os.getcwd())

            if (in_no) and ('Tracks' in sym_target):
                target = sym_target + '/' + \
                    '{:02d}. {}'.format(in_no, self.title)

                mk_symlink(src, target)

            else:
                txt_src = src + '/' + txt_filename
                txt_target = ''

                if in_no:
                    txt_target = sym_target + '/' + \
                        '{:02d}. {}'.format(in_no, txt_filename)
                else:
                    txt_target = sym_target + '/' + txt_filename

                mk_symlink(txt_src, txt_target)

                if video_filename:
                    video_src = src + '/' + video_filename
                    video_target = ''

                    if in_no:
                        video_target = sym_target + '/' + \
                            '{:02d}. {}'.format(in_no, video_filename)
                    else:
                        video_target = sym_target + '/' + video_filename

                    mk_symlink(video_src, video_target)


class Video:
    def __init__(self, title, url):
        self.title = title
        self.url = url


class Paragraph:
    def __init__(self):
        self.tag = ''
        self.text = ''
        self.type = ''

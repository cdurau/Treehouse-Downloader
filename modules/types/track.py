import sys
import os
from bs4 import BeautifulSoup

from modules.helper import *
from modules.types.course import *
from modules.types.workshop import *
from modules.types.instruction import *
from modules.types.practice import *


class Track:
    def __init__(self, driver, root_path):
        self.driver = driver
        self.url = driver.current_url
        self.title = ''
        self.description = []
        self.steps = []
        self.dir = ''
        self.duration = ''
        self.root = root_path


    def get_meta(self):
        title = ''
        duration = ''
        about = []
        track_steps = []

        driver = self.driver
        
        soup = BeautifulSoup(driver.page_source, 'lxml')

        track_meta = soup.find('div', id='track-meta')

        # Title
        title = track_meta.find('h2').getText().strip()

        # Estimated Duration
        duration = track_meta.find('span', class_='estimate').getText().strip()

        # Description
        meta_about = track_meta.findAll('p', recursive=False)
        meta_industry = track_meta.find('ul', class_='track-industry')

        for p in meta_about:
            about.append(transform_links(p))

        if meta_industry:
            items = meta_industry.findAll('li', recursive=False)
            for li in items:
                p = li.find('p')
                p = transform_links(p)
                about.append('* {}'.format(p))
        

        # Steps
        steps = soup.find('div', id='track-steps').findAll('li', class_='card')

        step_no = None

        if (len(steps) > 1):
            step_no = 1

        for card in steps:
            step = Step()

            # Step URL
            s_url = card.find('a', class_='card-box')
            step.url = 'https://teamtreehouse.com' + s_url['href']

            # Step Number
            step.no = step_no

            # Step Title, Description and Type
            step.title = card.find('h3', class_='card-title').getText().strip()
            step.description = transform_links(card.find('p', class_='card-description'))

            driver.get(step.url)
            step.type = get_page_type(driver)

            # Duration
            step_duration = card.find('span', class_='card-estimate')
            if step_duration:
                step.duration = step_duration.getText().strip()

            # Add step to Track Steps
            track_steps.append(step)

            step_no += 1

        # Add Track Properties
        self.title = title
        self.description = about
        self.duration = duration
        self.steps = track_steps


    def write_content(self):
        with open(self.title + '.md', 'w') as f:
            # Title
            f.write('## [{}]({})\n'.format(self.title, self.url))

            # Description
            for p in self.description:
                f.write(p + '\n\n')
            
            f.write('\n## [Steps]({})\n\n'.format(self.url))

            # Steps
            for step in self.steps:
                f.write('### [{:02d} - {}]({})\n'.format(step.no, step.title, step.url))
                f.write('**({}{})**\n\n'.format(step.duration.title() + ' ' if step.duration else '', step.type.title()))
                f.write('{}\n\n'.format(step.description))


    def start_download(self):
        driver = self.driver
        wait_driver(driver, 'class_name', 'card-box')

        # Get Track Meta
        self.get_meta()

        print(txt.warning + 'Downloading Track: ' + txt.normal + self.title)

        # Create and go to Track folder
        self.dir = create_folder(self.title)

        self.write_content()

        for step in self.steps:
            driver.get(step.url)

            # Course
            if (step.type == 'course'):
                os.chdir(self.root)
                create_folder('Courses')

                course = Course(driver, self.root)
                course.start_download(step.no, self.dir)

            # Workshop
            elif (step.type == 'workshop'):
                os.chdir(self.root)
                create_folder('Workshops')

                workshop = Workshop(driver, self.root)
                workshop.start_download(step.no, self.dir)

            # Instruction
            elif (step.type == 'instruction'):
                os.chdir(self.root)
                create_folder('Instructions')

                instruction = Instruction(driver, self.root)
                instruction.start_download(step.no, self.dir)

            # Practice
            elif (step.type == 'practice'):
                # TODO: Download Practice
                pass

            else:
                print(txt.error + 'Couldn\'t get Step Type for: ' + txt.normal + step.url)
                sys.exit()


class Step:
    def __init__(self):
        self.url = ''
        self.no = None
        self.title = ''
        self.description = ''
        self.type = ''
        self.duration = ''
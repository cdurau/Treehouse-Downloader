import cssutils
from bs4 import BeautifulSoup

from modules.helper import *
from modules.download_helper import *


class Workshop:
    def __init__(self, driver, root_path):
        self.driver = driver
        self.url = driver.current_url
        self.dir = ''
        self.topic = ''
        self.skill_level = ''
        self.title = ''
        self.subtitle = ''
        self.description = []
        self.teachers = []
        self.steps = []
        self.root = root_path

    
    def get_meta(self):
        workshop_title = ''
        workshop_subtitle = ''
        workshop_teachers = []
        workshop_about = []
        workshop_steps = []
        workshop_topic = ''
        workshop_skill_level = ''

        driver = self.driver

        try:
            wait_driver(driver, 'class_name', 'stage-progress-item')
        except:
            wait_driver(driver, 'class_name', 'stage-progress-list')

        soup = BeautifulSoup(driver.page_source, 'lxml')

        header = soup.find('div', id='workshop-title')
        
        # Title
        workshop_title = header.find('h1').getText().strip()
        workshop_title = sanitize_special_chars(workshop_title)

        # Subtitle
        workshop_subtitle = header.find('h2')

        if workshop_subtitle:
            workshop_subtitle = workshop_subtitle.getText().strip()
            workshop_subtitle = sanitize_special_chars(workshop_subtitle)

        # Topic and Skill Level
        workshop_topic = get_topic(soup)
        workshop_skill_level = get_skill_level(soup)

        # About
        w_about = soup.find('div', id='workshop-meta').find('div', class_='grid-66').findAll('p')
        
        for p in w_about:
            p = transform_links(p)

            if p:
                workshop_about.append(p)

        # Teacher
        teachers = soup.find('div', id='workshop-authors').find('ul').findAll('li')

        for teacher in teachers:
            teacherObj = Teacher()

            # Full Name
            teacherObj.name = teacher.find('h4').getText().strip()

            # Get Photo
            img_a = teacher.find(class_='instructor-avatar')['style']
            img_style = cssutils.parseStyle(img_a)
            img_url = img_style['background-image']

            teacherObj.img = img_url.replace('url(', '').replace(')', '')

            # Description
            teacher_desc = teacher.findAll('p')

            for p in teacher_desc:
                if p:
                    p = transform_links(p)

                    # Add Teacher to Course
                    teacherObj.description.append(p)

            workshop_teachers.append(teacherObj)

        # Steps
        step_list = soup.find('ul', class_='stage-progress-list')
        steps = step_list.findAll('a')
        if not steps:
            steps = soup.findAll('a', id='workshop-hero')

        for s in steps:
            step = get_step_meta(driver, s['href'], Step())
            workshop_steps.append(step)

        # Set Class Properties
        self.title = workshop_title
        self.subtitle = workshop_subtitle
        self.description = workshop_about
        self.teachers = workshop_teachers
        self.steps = workshop_steps
        self.topic = workshop_topic
        self.skill_level = workshop_skill_level


    def write_content(self):
        with open(self.title + '.md', 'w') as f:
            # Title and Subtitle
            f.write('## [{}]({})\n'.format(self.title, self.url))
            f.write('##### {}\n\n'.format(self.subtitle))

            # Teacher
            for teacher in self.teachers:
                f.write('### Teacher\n')
                f.write('<img src="{}" alt="{}" width="60" height="60" style="border-radius: 50%" >\n\n'.format(teacher.img, teacher.name))
                f.write('**{}**\n\n'.format(teacher.name))
                for p in teacher.description:
                    f.write(p + '\n\n')

            # Workshop Description
            f.write('### About this Course\n')
            for p in self.description:
                f.write(p + '\n\n')

            for step in self.steps:

                f.write('* **[{}]({})** *<small>({})</small>*\n\n'.format(step.title, step.url, step.duration if step.duration else step.type.title()))

    
    def start_download(self, workshop_no=None, target=''):
        driver = self.driver 

        # Wait for steps to load
        wait_driver(driver, 'class_name', 'stage-progress-list')

        self.get_meta()

        # Create Topic and Skill Folder
        create_folder(self.topic)
        create_folder(self.skill_level)

        # Create and go to Workshop folder
        self.dir = create_folder(self.title)

        if workshop_no:
            print(txt.green + '{:02d}. {}'.format(workshop_no, self.title) + txt.normal)
        else:
            print(txt.green + self.title + txt.normal)

        self.write_content()

        download_steps(driver, self.steps, self.root, self.dir)

        # Create Symlinks for Tracks
        if target:
            src = self.dir

            if workshop_no:
                target = target + '/' + '{:02d}. {}'.format(workshop_no, self.title)
            else:
                target = target + '/' + self.title

            mk_symlink(src, target)


class Teacher:
    def __init__(self):
        self.name = ''
        self.description = []
        self.img = ''


class Step:
    def __init__(self):
        self.title = ''
        self.url = ''
        self.type = ''
        self.duration = ''
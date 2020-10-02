import cssutils
from pathvalidate import sanitize_filename, sanitize_filepath
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from modules.helper import *
from modules.download_helper import *
from modules.downloader import *
from modules.types.instruction import Instruction


class Course:
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
        self.check_list = []
        self.prereqs = []
        self.stages = []
        self.root = root_path


    def get_meta(self):
        course_topic = ''
        course_skill_level = ''
        course_title = ''
        course_subtitle = ''
        course_checklist = []
        course_prereqs = []
        course_description = []
        course_stages = []
        stage_description = []
        stage_steps = []
        course_teachers = []

        driver = self.driver
        wait_driver(driver, 'class_name', 'steps-list')

        soup = BeautifulSoup(driver.page_source, 'lxml')

        meta = soup.find('div', id='syllabus-meta')
        header = soup.find('div', id='syllabus-title')

        # Topic and Skill Level
        course_topic = get_topic(soup)
        course_skill_level = get_skill_level(soup)

        # Teacher
        teachers = meta.find('div', id='syllabus-authors').find('ul').findAll('li')

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

            course_teachers.append(teacherObj)


        # Title
        course_title = header.find('h1').getText().strip()
        course_title = sanitize_special_chars(course_title)

        # Subtitle
        course_subtitle = header.find('h2')
        if course_subtitle:
            course_subtitle = course_subtitle.getText().strip()
            course_subtitle = sanitize_special_chars(course_subtitle)

        # Description
        course_desc = meta.find('div', id='syllabus-description')
        if course_desc:
            paragraphs = course_desc.findAll('p')

        for p in paragraphs:
            # Transform Links to Markup
            p = transform_links(p)

            # Add Paragraph to description
            course_description.append(p)

        # Check List
        check_list = meta.find('ul', class_='check-list')
        if check_list:
            check_items = check_list.findAll('li')

            for c_item in check_items:
                c_title = c_item.getText().strip()
                course_checklist.append(c_title)
        
        # Prerequisites
        prereqs = meta.find('div', id='syllabus-prereqs')
        if prereqs:
            pre_list = prereqs.find('ul', class_='queue-content-list').findAll('a', class_='queue-content-title')
            for pre_item in pre_list:
                preObj = Prereq()

                preObj.title = pre_item.find('h3').getText().strip()
                preObj.url = 'https://teamtreehouse.com' + pre_item['href']
                preObj.type = pre_item.find('strong').getText().strip()

                course_prereqs.append(preObj)

        # Stages
        syllabus_stages = meta.find('div',id='syllabus-stages')
        stages = syllabus_stages.findAll('div', class_='stage-meta')
        stage_no = 1

        for stage in stages:
            stageObj = Stage()

            # Title
            stage_title = ''
            stage_title = stage.find('h2').getText().strip()
            stage_title = sanitize_special_chars(stage_title)
            stageObj.title = stage_title

            # Description
            stage_desc = stage.findAll('p', recursive=False)
            for stage_p in stage_desc:
                # Transform Links to Markup
                stage_p = transform_links(stage_p)

                # Add Paragraph to Description
                stageObj.description.append(stage_p)

            # Steps
            steps_list = stage.find('ul', class_='steps-list')
            steps = steps_list.findAll('a', class_='has-topic-fill-to-child-on-hover')

            for s in steps:
                step = get_step_meta(driver, s['href'], Step())
  
                # Add steps to stage
                stageObj.steps.append(step)

            # Extra Credit
            stage_credit = stage.find('li', class_='extra-credit')

            if stage_credit:
                stage_credit = stage_credit.find('div', class_='markdown-zone')

                stageObj.credit = transform_links(stage_credit)

            # Stage Number
            stageObj.no = stage_no

            course_stages.append(stageObj)

            stage_no += 1

        # Add course properties
        self.topic = course_topic
        self.skill_level = course_skill_level
        self.title = course_title
        self.subtitle = course_subtitle
        self.check_list = course_checklist
        self.prereqs = course_prereqs
        self.description = course_description
        self.stages = course_stages
        self.teachers = course_teachers

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

            # Course Description
            f.write('### About this Course\n')
            for p in self.description:
                f.write(p + '\n\n')

            # Check List
            if self.check_list:
                f.write('#### What you\'ll learn\n')
                for item in self.check_list:
                    f.write('- [x] {}\n'.format(item))
                
                f.write('\n')

            # Prerequisites
            if self.prereqs:
                f.write('\n**For best results, we recommend first taking these prerequisite courses...**\n\n')
                for pre in self.prereqs:
                    f.write('**{}** - [{}]({})\n\n'.format(pre.type, pre.title, pre.url))

            # Stages
            for stage in self.stages:
                f.write('### {}\n'.format(stage.title))
                for p in stage.description:
                    f.write(p + '\n')
                for step in stage.steps:
                    f.write('* **[{}]({})** *({})*\n\n'.format(step.title, step.url, step.duration if step.duration else step.type.title()))

                # Extra Credit
                if stage.credit:
                    f.write('##### Extra Credit\n')
                    f.write(stage.credit + '\n\n')


    def start_download(self, course_no=None, target=''):
        driver = self.driver        

        # Wait for stages to be loaded
        wait_driver(driver, 'class_name', 'featurette')

        # Get course description
        self.get_meta()

        if course_no:
            print(txt.green + 'Course: ' + txt.normal + ' {:02d}. {}'.format(course_no, self.title))
        else:
            print(txt.green + 'Course: ' + txt.normal + self.title)

        # Create Topic and Skill Folder
        create_folder(self.topic)
        create_folder(self.skill_level)

        # Create and go to Course Folder
        self.dir = create_folder(self.title)

        self.write_content()

        stage_no = 1        

        for stage in self.stages:
            stage_title = stage.title

            if (len(self.stages) > 1):
                stage_title = '{:02d}. {}'.format(stage_no, stage.title)

            # Create folder for stages
            stage.dir = create_folder(stage_title)

            print(txt.green + 'Chapter: ' + txt.normal + stage_title)

            download_steps(driver, stage.steps, self.root, stage.dir)

            # Move back to course dir
            os.chdir(self.dir)

            stage_no += 1

        # Create Symlinks for Tracks
        if target:
            src = self.dir

            if course_no:
                target = target + '/' + '{:02d}. {}'.format(course_no, self.title)
            else:
                target = target + '/' + self.title

            mk_symlink(src, target)

class Prereq:
    def __init__(self):
        self.title = ''
        self.url = ''
        self.type = ''


class Stage:
    def __init__(self):
        self.no = None
        self.title = ''
        self.description = []
        self.steps = []
        self.credit = ''
        self.dir = ''


class Step:
    def __init__(self):
        self.title = ''
        self.url = ''
        self.duration = ''
        self.type = ''


class Teacher:
    def __init__(self):
        self.name = ''
        self.description = []
        self.img = ''
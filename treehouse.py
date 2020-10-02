from modules.helper import *
from modules.types.track import *
from modules.types.course import *
from modules.types.workshop import *
from modules.types.instruction import *
from modules.types.practice import *


def main():
    # Start Timer
    timer = Timer()

    print('Searching for Downloads...')

    # Read Settings From JSON
    settings = get_settings()
    root_path = Path(settings['download_folder'])

    # Login
    driver = login(settings)

    # Download Links
    download_links = get_links()

    for link in download_links:
        os.chdir(root_path)
        driver.get(link)

        page_type = get_page_type(driver)

        # Track
        if (page_type == 'track'):
            create_folder('Tracks')

            track = Track(driver, root_path)
            track.start_download()

        # Course
        elif (page_type == 'course'):
            create_folder('Courses')

            course = Course(driver, root_path)
            course.start_download()

        # Workshop
        elif (page_type == 'workshop'):
            create_folder('Workshops')

            workshop = Workshop(driver, root_path)
            workshop.start_download()

        # Instruction
        elif (page_type == 'instruction'):
            create_folder('Instructions')

            instruction = Instruction(driver, root_path)
            instruction.start_download()

        # Practice
        elif (page_type == 'instruction'):
            create_folder('Practice')
            pass

    # Print Total Time for Downloads
    timer.total_time()
    print(timer.end)

    print('Finished, Have Fun Learning =)')


main()

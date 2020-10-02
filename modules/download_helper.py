from modules.downloader import *
from modules.types.instruction import *


def download_steps(driver, steps, root_path=None, target=None):
    step_no = None

    if (len(steps) > 1):
        step_no = 1

    for step in steps:
        os.chdir(target)

        driver.get(step.url)

        if (step.type == 'video'):
            download_video(driver, step, step_no)
            download_project_files(driver)
        elif (step.type == 'instruction'):
            instruction = Instruction(driver, root_path)
            instruction.start_download(step_no, target)
        else:
            continue

        if step_no:
            step_no += 1
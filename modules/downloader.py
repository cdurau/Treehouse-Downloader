from modules.helper import *


def download_video(driver, video, video_no=''):
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Get Download Link
    video_url = soup.find('source', type='video/webm')['src']

    # Get File Extension
    ext = re.sub('\?token=.{0,}', '', video_url)
    ext = '.' + re.sub('^.{0,}\.', '', ext)

    # Filename
    if video_no:
        filename = '{:02d}. {}'.format(video_no, video.title)
    else:
        filename = video.title

    filename = filename + ext

    # Check if file exists
    if not os.path.isfile(filename):
        print(txt.blue + 'Downloading Video: ' + txt.normal + filename)

        # Multi connection download with aria2c
        os.system(
            "aria2c -c -j 3 -x 3 -s 3 -k 1M -q -o '{}' {}".format(filename, video_url))

    return filename


def download_project_files(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Get Project Files
    project_files = soup.findAll('a', {'title': 'Download'})

    if project_files:
        create_folder('Project Files')

        for project_file in project_files:
            file_url = project_file['href']
            filename = file_url.rsplit('/', 1)[-1]

            # Check Download
            if not os.path.isfile(filename):
                print(txt.warning + 'Downloading Project Files: ' +
                      txt.normal + filename)

                os.system(
                    "aria2c -c -j 3 -x 3 -s 3 -k 1M -q -o '{}' {}".format(filename, file_url))

        # Go Directory Up
        os.chdir('..')

import csv
import json
import os
import signal
import time

from captchaSolver.config import HEADERS, SCHOOLS

try:
    import requests
    from alive_progress import alive_bar
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    import subprocess
    import sys
    print("Installing dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ]
    )
    print("====================================")
    print("**     Dependencies installed.    **")
    print("**  Please restart the program.   **")
    print("====================================")
    exit(1)


def signal_handler(sig, frame):
    print("\n=================")
    print("Crawler stopped by user.")
    exit(0)


class Paper:
    def __init__(self, school: str, total_paper: int):
        self.done = False
        self.total_paper = total_paper
        self.school = school
        self.filepath = school + ".json"
        self.papers = self.readJson(self.filepath)

    def readJson(self, file: str) -> dict:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
        else:
            papers = {
                self.school: {}
            }

        papers["current_paper"] = len(papers[self.school])
        papers["total_paper"] = self.total_paper

        if papers["current_paper"] >= papers["total_paper"]:
            self.done = True

        return papers

    def getPaper(self, soup: BeautifulSoup) -> bool:

        if soup == None:
            raise Exception("soup is None")

        table = soup.find(
            'table', {'id': 'format0_disparea'}).find_all('tr')

        link = table[0].find(
            'input', {'id': 'fe_text1'})["value"]

        if link not in self.papers[self.school]:

            self.papers[self.school][link] = {}
            self.papers[self.school][link]["本論文永久網址"] = link

            for d in table[2:]:
                th = d.find('th', {'headers': 'format_0_table'})
                td = d.find('td')
                key = th.text[:-1]
                if key == "相關次數":
                    li_list = td.find_all('li')
                    metrics = [li.text for li in li_list]
                    value = {
                        metrics[0].split(':')[0]: metrics[0].split(':')[1],
                        metrics[1].split(':')[0]: metrics[1].split(':')[1],
                        metrics[3].split(':')[0]: metrics[3].split(':')[1],
                        metrics[4].split(':')[0]: metrics[4].split(':')[1],
                    }
                elif key == "中文關鍵詞" or key == "外文關鍵詞":
                    keywords = td.find_all('a')
                    value = [k.text for k in keywords]
                elif key == "指導教授" or key == "指導教授(外文)":
                    professors = td.find_all('a')
                    value = [p.text for p in professors]
                    for v in value:
                        if ',' in v:
                            value.remove(v)
                            value.append(v.split(',')[0])
                            value.append(v.split(',')[1])
                    # remove empty string in value
                    value = list(filter(None, value))
                else:
                    value = td.text

                self.papers[self.school][link][key] = value

            self.papers["current_paper"] += 1

            if self.papers["current_paper"] % 250 == 0 or self.papers["current_paper"] == self.papers["total_paper"]:
                print("Auto-save at", self.papers["current_paper"], "papers")
                self.save()

            # print(link)
            return True

        else:
            print("Paper", os.path.basename(link), "already exists.")
            return False

    def save(self) -> None:
        max = self.papers["total_paper"]
        current = self.papers["current_paper"]
        if current >= max:
            self.papers["total_paper"] = current
            self.done = True
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.papers, f, indent=4, ensure_ascii=False)


class PaperCrawler:

    def __init__(self, schools: list = []):
        self.done = False
        self.session = None
        self.headers = HEADERS
        self.schools = schools

    # def getSchool(self) -> None:
    #     """
    #     get Taiwanese university list
    #     """

    #     self.schools = []
    #     url = f"https://zh.wikipedia.org/zh-tw/%E5%8F%B0%E7%81%A3%E5%A4%A7%E5%B0%88%E9%99%A2%E6%A0%A1%E5%88%97%E8%A1%A8"

    #     r = requests.get(url, headers=self.headers)
    #     try:
    #         soup = BeautifulSoup(r.text, 'html.parser')
    #         tables = soup.find_all('table', {'class': 'wikitable'})
    #         for table in tables:
    #             rows = table.find_all('tr')
    #             for row in rows:
    #                 cols = row.find_all('td')
    #                 if len(cols) > 0:
    #                     school = cols[1].text.strip()
    #                     # remove parentheses
    #                     school = re.sub(r'\([^)]*\)', '', school)
    #                     self.schools.append(school)
    #     except Exception as e:
    #         print("Error: {}".format(e))
    #         print("Failed to fetch university list.")
    #         exit(1)

    #     # write to file
    #     with open("schools.txt", "w", encoding="utf-8") as f:
    #         for school in self.schools:
    #             f.write(school + "\n")

    #     print("University list fetched.")

    def setWebSession(self) -> dict:
        """
        set web session
        """

        # create session
        self.session = requests.Session()
        url = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge"

        # get session cookies
        try:
            r = self.session.get(url, headers=self.headers)
            cookies = self.session.cookies.get_dict()
            if "ccd" not in cookies:
                print("Failed to get cookies.")
                print("Please check your internet connection.")
                print("If you are using VPN, please turn it off.")
                exit(1)
            print("Cookies fetched.")
            print("Your access token is {}.".format(cookies['ccd']))
            print("=================")
            return cookies
        except Exception as e:
            print("Error: {}".format(e))
            print("Failed to get cookies.")
            print("Captcha may be required.")
            print("Note: This program does not support captcha.")
            print("Please try again later or use VPN.")
            exit(1)

    def paperOfSchools(self) -> None:
        """
        get paper of schools
        """

        if self.session == None:
            cookies = self.setWebSession()

        # baseURL = "https://ndltd.ncl.edu.tw"
        pageURL = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd={}/search"
        recordURL = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd={}/record?r1={}"

        for school in self.schools:

            paper_id = 1
            self.prev_school = school
            print("Crawling paper of {}...".format(school))

            # payload
            data = {
                "qs0": "({}.asc)".format(school),
                "qf0": "_hist_",
                "displayonerecdisable": "1",
                "dbcode": "nclcdr",
                "opt": "m",
                "_status_": "search__v2",
            }

            try:
                r = self.session.post(pageURL.format(
                    cookies["ccd"]), data=data, headers=self.headers, timeout=30)
            except requests.exceptions.Timeout:
                print("Web request timeout.")

                # wait for 5 minutes and auto retry
                print("Wait for 5 minutes...")
                with alive_bar(300, bar="blocks", spinner="dots_waves", title="Retry in") as bar:
                    for i in range(300):
                        time.sleep(1)
                        bar()

                print("=== Restarting ===")
                self.session = None
                return

            try:
                soup = BeautifulSoup(r.text, 'html.parser')
                paper_num = soup.find(
                    'table', {'class': 'brwrestable'}
                ).find_all("span")[1].text.strip()

                print("{}, total {} papers.".format(school, paper_num))
                paperCollector = Paper(school, int(paper_num))

                if paperCollector.done:
                    print("Paper of {} done.".format(school))
                    print("=================")
                    self.prev_id = 0
                    continue

                if hasattr(self, "prev_id") and self.prev_id != 0:
                    paper_id = self.prev_id
                else:
                    paper_id = paperCollector.papers["current_paper"] + 1
                paper_set = len(list(paperCollector.papers[school].keys()))

                print("Already fetched {} papers.".format(paper_set))
                print("Checking paper from {}...".format(paper_id))

                # alive_bar
                with alive_bar(int(paper_num) - paper_set, bar="smooth", force_tty=True) as bar:
                    while not paperCollector.done:

                        # get paper id
                        r = self.session.post(recordURL.format(
                            cookies["ccd"], paper_id), headers=self.headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')

                        # get paper
                        if paperCollector.getPaper(soup):
                            bar()

                        # paper_id repeat from 1 to int(paper_num)
                        paper_id = paper_id % int(paper_num) + 1

            except Exception as e:
                # print("Error: {}".format(e))
                print("Failed while fetching {}: {}/{}.".format(school,
                      paper_id, paper_num))
                print("Save current progress.")
                self.prev_id = paper_id
                paperCollector.save()
                print("=== Auto Restart ===")

                self.session = None
                return

            print("Paper of {} complete.".format(school))
            self.prev_id = 0
            print("=================")

        print("All papers fetched.")
        self.done = True


def readCSV(info: dict) -> list:
    """
    read csv file
    """

    path = info["path"]
    encoding = info["encoding"]
    delimiter = info["delimiter"]
    mode = info["mode"]
    start = info["start"]
    end = info["end"]

    schools = []
    with open(path, mode=mode, encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            schools.append(row[0])

    return schools[start:end]


if __name__ == '__main__':

    schools = readCSV(SCHOOLS)
    print("===== Start =====")
    for i in schools:
        print(i)
    print("=================")

    crawler = PaperCrawler(schools)
    signal.signal(signal.SIGINT, signal_handler)

    while not crawler.done:
        crawler.paperOfSchools()
        crawler.schools = schools[schools.index(crawler.prev_school):]

    print("===== Done =====")

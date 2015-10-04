import requests
import json
import re
from bs4 import BeautifulSoup


class Scrapper():
    LOGIN_URL = 'http://coe1.annauniv.edu/home/index.php'
    PROFILE_URL = 'http://coe1.annauniv.edu/home/students_corner.php'

    EXAM_SCHEDULE = 'formExamSchedule'
    INTERNAL_MARK = 'formIntenalMark'
    EXAM_RESULTS = 'formExamResults'
    ELECTIVES = 'formElectiveData'
    ASSESSMENT = 'formAssMark'

    def __init__(self, register_no, dob):
        self.register_no = register_no
        self.dob = dob
        self.cookies = None
        self.proxies = {
            'http': '',
            'https': '',
        }
        self.current_page = None

    def login(self):
        home = requests.get(Scrapper.LOGIN_URL, proxies=self.proxies)
        self.cookies = home.cookies

        soup = BeautifulSoup(home.content, 'html.parser')
        captcha = str(soup.findAll('label', attrs={'class': 'login'})[-1].getText())
        captcha = re.search(r'\d+ (?:\-|\+) \d+', captcha, re.M|re.I).group()
        solution = str(eval(captcha))
        hidden_field = soup.findAll('input', attrs={'type': 'hidden'})[-1]
        post_data = {
            hidden_field.attrs['name']: hidden_field.attrs['value'],
            'register_no': self.register_no,
            'dob': self.dob,
            'security_code_student': solution,
            'gos': 'Login',
        }

        return post_data

    def get_profile_details(self, post_data):
    	headers = {'Content-type': 'application/x-www-form-urlencoded', 'Origin': 'http://coe1.annauniv.edu'}
        self.current_page = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies, headers=headers)

        if self.current_page.content.find("window.location='index.php'") == -1:
            soup = BeautifulSoup(self.current_page.content, 'html.parser')
            table = soup.findAll('table')[0]
            profile_details = {}
            for row in table.findAll('tr'):
                profile_details.update({row.findAll('td')[0].text.strip().replace(' ', '_').lower() : row.findAll('td')[1].text.strip()})
            return profile_details
        else:
            return None

    def get_exam_schedule_details(self, tab_id):
        soup = BeautifulSoup(self.current_page.content, 'html.parser')
        form = soup.find('form', attrs={'id': tab_id})
        post_data = {}
        for inp in form.findAll('input'):
            post_data.update({inp['name']: inp['value']})

        profile_exam_schedule = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies)
        self.current_page = profile_exam_schedule

        soup = BeautifulSoup(profile_exam_schedule.content, 'html.parser')
        schedule = soup.findAll('table')[1]
        schedule_fields = schedule.findAll('tr')[0].findAll('th')
        exam_schedule_details = []
        for row in schedule.findAll('tr')[1:]:
            i = 0
            detail = {}
            for col in row.findAll('th'):
                detail.update({schedule_fields[i].text.strip().replace(' ', '_').lower(): col.text.strip()})
                i += 1
            exam_schedule_details.append(detail)

        return exam_schedule_details

    def get_assessment_details(self, tab_id):
        soup = BeautifulSoup(self.current_page.content, 'html.parser')
        form = soup.find('form', attrs={'id': tab_id})
        post_data = {}
        for inp in form.findAll('input'):
            post_data.update({inp['name']: inp['value']})

        profile_assessment_details = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies)
        self.current_page = profile_assessment_details

        soup = BeautifulSoup(profile_assessment_details.content, 'html.parser')
        table = soup.findAll('table')[1]
        rows = table.findAll('tr')
        assesment_detail = []
        for row in rows[2:]:
            cols = row.findAll('th')
            assesment_detail += [{
                'subject_code': cols[0].text,
                'report_period1': {
                    'total_period': cols[1].text.strip(),
                    'attended_period': cols[2].text.strip(),
                    'assesment_mark': None
                },
                'report_period2': {
                    'total_period': cols[3].text.strip(),
                    'attended_period': cols[4].text.strip(),
                    'assesment_mark': cols[5].text.strip()
                },
                'report_period3': {
                    'total_period': cols[6].text.strip(),
                    'attended_period': cols[7].text.strip(),
                    'assesment_mark': cols[8].text.strip()
                },
                'report_period4': {
                    'total_period': cols[9].text.strip(),
                    'attended_period': cols[10].text.strip(),
                    'assesment_mark': cols[11].text.strip()
                }
            }]

        return assesment_detail

    def get_exam_result_details(self, tab_id):
        soup = BeautifulSoup(self.current_page.content, 'html.parser')
        form = soup.find('form', attrs={'id': tab_id})
        post_data = {}
        for inp in form.findAll('input'):
            post_data.update({inp['name']: inp['value']})

        profile_exam_result = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies)
        self.current_page = profile_exam_result

        if profile_exam_result.content.find('No Record Found') == -1:
            soup = BeautifulSoup(profile_exam_result.content, 'html.parser')
            details = []
            table = soup.findAll('table')[1]
            rows = table.findAll('tr')[4:]
            fields = rows[0].findAll('th')
            for row in rows[1:]:
                i = 0
                detail = {}
                for col in row.findAll('th'):
                    detail.update({fields[i].text.strip().replace(' ', '_').lower(): col.text.strip()})
                    i += 1
                details.append(detail)
            exam_result_details = {
                'meta': soup.find('h2').text.strip(),
                'results': details
            }
            return exam_result_details
        else:
            return None

    def get_exam_reval_result_details(self):
        if self.current_page.content.find('Revaluation / Photocopy Result') != -1:
            soup = BeautifulSoup(self.current_page.content, 'html.parser')
            table = soup.findAll('table')[3]
            rows = table.findAll('tr')
            fields = rows[0].findAll('th')
            details = []
            for row in rows[1:]:
                i = 0
                detail = {}
                for col in row.findAll('th'):
                    detail.update({fields[i].text.strip().replace(' ', '_').lower(): col.text.strip()})
                    i += 1
                details.append(detail)
            exam_reval_result_details = {
                'meta': soup.findAll('h1')[1].text.strip(),
                'results': details
            }
            return exam_reval_result_details
        else:
            return None

    def get_elective_details(self, tab_id):
        soup = BeautifulSoup(self.current_page.content, 'html.parser')
        form = soup.find('form', attrs={'id': tab_id})
        post_data = {}
        for inp in form.findAll('input'):
            post_data.update({inp['name']: inp['value']})

        profile_elective = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies)
        self.current_page = profile_elective

        if profile_elective.content.find('No Data or Elective Found') == -1:
            soup = BeautifulSoup(profile_elective.content, 'html.parser')
            table = soup.findAll('table')[1]
            elective_details = []
            for row in table.findAll('tr')[1:]:
                code, name = row.findAll('td')[1].text.strip().split('-')
                elective_details.append({'code': code, 'name': name})
            return elective_details
        else:
            return None

    def get_internal_mark_details(self, tab_id):
        soup = BeautifulSoup(self.current_page.content, 'html.parser')
        form = soup.find('form', attrs={'id': tab_id})
        post_data = {}
        for inp in form.findAll('input'):
            post_data.update({inp['name']: inp['value']})

        profile_internal_mark = requests.post(Scrapper.PROFILE_URL, data=post_data, cookies=self.cookies, proxies=self.proxies)
        self.current_page = profile_internal_mark

        soup = BeautifulSoup(profile_internal_mark.content, 'html.parser')
        table = soup.findAll('table')[1]
        rows = table.findAll('tr')
        fields = rows[0].findAll('th')
        internal_mark_details = []
        for row in rows[1:]:
            i = 0
            detail = {}
            for col in row.findAll('th'):
                detail.update({fields[i].text.strip().replace('*', '').strip().replace(' ', '_').lower(): col.text.strip()})
                i += 1
            internal_mark_details.append(detail)
        return internal_mark_details

    def get_json(self):
        json_string = None;
        try:
            post_data = self.login()
            # print "Post data\n{0}".format(post_data)

            profile_details = self.get_profile_details(post_data)
            if profile_details is not None:
                # print "Profile details\n{0}".format(profile_details)

                exam_schedule_details = self.get_exam_schedule_details(Scrapper.EXAM_SCHEDULE)
                # print 'Exam schedule\n{0}'.format(exam_schedule_details)

                assessment_details = self.get_assessment_details(Scrapper.ASSESSMENT)
                # print 'Assessment details\n{0}'.format(assessment_details)

                exam_result_details = self.get_exam_result_details(Scrapper.EXAM_RESULTS)
                # print 'Result\n{0}'.format(exam_result_details)
                
                exam_reval_result_details = self.get_exam_reval_result_details()
                # print 'Reval result\n{0}'.format(exam_reval_result_details)

                elective_details = self.get_elective_details(Scrapper.ELECTIVES)
                # print 'Electives\n{0}'.format(elective_details)

                internal_mark_details = self.get_internal_mark_details(Scrapper.INTERNAL_MARK)
                # print 'Internal marks\n{0}'.format(internal_mark_details)

                json_string = json.dumps({
                    'profile': profile_details,
                    'exam_schedule': exam_schedule_details,
                    'assessment': assessment_details,
                    'exam_result': exam_result_details,
                    'exam_reval_result': exam_reval_result_details,
                    'electives': elective_details,
                    'internals': internal_mark_details
                }, sort_keys=True)

                # print "Successfully fetched all details."
            else:
                message = "Invalid data! Try again."
                print message

        except requests.exceptions.ConnectionError as e:
            message = "Failed to connect. AU Web Portal may be down right now. Please try again after sometime"
            print message

        if json_string is None:
            json_string = json.dumps({
                'error': message
            })

        return json_string

if __name__ == '__main__':
    scrapper = Scrapper('your-register-number', 'date-of-birth')
    json_string = scrapper.get_json()
    print "Full JSON\n{0}".format(json_string)
import gspread
from gspread_formatting import *
from apiclient import errors
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time


SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=SCOPES)


service = build('drive', 'v3', credentials=creds)

def drive_list_files(service):
    results = service.files().list(fields="files(id, name)").execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    print('Files:')
    for item in items:
        print(u'{0}: {1}'.format(item['name'], item['id']))

def drive_delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def drive_stats(service):
    results = service.about().get(fields='storageQuota').execute()
    print(results)


def copy_master_sheet(username):
    master_sheet_id = '1S2rFWculUT5rv6YX9-JgGQgjBUMEmoykaSTM1Hdzuoc'
    success = None
    error = None
    try:
        client = gspread.authorize(creds)
        copy_sheet = client.copy(master_sheet_id, title='Task App Progress: %s' % username, copy_permissions=True)
        spreadsheet_id = copy_sheet.id
        print('Spreadsheet ID: %s' % spreadsheet_id)
        success = True
        return success, spreadsheet_id
    except Exception as e:
        error = 'Error copying master sheet. Likely a Google API limit error. Try again later.'
        return error

def update_spreadsheet(
    username,
    email_address,
    spreadsheet_id,
    easy_progress,
    medium_progress,
    hard_progress,
    elite_progress,
    easy_list,
    medium_list,
    hard_list,
    elite_list,
    bosspet_list,
    skillpet_list,
    otherpet_list,
    extra_list, 
    passive_list,
    lms_status):

    def get_task_list(task_list):
        tasknames_list = []
        status_list = []
        for task in task_list:
            for ele in task['taskname']:
                if 'LMS' not in ele:
                    task_name = ele
            if task['status'] == 'Complete':
                task_status = 'x'
            else:
                task_status = ''
            tasknames_list.append([task_name])
            status_list.append([task_status])

        return tasknames_list, status_list
    success = None
    error = None
    try:
        service = gspread.service_account(filename="service_account.json")
        google_sheet = service.open_by_key(spreadsheet_id)

        easy_tasks, easy_status = get_task_list(easy_list)
        medium_tasks, medium_status = get_task_list(medium_list)
        hard_tasks, hard_status = get_task_list(hard_list)
        elite_tasks, elite_status = get_task_list(elite_list)
        bosspet_tasks, bosspet_status = get_task_list(bosspet_list)
        skillpet_tasks, skillpet_status = get_task_list(skillpet_list)
        otherpet_tasks, otherpet_status = get_task_list(otherpet_list)
        extra_tasks, extra_status = get_task_list(extra_list)
        passive_tasks, passive_status = get_task_list(passive_list)

        worksheet = google_sheet.worksheet("Info")
        worksheet.batch_update([
            {
                'range': 'G10:H13',
                'values': [[f'{easy_progress}%']]
            },
            {
                'range': 'G14:H17',
                'values': [[f'{medium_progress}%']]
            },
            {
                'range': 'G18:H21',
                'values': [[f'{hard_progress}%']]
            },
            {
                'range': 'G22:H25',
                'values': [[f'{elite_progress}%']]
            },
            {
                'range': 'G26:H29',
                'values': [[f'{lms_status}']]
            }

        ])

        if lms_status is False:
            worksheet.update_cell(30, 4, 'LMS is disabled, any LMS tasks completed or not, are NOT be included in progress percentage')
        else:
            worksheet.update_cell(30, 4, 'LMS is enabled, LMS tasks ARE included in progress percentage')


        # write easy progress to worksheet(Easy)
        worksheet = google_sheet.worksheet("Easy")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': easy_tasks,
            },
            {
            'range': 'B2:B',
            'values': easy_status
            }

        ])


        # write medium progress to worksheet(Medium)
        worksheet = google_sheet.worksheet("Medium")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': medium_tasks,
            },
            {
            'range': 'B2:B',
            'values': medium_status
            }

        ])

        # write hard progress to worksheet(Hard)
        worksheet = google_sheet.worksheet("Hard")
        
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': hard_tasks,
            },
            {
            'range': 'B2:B',
            'values': hard_status
            }

        ])

        # write elite progress to worksheet(Elite)
        worksheet = google_sheet.worksheet("Elite")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': elite_tasks,
            },
            {
            'range': 'B2:B',
            'values': elite_status
            }

        ])

        # write pet progress to worksheet(Pets)
        worksheet = google_sheet.worksheet("Pets")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Boss Pets']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
                'range': 'A34:A34',
                'values': [['Skill Pets']]
            },
            {
                'range': 'A43:A43',
                'values': [['Other Pets']]
            },
            {
            'range': 'A2:A33',
            'values': bosspet_tasks,
            },
            {
            'range': 'B2:B33',
            'values': bosspet_status
            },
            {
            'range': 'A35:A42',
            'values': skillpet_tasks,
            },
            {
            'range': 'B35:B42',
            'values': skillpet_status
            },
            {
            'range': 'A44:A53',
            'values': otherpet_tasks,
            },
            {
            'range': 'B44:B53',
            'values': otherpet_status
            }

        ])

        # write extra progress to worksheet(Extra)
        worksheet = google_sheet.worksheet("Extra")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': extra_tasks,
            },
            {
            'range': 'B2:B',
            'values': extra_status
            }

        ])


        # write passive progress to worksheet(Passive)
        worksheet = google_sheet.worksheet("Passive")
        worksheet.batch_update([
            {
                'range': 'A1:A1',
                'values': [['Task']]
            },
            {
                'range': 'B1:B1',
                'values': [['Status']]
            },
            {
            'range': 'A2:A',
            'values': passive_tasks,
            },
            {
            'range': 'B2:B',
            'values': passive_status
            }

        ])
        google_sheet.share(None, perm_type='anyone', role='reader', with_link=True)
        success = True
        return success, 'https://docs.google.com/spreadsheets/d/%s' % spreadsheet_id
    except Exception as e:
        error = 'error occurred while processing the request'
        return error

if __name__ == "__main__":
    # drive_delete_file(service, '')
    # drive_stats(service)
    # drive_list_files(service)
    pass


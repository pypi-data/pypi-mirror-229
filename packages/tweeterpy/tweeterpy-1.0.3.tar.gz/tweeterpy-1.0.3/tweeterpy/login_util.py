from .constants import Path
from .request_util import make_request
from . import util
from .logging_util import disable_logger


class TaskHandler:
    def __init__(self):
        pass

    def _create_task_mapper(self, username, password, otp):
        # fmt: off  - Turns off formatting for this block of code. Just for the readability purpose.
        task_flow_mapper = {"LoginJsInstrumentationSubtask":{"task_executor": self._get_user_flow_token,"task_parameter":None},
                                 "LoginEnterUserIdentifierSSO":{"task_executor": self._get_password_flow_token,"task_parameter":username},
                                 "LoginEnterPassword":{"task_executor": self._get_account_duplication_flow_token,"task_parameter":password},
                                 "DenyLoginSubtask":{"task_executor": self._check_suspicious_login,"task_parameter":None},
                                 "AccountDuplicationCheck":{"task_executor": self._check_account_duplication,"task_parameter":None},
                                 "LoginAcid":{"task_executor":self._handle_suspicious_login,"task_parameter":otp},
                                 "LoginSuccessSubtask":{"task_output": "\nSuccessfully Logged In.."}}
        return task_flow_mapper

    def _get_flow_token(self):
        params = {'flow_name': 'login'}
        payload = {'input_flow_data': {
            'flow_context': {'debug_overrides': {}, 'start_location': {'location': 'manual_link'}, }, },
            'subtask_versions': {'action_list': 2, 'alert_dialog': 1, 'app_download_cta': 1, 'check_logged_in_account': 1,
                                 'choice_selection': 3, 'contacts_live_sync_permission_prompt': 0, 'cta': 7, 'email_verification': 2, 'end_flow': 1,
                                 'enter_date': 1, 'enter_email': 2, 'enter_password': 5, 'enter_phone': 2, 'enter_recaptcha': 1, 'enter_text': 5,
                                 'enter_username': 2, 'generic_urt': 3, 'in_app_notification': 1, 'interest_picker': 3, 'js_instrumentation': 1,
                                 'menu_dialog': 1, 'notifications_permission_prompt': 2, 'open_account': 2, 'open_home_timeline': 1, 'open_link': 1,
                                 'phone_verification': 4, 'privacy_options': 1, 'security_key': 3, 'select_avatar': 4, 'select_banner': 2,
                                 'settings_list': 7, 'show_code': 1, 'sign_up': 2, 'sign_up_review': 4, 'tweet_selection_urt': 1, 'update_users': 1,
                                 'upload_media': 1, 'user_recommendations_list': 4, 'user_recommendations_urt': 1, 'wait_spinner': 3, 'web_modal': 1}}
        return make_request(Path.TASK_URL, method="POST", params=params, json=payload)

    def _get_javscript_instrumentation_subtask(self):
        params = {'c_name': 'ui_metrics'}
        return make_request(Path.JAVSCRIPT_INSTRUMENTATION_URL, params=params)

    def _get_user_flow_token(self, flow_token, subtask_id="LoginJsInstrumentationSubtask"):
        payload = {'flow_token': flow_token,
                   'subtask_inputs': [{'subtask_id': subtask_id,
                                      'js_instrumentation': {
                                          'response': '',
                                          'link': 'next_link'}}]}
        return make_request(Path.TASK_URL, method="POST", json=payload)

    @disable_logger
    def _get_password_flow_token(self, flow_token, subtask_id="LoginEnterUserIdentifierSSO", username=None):
        payload = {'flow_token': flow_token,
                   'subtask_inputs': [{'subtask_id': subtask_id,
                                      'settings_list': {
                                          'setting_responses': [{'key': 'user_identifier', 'response_data': {'text_data': {'result': username}}}],
                                          'link': 'next_link'}}]}
        return util.check_for_errors(make_request(Path.TASK_URL, method="POST", json=payload))

    @disable_logger
    def _get_account_duplication_flow_token(self, flow_token, subtask_id="LoginEnterPassword", password=None):
        payload = {'flow_token': flow_token,
                   'subtask_inputs': [{'subtask_id': subtask_id,
                                      'enter_password': {'password': password, 'link': 'next_link'}}]}
        return make_request(Path.TASK_URL, method="POST", json=payload)

    def _check_suspicious_login(self, flow_token, subtask_id="DenyLoginSubtask"):
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": subtask_id, "cta": {"link": "next_link"}}]}
        return make_request(Path.TASK_URL, method="POST", json=payload)

    def _check_account_duplication(self, flow_token, subtask_id="AccountDuplicationCheck"):
        payload = {'flow_token': flow_token,
                   'subtask_inputs': [{'subtask_id': subtask_id, 'check_logged_in_account': {'link': 'AccountDuplicationCheck_false'}}]}
        return make_request(Path.TASK_URL, method="POST", json=payload)

    def _handle_suspicious_login(self, flow_token, subtask_id="LoginAcid",otp=None):
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": subtask_id, "enter_text": {"text": otp,"link":"next_link"}}]}
        return make_request(Path.TASK_URL, method="POST", json=payload)

    @disable_logger
    def login(self, username, password):
        # MANUAL WAY OF HANDLING LOG IN
        """
        initital_flow_token = self._get_flow_token()
        self._get_javscript_instrumentation_subtask()
        user_flow_token = self._get_user_flow_token(initital_flow_token)
        password_flow_token = self._get_password_flow_token(
            user_flow_token, username=username)
        account_duplication_flow_token = self._get_account_duplication_flow_token(
            password_flow_token, password=password)
        return self._check_account_duplication(account_duplication_flow_token)
        """

        # DYNAMIC WAY OF HANDLING LOG IN - BETTER
        tasks_pending = True
        otp = None
        try:
            task_flow_mapper = self._create_task_mapper(username,password,otp)
            response = self._get_flow_token()
            self._get_javscript_instrumentation_subtask()
            while tasks_pending:
                tasks = [task['subtask_id'] for task in response['subtasks']]
                flow_token = response['flow_token']
                task_id = [task_id for task_id in task_flow_mapper.keys() if task_id in tasks][0]
                task = task_flow_mapper.get(task_id)
                if task:
                    if task_id == 'LoginAcid':
                        otp_required = any([subtask.get("enter_text",{}).get("hint_text","").lower() == "confirmation code" for subtask in response.get("subtasks")])
                        email_verification = any([subtask.get("enter_text",{}).get("keyboard_type","").lower() == "email" for subtask in response.get("subtasks")])
                        error_message = "Check your email. Enter the confirmation code : " if otp_required else "Confirm your email, Enter your email :" if email_verification else None
                        if error_message:
                            otp = str(input(error_message))
                            task_flow_mapper["LoginAcid"].update({"task_parameter":otp}) 
                    if task_id == 'LoginSuccessSubtask':
                        tasks_pending = False
                        print(task['task_output'])
                        continue
                    if task['task_parameter'] is None:
                        response = task.get('task_executor')(flow_token,task_id)
                    else:
                        parameter = task.get('task_parameter')
                        response =  task.get('task_executor')(flow_token,task_id,parameter)
                else:
                    print(f"\n{response}")
                    tasks_pending = False
        except Exception as error:
            raise error
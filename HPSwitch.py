import logging
import requests
import config

logging.basicConfig(level=logging.DEBUG)

OPERATION_STATUS_UPLOAD_RESPONSE = 'successful'
ERROR_MESSAGES_UPLOAD_RESPONSE = 'errorMsgs'
CPU_STRING = 'id="cpu_util_prog_bar_val">'
MEMORY_STRING = 'id="mem_util_prog_bar_val">'
TRANSFER_STATUS = 'xferStatus'

url = 'http://' + config.COMMUTATOR_ADDRESS
url_login = '/htdocs/login/login.lua'
url_data = '/htdocs/pages/base/support.lsp'
url_logout = '/htdocs/pages/main/logout.lsp'
url_file_transfer_tftp = '/htdocs/lua/ajax/file_upload_ajax.lua?protocol=1'
url_status_file_transfer_tftp = '/htdocs/lua/ajax/file_transfer_ajax.lua?json=1'

session = requests.Session()
session.trust_env = False


def upload_to_tftp(tftp_address, config_filename):
    result = ''

    file_transfer_fields = dict({
        'file_type_sel[]': 'config',
        'transfer_server_addr': tftp_address,
        'transfer_file_name': config_filename,
    })

    if login():
        try:
            file_upload_result = session.post(url + url_file_transfer_tftp, data=file_transfer_fields)
            print(f'Status code of url {url + url_file_transfer_tftp}: {file_upload_result.status_code}')
            if file_upload_result.status_code == 200:

                try:
                    result_json = file_upload_result.json()
                    logging.debug(result_json)
                    if OPERATION_STATUS_UPLOAD_RESPONSE in result_json:
                        operation_status = bool(result_json[OPERATION_STATUS_UPLOAD_RESPONSE])
                        if operation_status:
                            logging.info(f'Successfully backup config: {config_filename}')

                            file_transfer_status = session.get(url + url_status_file_transfer_tftp)
                            logging.debug(f'Status code of url {url + url_status_file_transfer_tftp} : {file_transfer_status.status_code}')
                            if file_transfer_status.status_code == 200:
                                status_json = file_transfer_status.json()
                                logging.debug(f'status_json: {status_json}')
                                # Success upload:
                                # {'xferCodeStatus': 0, 'xferDownloadResult': 0, 'statusReadError': False, 'xferInProgress': 0, 'progressVal': 100, 'xferMessage': '', 'xferStatus': 10}
                                # Progress uload:
                                # {'xferCodeStatus': 0, 'xferDownloadResult': 0, 'statusReadError': False, 'xferInProgress': 1, 'progressVal': 0, 'xferMessage': 'TFTP Config transfer starting...', 'xferStatus': 1}
                                if TRANSFER_STATUS in status_json:
                                    result = str(status_json[TRANSFER_STATUS])
                                    logging.info(f'Результат передачи: {result}')
                                    return result
                        else:
                            logging.info(f'Error backup config: {result_json[ERROR_MESSAGES_UPLOAD_RESPONSE]}')
                except (ValueError, KeyError):
                    logging.info('Ошибка данных')

        except requests.RequestException:
            logging.info('Ошибка сети')

    else:
        logging.info("Login failed...")
    logout()
    return result


def get_cpu():
    response_data = login()
    if response_data:
        html = response_data.text
        search_cpu_str = html.find(CPU_STRING)
        cpu_str_len = len(CPU_STRING)
        cpu_value = response_data.text[search_cpu_str + cpu_str_len:(search_cpu_str + cpu_str_len + 2)]
        logging.info(f'CPU_value(%): {cpu_value}')
    else:
        logging.info("Login failed...")
    logout()


def get_mem():
    response_data = login()
    if response_data:
        html = response_data.text
        search_memory_string = html.find(MEMORY_STRING)
        memory_string_length = len(MEMORY_STRING)
        memory = response_data.text[search_memory_string + memory_string_length:(search_memory_string + memory_string_length + 2)]
        logging.info(f'Memory(%): {memory}')
    else:
        logging.info("Login failed...")
    logout()


def login():
    data = {'username': config.USERNAME, 'password': config.PASSWORD}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response_login = session.post(url + url_login, data, headers)
    if response_login.status_code == 200:
        response_data = session.post(url + url_data)
        return response_data


def logout():
    session.post(url + url_logout)
    session.close()


if __name__ == "__main__":
    config_name = 'test123.cfg'
    if upload_to_tftp(config.TFTP_ADDRESS, config_name):
        message = f'Success upload config {config_name} on {config.TFTP_ADDRESS}'
    else:
        message = f'Error upload config {config_name} on {config.TFTP_ADDRESS}'
    print(message)

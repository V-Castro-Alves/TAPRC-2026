import logging
from urllib.parse import urlencode
from urllib.request import urlopen

import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger_hello(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Hello World!')

@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger_http_call(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    url = 'https://funcapp-vitor0001-egbfcmd9epcyamhb.eastus2-01.azurewebsites.net/api/http_trigger'
    query = urlencode({'name': 'Information sent by timer trigger'})

    with urlopen(f'{url}?{query}', timeout=10) as response:
        logging.info('HTTP function response: %s', response.read().decode('utf-8'))
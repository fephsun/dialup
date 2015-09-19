is_dev_server = False

if is_dev_server:
    from actual_secrets import *
else:
    import os
    clarifai_access_token = os.environ['clarifai_access_token']
    witai_api_key = os.environ['witai_api_key']

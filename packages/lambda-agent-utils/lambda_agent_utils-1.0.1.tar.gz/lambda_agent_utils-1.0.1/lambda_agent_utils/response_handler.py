import json

def response(data, trigger_source):
    try:
        if trigger_source == 'api-gateway':
            return  {
                'statusCode': 200,
                'body': json.dumps({'data': data, 'source': trigger_source }),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        elif trigger_source == 'aws-service-kafka':
            # send data to Kafka topic (You can implement this part)
            print('kafka output')
            print(data)
        elif trigger_source == 'cli':
            return {'data': data, 'source': trigger_source }
        else:
            raise Exception("Unexpected trigger source.")
    except Exception as e:
        raise Exception(e)
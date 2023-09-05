# output_handler.py
def send_output(data, trigger_source):
    try:
        if trigger_source == 'api-gateway':
            return {
                'statusCode': 200,
                'body': {'data': data, 'source': trigger_source}
            }
        elif trigger_source == 'aws-service-kafka':
            # send data to Kafka topic (You can implement this part)
            print(data)
        elif trigger_source == 'cli':
            return data
        else:
            raise Exception("Source is not valid.")
    except Exception as e:
        raise Exception(e)
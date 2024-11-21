def lambda_handler(event, context):
    body = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pointless Analogies</title>
    </head>
    <body>
        <h1>Pointless Analogies</h1>
        <p>Initial lambda function</p>
    </html>
    '''

    response = {
        'statusCode': 200,
        'headers': {"Content-Type": "text/html",},
        'body': body
    }

    return response
import logging

logging.getLogger().setLevel(logging.DEBUG)

def write_response(response, status, data = None, message = None):
    response.out.write('{"status": %s' % status)
    if message != None:
        logging.debug("Got status %s with message '%s'" % (status, message))
        response.out.write(', "message": "%s"' % message)

    if data != None:
        response.out.write(', "data": %s' % data)

    response.out.write('}')
    response.out.write('')
    return

def missing_keys(response, required):
    missing = []
    for arg in required:
        value = response.get(arg)
        if value == None or value == '':
            missing.append(arg)
    return missing

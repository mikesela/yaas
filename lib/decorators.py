def validate_inputs(required=None):

    def function_wrapper(func):

        def validator(self):
            if required:
                missing = []
                request = self.request
                for required_arg in required:
                    value = request.get(required_arg)
                    if value == None or value == '':
                        missing.append(required_arg)
                if missing:
                    self.response.out.write('{"status":"1","message":"Required fields are missing: %s."}' % ",".join(missing))
                    return


            return func(self)

        return validator

    return function_wrapper

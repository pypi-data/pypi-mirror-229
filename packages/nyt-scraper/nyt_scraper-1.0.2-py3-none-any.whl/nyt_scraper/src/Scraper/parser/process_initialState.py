import sys

class process_():
    def __init__(self, response, type_ = 'Article'):
        self.data = self.get_first_id(response, type_)

        if self.data == None:
            raise Exception('Error, no se encontraron los datos principales')

        for k,v in self.data.items():
            self.data[k] = self.recursivity(response, v)

    def get_first_id(self, response, type_):
        for x in response.get('ROOT_QUERY').values():
            if isinstance(x, dict) and x['typename'] == type_:
                return response.get(x['id'])

    def recursivity(self, response, data):
        if isinstance(data, dict):
            if data.get('id') and data.get('type') == 'id':
                data = self.recursivity(response, data['id'])
                return data
            else:
                for k,v in data.items():
                    res = self.recursivity(response, v)

                    if isinstance(res, dict) and len(data) == 4 and data.get('generated') and data.get('type') == 'id':
                        data = res
                    else:
                        data[k] = res
                return data

        elif isinstance(data, list):
            for c,x in enumerate(data):
                data[c] = self.recursivity(response, x)
            return data
        
        elif isinstance(data, str):
            if data in response:
                return self.recursivity(response, response[data])
            else:
                return data
        else:
            return data
        
def process_initialState(response, type_):
    return process_(response, type_).data
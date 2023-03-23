from debuggingbook.DynamicInvariants import precondition, postcondition

data = 'password:hjasdiebk456jhaccount:smytzek'

def store_data(payload: str):
    global data
    data = payload + data

@postcondition(lambda return_value,length, : len(return_value)==length)
def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]

@precondition(lambda length, payload: length==len(payload))
@postcondition(lambda return_value, length, payload: len(return_value)==length)
@postcondition(lambda return_value, length, payload: return_value==payload)                
def heartbeat(length: int, payload: str) -> str:
    store_data(payload)
    return get_data(length)


#if __name__ == "__main__":
#    heartbeat(3,'bob')
#    heartbeat(2,'bob')

data = 'password:hjasdiebk456jhaccount:smytzek'

def store_data(payload: str):
    global data
    data = payload + data

def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]
    
def heartbeat(length: int, payload: str) -> str:
    assert length==len(payload)
    x=len(data)
    store_data(payload)
    assert len(data)==x+len(payload)
    assert data.startswith(payload)
    res=get_data(length)
    assert len(res)==length
    assert res==payload 
    return get_data(length)

if __name__=="__main__":
    print(heartbeat(3,"foo"))

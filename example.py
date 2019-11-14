from pepgrave.magic import Magic

with Magic(313, "346"):
    assert IV == 4
    print(XX)

try:
    assert XX == 4
except:
    print("yea some normal non-magical code")

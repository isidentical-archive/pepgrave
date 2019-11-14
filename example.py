from pepgrave import magic

with magic.Magic(313, 204):
    assert IV == 4
    print(XX)

try:
    assert XX == 4
except:
    print("yea some normal non-magical code")

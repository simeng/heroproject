# What

Dumping some data via offical HoTS replay lib from Blizzard

# Howto 

python info.py "replays/Dragon Shire.StormReplay"

If it complains protocol version not supported you can try and update the 
submodule for the heroprotocol repo.  

If no new protocols are added by Blizzard you can probably copy the highest
protocol number file from heroprotocol/protocol39445.py (currently highest) to
the latest version number heroprotocol/protocol39709.py (currently) and it will
work (unless they changed the protocol which they only seem to do every 5-10
versions (probably when new heroes are added).


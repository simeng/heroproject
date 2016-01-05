#!/usr/bin/env python

from heroprotocol.mpyq import mpyq
from heroprotocol import protocol29406
import argparse
import datetime
import sys
from pprint import pprint

def loop2dur(loops):
    # 16 gameloops per second
    seconds = loops / 16
    mins = seconds / 60
    secs = seconds % 60
    timestring = ""
    if mins > 0:
        timestring = "%02dm" % mins
    timestring += "%02ds" % secs
    return {'sec': seconds, 'duration': { 'min': mins, 'sec': secs, 'string': timestring }}

parser = argparse.ArgumentParser()
parser.add_argument('replay_file', help='.SC2Replay file to load')
args = parser.parse_args()
archive = mpyq.MPQArchive(args.replay_file)

contents = archive.header['user_data_header']['content']
header = protocol29406.decode_replay_header(contents)

# The header's baseBuild determines which protocol to use
baseBuild = header['m_version']['m_baseBuild']
try:
    protocol_name = 'protocol%s' % (baseBuild,)
    protocols = __import__('heroprotocol', globals(), locals(), [protocol_name])
    protocol = getattr(protocols, protocol_name)
except Exception as e:
    print >> sys.stderr, 'Unsupported base build: %d, %s' % (baseBuild, e)
    sys.exit(1)

contents = archive.read_file('replay.details')
details = protocol.decode_replay_details(contents)

contents = archive.read_file('replay.initData')
initdata = protocol.decode_replay_initdata(contents)

contents = archive.read_file('replay.message.events')
messages = protocol.decode_replay_message_events(contents)

game_options = initdata['m_syncLobbyState']['m_gameDescription']['m_gameOptions']
lobby_state = initdata['m_syncLobbyState']['m_lobbyState']


print details['m_title']
print "Elapsed time: %s (%d)" % (loop2dur(header['m_elapsedGameLoops'])['duration']['string'], header['m_elapsedGameLoops'])
print "RNGesus says: %s" % (lobby_state['m_randomSeed'])
if game_options['m_competitive']:
    print "<competative game>"

if game_options['m_cooperative']:
    print "<coop game>"

for player_state in lobby_state['m_slots']:
    print "%s/%s (%s): %s[%s] (%s) rewards: %s" % (player_state['m_teamId'], player_state['m_userId'], player_state['m_toonHandle'], player_state['m_hero'], player_state['m_skin'], player_state['m_mount'], len(player_state['m_rewards']))

for player in details['m_playerList']:
    print "%d: %s (%s) [playerId: %d]" % (player['m_teamId'], player['m_hero'], player['m_name'], player['m_toon']['m_id'])

for message in messages:
    duration = loop2dur(message['_gameloop'])
    if message['_event'] == 'NNet.Game.SPingMessage':
        if message['m_recipient'] == 1:
            target = 'all'
        else:
            target = 'allies? (%s)' % (message['m_recipient'])
        player_name = details['m_playerList'][message['_userid']['m_userId']]['m_name']
        print "%s: #%s [%s] PING (%s, %s)" % (duration['duration']['string'], target, player_name, message['m_point']['x'], message['m_point']['y'])
    elif message['_event'] == 'NNet.Game.SChatMessage':
        if message['m_recipient'] == 1:
            target = 'all'
        else:
            target = 'allies? (%s)' % (message['m_recipient'])
        player_name = details['m_playerList'][message['_userid']['m_userId']]['m_name']
        print "%s: #%s <%s> %s" % (duration['duration']['string'], target, player_name, message['m_string'])


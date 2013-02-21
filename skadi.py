from StringIO import StringIO

import os, sys, snappy
import skadi.parser as sp
import skadi.generated.demo_pb2 as pb_demo
import skadi.generated.netmessages_pb2 as pb_netmessages

pwd, demofile = os.path.dirname(__file__), 'mugsy-104349527.dem'
src_path      = os.path.join(pwd, 'demos', demofile)

src = open(src_path, 'rb')
src.seek(12)

def buffer(src, buf= '', pos = 0, to = 1024):
    """
    Given a buffer (i.e. a string), grow it to the desired size,
    reading appropriately from source.
    """
    deficit = to - (len(buf) - pos)
    if deficit < 0:
        return buf[pos:]
    return buf[pos:] + src.read(deficit)

while True:
    cmd_tell = src.tell()
    cmd_meta = buffer(src, pos = 0, to = 18)

    if len(cmd_meta) == 0:
        break;

    cmd,      cmd_pos = sp.decode_varint(cmd_meta,       0)
    cmd_tick, cmd_pos = sp.decode_varint(cmd_meta, cmd_pos)
    cmd_size, cmd_pos = sp.decode_varint(cmd_meta, cmd_pos)

    compressed = pb_demo.DEM_IsCompressed & cmd
    cmd_data   = buffer(src, cmd_meta, pos = cmd_pos, to = cmd_size)

    if compressed:
        cmd      = cmd & ~pb_demo.DEM_IsCompressed
        cmd_data = snappy.uncompress(cmd_data)

    if cmd == pb_demo.DEM_Stop:
        print "## STOP ##"

    elif cmd == pb_demo.DEM_FileInfo:
        pb_msg = pb_demo.CDemoFileInfo()
        pb_msg.ParseFromString(cmd_data)

        print pb_msg

    elif cmd == pb_demo.DEM_StringTables:
        pb_msg = pb_demo.CDemoStringTables()
        pb_msg.ParseFromString(cmd_data)

        print pb_msg

    elif cmd == pb_demo.DEM_FileHeader:
        pb_msg = pb_demo.CDemoFileHeader()
        pb_msg.ParseFromString(cmd_data)

        print pb_msg

    elif cmd == pb_demo.DEM_SignonPacket:
        print "## SOMEONE SIGNED ON ##"
        print cmd, cmd_tick, cmd_size

        #pb_msg = pb_netmessages.CNETMsg_SignonState()
        #try:
        #   pb_msg.ParseFromString(cmd_data)
        #   print pb_msg
        #except:
        #   print "FAILURE"

    elif cmd == pb_demo.DEM_SyncTick:
        print "## SYNC TICK ##"
        print cmd, cmd_tick, cmd_size

        #pb_msg = pb_demo.CDemoSyncTick()
        #pb_msg.ParseFromString(cmd_data)
        #
        #print pb_msg

    elif cmd == pb_demo.DEM_SendTables:
        pb_msg = pb_demo.CDemoSendTables()
        pb_msg.ParseFromString(cmd_data)

        msg_src = StringIO(pb_msg.data)

        print "## BEGIN DEM_SENDTABLES AT %i ##" % (src.tell())

        while True:
            msg_tell = msg_src.tell()
            msg_meta = buffer(msg_src, pos = 0, to = 12)

            if len(msg_meta) == 0:
                print "## END DEM_SENDTABLES ##"
                break;

            msg,      msg_pos = skadi._DecodeVarint32(msg_meta,       0)
            msg_size, msg_pos = skadi._DecodeVarint32(msg_meta, msg_pos)

            msg_data = buffer(msg_src, msg_meta, pos = msg_pos, to = msg_size)

            if msg == pb_netmessages.svc_SendTable:
                pb_svc_msg = pb_netmessages.CSVCMsg_SendTable()
                try:
                    pb_svc_msg.ParseFromString(msg_data)
                except:
                    print "EXCEPTION PARSING MESSAGE"

                print pb_svc_msg

            msg_src.seek(msg_tell + msg_pos + msg_size, 0)
    elif cmd == pb_demo.DEM_ClassInfo:
        print "## BEGIN CLASS INFO ##"

        pb_msg = pb_demo.CDemoClassInfo()
        pb_msg.ParseFromString(cmd_data)

        print pb_msg

        print "## END CLASS INFO ##"
    elif cmd == pb_demo.DEM_Packet or cmd == pb_demo.DEM_FullPacket:
        pb_msg = pb_demo.CDemoPacket()
        pb_msg.ParseFromString(cmd_data)

        msg_src = StringIO(pb_msg.data)

        # This code won't work for DEM_FullPacket... it needs
        if cmd == pb_demo.DEM_Packet:
            packet_type = 'PACKET'
        else:
            packet_type = 'FULLPACKET'

        print "## BEGIN DEM_%s AT %i ##" % (packet_type, src.tell())

        while True:
            msg_tell = msg_src.tell()
            msg_meta = buffer(msg_src, pos = 0, to = 12)

            if len(msg_meta) == 0:
                print "## END DEM_%s ##" % packet_type
                print
                break;

            msg,      msg_pos = skadi._DecodeVarint32(msg_meta,       0)
            msg_size, msg_pos = skadi._DecodeVarint32(msg_meta, msg_pos)

            msg_data = buffer(msg_src, msg_meta, pos = msg_pos, to = msg_size)

            if msg == pb_netmessages.net_Tick: # 4
                print "  tick"
                pass
            elif msg == pb_netmessages.svc_UpdateStringTable: # 13
                print "  update string table"
                pass
            elif msg == pb_netmessages.svc_Sounds: # 17
                print "  sounds"
                pass
            elif msg == pb_netmessages.svc_UserMessage: # 23
                print "  user message"
                pass
            elif msg == pb_netmessages.svc_GameEvent: #25
                print "  game event"
                pass
            elif msg == pb_netmessages.svc_PacketEntities: # 26
                print "  packet entities"
                temp_msg = pb_netmessages.CSVCMsg_PacketEntities()
                temp_msg.ParseFromString(msg_data)
                # print "%s (%i)" % (''.join([ bin(ord(ch))[2:].zfill(8) for ch in temp_msg.entity_data ]), temp_msg.updated_entries)
            elif msg == pb_netmessages.svc_TempEntities: # 27
                print "  temp entities"
                pass
            else:
                print msg, msg_size

            msg_src.seek(msg_tell + msg_pos + msg_size, 0)
    else:
        print "FOOB"
        print cmd, cmd_tick, cmd_size

    print

    src.seek(cmd_tell + cmd_pos + cmd_size, 0)

from pieraknet.packets.packet import Packet


class OpenConnectionReply1(Packet):
    packet_id = 0x06
    packet_type = 'open_connection_reply_1'

    magic: bytes = None
    server_guid: int = None
    use_security: bool = None
    mtu_size: int = None

    def encode_payload(self):
        self.write_magic(self.magic)  # TODO: server.magic
        self.write_long(self.server_guid)
        self.write_bool(self.use_security)
        self.write_short(self.mtu_size)

import eventlet
eventlet.monkey_patch()

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types


class CleanPathTracer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(CleanPathTracer, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.paths = {}
        self.all_paths = []

        print("\n" + "=" * 50)
        print(" CLEAN SDN PATH TRACING STARTED ")
        print("=" * 50 + "\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print(f"[SWITCH CONNECTED] S{datapath.id}")

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER,
            ofproto.OFPCML_NO_BUFFER)]

        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if not eth:
            return

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        if eth.dst.startswith("33:33"):
            return

        src = eth.src
        dst = eth.dst
        in_port = msg.match['in_port']

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        path_key = (src, dst)
        if path_key not in self.paths:
            self.paths[path_key] = []

        if f"S{dpid}" not in self.paths[path_key]:
            self.paths[path_key].append(f"S{dpid}")

        if out_port != ofproto.OFPP_FLOOD:
            if path_key not in self.all_paths:
                reverse_key = (dst, src)
                if reverse_key in self.paths and len(self.paths[reverse_key]) > len(self.paths[path_key]):
                    complete_path = self.paths[reverse_key][::-1]
                    self.paths[path_key] = complete_path
                else:
                    complete_path = self.paths[path_key]

                path_str = f"{src[-5:]} → " + " → ".join(complete_path) + f" → {dst[-5:]}"
                print(f"🔥 FULL PATH: {path_str}")

                with open("logs/paths.csv", "a") as f:
                    f.write(path_str + "\n")

                self.all_paths.append(path_key)

            print(f"[FLOW] S{dpid}: {src} → {dst} via port {out_port}")

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )
            self.add_flow(datapath, 10, match, actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        )

        datapath.send_msg(out)

    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst
        )

        datapath.send_msg(mod)

import logging
import networkx

from pydot import Dot
from pydot import Edge
from pydot import Node

from barf.arch.x86.x86base import X86ImmediateOperand

logger = logging.getLogger(__name__)


class CallGraph(object):

    """Call graph.
    """

    def __init__(self, cfgs):

        # List of CFGs sorted by address.
        self._cfgs = sorted(cfgs, key=lambda cfg: cfg.start_address)

        # CFGs accessed by address
        self._cfg_by_addr = dict([(cfg.start_address, cfg) for cfg in cfgs])

        self._edges = {}

        # Basic block graph
        self._graph = self._build_graph()

    @property
    def cfgs(self):
        return self._cfgs

    def save(self, filename, format='dot'):
        renderer = CGSimpleRenderer()

        renderer.save(self, filename, format)

    # Auxiliary functions
    # ======================================================================== #
    def _build_graph(self):
        graph = networkx.DiGraph()

        # add nodes
        for cfg in self._cfgs:
            graph.add_node(cfg.start_address, address=cfg.start_address)

        graph.add_node("unknown", address="unknown")

        # add edges
        for cfg in self._cfgs:
            edges = self._edges.get(cfg.start_address, set())

            for bb in cfg.basic_blocks:
                for dinstr in bb:
                    if dinstr.asm_instr.mnemonic == "call":
                        if isinstance(dinstr.asm_instr.operands[0], X86ImmediateOperand):
                            target_addr = dinstr.asm_instr.operands[0].immediate

                            edges.add(target_addr)

                            graph.add_edge(cfg.start_address, target_addr, branch_type="direct")
                        else:
                            edges.add("unknown")

                            graph.add_edge(cfg.start_address, "unknown", branch_type="indirect")

            self._edges[cfg.start_address] = edges

        return graph

    def __getstate__(self):
        state = {}

        state['_cfgs'] = self._cfgs

        return state

    def __setstate__(self, state):
        cfgs = state['_cfgs']

        # List of CFGs sorted by address.
        self._cfgs = sorted(cfgs, key=lambda cfg: cfg.start_address)

        # CFGs accessed by address
        self._cfg_by_addr = dict([(cfg.start_address, cfg) for cfg in cfgs])


class CGRenderer(object):

    def save(self):
        raise NotImplementedError()


class CGSimpleRenderer(CGRenderer):

    fontname = 'Ubuntu Mono'
    # fontname = 'DejaVu Sans Mono'
    # fontname = 'DejaVu Sans Condensed'
    # fontname = 'DejaVu Sans Light'
    # fontname = 'Liberation Mono'
    # fontname = 'DejaVu Serif Condensed'
    # fontname = 'Ubuntu Condensed'

    graph_format = {
        'graph_type' : 'digraph',
        'rankdir'    : 'TB',
        'splines'    : 'ortho',
        'nodesep'    : '1.2',
    }

    node_format = {
        'shape'     : 'plaintext',
        'rankdir'   : 'LR',
        'fontname'  : fontname,
        'fontsize'  : 9.0,
        'penwidth'  : 0.5,
    }

    edge_format = {
        'fontname'  : fontname,
        'fontsize'  : 8.0,
        'penwidth'  : 0.5,
        'arrowsize' : 0.6,
        'arrowhead' : 'vee',
    }

    edge_color = {
        'direct'   : 'blue',
        'indirect' : 'red',
    }

    # Templates.
    node_tpl  = '<'
    node_tpl += '<table border="1.0" cellborder="0" cellspacing="1" cellpadding="0" valign="middle">'
    node_tpl += '  <tr><td align="center" cellpadding="1" port="enter"></td></tr>'
    node_tpl += '  <tr><td align="left" cellspacing="1">{label}</td></tr>'
    node_tpl += '  <tr><td align="center" cellpadding="1" port="exit" ></td></tr>'
    node_tpl += '</table>'
    node_tpl += '>'

    def save(self, cf, filename, format='dot'):
        """Save basic block graph into a file.
        """
        try:
            dot_graph = Dot(**self.graph_format)

            # add nodes
            nodes = {}
            for cfg_addr in cf._graph.node.keys():
                nodes[cfg_addr] = self._create_node(cfg_addr, cf)

                dot_graph.add_node(nodes[cfg_addr])

            # add edges
            for cfg_src_addr in cf._graph.node.keys():
                for cfg_dst_addr in cf._edges.get(cfg_src_addr, []):
                    edge = self._create_edge(nodes, cfg_src_addr, cfg_dst_addr)

                    dot_graph.add_edge(edge)

            dot_graph.write("{}.{}".format(filename, format), format=format)
        except Exception as err:
           logger.error("Failed to save call graph: %s (%s)", filename, format, exc_info=True)

    def _create_node(self, cfg_addr, cf):
        if cfg_addr != "unknown":
            if cfg_addr in cf._cfg_by_addr and not isinstance(cf._cfg_by_addr[cfg_addr], str) and cf._cfg_by_addr[cfg_addr].name:
                cfg_label = cf._cfg_by_addr[cfg_addr].name
            else:
                cfg_label = "sub_{:x}".format(cfg_addr)
        else:
            cfg_label = "unknown"

        label = self.node_tpl.format(label=cfg_label)

        return Node(cfg_addr, label=label, **self.node_format)

    def _create_edge(self, nodes, cfg_src_addr, cfg_dst_addr):
        if cfg_dst_addr == "unknown":
            branch_type = "indirect"
        else:
            branch_type = "direct"

        return Edge(nodes[cfg_src_addr], nodes[cfg_dst_addr], color=self.edge_color[branch_type], **self.edge_format)

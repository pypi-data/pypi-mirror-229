from coopgame.colors import Color
import pygame
from coopgraph.graphs import Graph, AStarResults
import coopgame.pygamehelpers as help
from typing import List, Callable, Iterable
import coopgame.grids_graphs.draw_graph_utils as utils
import coopgame.linedrawing.line_draw_utils as lutils
import coopgame.label_drawing.label_drawing_utils as labutils
from cooptools.coopEnum import CoopEnum
from coopgame.surfaceManager import SurfaceManager, SurfaceRegistryArgs
import coopgame.pointdrawing.point_draw_utils as putils
import cooptools.geometry_utils.vector_utils as vec

class GraphSurfaceType(CoopEnum):
    EDGES_SURFACE_ID = 'EDGES_SURFACE_ID'
    NODES_SURFACE_ID = 'NODES_SURFACE_ID'
    NODE_LABELS_SURFACE_ID = 'NODE_LABELS_SURFACE_ID'
    EDGE_LABELS_SURFACE_ID = 'EDGE_LABELS_SURFACE_ID'
    OVERLAY_SURFACE_ID = 'OVERLAY_SURFACE_ID'
    ROUTES_SURFACE_ID = 'ROUTES_SURFACE_ID'

DEFAULT_DRAW_CONFIG = utils.GraphDrawArgs(
            node_draw_args=putils.DrawPointArgs(
                color=Color.DARK_BLUE,
                radius=5,
            ),
            enabled_edge_args=lutils.DrawLineArgs(
                color=Color.ORANGE,
                directionality_draw_args=lutils.DirectionalityIndicatorDrawArgs(
                    color=Color.ORANGE,
                    height=10,
                    width=10
                ),
                draw_label_args=labutils.DrawLabelArgs(
                    color=Color.WHEAT
                )
            ),
            disabled_edge_args=lutils.DrawLineArgs(
                color=Color.BROWN,
                directionality_draw_args=lutils.DirectionalityIndicatorDrawArgs(
                    color=Color.BROWN,
                    height=10,
                    width=10
                ),
                draw_label_args=labutils.DrawLabelArgs(
                    color=Color.BROWN
                )
            ),
            node_label_args=labutils.DrawLabelArgs(
                color=Color.WHEAT
            ),
            articulation_points_args=putils.DrawPointArgs(
                outline_color=Color.PURPLE,
                radius=10,
                outline_width=3
            ),
            sink_node_args=putils.DrawPointArgs(
                color=Color.RED,
                radius=10
            ),
            source_node_args=putils.DrawPointArgs(
                color=Color.GREEN,
                radius=10
            ),
            orphan_node_args=putils.DrawPointArgs(
                outline_color=Color.RED,
                radius=10
            )
        )

GraphGetter = Callable[[], Graph]
RouteDrawArgsGetter = Callable[[], List[utils.RouteDrawArgs]]

class PyGraphHandler:
    def __init__(self,
                 screen: pygame.Surface,
                 graph_getter: GraphGetter,
                 draw_config: utils.GraphDrawArgs = None,
                 route_draw_args_getter: RouteDrawArgsGetter = None,
                 vec_transformer: vec.VecTransformer = None):
        self.parent_screen = screen
        self.graph_getter = graph_getter
        self._draw_config: utils.GraphDrawArgs = draw_config if draw_config else DEFAULT_DRAW_CONFIG
        self._route_draw_args_getter = route_draw_args_getter
        self._vec_transformer = vec_transformer

        self.surface_manager = SurfaceManager(
            surface_draw_callbacks=[
                SurfaceRegistryArgs(GraphSurfaceType.EDGES_SURFACE_ID.value, self.redraw_edges_surface),
                SurfaceRegistryArgs(GraphSurfaceType.NODES_SURFACE_ID.value, self.redraw_nodes_surface),
                SurfaceRegistryArgs(GraphSurfaceType.EDGE_LABELS_SURFACE_ID.value, self.redraw_edge_labels_surface),
                SurfaceRegistryArgs(GraphSurfaceType.NODE_LABELS_SURFACE_ID.value, self.redraw_node_labels_surface),
                SurfaceRegistryArgs(GraphSurfaceType.OVERLAY_SURFACE_ID.value, self.redraw_overlay_surface),
                SurfaceRegistryArgs(GraphSurfaceType.ROUTES_SURFACE_ID.value, self.redraw_routes_surface),
            ]
        )

    def set_config(self,
                   draw_config: utils.GraphDrawArgs):
        self._draw_config = draw_config

    def redraw_edges_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.EdgesBaseArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_nodes_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.NodesBaseArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_node_labels_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.NodesLabelArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_edge_labels_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.EdgesLabelArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_overlay_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())
        utils.draw_to_surface(
            surface=surf,
            graph=self.graph_getter(),
            args=self._draw_config.OverlayArgs,
            vec_transformer=self._vec_transformer
        )
        return surf

    def redraw_routes_surface(self):
        surf = help.init_surface(self.parent_screen.get_size())

        if self._route_draw_args_getter is not None:
            utils.draw_to_surface(
                surface=surf,
                graph=self.graph_getter(),
                routes=self._route_draw_args_getter(),
                vec_transformer=self._vec_transformer
            )

        return surf


    def update(self):
        # No surfaces require redrawing every iteration
        pass

    def invalidate(self, surfaces: Iterable[GraphSurfaceType]):
        self.surface_manager.invalidate([x.name for x in surfaces])

    def redraw(self):
        self.surface_manager.redraw([x.name for x in GraphSurfaceType])

    def render(self,
               surface: pygame.Surface):
        self.update()
        self.surface_manager.render(surface)

    def toggle_surface(self, graphSurfaceTypes: List[GraphSurfaceType]):
        self.surface_manager.toggle_visible([x.value for x in graphSurfaceTypes])

    def show_all(self):
        self.surface_manager.show_all()

    def hide_all(self):
        self.surface_manager.hide_all()

import mujoco_viewer
import numpy as np
from mujoco._structs import MjData, MjModel

from ..configs import ViewCfg


class View:
    """A class that uses mujoco_viewer to render MuJoCo. Used by the main FullSimulation class to make rendering user-friendly."""

    def __init__(self, cfg: ViewCfg):
        # translate AI gym modes to mujoco_viewer modes if necessary
        if cfg.mode == "human":
            self.mode = "window"
        elif cfg.mode == "rgb_array":
            self.mode = "offscreen"
        else:
            self.mode = cfg.mode
        self.window_width = cfg.window_width
        self.window_height = cfg.window_height
        self.viewer = None

    def render(self, model: MjModel, data: MjData) -> np.ndarray | None:
        if self.viewer is None:
            self.viewer = mujoco_viewer.MujocoViewer(
                model,
                data,
                self.mode,
                width=self.window_width,
                height=self.window_height,
            )
        self.viewer.data, self.viewer.model = data, model
        if self.mode == "window":
            self.viewer.render()
        else:
            return self.viewer.read_pixels()

    def close(self):
        self.viewer.close()

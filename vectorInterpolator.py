class VectorInterpolator:
    def __init__(self, nodes=[]):
        self.nodes = nodes
        self.interpolation = ""

    def setNodes(self, nodes):
        self.interpolation = ""
        self.nodes = nodes

    def interpolate(self):
        self.interpolation = " ".join(self.nodes)
        return self.interpolation


if __name__ == "__main__":
    nodes = [
        "story",
        "crazy"
    ]
    interpolator = VectorInterpolator(nodes)
    print(interpolator.interpolate())

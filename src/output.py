
class Output:
    def __init__(self, file_path):
        self.file_path = file_path
        self.out = []

    def _action(self, action, a, b, c, d):
        self.out.append(str(a) + " " + action + " " + str(b) + " " + str(c) + " " + str(d))

    def load(self, d_id, w_id, p_id, p_qty):
        self._action("L", d_id, w_id, p_id, p_qty)

    def unload(self, d_id, w_id, p_id, p_qty):
        self._action("U", d_id, w_id, p_id, p_qty)

    def deliver(self, d_id, o_id, p_id, p_qty):
        self._action("D", d_id, o_id, p_id, p_qty)

    def wait(self, d_id, turns):
        self.out.append(str(d_id) + " W " + str(turns))

    def write_to_file(self):
        with open(self.file_path, "w") as f:
            self.out.insert(0, str(len(self.out)))
            f.write("\n".join(self.out))

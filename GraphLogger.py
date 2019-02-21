
#DOESNT WORK YET
from ray.tune.logger import Logger
import tensorflow as tf

class GraphLogger(Logger):
    def _init(self):
        self._file_writer = tf.summary.FileWriter(self.logdir)

    def on_result(self, result):
        self._file_writer.add_graph(tf.get_default_graph())
        self._file_writer.flush()

    def flush(self):
        self._file_writer.flush()

    def close(self):
        self._file_writer.close()

from ray.tune.logger import _TFLogger, to_tf_values
import tensorflow as tf
import numpy as np
import os
from util import _calculate_green_time

def create_HistogramProto(values, bins = 9):
    """Returns a tf.HistogramProto from values
    https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/framework/summary.proto#L30

    Input:
        values : an array of numbers
        bins   : number of bins
    Returns:
        tf.HistogramProto
    """

    # Create histogram using numpy
    counts, bin_edges = np.histogram(values, bins=bins)

    # Fill fields of histogram proto
    hist = tf.HistogramProto()
    hist.min = float(np.min(values))
    hist.max = float(np.max(values))
    hist.num = int(np.prod(values.shape))
    hist.sum = float(np.sum(values))
    hist.sum_squares = float(np.sum(values**2))

    # since first bucket is from -DBL_MAX to bucket_limit(0)
    bin_edges = bin_edges[1:]
    # Add bin edges and counts
    for edge in bin_edges:
        hist.bucket_limit.append(edge)
    for c in counts:
        hist.bucket.append(c)

    return hist

class ActionLogger(_TFLogger):

    def _init(self):
        _LOG_DIR = os.path.join(self.logdir, 'custom_events')
        print("ActionLogger Logging at " , _LOG_DIR)
        if not os.path.exists(_LOG_DIR):
            os.makedirs(_LOG_DIR)
        self._file_writer = tf.summary.FileWriter(_LOG_DIR)

    def on_result(self, result):
        # === From _TFLogger ===
        tmp = result.copy()
##        for k in [
##                "config", "pid", "timestamp", "time_total_s", "training_iteration"
##        ]:
##            if k in tmp:
##                del tmp[k]  # not useful to tf log these
##        values = to_tf_values(tmp, ["ray", "tune"])
##        train_stats = tf.Summary(value=values)
        t = result.get("timesteps_total") or result["training_iteration"]
##        self._file_writer.add_summary(train_stats, t)
##        iteration_value = to_tf_values({
##            "training_iteration": result["training_iteration"]
##        }, ["ray", "tune"])
##        iteration_stats = tf.Summary(value=iteration_value)
##        self._file_writer.add_summary(iteration_stats, t)
        # =========================
        
        actions = tmp['actions']
        # note that bin_edges will return not exact 0..9, but is correct
        #     can check with:
        # >> unique, counts = np.unique(values, return_counts=True)
        # >> np.asarray((unique, counts)).T

        # print("i am now logging actions", _actions, " timesteps ", t)
        _hist = create_HistogramProto(np.array(actions), bins=9)
        action_stats = tf.Summary(value = [tf.Summary.Value(tag="actions", histo=_hist)])
        self._file_writer.add_summary(action_stats, t)

        # Flush a lot before Segmentation Fault
        self._file_writer.flush()

        _green_times = _calculate_green_time(actions, 10 ,5)
        for phase in _green_times:
            _hist = create_HistogramProto(np.array(_green_times[phase]), bins=15)
            action_stats = tf.Summary(value = [tf.Summary.Value(tag="action_green_time_{}".format(phase), histo=_hist)])
            self._file_writer.add_summary(action_stats, t)

            # Flush a lot before Segmentation Fault
            if phase%3 == 0 and phase != 0:
                self._file_writer.flush()

        self._file_writer.flush()


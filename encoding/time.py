import numpy as np


class TimeEncoder:
    def __call__(self, size: int, depth: int, time_diff: float):
        if size <= 0:
            return np.array([])
        if time_diff == 0:
            return np.zeros((size,))
        time_vec = np.arange(1, size + 1, dtype=np.float32)
        depth_vec = np.arange(1, depth + 1, dtype=np.float32)
        depth_vec = np.sqrt(depth_vec) / depth
        time_vec = time_vec * time_diff
        per_time_vec = np.sin(time_vec * 2 * np.pi) / time_diff / size
        log_time_vec = np.log(time_vec) / time_diff / size
        time_vec = per_time_vec
        time_vec = np.matmul(depth_vec[:, None], time_vec[None, :])
        time_vec += log_time_vec[None, :]
        time_vec -= np.min(time_vec)
        return time_vec


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    size = 1000
    depth = 100
    t_vec = TimeEncoder()(size, depth, 0.01)
    plt.pcolormesh(t_vec, cmap='RdBu')
    plt.ylabel('Depth')
    plt.xlabel('Position')
    plt.colorbar()
    plt.show()

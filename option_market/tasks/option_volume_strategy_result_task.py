from core.utils import task_timing
from option_market.utils import get_option_volume_strategy_result
from tqdm import tqdm


@task_timing
def option_volume_strategy_result():
    m = [2, 3, 4, 5, 6, 7]
    d = [4, 5, 6, 7, 8, 9, 10]
    t = [0, 20, 40]

    number_of_loops = len(m) * len(d) * len(t)
    progress_bar = tqdm(total=number_of_loops, desc="Volume strategy", ncols=10)

    for volume_change_ratio in m:
        for return_period in d:
            for threshold in t:
                get_option_volume_strategy_result(
                    volume_change_ratio=volume_change_ratio,
                    return_period=return_period,
                    threshold=threshold,
                )
                progress_bar.update(1)

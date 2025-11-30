from collections import defaultdict

metrics = defaultdict(int)

def inc(key: str):
    metrics[key] += 1

def get_metrics():
    return dict(metrics)
from pylsl import StreamOutlet, local_clock

def push_sample_current_time(outlet, sample = []):
    outlet.push_sample(sample, local_clock())